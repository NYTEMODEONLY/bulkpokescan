import SwiftUI

/// Animated capture reticle: pulse 0.45 → 1.0 opacity, ~1s cycle.
struct Reticle: View {
    @State private var pulse = false

    var body: some View {
        GeometryReader { geo in
            let dim = min(geo.size.width, geo.size.height) * 0.6
            ZStack {
                cornerMarks(size: dim)
                    .stroke(Palette.scan, lineWidth: 2.5)
                    .opacity(pulse ? 1.0 : 0.45)
                    .frame(width: dim, height: dim)
            }
            .frame(width: geo.size.width, height: geo.size.height)
            .onAppear {
                withAnimation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true)) {
                    pulse = true
                }
            }
        }
        .accessibilityHidden(true)
    }

    /// Four L-shaped corner marks instead of a full rectangle — cleaner look.
    private func cornerMarks(size: CGFloat) -> Path {
        Path { p in
            let armLen = size * 0.18
            // top-left
            p.move(to: CGPoint(x: 0, y: armLen))
            p.addLine(to: CGPoint(x: 0, y: 0))
            p.addLine(to: CGPoint(x: armLen, y: 0))
            // top-right
            p.move(to: CGPoint(x: size - armLen, y: 0))
            p.addLine(to: CGPoint(x: size, y: 0))
            p.addLine(to: CGPoint(x: size, y: armLen))
            // bottom-right
            p.move(to: CGPoint(x: size, y: size - armLen))
            p.addLine(to: CGPoint(x: size, y: size))
            p.addLine(to: CGPoint(x: size - armLen, y: size))
            // bottom-left
            p.move(to: CGPoint(x: armLen, y: size))
            p.addLine(to: CGPoint(x: 0, y: size))
            p.addLine(to: CGPoint(x: 0, y: size - armLen))
        }
    }
}

#Preview {
    Reticle()
        .frame(width: 300, height: 300)
        .background(Palette.bg)
}
