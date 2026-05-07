import SwiftUI
import UIKit

struct AllCodesList: View {
    @EnvironmentObject var session: Session
    @EnvironmentObject var sessionStore: SessionStoreHolder
    @State private var copiedValue: String?

    var body: some View {
        Group {
            if session.codes.isEmpty {
                emptyState
            } else {
                List {
                    ForEach(Array(session.codes.enumerated()), id: \.element.id) { idx, code in
                        row(idx: idx, code: code)
                            .listRowBackground(Palette.input)
                            .listRowSeparatorTint(Palette.border)
                    }
                    .onDelete(perform: delete)
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
                .background(Palette.bg)
            }
        }
        .overlay(alignment: .bottom) {
            if let copied = copiedValue {
                toast("Copied \(copied)")
            }
        }
    }

    private func row(idx: Int, code: ScannedCode) -> some View {
        let energy = EnergyType.forCode(code.value)
        return HStack(spacing: 12) {
            Text(String(format: "#%03d", idx + 1))
                .font(Typography.mono(12, weight: .bold))
                .foregroundStyle(Palette.textMuted)
                .frame(width: 44, alignment: .leading)
            Circle()
                .fill(energy.color)
                .frame(width: 8, height: 8)
            Text(code.value)
                .font(Typography.mono(13, weight: .regular))
                .foregroundStyle(Palette.text)
                .lineLimit(1)
                .truncationMode(.middle)
            Spacer()
            if code.source == .manual {
                Image(systemName: "square.and.pencil")
                    .font(.system(size: 11))
                    .foregroundStyle(Palette.textMuted)
            }
        }
        .contentShape(Rectangle())
        .onTapGesture { copy(code.value) }
    }

    private var emptyState: some View {
        VStack(spacing: 8) {
            Image(systemName: "qrcode")
                .font(.system(size: 36))
                .foregroundStyle(Palette.textMuted)
            Text("No codes yet")
                .font(Typography.display(14, weight: .bold))
                .foregroundStyle(Palette.text)
            Text("Point the camera at a redemption code QR to capture it.")
                .font(Typography.body(12))
                .foregroundStyle(Palette.text2)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(.vertical, 30)
        .background(Palette.bg)
    }

    private func toast(_ text: String) -> some View {
        Text(text)
            .font(Typography.body(12, weight: .semibold))
            .foregroundStyle(Palette.text)
            .padding(.horizontal, 14)
            .padding(.vertical, 8)
            .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface3))
            .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.borderStrong, lineWidth: 1))
            .padding(.bottom, 18)
            .transition(.move(edge: .bottom).combined(with: .opacity))
    }

    private func copy(_ value: String) {
        UIPasteboard.general.string = value
        withAnimation { copiedValue = value }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            withAnimation { copiedValue = nil }
        }
    }

    private func delete(at offsets: IndexSet) {
        for idx in offsets {
            let value = session.codes[idx].value
            session.remove(value)
        }
        sessionStore.store.scheduleSave()
    }
}
