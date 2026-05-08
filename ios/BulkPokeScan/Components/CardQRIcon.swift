import SwiftUI

/// Trading-card brand mark: white card → yellow→red gradient interior →
/// stylized QR square → yellow energy bar. Matches the v1.0 AppIcon
/// (`Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png`) and is
/// mirrored by `paint_card_qr` in `src/theme.py` and `<CardQR />` on web.
struct CardQRIcon: View {
    var monochrome: Bool = false

    /// 7×7 finder-pattern-style grid — recognizable as "QR-like" at any size,
    /// readable as a logo even at 32px where a real QR would be noise.
    private static let qrGrid: [[UInt8]] = [
        [1,1,1,0,1,1,1],
        [1,0,1,0,0,0,1],
        [1,1,1,1,1,0,1],
        [0,0,1,1,0,1,0],
        [1,1,1,0,1,1,1],
        [1,0,0,1,0,0,1],
        [1,1,1,0,1,1,1],
    ]

    var body: some View {
        Canvas { ctx, size in
            let dim = min(size.width, size.height)
            let cx = size.width / 2
            let cy = size.height / 2

            // Card geometry — portrait 3:4-ish, sits inside a 1:1 frame
            let cardW = dim * 0.78
            let cardH = dim * 0.96
            let cardRect = CGRect(x: cx - cardW / 2, y: cy - cardH / 2,
                                  width: cardW, height: cardH)
            let cardCorner = cardW * 0.12

            // White card border
            ctx.fill(Path(roundedRect: cardRect, cornerRadius: cardCorner),
                     with: .color(.white))

            // Gradient interior
            let inset = cardW * 0.045
            let inner = cardRect.insetBy(dx: inset, dy: inset)
            let innerCorner = max(0, cardCorner - inset)
            let innerPath = Path(roundedRect: inner, cornerRadius: innerCorner)

            if monochrome {
                ctx.fill(innerPath, with: .color(Palette.textMuted))
            } else {
                ctx.fill(innerPath, with: .linearGradient(
                    Gradient(colors: [Palette.yellow, Palette.red]),
                    startPoint: CGPoint(x: inner.midX, y: inner.minY),
                    endPoint: CGPoint(x: inner.midX, y: inner.maxY)))
            }

            // QR plate
            let qrSize = cardW * 0.62
            let qrRect = CGRect(x: cx - qrSize / 2,
                                y: cardRect.minY + cardH * 0.16,
                                width: qrSize, height: qrSize)
            let qrCorner = qrSize * 0.10
            ctx.fill(Path(roundedRect: qrRect, cornerRadius: qrCorner),
                     with: .color(.white))

            // QR modules
            let modules = Self.qrGrid.count
            let qrPad = qrSize * 0.10
            let cell = (qrSize - 2 * qrPad) / CGFloat(modules)
            let inkColor = monochrome ? Color(white: 0.20)
                                      : Color(red: 0.06, green: 0.06, blue: 0.10)
            for r in 0..<modules {
                for c in 0..<modules where Self.qrGrid[r][c] == 1 {
                    let cellRect = CGRect(
                        x: qrRect.minX + qrPad + CGFloat(c) * cell,
                        y: qrRect.minY + qrPad + CGFloat(r) * cell,
                        width: cell, height: cell)
                    ctx.fill(Path(cellRect), with: .color(inkColor))
                }
            }

            // Energy bar
            let bandW = cardW * 0.50
            let bandH = max(2.0, cardH * 0.06)
            let bandRect = CGRect(
                x: cx - bandW / 2,
                y: cardRect.maxY - inset - bandH - cardH * 0.05,
                width: bandW, height: bandH)
            let bandPath = Path(roundedRect: bandRect, cornerRadius: bandH / 2)
            ctx.fill(bandPath,
                     with: .color(monochrome ? Color(white: 0.65) : Palette.yellow))
            ctx.stroke(bandPath, with: .color(inkColor),
                       lineWidth: max(1.0, dim * 0.012))
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

#Preview {
    HStack(spacing: 18) {
        CardQRIcon().frame(width: 36, height: 36)
        CardQRIcon().frame(width: 96, height: 96)
        CardQRIcon(monochrome: true).frame(width: 96, height: 96)
    }
    .padding(40)
    .background(Palette.bg)
}
