"""Visual theme — palette, typography, global stylesheet, programmatic icon.

Ported from the BulkPokeScan Redesign design package
(trading-card inspired, creature-ball red + electric yellow,
8 energy-type accent colors, JetBrains Mono codes).
"""

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (QBrush, QColor, QIcon, QLinearGradient, QPainter,
                          QPen, QPixmap, QRadialGradient)


# Core palette: creature-ball red + electric yellow on cool deep ink.
PALETTE = {
    "red":            "#E63946",
    "red_deep":       "#B0202E",
    "red_soft":       "#FF6B6B",
    "yellow":         "#FFCB05",
    "yellow_deep":    "#E5A100",
    "yellow_soft":    "#FFE066",
    "gold":           "#C9A227",

    "bg":             "#0B0D14",
    "bg_2":           "#11131C",
    "surface":        "#161823",
    "surface_2":      "#1C1F2D",
    "surface_3":      "#232739",
    "input":          "#181B27",
    "border":         "#262A3B",
    "border_strong":  "#363B52",

    "text":           "#F1F2F7",
    "text_2":         "#A4A7B6",
    "text_muted":     "#6E7287",
    "text_disabled":  "#454962",

    "success":        "#34C759",
    "warning":        "#FF9F0A",
    "danger":         "#FF453A",
    "scan":           "#5AC8FA",

    # Energy types — used for code-row indicators
    "en_fire":        "#F45A2A",
    "en_water":       "#3798E1",
    "en_grass":       "#5FA84A",
    "en_electric":    "#FFCB05",
    "en_psychic":     "#B563D6",
    "en_fighting":    "#C8623A",
    "en_dark":        "#4D4D58",
    "en_fairy":       "#E89AC0",
}

# Font stacks. Space Grotesk / Inter Tight / JetBrains Mono are not bundled —
# Qt will fall back to the next-listed family if the user doesn't have them.
FONT_DISPLAY = '"Space Grotesk", "SF Pro Display", "Helvetica Neue", -apple-system, "Segoe UI", sans-serif'
FONT_BODY    = '"Inter Tight", "SF Pro Text", "Helvetica Neue", -apple-system, "Segoe UI", sans-serif'
FONT_MONO    = '"JetBrains Mono", "SF Mono", Menlo, Consolas, "Courier New", monospace'


def color(name: str) -> str:
    return PALETTE[name]


