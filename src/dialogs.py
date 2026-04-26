"""Application modals: Settings, About, Add Code Manually."""

from PyQt5.QtCore import QRectF, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QPainter, QPixmap
from PyQt5.QtWidgets import (QDialog, QDoubleSpinBox, QFrame, QGridLayout,
                              QHBoxLayout, QLabel, QLineEdit, QPushButton,
                              QSpinBox, QVBoxLayout, QWidget)

from src.config import Config
from src.theme import FONT_BODY, FONT_DISPLAY, FONT_MONO, color, paint_pokeball
from src.widgets import Moon, Toggle


NYTEMODE_URL = "https://nytemode.com"


def _modal_chrome(dialog: QDialog) -> QVBoxLayout:
    """Apply the standard modal chrome — root layout returned for content."""
    dialog.setObjectName("modal")
    dialog.setModal(True)
    dialog.setWindowFlags(dialog.windowFlags() | Qt.Dialog)

    root = QVBoxLayout(dialog)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)
    return root


def _modal_header(text: str) -> QFrame:
    h = QFrame()
    h.setObjectName("modalHeader")
    layout = QHBoxLayout(h)
    layout.setContentsMargins(22, 16, 22, 16)
    label = QLabel(text)
    label.setObjectName("modalTitle")
    layout.addWidget(label)
    layout.addStretch(1)
    return h


def _modal_footer(buttons) -> QFrame:
    f = QFrame()
    f.setObjectName("modalFooter")
    layout = QHBoxLayout(f)
    layout.setContentsMargins(22, 14, 22, 14)
    layout.setSpacing(10)
    layout.addStretch(1)
    for b in buttons:
        layout.addWidget(b)
    return f


# =================================================================== settings

class SettingsDialog(QDialog):
    """Three-group settings panel matching the design's modal."""

    def __init__(self, parent=None, config: Config = None):
        super().__init__(parent)
        self.config = config or Config()
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Settings")
        self.setMinimumWidth(560)
        root = _modal_chrome(self)
        root.addWidget(_modal_header("Settings"))

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(22, 22, 22, 22)
        body_layout.setSpacing(14)

        body_layout.addWidget(self._build_camera_group())
        body_layout.addWidget(self._build_behavior_group())
        body_layout.addWidget(self._build_capture_group())
        body_layout.addStretch(1)
        root.addWidget(body, 1)

        cancel = QPushButton("Cancel")
        cancel.setProperty("variant", "ghost")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save")
        save.setProperty("variant", "primary")
        save.setCursor(Qt.PointingHandCursor)
        save.setDefault(True)
        save.clicked.connect(self.accept)

        root.addWidget(_modal_footer([cancel, save]))

    # -------- groups --------

    def _build_camera_group(self) -> QFrame:
        group, body = self._group("CAMERA")

        self.camera_spinbox = QSpinBox()
        self.camera_spinbox.setRange(0, 10)
        self.camera_spinbox.setValue(self.config.camera_index)
        self.camera_spinbox.setFixedWidth(96)
        self.camera_spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        body.addLayout(self._row(
            "Camera index",
            "Index of webcam to use (0 is default).",
            self.camera_spinbox,
        ))

        self.auto_detect_toggle = Toggle(self.config.auto_detect)
        body.addLayout(self._row(
            "Auto-detect QR codes",
            "Continuously scan while the camera is on.",
            self.auto_detect_toggle,
        ))
        return group

    def _build_behavior_group(self) -> QFrame:
        group, body = self._group("SCAN BEHAVIOR")

        self.scan_interval_spinbox = QSpinBox()
        self.scan_interval_spinbox.setRange(100, 2000)
        self.scan_interval_spinbox.setSingleStep(50)
        self.scan_interval_spinbox.setSuffix(" ms")
        self.scan_interval_spinbox.setValue(self.config.scan_interval)
        self.scan_interval_spinbox.setFixedWidth(110)
        self.scan_interval_spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        body.addLayout(self._row(
            "Scan interval",
            "Milliseconds between auto-scans.",
            self.scan_interval_spinbox,
        ))

        self.scan_cooldown_spinbox = QDoubleSpinBox()
        self.scan_cooldown_spinbox.setRange(0.5, 10.0)
        self.scan_cooldown_spinbox.setSingleStep(0.5)
        self.scan_cooldown_spinbox.setDecimals(1)
        self.scan_cooldown_spinbox.setSuffix(" sec")
        self.scan_cooldown_spinbox.setValue(self.config.scan_cooldown)
        self.scan_cooldown_spinbox.setFixedWidth(110)
        self.scan_cooldown_spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        body.addLayout(self._row(
            "Cooldown after scan",
            "Seconds before the next capture is accepted.",
            self.scan_cooldown_spinbox,
        ))
        return group

    def _build_capture_group(self) -> QFrame:
        group, body = self._group("CAPTURE & SOUND")

        self.flash_toggle = Toggle(self.config.flash)
        body.addLayout(self._row(
            "Success flash",
            "Green flash on the camera viewport when a code is captured.",
            self.flash_toggle,
        ))

        self.sound_toggle = Toggle(self.config.sound)
        body.addLayout(self._row(
            "Sound effects",
            "Play a chime when a code is added.",
            self.sound_toggle,
        ))
        return group

    # -------- helpers --------

    @staticmethod
    def _group(title: str):
        frame = QFrame()
        frame.setObjectName("settingsGroup")
        v = QVBoxLayout(frame)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(0)

        header = QLabel(title)
        header.setObjectName("groupTitle")
        v.addWidget(header)
        v.addSpacing(8)
        return frame, v

    def _row(self, title: str, hint: str, control: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 8, 0, 8)
        row.setSpacing(14)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("settingLabel")
        text_col.addWidget(t)
        h = QLabel(hint)
        h.setObjectName("settingHint")
        h.setWordWrap(True)
        text_col.addWidget(h)
        row.addLayout(text_col, 1)

        row.addWidget(control, 0, Qt.AlignVCenter)
        return row

    # -------- public --------

    def get_settings(self) -> dict:
        return {
            "camera_index": self.camera_spinbox.value(),
            "auto_detect": self.auto_detect_toggle.isChecked(),
            "scan_interval": self.scan_interval_spinbox.value(),
            "scan_cooldown": self.scan_cooldown_spinbox.value(),
            "flash": self.flash_toggle.isChecked(),
            "sound": self.sound_toggle.isChecked(),
        }


