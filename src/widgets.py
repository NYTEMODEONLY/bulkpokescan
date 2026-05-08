"""Custom widgets — camera viewfinder, status indicator, toast, toggle,
energy pip strip, code row, empty state, section title, footer link."""

from PyQt5.QtCore import (QEasingCurve, QPoint, QPropertyAnimation, QRect,
                          QRectF, QSize, Qt, QTimer, QUrl, pyqtSignal)
from PyQt5.QtGui import (QBrush, QColor, QCursor, QDesktopServices, QFont,
                          QLinearGradient, QPainter, QPen, QPixmap)
from PyQt5.QtWidgets import (QFrame, QGraphicsOpacityEffect, QHBoxLayout,
                              QLabel, QPushButton, QSizePolicy, QStyle,
                              QVBoxLayout, QWidget)

from src.theme import PALETTE, color, paint_card_qr, FONT_BODY, FONT_DISPLAY, FONT_MONO


# ============================================================ section title

class SectionTitle(QWidget):
    """Section title — colored accent stripe + uppercase text."""

    def __init__(self, text: str, accent: str = None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._accent = QFrame()
        self._accent.setFixedSize(4, 18)
        self._accent.setStyleSheet(
            f"background-color: {accent or color('red')};"
            f" border-radius: 2px;"
        )
        layout.addWidget(self._accent, 0, Qt.AlignVCenter)

        self._label = QLabel(text.upper())
        self._label.setObjectName("sectionTitle")
        layout.addWidget(self._label, 0, Qt.AlignVCenter)


# ============================================================ status pulse

class StatusIndicator(QWidget):
    """Outer halo ring + inner core dot. Three states: off, live, scanning."""

    OFF, LIVE, SCANNING = 0, 1, 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = self.OFF
        self._pulse_t = 0.0  # 0..1 oscillating
        self._pulse_dir = 1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        self._ring = _PulseRing(self)
        layout.addWidget(self._ring, 0, Qt.AlignVCenter)

        self._label = QLabel("CAMERA OFF")
        layout.addWidget(self._label, 0, Qt.AlignVCenter)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(40)
        self._pulse_timer.timeout.connect(self._tick)

        self.set_state(self.OFF)

    def set_state(self, state: int):
        self._state = state
        if state == self.OFF:
            self._pulse_timer.stop()
            text = "CAMERA OFF"
            text_color = color("text_muted")
            ring_color = color("text_muted")
            halo_color = None
        elif state == self.LIVE:
            self._pulse_timer.start()
            text = "LIVE"
            text_color = color("success")
            ring_color = color("success")
            halo_color = color("success")
        else:  # SCANNING
            self._pulse_timer.start()
            text = "SCANNING"
            text_color = color("scan")
            ring_color = color("scan")
            halo_color = color("scan")

        self._label.setText(text)
        self._label.setStyleSheet(
            f"font-family: {FONT_MONO}; font-size: 11px;"
            f" font-weight: 700; letter-spacing: 0.10em;"
            f" color: {text_color};"
        )
        self._ring.set_colors(ring_color, halo_color)
        self._ring.update()

    def _tick(self):
        self._pulse_t += 0.05 * self._pulse_dir
        if self._pulse_t >= 1.0:
            self._pulse_t, self._pulse_dir = 1.0, -1
        elif self._pulse_t <= 0.0:
            self._pulse_t, self._pulse_dir = 0.0, 1
        self._ring.set_pulse(self._pulse_t)


class _PulseRing(QWidget):
    """Inner widget for StatusIndicator — paints halo + core dot."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(18, 18)
        self._core_color = color("text_muted")
        self._halo_color = None
        self._pulse = 0.0

    def set_colors(self, core: str, halo: str = None):
        self._core_color = core
        self._halo_color = halo
        self.update()

    def set_pulse(self, t: float):
        self._pulse = t
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2

        if self._halo_color is not None:
            halo_radius = 4 + 6 * self._pulse  # 4..10
            halo = QColor(self._halo_color)
            halo.setAlphaF(0.25 + 0.25 * (1 - self._pulse))
            painter.setPen(Qt.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(QRectF(cx - halo_radius, cy - halo_radius,
                                          2 * halo_radius, 2 * halo_radius))

        core = QColor(self._core_color)
        painter.setBrush(core)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(cx - 3, cy - 3, 6, 6))
        painter.end()


# ============================================================ camera view

class CameraView(QWidget):
    """Live camera viewfinder with 16:9 stage, scan-line sweep, reticle,
    flash overlay, and a Pokéball off-state watermark."""

    OFF, LIVE, SCANNING = 0, 1, 2
    STAGE_BG = QColor("#050507")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoFillBackground(False)

        self._frame_pixmap = None
        self._state = self.OFF

        self._reticle_pulse = 0.6
        self._reticle_pulse_dir = 1
        self._scan_line_pos = 0.08  # 0..1 vertical position
        self._scan_line_dir = 1
        self._flash_alpha = 0

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(28)
        self._anim_timer.timeout.connect(self._tick)

        self._flash_timer = QTimer(self)
        self._flash_timer.setInterval(20)
        self._flash_timer.timeout.connect(self._tick_flash)

    # --------------------------------------------------------------- API

    def set_state(self, state: int):
        self._state = state
        if state == self.OFF:
            self._anim_timer.stop()
            self._frame_pixmap = None
        else:
            if not self._anim_timer.isActive():
                self._anim_timer.start()
        self.update()

    def set_camera_on(self, on: bool):
        # Backwards-compatible helper: maps a bool to LIVE/OFF.
        self.set_state(self.LIVE if on else self.OFF)

    def set_frame(self, pixmap: QPixmap):
        self._frame_pixmap = pixmap
        self.update()

    def flash_success(self):
        self._flash_alpha = 170
        if not self._flash_timer.isActive():
            self._flash_timer.start()
        self.update()

    # ---------------------------------------------------------- internals

    def _stage_rect(self) -> QRect:
        w, h = self.width(), self.height()
        target = 16 / 9
        if w / max(h, 1) > target:
            sh = h
            sw = int(h * target)
        else:
            sw = w
            sh = int(w / target)
        x = (w - sw) // 2
        y = (h - sh) // 2
        return QRect(x, y, sw, sh)

    def _tick(self):
        # reticle pulse
        speed = 0.05 if self._state == self.SCANNING else 0.03
        self._reticle_pulse += speed * self._reticle_pulse_dir
        if self._reticle_pulse >= 1.0:
            self._reticle_pulse, self._reticle_pulse_dir = 1.0, -1
        elif self._reticle_pulse <= 0.45:
            self._reticle_pulse, self._reticle_pulse_dir = 0.45, 1

        # scan line sweep (0.08 -> 0.92 over ~2.4s)
        self._scan_line_pos += 0.012 * self._scan_line_dir
        if self._scan_line_pos >= 0.92:
            self._scan_line_pos, self._scan_line_dir = 0.92, -1
        elif self._scan_line_pos <= 0.08:
            self._scan_line_pos, self._scan_line_dir = 0.08, 1
        self.update()

    def _tick_flash(self):
        self._flash_alpha = max(0, self._flash_alpha - 14)
        if self._flash_alpha == 0:
            self._flash_timer.stop()
        self.update()

    # ------------------------------------------------------------ paint

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.fillRect(self.rect(), self.STAGE_BG)
        stage = self._stage_rect()

        # subtle vignette
        grad = QLinearGradient(0, stage.top(), 0, stage.bottom())
        grad.setColorAt(0, QColor("#0A0E18"))
        grad.setColorAt(1, QColor("#070912"))
        painter.fillRect(stage, QBrush(grad))

        if self._state in (self.LIVE, self.SCANNING):
            if self._frame_pixmap and not self._frame_pixmap.isNull():
                scaled = self._frame_pixmap.scaled(
                    stage.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x = stage.x() + (stage.width() - scaled.width()) // 2
                y = stage.y() + (stage.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
            else:
                self._paint_warming(painter, stage)

            self._paint_scan_line(painter, stage)
            self._paint_reticle(painter, stage)
        else:
            self._paint_off(painter, stage)

        if self._flash_alpha > 0:
            painter.fillRect(stage, QColor(52, 199, 89, self._flash_alpha))

        painter.end()

    def _paint_off(self, painter: QPainter, stage: QRect):
        size = min(stage.width(), stage.height()) * 0.30
        ball = QRectF(stage.center().x() - size / 2,
                       stage.top() + stage.height() * 0.18,
                       size, size)
        paint_card_qr(painter, ball, opacity=0.20)

        title_font = QFont()
        title_font.setFamily("SF Pro Display")
        title_font.setPointSize(17)
        title_font.setWeight(QFont.DemiBold)
        painter.setFont(title_font)
        painter.setPen(QColor(color("text")))
        title_y = ball.bottom() + 22
        painter.drawText(QRect(stage.x(), int(title_y), stage.width(), 26),
                          Qt.AlignHCenter | Qt.AlignTop, "Camera Off")

        hint_font = QFont()
        hint_font.setFamily("SF Pro Text")
        hint_font.setPointSize(12)
        painter.setFont(hint_font)
        painter.setPen(QColor(color("text_muted")))
        painter.drawText(
            QRect(stage.x() + 30, int(title_y + 30),
                   stage.width() - 60, 36),
            Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
            "Press Start Camera to begin scanning Pokémon TCG codes.")

    def _paint_warming(self, painter: QPainter, stage: QRect):
        size = min(stage.width(), stage.height()) * 0.20
        rect = QRectF(stage.center().x() - size / 2,
                       stage.center().y() - size / 2,
                       size, size)
        paint_card_qr(painter, rect, opacity=0.55)
        font = QFont()
        font.setFamily("SF Pro Text")
        font.setPointSize(11)
        font.setWeight(QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(color("text_2")))
        painter.drawText(
            QRect(stage.x(), int(rect.bottom() + 16), stage.width(), 18),
            Qt.AlignHCenter | Qt.AlignTop, "WARMING UP CAMERA…")

    def _paint_scan_line(self, painter: QPainter, stage: QRect):
        y = int(stage.top() + stage.height() * self._scan_line_pos)
        line_color = QColor(color("scan"))
        line_color.setAlphaF(0.55)
        glow_color = QColor(color("scan"))
        glow_color.setAlphaF(0.10)

        # soft wider glow band first, then crisp 2px line on top
        painter.fillRect(QRect(stage.x(), y - 8, stage.width(), 16), glow_color)
        painter.fillRect(QRect(stage.x(), y - 1, stage.width(), 2), line_color)

    def _paint_reticle(self, painter: QPainter, stage: QRect):
        side = int(min(stage.width(), stage.height()) * 0.58)
        x = stage.center().x() - side // 2
        y = stage.center().y() - side // 2
        corner = max(22, int(side * 0.12))
        stroke = 3

        c = QColor(color("scan"))
        c.setAlphaF(self._reticle_pulse)
        pen = QPen(c, stroke, Qt.SolidLine, Qt.SquareCap)
        painter.setPen(pen)

        r = 8  # rounded corner radius
        # top-left (open at top-left, lines going right and down)
        painter.drawArc(x, y, r * 2, r * 2, 90 * 16, 90 * 16)
        painter.drawLine(x + r, y, x + corner, y)
        painter.drawLine(x, y + r, x, y + corner)
        # top-right
        painter.drawArc(x + side - r * 2, y, r * 2, r * 2, 0 * 16, 90 * 16)
        painter.drawLine(x + side - corner, y, x + side - r, y)
        painter.drawLine(x + side, y + r, x + side, y + corner)
        # bottom-left
        painter.drawArc(x, y + side - r * 2, r * 2, r * 2, 180 * 16, 90 * 16)
        painter.drawLine(x, y + side - corner, x, y + side - r)
        painter.drawLine(x + r, y + side, x + corner, y + side)
        # bottom-right
        painter.drawArc(x + side - r * 2, y + side - r * 2, r * 2, r * 2,
                          270 * 16, 90 * 16)
        painter.drawLine(x + side - corner, y + side, x + side - r, y + side)
        painter.drawLine(x + side, y + side - corner, x + side, y + side - r)

        # Crosshair
        cross = max(7, int(side * 0.04))
        cx, cy = x + side // 2, y + side // 2
        c2 = QColor(color("scan"))
        c2.setAlphaF(self._reticle_pulse * 0.6)
        painter.setPen(QPen(c2, 1))
        painter.drawLine(cx - cross, cy, cx + cross, cy)
        painter.drawLine(cx, cy - cross, cx, cy + cross)


# ============================================================ energy strip

class EnergyPip(QWidget):
    """Small rotated-square decorative pip (used in the header strip)."""

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = QColor(hex_color)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(45)
        c = QColor(self._color)
        c.setAlphaF(0.7)
        painter.setBrush(c)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(-4, -4, 8, 8), 1.5, 1.5)
        painter.end()


class EnergyStrip(QWidget):
    """Decorative strip of energy-type pips (header decoration)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        for key in ("en_fire", "en_water", "en_grass",
                     "en_electric", "en_psychic", "en_fairy"):
            layout.addWidget(EnergyPip(PALETTE[key]))


# ============================================================ energy dot

class EnergyDot(QWidget):
    """Small energy-color circle for the right edge of a code row."""

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self._color = QColor(hex_color)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(QPen(QColor(255, 255, 255, 38), 1.5))
        painter.drawEllipse(QRectF(1, 1, self.width() - 2, self.height() - 2))
        painter.end()


# ============================================================ code row

class CodeRow(QWidget):
    """Single row in the codes list — #001 number + code + source dot."""

    def __init__(self, index: int, code: str, source: str = "scan",
                  parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(12)

        num = QLabel(f"#{index:03d}")
        num.setFixedWidth(38)
        num.setStyleSheet(
            f"color: {color('text_muted')};"
            f" font-family: {FONT_MONO};"
            f" font-size: 11px;"
            f" letter-spacing: 0.06em;"
        )
        num.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(num)

        val = QLabel(code)
        val.setStyleSheet(
            f"color: {color('text')};"
            f" font-family: {FONT_MONO};"
            f" font-size: 13px;"
            f" letter-spacing: 0.04em;"
        )
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(val, 1)

        if source == "scan":
            dot = EnergyDot(color("success"))
            dot.setToolTip("Scanned via camera")
        else:
            dot = EnergyDot(color("text_muted"))
            dot.setToolTip("Added manually")
        layout.addWidget(dot, 0, Qt.AlignVCenter)


# ============================================================ empty state

class EmptyStatePanel(QFrame):
    """Centered empty-state — Pokéball watermark + title + hint."""

    def __init__(self, title: str, hint: str, parent=None):
        super().__init__(parent)
        self.setObjectName("codesEmpty")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(14)
        layout.addStretch(1)

        mark = QLabel()
        mark.setFixedSize(68, 68)
        mark.setAlignment(Qt.AlignCenter)
        mark.setPixmap(self._render_mark(68))
        layout.addWidget(mark, 0, Qt.AlignHCenter)

        t = QLabel(title)
        t.setAlignment(Qt.AlignHCenter)
        t.setStyleSheet(
            f"color: {color('text')};"
            f" font-family: {FONT_DISPLAY};"
            f" font-size: 16px; font-weight: 600;"
        )
        layout.addWidget(t)

        h = QLabel(hint)
        h.setAlignment(Qt.AlignHCenter)
        h.setWordWrap(True)
        h.setStyleSheet(
            f"color: {color('text_muted')};"
            f" font-size: 13px;"
        )
        h.setMaximumWidth(360)
        layout.addWidget(h, 0, Qt.AlignHCenter)

        layout.addStretch(1)

    @staticmethod
    def _render_mark(size: int) -> QPixmap:
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        paint_card_qr(painter, QRectF(0, 0, size, size), opacity=0.35)
        painter.end()
        return pix


# ============================================================ toggle

class Toggle(QWidget):
    """Custom toggle switch — replaces QCheckBox for settings rows."""

    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 24)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._checked = checked
        self._knob_x = 20.0 if checked else 2.0

        self._anim = QPropertyAnimation(self, b"_knob_x_prop", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if checked == self._checked:
            return
        self._checked = checked
        self._animate()
        self.toggled.emit(checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

    def _animate(self):
        self._anim.stop()
        self._anim.setStartValue(self._knob_x)
        self._anim.setEndValue(20.0 if self._checked else 2.0)
        self._anim.start()

    # --- pyqtProperty for animation ---
    def _get_knob_x(self):
        return self._knob_x

    def _set_knob_x(self, v):
        self._knob_x = v
        self.update()

    from PyQt5.QtCore import pyqtProperty
    _knob_x_prop = pyqtProperty(float, _get_knob_x, _set_knob_x)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        track_rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        if self._checked:
            track_color = QColor(color("yellow"))
            track_color.setAlphaF(0.25)
            border_color = QColor(color("yellow"))
            knob_color = QColor(color("yellow"))
        else:
            track_color = QColor(color("surface_3"))
            border_color = QColor(color("border"))
            knob_color = QColor(color("text_muted"))

        painter.setBrush(track_color)
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(track_rect, 12, 12)

        painter.setPen(Qt.NoPen)
        painter.setBrush(knob_color)
        painter.drawEllipse(QRectF(self._knob_x, 4, 16, 16))
        painter.end()


# ============================================================ toast

class Toast(QWidget):
    """Floating toast — green check + message + optional yellow code."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        bg = QFrame(self)
        bg.setObjectName("toastBg")
        bg.setStyleSheet(
            f"#toastBg {{"
            f"  background-color: rgba(28, 31, 45, 0.97);"
            f"  border: 1px solid {color('border_strong')};"
            f"  border-radius: 12px;"
            f"}}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(bg)

        inner = QHBoxLayout(bg)
        inner.setContentsMargins(16, 11, 22, 11)
        inner.setSpacing(10)

        self._check = QLabel("✓")
        self._check.setFixedSize(18, 18)
        self._check.setAlignment(Qt.AlignCenter)
        self._check.setStyleSheet(
            f"background-color: {color('success')}; color: white;"
            f" border-radius: 9px; font-weight: 900; font-size: 11px;"
        )
        inner.addWidget(self._check, 0, Qt.AlignVCenter)

        self._text = QLabel("")
        self._text.setStyleSheet(
            f"color: {color('text')}; font-family: {FONT_BODY};"
            f" font-weight: 600; font-size: 13px;"
        )
        inner.addWidget(self._text, 0, Qt.AlignVCenter)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)
        self.hide()

        self._anim_in = QPropertyAnimation(self._opacity, b"opacity", self)
        self._anim_in.setDuration(180)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)
        self._anim_in.setEasingCurve(QEasingCurve.OutCubic)

        self._anim_out = QPropertyAnimation(self._opacity, b"opacity", self)
        self._anim_out.setDuration(220)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.InCubic)
        self._anim_out.finished.connect(self.hide)

        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self._anim_out.start)

    def show_message(self, message: str, code: str = None,
                     show_check: bool = True, duration_ms: int = 2000):
        if code:
            self._text.setText(
                f'{message} · <span style="font-family: {FONT_MONO};'
                f' color: {color("yellow")};">{code}</span>')
            self._text.setTextFormat(Qt.RichText)
        else:
            self._text.setText(message)
            self._text.setTextFormat(Qt.PlainText)
        self._check.setVisible(show_check)

        self.adjustSize()
        self._reposition()
        self.show()
        self.raise_()
        self._anim_out.stop()
        self._opacity.setOpacity(0.0)
        self._anim_in.start()
        self._dismiss_timer.start(duration_ms)

    def _reposition(self):
        parent = self.parentWidget()
        if not parent:
            return
        x = (parent.width() - self.width()) // 2
        y = parent.height() - self.height() - 90
        self.move(x, y)


# ============================================================ footer link

class FooterLink(QLabel):
    """Plain hyperlink-style label for footer."""

    clicked = pyqtSignal()

    def __init__(self, text: str, url: str = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("footerLink")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._url = url

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._url:
                QDesktopServices.openUrl(QUrl(self._url))
            self.clicked.emit()


class Moon(QWidget):
    """Tiny crescent-moon mark used in the nytemode credit line."""

    def __init__(self, size: int = 12, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        s = self.width()
        # Yellow disk
        painter.setBrush(QColor(color("yellow")))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(0, 0, s, s))
        # Bg-colored bite to make a crescent
        painter.setBrush(QColor(color("surface")))
        painter.drawEllipse(QRectF(s * 0.30, -s * 0.10, s, s))
        painter.end()
