import SwiftUI

/// Cyan badge showing the live global scan tally. Polls via TallyClient.
struct GlobalTallyBadge: View {
    @ObservedObject var tally: TallyClient

    var body: some View {
        HStack(spacing: 4) {
            Text(formatted)
                .font(Typography.mono(10, weight: .bold))
                .tracking(1.0)
            Text("SCANNED")
                .font(Typography.mono(10, weight: .bold))
                .tracking(1.0)
                .opacity(0.85)
        }
        .foregroundStyle(Palette.scan)
        .lineLimit(1)
        .fixedSize(horizontal: true, vertical: false)
        .padding(.horizontal, 9)
        .padding(.vertical, 4)
        .background(
            RoundedRectangle(cornerRadius: 10)
                .fill(Palette.scan.opacity(0.10))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(Palette.scan.opacity(0.35), lineWidth: 1)
        )
        .accessibilityLabel("Global scan tally: \(formatted)")
    }

    private var formatted: String {
        guard let total = tally.globalTotal else { return "—" }
        let f = NumberFormatter()
        f.numberStyle = .decimal
        return f.string(from: NSNumber(value: total)) ?? "\(total)"
    }
}
