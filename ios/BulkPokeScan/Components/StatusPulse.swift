import SwiftUI

/// Pulsing dot showing camera status: live (green) / scanning (cyan) / idle (gray).
struct StatusPulse: View {
    enum State { case live, scanning, idle }
    let state: State

    @SwiftUI.State private var pulse = false

    var body: some View {
        HStack(spacing: 6) {
            ZStack {
                Circle()
                    .fill(color.opacity(0.35))
                    .frame(width: 14, height: 14)
                    .scaleEffect(pulse ? 1.6 : 1.0)
                    .opacity(pulse ? 0.0 : 0.7)
                Circle()
                    .fill(color)
                    .frame(width: 8, height: 8)
            }
            Text(label)
                .font(Typography.mono(10, weight: .bold))
                .tracking(1.6)
                .foregroundStyle(Palette.text2)
        }
        .onAppear {
            guard state != .idle else { return }
            withAnimation(.easeOut(duration: 1.2).repeatForever(autoreverses: false)) {
                pulse = true
            }
        }
    }

    private var color: Color {
        switch state {
        case .live:     return Palette.success
        case .scanning: return Palette.scan
        case .idle:     return Palette.textMuted
        }
    }

    private var label: String {
        switch state {
        case .live:     return "LIVE"
        case .scanning: return "SCANNING"
        case .idle:     return "OFF"
        }
    }
}

#Preview {
    VStack(spacing: 16) {
        StatusPulse(state: .live)
        StatusPulse(state: .scanning)
        StatusPulse(state: .idle)
    }
    .padding()
    .background(Palette.bg)
}
