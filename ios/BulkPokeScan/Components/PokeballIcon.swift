import SwiftUI

/// Programmatic Pokéball matching `paint_pokeball` in src/theme.py.
struct PokeballIcon: View {
    var monochrome: Bool = false

    var body: some View {
        Canvas { ctx, size in
            let dim = min(size.width, size.height)
            let cx = size.width / 2
            let cy = size.height / 2
            let pad = dim * 0.06
            let ball = CGRect(x: cx - dim/2 + pad, y: cy - dim/2 + pad,
                              width: dim - 2*pad, height: dim - 2*pad)
            let line = Palette.bg

            if monochrome {
                ctx.fill(Path(ellipseIn: ball), with: .color(Palette.textMuted))
            } else {
                let topPath = Path { p in
                    p.addArc(center: CGPoint(x: ball.midX, y: ball.midY),
                             radius: ball.width / 2,
                             startAngle: .degrees(180),
                             endAngle: .degrees(360),
                             clockwise: false)
                    p.closeSubpath()
                }
                ctx.fill(topPath, with: .color(Palette.red))

                let bottomPath = Path { p in
                    p.addArc(center: CGPoint(x: ball.midX, y: ball.midY),
                             radius: ball.width / 2,
                             startAngle: .degrees(0),
                             endAngle: .degrees(180),
                             clockwise: false)
                    p.closeSubpath()
                }
                ctx.fill(bottomPath, with: .color(.white))

                // Highlight on the upper-left of the red dome
                let glintRect = CGRect(x: ball.minX, y: ball.minY,
                                       width: ball.width, height: ball.height / 2)
                ctx.clip(to: Path(glintRect))
                let glint = GraphicsContext.Shading.radialGradient(
                    Gradient(colors: [Color.white.opacity(0.55), Color.white.opacity(0)]),
                    center: CGPoint(x: ball.minX + ball.width * 0.30,
                                    y: ball.minY + ball.height * 0.28),
                    startRadius: 0,
                    endRadius: ball.width * 0.38)
                ctx.fill(Path(ellipseIn: ball), with: glint)
            }

            // Horizontal divider band
            let bandH = max(2.0, dim * 0.07)
            let bandRect = CGRect(x: ball.minX, y: ball.midY - bandH/2,
                                  width: ball.width, height: bandH)
            // Reset clip
            let ctxNoClip = ctx
            ctxNoClip.fill(Path(bandRect), with: .color(line))

            // Outer ring
            ctxNoClip.stroke(Path(ellipseIn: ball), with: .color(line),
                             lineWidth: max(2.0, dim * 0.045))

            // Center button rings
            let btnOuter = dim * 0.22
            ctxNoClip.fill(Path(ellipseIn: CGRect(x: cx - btnOuter/2, y: cy - btnOuter/2,
                                                    width: btnOuter, height: btnOuter)),
                           with: .color(line))
            let btnMid = dim * 0.16
            ctxNoClip.fill(Path(ellipseIn: CGRect(x: cx - btnMid/2, y: cy - btnMid/2,
                                                    width: btnMid, height: btnMid)),
                           with: .color(.white))
            let btnInner = dim * 0.10
            ctxNoClip.fill(Path(ellipseIn: CGRect(x: cx - btnInner/2, y: cy - btnInner/2,
                                                    width: btnInner, height: btnInner)),
                           with: .color(line))
            let btnCore = dim * 0.05
            ctxNoClip.fill(Path(ellipseIn: CGRect(x: cx - btnCore/2, y: cy - btnCore/2,
                                                    width: btnCore, height: btnCore)),
                           with: .color(.white))
        }
        .aspectRatio(1, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

#Preview {
    PokeballIcon()
        .frame(width: 200, height: 200)
        .padding(40)
        .background(Palette.bg)
}
