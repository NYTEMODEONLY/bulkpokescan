import SwiftUI

/// 8 rotated squares in energy-type colors — header decoration matching desktop.
struct EnergyStrip: View {
    var size: CGFloat = 8
    var spacing: CGFloat = 6

    var body: some View {
        HStack(spacing: spacing) {
            ForEach(EnergyType.allCases, id: \.self) { e in
                Rectangle()
                    .fill(e.color)
                    .frame(width: size, height: size)
                    .rotationEffect(.degrees(45))
            }
        }
        .accessibilityHidden(true)
    }
}

#Preview {
    EnergyStrip()
        .padding()
        .background(Palette.bg)
}