def build_stylesheet() -> str:
    p = PALETTE
    return f"""
    /* ---------- base ---------- */
    QWidget {{
        color: {p['text']};
        font-family: {FONT_BODY};
        font-size: 13px;
    }}
    QLabel, QCheckBox {{
        background: transparent;
    }}
    QMainWindow, QDialog, QMainWindow > QWidget {{
        background-color: {p['bg']};
    }}
    QStatusBar {{
        background-color: {p['surface']};
        color: {p['text_muted']};
        padding: 8px 28px;
        font-size: 11px;
        font-family: {FONT_MONO};
        letter-spacing: 0.06em;
        border-top: 1px solid {p['border']};
    }}
    QToolTip {{
        background-color: {p['surface_3']};
        color: {p['text']};
        border: 1px solid {p['border_strong']};
        padding: 6px 10px;
        border-radius: 6px;
    }}

    /* ---------- header ---------- */
    QFrame#header {{
        background-color: {p['surface']};
        border: none;
        border-bottom: 1px solid {p['border']};
    }}
    QLabel#brandName {{
        font-family: {FONT_DISPLAY};
        font-weight: 700;
        font-size: 22px;
        letter-spacing: -0.01em;
        color: {p['text']};
    }}
    QLabel#brandPro {{
        font-family: {FONT_DISPLAY};
        font-weight: 500;
        font-size: 22px;
        color: {p['yellow']};
        padding-left: 4px;
    }}
    QLabel#brandTag {{
        font-family: {FONT_MONO};
        font-size: 9px;
        letter-spacing: 0.22em;
        color: {p['text_muted']};
    }}
    QLabel#headerBadge {{
        background-color: rgba(255, 203, 5, 0.12);
        color: {p['yellow']};
        border: 1px solid rgba(255, 203, 5, 0.40);
        border-radius: 12px;
        padding: 5px 14px;
        font-family: {FONT_MONO};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }}
    QLabel#globalBadge {{
        background-color: rgba(90, 200, 250, 0.10);
        color: {p['scan']};
        border: 1px solid rgba(90, 200, 250, 0.35);
        border-radius: 12px;
        padding: 5px 14px;
        font-family: {FONT_MONO};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }}
    QPushButton#iconButton {{
        background-color: {p['surface_2']};
        color: {p['text_2']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 0;
        min-width: 38px;
        max-width: 38px;
        min-height: 38px;
        max-height: 38px;
    }}
    QPushButton#iconButton:hover {{
        background-color: {p['surface_3']};
        color: {p['text']};
        border-color: {p['border_strong']};
    }}

    /* ---------- cards ---------- */
    QFrame#scannerCard, QFrame#codesCard {{
        background-color: {p['surface']};
        border: 1px solid {p['border']};
        border-radius: 16px;
    }}

    QLabel#sectionTitle {{
        font-family: {FONT_DISPLAY};
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: {p['text']};
    }}
    QLabel#countBadge {{
        background-color: {p['surface_2']};
        color: {p['text_2']};
        border: 1px solid {p['border']};
        border-radius: 12px;
        padding: 4px 12px;
        font-family: {FONT_MONO};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
    }}
    QLabel#countBadgeYellow {{
        background-color: rgba(255, 203, 5, 0.10);
        color: {p['yellow']};
        border: 1px solid rgba(255, 203, 5, 0.30);
        border-radius: 12px;
        padding: 4px 12px;
        font-family: {FONT_MONO};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
    }}

    /* ---------- buttons ---------- */
    QPushButton {{
        font-family: {FONT_BODY};
        font-weight: 600;
        font-size: 13px;
        background-color: {p['surface_2']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 0 16px;
        min-height: 38px;
    }}
    QPushButton:hover {{
        background-color: {p['surface_3']};
        border-color: {p['border_strong']};
    }}
    QPushButton:disabled {{
        background-color: {p['surface_2']};
        color: {p['text_disabled']};
        border-color: {p['border']};
    }}
    QPushButton[variant="primary"] {{
        background-color: {p['red']};
        color: white;
        border: 1px solid {p['red']};
    }}
    QPushButton[variant="primary"]:hover {{
        background-color: {p['red_soft']};
        border-color: {p['red_soft']};
    }}
    QPushButton[variant="primary"]:disabled {{
        background-color: {p['surface_2']};
        color: {p['text_disabled']};
        border-color: {p['border']};
    }}
    QPushButton[variant="secondary"] {{
        background-color: {p['yellow']};
        color: #1A1A22;
        border: 1px solid {p['yellow']};
    }}
    QPushButton[variant="secondary"]:hover {{
        background-color: {p['yellow_soft']};
        border-color: {p['yellow_soft']};
    }}
    QPushButton[variant="secondary"]:disabled {{
        background-color: {p['surface_2']};
        color: {p['text_disabled']};
        border-color: {p['border']};
    }}
    QPushButton[variant="danger"] {{
        background-color: {p['danger']};
        color: white;
        border: 1px solid {p['danger']};
    }}
    QPushButton[variant="danger"]:hover {{
        background-color: #FF6B62;
        border-color: #FF6B62;
    }}
    QPushButton[variant="ghost"] {{
        background-color: transparent;
        color: {p['text_2']};
        border: 1px solid {p['border']};
    }}
    QPushButton[variant="ghost"]:hover {{
        background-color: {p['surface_2']};
        color: {p['text']};
    }}

    /* ---------- inputs ---------- */
    QLineEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {p['input']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        padding: 6px 12px;
        font-family: {FONT_MONO};
        font-size: 13px;
        min-height: 22px;
        selection-background-color: {p['yellow']};
        selection-color: #1A1A22;
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {p['yellow']};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background: transparent;
        border: none;
        width: 18px;
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {p['text_2']};
        width: 0; height: 0;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {p['text_2']};
        width: 0; height: 0;
    }}

    QLineEdit#codeInput {{
        font-family: {FONT_MONO};
        font-size: 14px;
        letter-spacing: 0.08em;
        padding: 12px 14px;
        text-transform: uppercase;
        min-height: 28px;
    }}

    /* ---------- comboboxes ---------- */
    QComboBox {{
        background-color: {p['input']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 0 12px;
        font-family: {FONT_BODY};
        font-size: 13px;
        font-weight: 500;
        min-height: 38px;
    }}
    QComboBox:hover {{
        border-color: {p['border_strong']};
    }}
    QComboBox:focus, QComboBox:on {{
        border-color: {p['yellow']};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: right center;
        width: 24px;
        background-color: transparent;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {p['text_2']};
        width: 0; height: 0;
        margin-right: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p['surface_2']};
        color: {p['text']};
        border: 1px solid {p['border_strong']};
        border-radius: 10px;
        selection-background-color: {p['yellow']};
        selection-color: #1A1A22;
        padding: 4px;
        outline: 0;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 8px 10px;
        border-radius: 6px;
        margin: 1px;
    }}

    /* ---------- tabs (codes panel) ---------- */
    QTabWidget#codeTabs::pane {{
        border: none;
        background: transparent;
        top: -1px;
    }}
    QTabWidget#codeTabs > QTabBar {{
        background: transparent;
        border-bottom: 1px solid {p['border']};
    }}
    QTabWidget#codeTabs QTabBar::tab {{
        background: transparent;
        color: {p['text_muted']};
        padding: 10px 14px 12px;
        font-family: {FONT_BODY};
        font-weight: 600;
        font-size: 13px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    QTabWidget#codeTabs QTabBar::tab:selected {{
        color: {p['yellow']};
        border-bottom: 2px solid {p['yellow']};
    }}
    QTabWidget#codeTabs QTabBar::tab:!selected:hover {{
        color: {p['text']};
    }}

    /* ---------- codes list ---------- */
    QFrame#codesListWrap {{
        background-color: {p['input']};
        border: 1px solid {p['border']};
        border-radius: 10px;
    }}
    QListWidget#codesList {{
        background-color: transparent;
        color: {p['text']};
        border: none;
        padding: 6px;
        font-family: {FONT_MONO};
        font-size: 13px;
        outline: 0;
    }}
    QListWidget#codesList::item {{
        /* No padding — the embedded CodeRow widget supplies its own.
           Padding here would double-up and clip the row content. */
        padding: 0;
        border-radius: 6px;
        margin: 1px 0;
        color: {p['text']};
    }}
    QListWidget#codesList::item:hover {{
        background-color: rgba(90, 200, 250, 0.06);
    }}
    QListWidget#codesList::item:selected {{
        background-color: rgba(90, 200, 250, 0.16);
        color: {p['text']};
    }}

    QFrame#codesEmpty {{
        background-color: {p['input']};
        border: 1.5px dashed {p['border_strong']};
        border-radius: 10px;
    }}

    QTextEdit#blockDisplay {{
        background-color: {p['input']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 14px 16px;
        font-family: {FONT_MONO};
        font-size: 13px;
        line-height: 1.6;
    }}
    QTextEdit#blockDisplay[empty="true"] {{
        color: {p['text_muted']};
        font-family: {FONT_BODY};
        font-style: italic;
    }}

    /* ---------- tip strip ---------- */
    QFrame#tipStrip {{
        background-color: {p['surface_2']};
        border: 1px solid {p['border']};
        border-radius: 10px;
    }}
    QLabel#tipTag {{
        background-color: rgba(255, 203, 5, 0.10);
        color: {p['yellow']};
        border-radius: 4px;
        padding: 3px 8px;
        font-family: {FONT_MONO};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
    }}
    QLabel#tipText {{
        color: {p['text_2']};
        font-size: 12px;
    }}

    /* ---------- form labels (inside cards) ---------- */
    QLabel#fieldLabel {{
        color: {p['text_2']};
        font-family: {FONT_MONO};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.14em;
    }}

    /* ---------- footer ---------- */
    QFrame#footer {{
        background-color: {p['surface']};
        border-top: 1px solid {p['border']};
    }}
    QLabel#footerText {{
        color: {p['text_muted']};
        font-family: {FONT_MONO};
        font-size: 11px;
        letter-spacing: 0.08em;
    }}
    QLabel#footerLink {{
        color: {p['text_2']};
        font-family: {FONT_MONO};
        font-size: 11px;
        letter-spacing: 0.08em;
    }}
    QLabel#footerLink:hover {{
        color: {p['yellow']};
    }}
    QLabel#footerNyte {{
        color: {p['text_muted']};
        font-family: {FONT_MONO};
        font-size: 11px;
        letter-spacing: 0.08em;
    }}

    /* ---------- modals ---------- */
    QDialog#modal {{
        background-color: {p['surface']};
        border: 1px solid {p['border_strong']};
        border-radius: 16px;
    }}
    QFrame#modalHeader {{
        background-color: {p['surface']};
        border-bottom: 1px solid {p['border']};
    }}
    QFrame#modalFooter {{
        background-color: {p['surface_2']};
        border-top: 1px solid {p['border']};
    }}
    QLabel#modalTitle {{
        font-family: {FONT_DISPLAY};
        font-size: 16px;
        font-weight: 700;
        color: {p['text']};
        letter-spacing: -0.01em;
    }}

    QFrame#settingsGroup {{
        background-color: {p['surface_2']};
        border: 1px solid {p['border']};
        border-radius: 12px;
    }}
    QLabel#groupTitle {{
        font-family: {FONT_MONO};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.18em;
        color: {p['yellow']};
    }}
    QLabel#settingLabel {{
        color: {p['text']};
        font-family: {FONT_BODY};
        font-size: 13px;
    }}
    QLabel#settingHint {{
        color: {p['text_muted']};
        font-family: {FONT_BODY};
        font-size: 11px;
    }}

    /* About dialog */
    QLabel#aboutHeroTitle {{
        font-family: {FONT_DISPLAY};
        font-size: 22px;
        font-weight: 700;
        color: {p['text']};
        letter-spacing: -0.01em;
    }}
    QLabel#aboutHeroPro {{
        font-family: {FONT_DISPLAY};
        font-size: 22px;
        font-weight: 500;
        color: {p['yellow']};
        padding-left: 4px;
    }}
    QLabel#aboutVer {{
        font-family: {FONT_MONO};
        font-size: 11px;
        color: {p['text_muted']};
        letter-spacing: 0.10em;
    }}
    QLabel#aboutBody {{
        color: {p['text_2']};
        font-size: 13px;
    }}
    QFrame#aboutCredits {{
        background-color: {p['surface_2']};
        border: 1px solid {p['border']};
        border-radius: 10px;
    }}
    QLabel#aboutCreditsText {{
        color: {p['text_2']};
        font-size: 12px;
    }}
    QLabel#aboutFeat {{
        color: {p['text_2']};
        font-size: 12px;
    }}

    /* ---------- scrollbars ---------- */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {p['surface_3']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p['border_strong']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 2px 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p['surface_3']};
        border-radius: 5px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {p['border_strong']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    """