# ====================================================================== about

class AboutDialog(QDialog):
    """About modal — Pokéball hero, feature list, nytemode credit."""

    VERSION_LINE = "VERSION 1.4.2  ·  MIT LICENSE"

    DESCRIPTION = (
        "The professional Pokémon TCG code scanner — built by collectors, "
        "for collectors. Scan, organize, and export hundreds of redemption "
        "codes at lightning speed without ever leaving your desk."
    )

    FEATURES = [
        "Ultra-fast continuous QR scanning",
        "Batch processing of full booster boxes",
        "Numbered, space, comma, raw export",
        "One-click copy by block of 10",
        "TXT and Markdown file exports",
        "100% local — codes never leave your device",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("About CodeDex Pro")
        self.setMinimumWidth(560)
        root = _modal_chrome(self)
        root.addWidget(_modal_header("About CodeDex Pro"))

        body = QWidget()
        b = QVBoxLayout(body)
        b.setContentsMargins(22, 22, 22, 22)
        b.setSpacing(0)

        # ----- hero -----
        hero = QHBoxLayout()
        hero.setSpacing(16)

        ball = QLabel()
        ball.setFixedSize(52, 52)
        pix = QPixmap(52, 52)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        paint_pokeball(painter, QRectF(0, 0, 52, 52))
        painter.end()
        ball.setPixmap(pix)
        hero.addWidget(ball, 0, Qt.AlignTop)

        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(0)
        name = QLabel("CodeDex")
        name.setObjectName("aboutHeroTitle")
        name_row.addWidget(name)
        pro = QLabel("Pro")
        pro.setObjectName("aboutHeroPro")
        name_row.addWidget(pro)
        name_row.addStretch(1)
        title_block.addLayout(name_row)

        ver = QLabel(self.VERSION_LINE)
        ver.setObjectName("aboutVer")
        title_block.addWidget(ver)
        hero.addLayout(title_block, 1)
        b.addLayout(hero)

        # divider
        b.addSpacing(16)
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {color('border')};")
        b.addWidget(line)
        b.addSpacing(16)

        # ----- description -----
        desc = QLabel(self.DESCRIPTION)
        desc.setWordWrap(True)
        desc.setObjectName("aboutBody")
        b.addWidget(desc)
        b.addSpacing(16)

        # ----- feature grid -----
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)
        for i, feat in enumerate(self.FEATURES):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(8)
            dot = QLabel("●")
            dot.setStyleSheet(
                f"color: {color('yellow')}; font-size: 9px;")
            row.addWidget(dot, 0, Qt.AlignTop)
            f = QLabel(feat)
            f.setObjectName("aboutFeat")
            f.setWordWrap(True)
            row.addWidget(f, 1)
            container = QWidget()
            container.setLayout(row)
            grid.addWidget(container, i // 2, i % 2)
        b.addLayout(grid)
        b.addSpacing(16)

        # ----- learn more line -----
        learn = QLabel(
            f'Learn more or grab the latest release at '
            f'<a href="{NYTEMODE_URL}" '
            f'style="color: {color("yellow")}; text-decoration: none;">'
            f'nytemode.com</a>.')
        learn.setObjectName("aboutBody")
        learn.setWordWrap(True)
        learn.setOpenExternalLinks(True)
        learn.setTextFormat(Qt.RichText)
        b.addWidget(learn)
        b.addSpacing(16)

        # ----- credits panel -----
        credits_frame = QFrame()
        credits_frame.setObjectName("aboutCredits")
        credits_layout = QHBoxLayout(credits_frame)
        credits_layout.setContentsMargins(14, 12, 14, 12)
        credits_layout.setSpacing(12)

        moon = Moon(16)
        credits_layout.addWidget(moon, 0, Qt.AlignTop)

        credits_text = QLabel(
            f'CodeDex Pro is a '
            f'<a href="{NYTEMODE_URL}" '
            f'style="color: {color("yellow")}; text-decoration: none;">'
            f'nytemode</a> project. Pokémon is a trademark of Nintendo, '
            f'Creatures Inc., and GAME FREAK Inc. — this app is unofficial '
            f'and unaffiliated.')
        credits_text.setObjectName("aboutCreditsText")
        credits_text.setWordWrap(True)
        credits_text.setOpenExternalLinks(True)
        credits_text.setTextFormat(Qt.RichText)
        credits_layout.addWidget(credits_text, 1)
        b.addWidget(credits_frame)

        b.addStretch(1)
        root.addWidget(body, 1)

        # ----- footer -----
        visit = QPushButton("Visit nytemode.com")
        visit.setProperty("variant", "ghost")
        visit.setCursor(Qt.PointingHandCursor)
        visit.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(NYTEMODE_URL)))

        close = QPushButton("Close")
        close.setProperty("variant", "primary")
        close.setCursor(Qt.PointingHandCursor)
        close.setDefault(True)
        close.clicked.connect(self.accept)

        root.addWidget(_modal_footer([visit, close]))


# =================================================================== add code

class AddCodeDialog(QDialog):
    """Slim modal for entering a Pokémon TCG code manually."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = ""
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Add Code Manually")
        self.setFixedWidth(440)
        root = _modal_chrome(self)
        root.addWidget(_modal_header("Add Code Manually"))

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        label = QLabel("POKÉMON TCG CODE")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        self.input = QLineEdit()
        self.input.setObjectName("codeInput")
        self.input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(self._submit)
        layout.addWidget(self.input)
        root.addWidget(body, 1)

        cancel = QPushButton("Cancel")
        cancel.setProperty("variant", "ghost")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)

        self.add_btn = QPushButton("Add Code")
        self.add_btn.setProperty("variant", "primary")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setEnabled(False)
        self.add_btn.setDefault(True)
        self.add_btn.clicked.connect(self._submit)

        root.addWidget(_modal_footer([cancel, self.add_btn]))

    def _on_text_changed(self, text: str):
        self.add_btn.setEnabled(bool(text.strip()))

    def _submit(self):
        val = self.input.text().strip().upper()
        if not val:
            return
        self._value = val
        self.accept()

    def value(self) -> str:
        return self._value
