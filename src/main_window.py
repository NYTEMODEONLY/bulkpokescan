"""Main application window for BulkPokeScan."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
from PyQt5.QtCore import QRectF, QSize, Qt, QTimer, QUrl
from PyQt5.QtGui import (QBrush, QColor, QDesktopServices, QFont, QIcon,
                          QImage, QKeySequence, QPainter, QPen, QPixmap)
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkReply,
                              QNetworkRequest)
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QFrame,
                              QHBoxLayout, QLabel, QListWidget,
                              QListWidgetItem, QMainWindow, QMessageBox,
                              QPushButton, QShortcut, QSizePolicy,
                              QStackedWidget, QTabWidget, QTextEdit,
                              QVBoxLayout, QWidget)

from src.config import Config
from src.dialogs import AboutDialog, AddCodeDialog, SettingsDialog
from src.scanner import QRScanner
from src.theme import (FONT_BODY, FONT_DISPLAY, FONT_MONO, build_app_icon,
                        color, paint_pokeball)
from src.widgets import (CameraView, CodeRow, EmptyStatePanel, EnergyStrip,
                          FooterLink, Moon, SectionTitle, StatusIndicator,
                          Toast)


SESSION_DIR = Path.home() / ".bulkpokescan"
SESSION_FILE = SESSION_DIR / "session.json"
ALL_CODES_LABEL = "All Codes (Complete Export)"
BLOCK_SIZE = 10
NYTEMODE_URL = "https://nytemode.com"
APP_VERSION = "1.4.2"

# Global tally — same endpoint that the web app uses. Counts only,
# never the codes themselves. Failures are silent.
TALLY_URL = "https://bulkpokescan.vercel.app/api/tally"
TALLY_POLL_MS = 60_000
TALLY_USER_AGENT = f"BulkPokeScan-Desktop/{APP_VERSION}"

FORMAT_NUMBERED = "Numbered List"
FORMAT_RAW = "Raw Codes (one per line)"
FORMAT_SPACE = "Space-Separated"
FORMAT_COMMA = "Comma-Separated"
FORMATS = [FORMAT_NUMBERED, FORMAT_RAW, FORMAT_SPACE, FORMAT_COMMA]


def _icon_about(size: int = 16) -> QIcon:
    pix = QPixmap(size * 2, size * 2)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor(color("text_2")), 2))
    painter.setBrush(Qt.NoBrush)
    s = size * 2
    painter.drawEllipse(QRectF(2, 2, s - 4, s - 4))
    # i — dot + bar
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(color("text_2")))
    painter.drawEllipse(QRectF(s / 2 - 1.5, s * 0.30, 3, 3))
    painter.fillRect(QRectF(s / 2 - 1.5, s * 0.45, 3, s * 0.30),
                       QColor(color("text_2")))
    painter.end()
    return QIcon(pix)


def _icon_settings(size: int = 16) -> QIcon:
    pix = QPixmap(size * 2, size * 2)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    s = size * 2
    cx, cy = s / 2, s / 2
    painter.setPen(QPen(QColor(color("text_2")), 1.8))
    painter.setBrush(Qt.NoBrush)
    # Outer cog: 8 small notches
    import math
    outer_r = s * 0.40
    notch = s * 0.08
    inner_r = outer_r - notch
    pts = []
    for i in range(16):
        angle = i * math.pi / 8
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    from PyQt5.QtGui import QPolygonF
    from PyQt5.QtCore import QPointF
    poly = QPolygonF([QPointF(x, y) for x, y in pts])
    painter.drawPolygon(poly)
    # Center hole
    painter.drawEllipse(QRectF(cx - s * 0.13, cy - s * 0.13,
                                  s * 0.26, s * 0.26))
    painter.end()
    return QIcon(pix)


def _icon_plus(size: int = 14) -> QIcon:
    pix = QPixmap(size * 2, size * 2)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor("white"), 2.8, Qt.SolidLine, Qt.RoundCap))
    s = size * 2
    painter.drawLine(int(s / 2), int(s * 0.25), int(s / 2), int(s * 0.75))
    painter.drawLine(int(s * 0.25), int(s / 2), int(s * 0.75), int(s / 2))
    painter.end()
    return QIcon(pix)


def _icon_brand_mark(size: int = 42) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    paint_pokeball(painter, QRectF(0, 0, size, size))
    painter.end()
    return pix


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BulkPokeScan")
        self.setMinimumSize(1180, 760)
        self.setWindowIcon(build_app_icon())

        self.config = Config()
        self.scanner = QRScanner()

        self.codes_found: List[str] = []
        self.code_sources: Dict[str, str] = {}  # code -> "scan" | "manual"
        self._undo_stack: List[Tuple[List[str], Dict[str, str]]] = []

        self.last_scan_time = 0.0

        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self._update_frame)
        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self._auto_scan)

        # Global tally — async HTTP via Qt's network stack
        self.nam = QNetworkAccessManager(self)
        self.nam.finished.connect(self._on_tally_reply)
        self.tally_timer = QTimer(self)
        self.tally_timer.setInterval(TALLY_POLL_MS)
        self.tally_timer.timeout.connect(self._fetch_tally)

        self._build_ui()
        self._install_shortcuts()
        self._load_session()
        self._refresh_codes_view()
        self._fetch_tally()
        self.tally_timer.start()

        self.statusBar().showMessage("Ready to scan Pokémon TCG codes")

    # =================================================================== UI

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(28, 20, 28, 20)
        body_layout.setSpacing(20)
        body_layout.addWidget(self._build_scanner_card(), 5)
        body_layout.addWidget(self._build_codes_card(), 6)
        root.addWidget(body, 1)

        root.addWidget(self._build_footer())

        self.toast = Toast(central)

    # ----- header -----

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 16, 22, 14)
        layout.setSpacing(14)

        # Brand mark
        ball_label = QLabel()
        ball_label.setFixedSize(42, 42)
        ball_label.setPixmap(_icon_brand_mark(42))
        layout.addWidget(ball_label, 0, Qt.AlignVCenter)

        # Brand text stack
        brand_text = QVBoxLayout()
        brand_text.setContentsMargins(0, 0, 0, 0)
        brand_text.setSpacing(3)

        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(0)
        name = QLabel("Bulk")
        name.setObjectName("brandName")
        name_row.addWidget(name)
        pro = QLabel("PokeScan")
        pro.setObjectName("brandPro")
        name_row.addWidget(pro)
        name_row.addStretch(1)
        brand_text.addLayout(name_row)

        tag = QLabel("POKÉMON · TCG CODE SCANNER")
        tag.setObjectName("brandTag")
        brand_text.addWidget(tag)
        layout.addLayout(brand_text)

        # Energy strip decoration
        layout.addSpacing(10)
        layout.addWidget(EnergyStrip())
        layout.addStretch(1)

        # Global tally badge (cyan, live counter shared with the web app)
        self.global_badge = QLabel("— SCANNED")
        self.global_badge.setObjectName("globalBadge")
        self.global_badge.setToolTip(
            "Total codes scanned globally with BulkPokeScan\n"
            "(web + desktop combined)"
        )
        layout.addWidget(self.global_badge, 0, Qt.AlignVCenter)

        # Header count badge (yellow — this user's session)
        self.header_count = QLabel("NO CODES YET")
        self.header_count.setObjectName("headerBadge")
        self.header_count.setToolTip("Codes captured in this session")
        layout.addWidget(self.header_count, 0, Qt.AlignVCenter)

        # Icon buttons
        self.about_button = QPushButton()
        self.about_button.setObjectName("iconButton")
        self.about_button.setIcon(_icon_about(16))
        self.about_button.setToolTip("About BulkPokeScan")
        self.about_button.setCursor(Qt.PointingHandCursor)
        self.about_button.clicked.connect(self._show_about)
        layout.addWidget(self.about_button, 0, Qt.AlignVCenter)

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("iconButton")
        self.settings_button.setIcon(_icon_settings(16))
        self.settings_button.setToolTip("Settings  (⌘,)")
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.clicked.connect(self._show_settings)
        layout.addWidget(self.settings_button, 0, Qt.AlignVCenter)

        return header

    # ----- scanner card -----

    def _build_scanner_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("scannerCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(SectionTitle("SCANNER", accent=color("red")))
        head.addStretch(1)
        self.camera_status = StatusIndicator()
        head.addWidget(self.camera_status, 0, Qt.AlignVCenter)
        layout.addLayout(head)

        cam_frame = QFrame()
        cam_frame.setStyleSheet(
            f"background-color: #050507;"
            f" border: 1px solid {color('border')};"
            f" border-radius: 12px;"
        )
        cam_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cam_layout = QVBoxLayout(cam_frame)
        cam_layout.setContentsMargins(2, 2, 2, 2)
        self.camera_view = CameraView()
        cam_layout.addWidget(self.camera_view)
        layout.addWidget(cam_frame, 1)

        # Tip strip
        tip = QFrame()
        tip.setObjectName("tipStrip")
        tip_layout = QHBoxLayout(tip)
        tip_layout.setContentsMargins(14, 10, 14, 10)
        tip_layout.setSpacing(10)
        tag = QLabel("TIP")
        tag.setObjectName("tipTag")
        tip_layout.addWidget(tag, 0, Qt.AlignVCenter)
        tip_text = QLabel(
            "Hold the QR code 6–12 inches from the lens with even "
            "lighting for fastest captures.")
        tip_text.setObjectName("tipText")
        tip_text.setWordWrap(True)
        tip_layout.addWidget(tip_text, 1, Qt.AlignVCenter)
        layout.addWidget(tip)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.start_button = QPushButton("Start Camera")
        self.start_button.setProperty("variant", "primary")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.toggle_camera)
        controls.addWidget(self.start_button, 1)

        self.scan_button = QPushButton("Scan Now")
        self.scan_button.setProperty("variant", "secondary")
        self.scan_button.setCursor(Qt.PointingHandCursor)
        self.scan_button.setMinimumHeight(40)
        self.scan_button.setEnabled(False)
        self.scan_button.clicked.connect(self.manual_scan)
        controls.addWidget(self.scan_button, 1)

        layout.addLayout(controls)
        return card

    # ----- codes card -----

    def _build_codes_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("codesCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(0)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(SectionTitle("CODES", accent=color("yellow")))
        head.addStretch(1)
        self.codes_count_badge = QLabel("0 CAPTURED")
        self.codes_count_badge.setObjectName("countBadgeYellow")
        head.addWidget(self.codes_count_badge, 0, Qt.AlignVCenter)
        layout.addLayout(head)

        layout.addSpacing(14)

        self.code_tabs = QTabWidget()
        self.code_tabs.setObjectName("codeTabs")
        self.code_tabs.addTab(self._build_all_codes_tab(), "All Codes")
        self.code_tabs.addTab(self._build_blocks_tab(), "Code Blocks")
        layout.addWidget(self.code_tabs, 1)

        return card

    def _build_all_codes_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        self.codes_stack = QStackedWidget()
        self.codes_empty = EmptyStatePanel(
            title="No codes captured yet",
            hint=("Press Start Camera to begin scanning, or use Add Code "
                  "to enter one manually."),
        )
        self.codes_stack.addWidget(self.codes_empty)

        # Wrap the list in a frame for the rounded background
        self.codes_list_wrap = QFrame()
        self.codes_list_wrap.setObjectName("codesListWrap")
        wrap_layout = QVBoxLayout(self.codes_list_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)

        self.codes_list = QListWidget()
        self.codes_list.setObjectName("codesList")
        self.codes_list.setSelectionMode(QListWidget.ExtendedSelection)
        wrap_layout.addWidget(self.codes_list)

        self.codes_stack.addWidget(self.codes_list_wrap)
        layout.addWidget(self.codes_stack, 1)

        # Action row
        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.add_manual_button = QPushButton("Add Code")
        self.add_manual_button.setIcon(_icon_plus(14))
        self.add_manual_button.setProperty("variant", "primary")
        self.add_manual_button.setCursor(Qt.PointingHandCursor)
        self.add_manual_button.clicked.connect(self.add_code_manually)
        actions.addWidget(self.add_manual_button)

        actions.addStretch(1)

        self.copy_all_button = QPushButton("Copy All")
        self.copy_all_button.setCursor(Qt.PointingHandCursor)
        self.copy_all_button.clicked.connect(self.copy_all_codes)
        actions.addWidget(self.copy_all_button)

        self.export_txt_button = QPushButton("Export TXT")
        self.export_txt_button.setProperty("variant", "secondary")
        self.export_txt_button.setCursor(Qt.PointingHandCursor)
        self.export_txt_button.clicked.connect(lambda: self._export_to_file("txt"))
        actions.addWidget(self.export_txt_button)

        self.export_md_button = QPushButton("Export MD")
        self.export_md_button.setProperty("variant", "secondary")
        self.export_md_button.setCursor(Qt.PointingHandCursor)
        self.export_md_button.clicked.connect(lambda: self._export_to_file("md"))
        actions.addWidget(self.export_md_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setProperty("variant", "ghost")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_codes)
        actions.addWidget(self.clear_button)

        layout.addLayout(actions)
        return page

    def _build_blocks_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)

        controls = QHBoxLayout()
        controls.setSpacing(14)

        block_col = QVBoxLayout()
        block_col.setSpacing(6)
        block_label = QLabel("BLOCK")
        block_label.setObjectName("fieldLabel")
        block_col.addWidget(block_label)
        self.block_selector = QComboBox()
        self.block_selector.currentIndexChanged.connect(self._render_block)
        block_col.addWidget(self.block_selector)
        controls.addLayout(block_col, 1)

        fmt_col = QVBoxLayout()
        fmt_col.setSpacing(6)
        fmt_label = QLabel("FORMAT")
        fmt_label.setObjectName("fieldLabel")
        fmt_col.addWidget(fmt_label)
        self.format_selector = QComboBox()
        self.format_selector.addItems(FORMATS)
        self.format_selector.currentIndexChanged.connect(self._render_block)
        fmt_col.addWidget(self.format_selector)
        controls.addLayout(fmt_col, 1)

        layout.addLayout(controls)

        self.block_display = QTextEdit()
        self.block_display.setObjectName("blockDisplay")
        self.block_display.setReadOnly(True)
        layout.addWidget(self.block_display, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch(1)

        self.copy_block_button = QPushButton("Copy Block")
        self.copy_block_button.setProperty("variant", "primary")
        self.copy_block_button.setCursor(Qt.PointingHandCursor)
        self.copy_block_button.clicked.connect(self.copy_current_block)
        actions.addWidget(self.copy_block_button)

        self.export_block_txt_button = QPushButton("Export TXT")
        self.export_block_txt_button.setProperty("variant", "secondary")
        self.export_block_txt_button.setCursor(Qt.PointingHandCursor)
        self.export_block_txt_button.clicked.connect(lambda: self._export_to_file("txt"))
        actions.addWidget(self.export_block_txt_button)

        self.export_block_md_button = QPushButton("Export MD")
        self.export_block_md_button.setProperty("variant", "secondary")
        self.export_block_md_button.setCursor(Qt.PointingHandCursor)
        self.export_block_md_button.clicked.connect(lambda: self._export_to_file("md"))
        actions.addWidget(self.export_block_md_button)

        layout.addLayout(actions)
        return page

    # ----- footer -----

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("footer")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(28, 10, 28, 10)
        layout.setSpacing(14)

        ver = QLabel(f"V{APP_VERSION}")
        ver.setObjectName("footerText")
        layout.addWidget(ver)

        sep1 = QLabel("·")
        sep1.setObjectName("footerText")
        layout.addWidget(sep1)

        # local-processing dot
        dot = QFrame()
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(
            f"background-color: {color('success')};"
            f" border-radius: 3px;"
        )
        layout.addWidget(dot, 0, Qt.AlignVCenter)
        local = QLabel("LOCAL PROCESSING ONLY")
        local.setObjectName("footerText")
        layout.addWidget(local)

        layout.addStretch(1)

        about_link = FooterLink("ABOUT")
        about_link.clicked.connect(self._show_about)
        layout.addWidget(about_link)

        sep3 = QLabel("·")
        sep3.setObjectName("footerText")
        layout.addWidget(sep3)

        # nytemode credit  → "☾ a nytemode project"
        nyte_layout = QHBoxLayout()
        nyte_layout.setContentsMargins(0, 0, 0, 0)
        nyte_layout.setSpacing(6)
        nyte_layout.addWidget(Moon(10), 0, Qt.AlignVCenter)
        a_label = QLabel("A")
        a_label.setObjectName("footerNyte")
        nyte_layout.addWidget(a_label)
        nyte_link = FooterLink("NYTEMODE", url=NYTEMODE_URL)
        nyte_layout.addWidget(nyte_link)
        proj_label = QLabel("PROJECT")
        proj_label.setObjectName("footerNyte")
        nyte_layout.addWidget(proj_label)

        nyte_widget = QWidget()
        nyte_widget.setLayout(nyte_layout)
        layout.addWidget(nyte_widget, 0, Qt.AlignVCenter)

        return footer

    # ============================================================ shortcuts

    def _install_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+,"), self, activated=self._show_settings)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.toggle_camera)
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.manual_scan)
        QShortcut(QKeySequence("Ctrl+E"), self,
                   activated=lambda: self._export_to_file("txt"))
        QShortcut(QKeySequence("Ctrl+Shift+E"), self,
                   activated=lambda: self._export_to_file("md"))
        QShortcut(QKeySequence("Ctrl+Shift+C"), self,
                   activated=self.copy_all_codes)
        QShortcut(QKeySequence("Ctrl+Z"), self, activated=self._undo)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.add_code_manually)

    # ============================================================ camera

    def toggle_camera(self):
        if self.capture_timer.isActive():
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        try:
            ok = self.scanner.start_camera(self.config.camera_index)
        except Exception as exc:
            QMessageBox.critical(self, "Camera Error",
                                  f"Failed to start camera: {exc}")
            return
        if not ok:
            QMessageBox.critical(
                self, "Camera Error",
                f"Could not open camera at index {self.config.camera_index}.")
            return

        self.capture_timer.start(30)
        if self.config.auto_detect:
            self.scan_timer.start(self.config.scan_interval)
            self.camera_view.set_state(CameraView.SCANNING)
            self.camera_status.set_state(StatusIndicator.SCANNING)
        else:
            self.camera_view.set_state(CameraView.LIVE)
            self.camera_status.set_state(StatusIndicator.LIVE)

        self.scan_button.setEnabled(True)
        self.start_button.setText("Stop Camera")
        self.start_button.setProperty("variant", "danger")
        self._restyle(self.start_button)
        self.statusBar().showMessage("Scanning… show a TCG code to the camera")

    def _stop_camera(self):
        self.capture_timer.stop()
        self.scan_timer.stop()
        self.scanner.stop_camera()
        self.camera_view.set_state(CameraView.OFF)
        self.camera_status.set_state(StatusIndicator.OFF)
        self.scan_button.setEnabled(False)
        self.start_button.setText("Start Camera")
        self.start_button.setProperty("variant", "primary")
        self._restyle(self.start_button)
        self.statusBar().showMessage("Camera stopped")

    def _update_frame(self):
        frame = self.scanner.get_frame()
        if frame is None:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.camera_view.set_frame(QPixmap.fromImage(img))

    def _auto_scan(self):
        if time.time() - self.last_scan_time < self.config.scan_cooldown:
            return
        self._scan_current_frame()

    def manual_scan(self):
        if not self.capture_timer.isActive():
            return
        self._scan_current_frame(manual=True)

    def _scan_current_frame(self, manual: bool = False):
        frame = self.scanner.get_frame()
        if frame is None:
            return
        codes = self.scanner.scan_qr_code(frame)
        if not codes:
            if manual:
                self.statusBar().showMessage(
                    "No QR code detected in the current frame")
            return
        code = codes[0]["data"]
        self.last_scan_time = time.time()
        self._handle_detected_code(code)

    def _handle_detected_code(self, code: str):
        if not code:
            return
        if code in self.codes_found:
            self.statusBar().showMessage(f"Already captured: {code}")
            return
        self._add_code(code, source="scan")

    # ============================================================ codes

    def add_code_manually(self):
        dialog = AddCodeDialog(self)
        if not dialog.exec_():
            return
        code = dialog.value()
        if not code:
            return
        if code in self.codes_found:
            self.statusBar().showMessage(f"Already captured: {code}")
            return
        self._add_code(code, source="manual")

    def _add_code(self, code: str, source: str = "scan"):
        self._push_undo_snapshot()
        self.codes_found.append(code)
        self.code_sources[code] = source
        self._refresh_codes_view()
        self._save_session()
        self._post_tally()

        if source == "scan" and self.config.flash:
            self.camera_view.flash_success()
        verb = "Captured" if source == "scan" else "Added"
        self.toast.show_message(verb, code=code)
        self.statusBar().showMessage(f"{len(self.codes_found)} codes captured")

    def clear_codes(self):
        if not self.codes_found:
            return
        confirm = QMessageBox.question(
            self, "Clear all codes?",
            f"Remove all {len(self.codes_found)} captured codes?\n"
            "You can undo this with ⌘Z (Ctrl+Z).",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel)
        if confirm != QMessageBox.Yes:
            return
        self._push_undo_snapshot()
        self.codes_found = []
        self.code_sources = {}
        self._refresh_codes_view()
        self._save_session()
        self.toast.show_message("Cleared all codes — ⌘Z to undo",
                                  show_check=False)
        self.statusBar().showMessage("Cleared all codes — ⌘Z to undo")

    def copy_all_codes(self):
        if not self.codes_found:
            self.toast.show_message("Nothing to copy yet", show_check=False)
            return
        QApplication.clipboard().setText("\n".join(self.codes_found))
        n = len(self.codes_found)
        self.toast.show_message(f"Copied {n} code{'s' if n != 1 else ''} "
                                  f"to clipboard")

    def copy_current_block(self):
        block_codes, label, start_idx = self._current_block()
        if not block_codes:
            self.toast.show_message("Nothing to copy in this block",
                                      show_check=False)
            return
        text = self._format_codes(block_codes, start_idx,
                                    self.format_selector.currentText())
        QApplication.clipboard().setText(text)
        self.toast.show_message(f"Copied {label} · {len(block_codes)} codes")

    # ============================================================ render

    def _refresh_codes_view(self):
        n = len(self.codes_found)

        if n == 0:
            self.header_count.setText("NO CODES YET")
        elif n == 1:
            self.header_count.setText("1 CODE CAPTURED")
        else:
            self.header_count.setText(f"{n} CODES CAPTURED")
        self.codes_count_badge.setText(
            "0 CAPTURED" if n == 0 else f"{n} CAPTURED")
        self.code_tabs.setTabText(0, f"All Codes  ·  {n}")
        self.code_tabs.setTabText(1, f"Code Blocks  ·  {self._block_count()}")

        if n == 0:
            self.codes_stack.setCurrentWidget(self.codes_empty)
            self.codes_list.clear()
        else:
            self.codes_stack.setCurrentWidget(self.codes_list_wrap)
            self.codes_list.clear()
            for i, code in enumerate(self.codes_found, 1):
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 44))
                self.codes_list.addItem(item)
                source = self.code_sources.get(code, "scan")
                row_widget = CodeRow(i, code, source=source)
                self.codes_list.setItemWidget(item, row_widget)

        prev = self.block_selector.currentText()
        self.block_selector.blockSignals(True)
        self.block_selector.clear()
        if n > 0:
            self.block_selector.addItem(ALL_CODES_LABEL)
            for i in range(self._block_count()):
                start = i * BLOCK_SIZE + 1
                end = min(start + BLOCK_SIZE - 1, n)
                self.block_selector.addItem(f"Block {i + 1}  ·  {start}–{end}")
            idx = self.block_selector.findText(prev)
            self.block_selector.setCurrentIndex(idx if idx >= 0 else 0)
        self.block_selector.blockSignals(False)
        self._render_block()

        has_codes = n > 0
        for btn in (self.clear_button, self.copy_all_button,
                     self.export_txt_button, self.export_md_button,
                     self.copy_block_button, self.export_block_txt_button,
                     self.export_block_md_button):
            btn.setEnabled(has_codes)

    def _block_count(self) -> int:
        if not self.codes_found:
            return 0
        return (len(self.codes_found) + BLOCK_SIZE - 1) // BLOCK_SIZE

    def _current_block(self) -> tuple:
        if not self.codes_found:
            return [], "", 0
        idx = self.block_selector.currentIndex()
        text = self.block_selector.currentText()
        if idx <= 0 or text == ALL_CODES_LABEL:
            return list(self.codes_found), "All Codes", 0
        block_idx = idx - 1
        start = block_idx * BLOCK_SIZE
        end = min(start + BLOCK_SIZE, len(self.codes_found))
        return self.codes_found[start:end], f"Block {block_idx + 1}", start

    def _render_block(self):
        block_codes, _label, start_idx = self._current_block()
        if not block_codes:
            self.block_display.setProperty("empty", "true")
            self.block_display.setText(
                "Capture some codes and they'll appear here.")
        else:
            self.block_display.setProperty("empty", "false")
            self.block_display.setText(self._format_codes(
                block_codes, start_idx, self.format_selector.currentText()))
        self._restyle(self.block_display)

    @staticmethod
    def _format_codes(codes: List[str], start_idx: int, fmt: str) -> str:
        if fmt == FORMAT_NUMBERED:
            return "".join(f"{start_idx + i + 1}. {c}\n"
                            for i, c in enumerate(codes))
        if fmt == FORMAT_RAW:
            return "\n".join(codes)
        if fmt == FORMAT_SPACE:
            return " ".join(codes)
        if fmt == FORMAT_COMMA:
            return ",".join(codes)
        return "\n".join(codes)

    # ============================================================ export

    def _export_to_file(self, ext: str):
        if not self.codes_found:
            self.toast.show_message("Nothing to export yet", show_check=False)
            return
        default_name = f"pokemon_tcg_codes.{ext}"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Codes", default_name,
            f"{ext.upper()} Files (*.{ext})")
        if not path:
            return
        try:
            with open(path, "w") as f:
                f.write(self._render_export(ext))
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", str(exc))
            return
        self.toast.show_message(
            f"Exported {len(self.codes_found)} codes · "
            f"{os.path.basename(path)}")

    def _render_export(self, ext: str) -> str:
        fmt = self.format_selector.currentText()
        if ext == "md":
            n = len(self.codes_found)
            buf = ["# Pokémon TCG Codes\n",
                    f"_Exported from BulkPokeScan · {n} codes_\n\n"]
            if fmt == FORMAT_NUMBERED:
                buf.append("## Numbered List\n\n")
                for i, c in enumerate(self.codes_found, 1):
                    buf.append(f"{i}. `{c}`\n")
            elif fmt == FORMAT_RAW:
                buf.append("## Raw Codes\n\n```\n")
                buf.extend(f"{c}\n" for c in self.codes_found)
                buf.append("```\n")
            elif fmt == FORMAT_SPACE:
                buf.append("## Space-Separated\n\n```\n")
                buf.append(" ".join(self.codes_found))
                buf.append("\n```\n")
            else:
                buf.append("## Comma-Separated\n\n```\n")
                buf.append(",".join(self.codes_found))
                buf.append("\n```\n")
            return "".join(buf)
        return "\n".join(self.codes_found) + "\n"

    # ============================================================ undo

    def _push_undo_snapshot(self):
        self._undo_stack.append((list(self.codes_found),
                                   dict(self.code_sources)))
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _undo(self):
        if not self._undo_stack:
            self.toast.show_message("Nothing to undo", show_check=False)
            return
        self.codes_found, self.code_sources = self._undo_stack.pop()
        self._refresh_codes_view()
        self._save_session()
        self.statusBar().showMessage("Undid last change")

    # ============================================================ session

    def _load_session(self):
        if not SESSION_FILE.exists():
            return
        try:
            data = json.loads(SESSION_FILE.read_text())
            codes = data.get("codes", [])
            if isinstance(codes, list):
                self.codes_found = [str(c) for c in codes if c]
            sources = data.get("sources", {})
            if isinstance(sources, dict):
                self.code_sources = {
                    str(k): str(v) for k, v in sources.items()
                    if v in ("scan", "manual")
                }
            # Default unknown legacy codes to "scan" — most users captured
            # them with the camera before this field existed.
            for code in self.codes_found:
                self.code_sources.setdefault(code, "scan")
        except Exception:
            pass

    def _save_session(self):
        try:
            SESSION_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "codes": self.codes_found,
                "sources": {c: self.code_sources.get(c, "scan")
                              for c in self.codes_found},
            }
            SESSION_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    # ============================================================ misc

    def _show_settings(self):
        dialog = SettingsDialog(self, self.config)
        if not dialog.exec_():
            return
        for key, value in dialog.get_settings().items():
            self.config.update_setting(key, value)
        # Re-apply scan timer if running
        if self.scan_timer.isActive():
            self.scan_timer.stop()
            if self.config.auto_detect:
                self.scan_timer.start(self.config.scan_interval)
        # Re-evaluate camera state visualization
        if self.capture_timer.isActive():
            if self.config.auto_detect:
                self.camera_view.set_state(CameraView.SCANNING)
                self.camera_status.set_state(StatusIndicator.SCANNING)
            else:
                self.camera_view.set_state(CameraView.LIVE)
                self.camera_status.set_state(StatusIndicator.LIVE)
        self.statusBar().showMessage("Settings saved")

    def _show_about(self):
        AboutDialog(self).exec_()

    def _restyle(self, widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    # ============================================================ tally

    def _fetch_tally(self):
        request = QNetworkRequest(QUrl(TALLY_URL))
        request.setHeader(QNetworkRequest.UserAgentHeader, TALLY_USER_AGENT)
        self.nam.get(request)

    def _post_tally(self):
        request = QNetworkRequest(QUrl(TALLY_URL))
        request.setHeader(QNetworkRequest.UserAgentHeader, TALLY_USER_AGENT)
        request.setHeader(QNetworkRequest.ContentLengthHeader, 0)
        self.nam.post(request, b"")

    def _on_tally_reply(self, reply: QNetworkReply):
        try:
            if reply.error() == QNetworkReply.NoError:
                raw = bytes(reply.readAll()).decode("utf-8", errors="ignore")
                try:
                    payload = json.loads(raw)
                    total = payload.get("total")
                    if isinstance(total, int) and total >= 0:
                        self._set_global_total(total)
                except (json.JSONDecodeError, ValueError):
                    pass
        finally:
            reply.deleteLater()

    def _set_global_total(self, total: int):
        if total >= 1000:
            text = f"{total:,} SCANNED"
        else:
            text = f"{total} SCANNED"
        self.global_badge.setText(text)

    # ============================================================ qt events

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.toast.isVisible():
            self.toast._reposition()

    def closeEvent(self, event):
        self._save_session()
        self.scanner.stop_camera()
        event.accept()


