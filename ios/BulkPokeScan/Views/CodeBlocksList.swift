import SwiftUI
import UIKit

struct CodeBlocksList: View {
    @EnvironmentObject var session: Session
    @State private var copiedBlockIndex: Int?

    var body: some View {
        let blocks = session.blocks(of: 10)
        Group {
            if blocks.isEmpty {
                empty
            } else {
                List {
                    ForEach(Array(blocks.enumerated()), id: \.offset) { idx, block in
                        Section {
                            ForEach(block, id: \.id) { code in
                                Text(code.value)
                                    .font(Typography.mono(12))
                                    .foregroundStyle(Palette.text)
                                    .listRowBackground(Palette.input)
                            }
                        } header: {
                            blockHeader(index: idx, count: block.count)
                        }
                    }
                }
                .listStyle(.insetGrouped)
                .scrollContentBackground(.hidden)
                .background(Palette.bg)
            }
        }
        .overlay(alignment: .bottom) {
            if let i = copiedBlockIndex {
                Text("Copied block \(i + 1)")
                    .font(Typography.body(12, weight: .semibold))
                    .foregroundStyle(Palette.text)
                    .padding(.horizontal, 14).padding(.vertical, 8)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface3))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.borderStrong, lineWidth: 1))
                    .padding(.bottom, 18)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
    }

    private func blockHeader(index: Int, count: Int) -> some View {
        HStack {
            Text("BLOCK \(index + 1)")
                .font(Typography.mono(11, weight: .bold))
                .tracking(1.3)
                .foregroundStyle(Palette.yellow)
            Text("\(count)/10")
                .font(Typography.mono(11))
                .foregroundStyle(Palette.textMuted)
            Spacer()
            Button {
                copyBlock(index: index)
            } label: {
                Label("Copy", systemImage: "doc.on.doc")
                    .font(Typography.body(11, weight: .semibold))
                    .foregroundStyle(Palette.scan)
            }
        }
    }

    private var empty: some View {
        VStack(spacing: 8) {
            Image(systemName: "square.stack.3d.up")
                .font(.system(size: 32))
                .foregroundStyle(Palette.textMuted)
            Text("No blocks yet")
                .font(Typography.display(14, weight: .bold))
                .foregroundStyle(Palette.text)
            Text("Codes group into blocks of 10 as you scan.")
                .font(Typography.body(12))
                .foregroundStyle(Palette.text2)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Palette.bg)
    }

    private func copyBlock(index: Int) {
        let blocks = session.blocks(of: 10)
        guard blocks.indices.contains(index) else { return }
        UIPasteboard.general.string = blocks[index].map(\.value).joined(separator: "\n")
        withAnimation { copiedBlockIndex = index }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            withAnimation { copiedBlockIndex = nil }
        }
    }
}