# --------------------------------------------------------- Pokéball drawing

def paint_pokeball(painter: QPainter, rect: QRectF,
                    opacity: float = 1.0, monochrome: bool = False) -> None:
    """Draw a Pokéball into ``rect`` on an existing painter.
    Matches the design's `.ball` CSS — radial highlight + flat top/bottom."""
    painter.save()
    painter.setOpacity(opacity)
    painter.setRenderHint(QPainter.Antialiasing)

    size = min(rect.width(), rect.height())
    cx = rect.x() + rect.width() / 2
    cy = rect.y() + rect.height() / 2
    pad = size * 0.06
    ball = QRectF(cx - size / 2 + pad, cy - size / 2 + pad,
                   size - 2 * pad, size - 2 * pad)

    line_color = QColor(PALETTE["bg"])

    if monochrome:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(PALETTE["text_muted"]))
        painter.drawEllipse(ball)
    else:
        # Top half — flat creature red with subtle highlight
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(PALETTE["red"]))
        painter.drawPie(ball, 0 * 16, 180 * 16)

        # Bottom half — off-white
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawPie(ball, 180 * 16, 180 * 16)

        # Highlight on the upper-left of the red dome
        glint = QRadialGradient(
            ball.x() + ball.width() * 0.30,
            ball.y() + ball.height() * 0.28,
            ball.width() * 0.38)
        glint.setColorAt(0, QColor(255, 255, 255, 140))
        glint.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(glint))
        painter.setClipRect(QRectF(ball.x(), ball.y(),
                                      ball.width(), ball.height() / 2))
        painter.drawEllipse(ball)
        painter.setClipping(False)

    # Horizontal divider band
    band_h = max(2.0, size * 0.07)
    painter.setBrush(line_color)
    painter.setPen(Qt.NoPen)
    painter.drawRect(QRectF(ball.x(), ball.center().y() - band_h / 2,
                              ball.width(), band_h))

    # Outer ring
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(line_color, max(2.0, size * 0.045)))
    painter.drawEllipse(ball)

    # Center button — outer ink, inner white, inner ink ring
    btn_outer = size * 0.22
    painter.setPen(Qt.NoPen)
    painter.setBrush(line_color)
    painter.drawEllipse(QRectF(cx - btn_outer / 2, cy - btn_outer / 2,
                                  btn_outer, btn_outer))

    btn_mid = size * 0.16
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawEllipse(QRectF(cx - btn_mid / 2, cy - btn_mid / 2,
                                  btn_mid, btn_mid))

    btn_inner = size * 0.10
    painter.setBrush(line_color)
    painter.drawEllipse(QRectF(cx - btn_inner / 2, cy - btn_inner / 2,
                                  btn_inner, btn_inner))

    btn_core = size * 0.05
    painter.setBrush(QColor("#FFFFFF"))
    painter.drawEllipse(QRectF(cx - btn_core / 2, cy - btn_core / 2,
                                  btn_core, btn_core))

    painter.restore()


def build_app_icon(size: int = 256) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    paint_pokeball(painter, QRectF(0, 0, size, size))
    painter.end()
    return QIcon(pix)
