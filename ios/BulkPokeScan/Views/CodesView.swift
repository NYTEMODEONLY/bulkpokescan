import SwiftUI

struct CodesView: View {
    @EnvironmentObject var session: Session
    @EnvironmentObject var sessionStore: SessionStoreHolder
    @State private var tab: ListTab = .all
    @State private var showExport = false
    @State private var showClearConfirm1 = false
    @State private var showClearConfirm2 = false

    enum ListTab: Hashable { case all, blocks }

    var body: some View {
        VStack(spacing: 14) {
            Card { codesCard.padding(16) }
                .padding(.horizontal, 14)
                .padding(.top, 14)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .background(Palette.bg)
        .sheet(isPresented: $showExport) { ExportSheet() }
        // Two-step confirmation: prevents accidental loss of scanned codes.
        // First prompt acknowledges the action; second prompt re-confirms
        // because session.removeAll() is irreversible from the UI (the
        // shake-to-undo stack survives, but users won't always know that).
        .confirmationDialog(
            "Clear all \(session.codes.count) codes?",
            isPresented: $showClearConfirm1,
            titleVisibility: .visible
        ) {
            Button("Clear All", role: .destructive) { showClearConfirm2 = true }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("You're about to delete every code in this session.")
        }
        .confirmationDialog(
            "This cannot be easily undone",
            isPresented: $showClearConfirm2,
            titleVisibility: .visible
        ) {
            Button("Yes, Delete All \(session.codes.count) Codes", role: .destructive) {
                clearAll()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("All scanned codes will be permanently removed. (Shake-to-undo will still recover them once.)")
        }
    }

    private func clearAll() {
        session.removeAll()
        sessionStore.store.scheduleSave()
        HapticsManager.error()
    }

    private var codesCard: some View {
        VStack(spacing: 14) {
            SectionTitle("CODES", trailing: AnyView(headerActions))
            Picker("", selection: $tab) {
                Text("All Codes").tag(ListTab.all)
                Text("Code Blocks").tag(ListTab.blocks)
            }
            .pickerStyle(.segmented)

            Group {
                switch tab {
                case .all:    AllCodesList()
                case .blocks: CodeBlocksList()
                }
            }
            .frame(maxWidth: .infinity)
            .frame(minHeight: 320)
        }
    }

    private var headerActions: some View {
        HStack(spacing: 14) {
            Button {
                showClearConfirm1 = true
            } label: {
                Image(systemName: "trash")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundStyle(session.codes.isEmpty ? Palette.textMuted : Palette.red)
            }
            .disabled(session.codes.isEmpty)
            .accessibilityLabel("Clear all codes")

            Button {
                showExport = true
            } label: {
                Label("Export", systemImage: "square.and.arrow.up")
                    .font(Typography.body(13, weight: .semibold))
                    .foregroundStyle(session.codes.isEmpty ? Palette.textMuted : Palette.text)
            }
            .disabled(session.codes.isEmpty)
        }
    }
}
