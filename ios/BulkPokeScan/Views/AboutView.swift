import SwiftUI

struct AboutView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var tally: TallyClient

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 18) {
                    PokeballIcon()
                        .frame(width: 96, height: 96)
                        .padding(.top, 28)

                    HStack(spacing: 0) {
                        Text("Bulk")
                            .font(Typography.display(26, weight: .bold))
                            .foregroundStyle(Palette.text)
                        Text("PokeScan")
                            .font(Typography.display(26, weight: .medium))
                            .foregroundStyle(Palette.yellow)
                    }
                    HStack(spacing: 8) {
                        Text("v\(AppInfo.appVersion) (\(AppInfo.buildNumber))")
                            .font(Typography.mono(11))
                            .tracking(1.0)
                            .foregroundStyle(Palette.textMuted)
                        Circle()
                            .fill(tally.globalTotal != nil ? Palette.success : Palette.textMuted)
                            .frame(width: 8, height: 8)
                    }

                    Text("A high-performance scanner for Pokémon TCG redemption codes. Capture codes one at a time or in batches, group them in blocks of 10, and export with a tap.")
                        .font(Typography.body(13))
                        .foregroundStyle(Palette.text2)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 24)

                    globalTallyCard
                        .padding(.horizontal, 24)
                        .padding(.top, 6)

                    EnergyStrip(size: 9, spacing: 8)
                        .padding(.top, 4)

                    HStack(spacing: 6) {
                        Image(systemName: "moon.fill")
                            .font(.system(size: 10))
                            .foregroundStyle(Palette.yellow)
                        Text("Made by NYTEMODE")
                            .font(Typography.mono(11, weight: .bold))
                            .tracking(1.6)
                            .foregroundStyle(Palette.textMuted)
                    }
                    .padding(.top, 16)
                }
                .frame(maxWidth: .infinity)
                .padding(.bottom, 30)
            }
            .background(Palette.bg)
            .navigationTitle("About")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    private var globalTallyCard: some View {
        VStack(spacing: 6) {
            Text(formattedTotal)
                .font(Typography.display(40, weight: .bold))
                .foregroundStyle(Palette.yellow)
                .monospacedDigit()
                .contentTransition(.numericText())
                .animation(.easeOut(duration: 0.4), value: tally.globalTotal)
            Text("CARDS SCANNED WORLDWIDE")
                .font(Typography.mono(11, weight: .bold))
                .tracking(1.6)
                .foregroundStyle(Palette.text2)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 18)
        .background(RoundedRectangle(cornerRadius: 12).fill(Palette.surface2))
        .overlay(RoundedRectangle(cornerRadius: 12).stroke(Palette.border, lineWidth: 1))
    }

    private var formattedTotal: String {
        guard let total = tally.globalTotal else { return "—" }
        return Self.numberFormatter.string(from: NSNumber(value: total)) ?? "\(total)"
    }

    private static let numberFormatter: NumberFormatter = {
        let f = NumberFormatter()
        f.numberStyle = .decimal
        f.groupingSeparator = ","
        return f
    }()
}
