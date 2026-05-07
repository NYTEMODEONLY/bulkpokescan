import SwiftUI

enum AppTab: Hashable { case scanner, codes }

struct CustomTabBar: View {
    @Binding var selection: AppTab
    let codesCount: Int

    var body: some View {
        VStack(spacing: 0) {
            Rectangle()
                .fill(Palette.border)
                .frame(height: 1)
            HStack(spacing: 0) {
                tabButton(.scanner, label: "Scanner", systemImage: "camera.fill", badge: nil)
                tabButton(.codes, label: "Codes", systemImage: "list.bullet", badge: codesCount > 0 ? codesCount : nil)
            }
        }
        .background(Palette.bg)
    }

    private func tabButton(_ tab: AppTab, label: String, systemImage: String, badge: Int?) -> some View {
        let active = selection == tab
        let color: Color = active ? Palette.yellow : Palette.text2
        return Button {
            selection = tab
        } label: {
            VStack(spacing: 8) {
                HStack(spacing: 8) {
                    Image(systemName: systemImage)
                        .font(.system(size: 17, weight: .semibold))
                    Text(label)
                        .font(Typography.body(16, weight: .bold))
                    if let badge {
                        Text("\(badge)")
                            .font(Typography.mono(11, weight: .bold))
                            .foregroundStyle(Palette.yellow)
                            .padding(.horizontal, 7)
                            .padding(.vertical, 2)
                            .background(Capsule().fill(Palette.yellow.opacity(0.12)))
                            .overlay(Capsule().stroke(Palette.yellow.opacity(0.35), lineWidth: 1))
                    }
                }
                .foregroundStyle(color)
                Rectangle()
                    .fill(active ? Palette.yellow : Color.clear)
                    .frame(height: 3)
            }
            .frame(maxWidth: .infinity)
            .padding(.top, 14)
            .padding(.bottom, 0)
            .background(active ? Palette.yellow.opacity(0.06) : Color.clear)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }
}
