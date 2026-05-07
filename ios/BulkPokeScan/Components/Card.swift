import SwiftUI

/// Reusable card frame matching the desktop's QFrame#scannerCard / #codesCard.
struct Card<Content: View>: View {
    let content: () -> Content

    init(@ViewBuilder content: @escaping () -> Content) { self.content = content }

    var body: some View {
        content()
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Palette.surface)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Palette.border, lineWidth: 1)
            )
    }
}

/// Section-title row: red accent bar + bold tracked label.
struct SectionTitle: View {
    let label: String
    var trailing: AnyView?

    init(_ label: String, trailing: AnyView? = nil) {
        self.label = label
        self.trailing = trailing
    }

    var body: some View {
        HStack(spacing: 10) {
            Rectangle()
                .fill(Palette.red)
                .frame(width: 3, height: 16)
                .cornerRadius(1.5)
            Text(label)
                .font(Typography.display(13, weight: .bold))
                .tracking(1.6)
                .foregroundStyle(Palette.text)
            Spacer()
            if let trailing { trailing }
        }
    }
}
