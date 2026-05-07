import SwiftUI

struct AddCodeSheet: View {
    @EnvironmentObject var session: Session
    @EnvironmentObject var sessionStore: SessionStoreHolder
    @Environment(\.dismiss) var dismiss

    @State private var input = ""
    @State private var error: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Redemption code", text: $input)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()
                        .font(Typography.mono(15))
                        .listRowBackground(Palette.input)
                } header: {
                    Text("CODE").font(Typography.mono(10, weight: .bold)).tracking(1.4)
                } footer: {
                    if let error {
                        Text(error).foregroundStyle(Palette.danger)
                    } else {
                        Text("Enter the code from a redemption card. The QR scanner is faster — try it first.")
                    }
                }
            }
            .scrollContentBackground(.hidden)
            .background(Palette.bg)
            .navigationTitle("Add Code")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") { submit() }
                        .disabled(input.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
        }
    }

    private func submit() {
        let v = input.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        guard !v.isEmpty else { return }
        guard v.count <= 200 else { error = "Code is too long."; return }
        guard !session.contains(v) else { error = "That code is already in your session."; return }
        session.add(v, source: .manual)
        sessionStore.store.scheduleSave()
        dismiss()
    }
}
