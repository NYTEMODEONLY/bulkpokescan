import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var session: Session
    @EnvironmentObject var sessionStore: SessionStoreHolder
    @EnvironmentObject var camera: CameraSession
    @Environment(\.dismiss) var dismiss

    @AppStorage(AppConfigKey.hapticsEnabled) private var haptics = AppConfigDefault.hapticsEnabled
    @AppStorage(AppConfigKey.soundEnabled) private var sound = AppConfigDefault.soundEnabled
    @AppStorage(AppConfigKey.scanCooldown) private var cooldown = AppConfigDefault.scanCooldown
    @AppStorage(AppConfigKey.torchDefaultOn) private var torchDefault = AppConfigDefault.torchDefaultOn

    @State private var confirmReset = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Toggle("Haptic feedback on capture", isOn: $haptics)
                    Toggle("Sound on capture", isOn: $sound)
                } header: {
                    Text("FEEDBACK").font(Typography.mono(10, weight: .bold)).tracking(1.4).foregroundStyle(Palette.yellow)
                }

                Section {
                    HStack {
                        Text("Scan cooldown")
                        Spacer()
                        Text(String(format: "%.1fs", cooldown)).foregroundStyle(Palette.text2).font(Typography.mono(13))
                    }
                    Slider(value: $cooldown, in: 0.5...3.0, step: 0.1)
                        .onChange(of: cooldown) { new in camera.setCooldown(new) }
                    Toggle("Default torch on at launch", isOn: $torchDefault)
                } header: {
                    Text("SCANNER").font(Typography.mono(10, weight: .bold)).tracking(1.4).foregroundStyle(Palette.yellow)
                } footer: {
                    Text("Cooldown is the minimum gap between captures of the same code held in the viewfinder.")
                }

                Section {
                    Button(role: .destructive) {
                        confirmReset = true
                    } label: {
                        Text("Reset session…")
                    }
                } header: {
                    Text("DATA").font(Typography.mono(10, weight: .bold)).tracking(1.4).foregroundStyle(Palette.yellow)
                } footer: {
                    Text("Currently \(session.codes.count) code\(session.codes.count == 1 ? "" : "s") in this session.")
                }

                Section {
                    Link(destination: URL(string: "https://bulkpokescan.app/privacy")!) {
                        HStack {
                            Text("Privacy Policy").foregroundStyle(Palette.text)
                            Spacer()
                            Image(systemName: "arrow.up.right.square")
                                .font(.system(size: 12))
                                .foregroundStyle(Palette.textMuted)
                        }
                    }
                    Link(destination: URL(string: "https://bulkpokescan.app/terms")!) {
                        HStack {
                            Text("Terms of Use").foregroundStyle(Palette.text)
                            Spacer()
                            Image(systemName: "arrow.up.right.square")
                                .font(.system(size: 12))
                                .foregroundStyle(Palette.textMuted)
                        }
                    }
                    Link(destination: URL(string: "https://bulkpokescan.app/support")!) {
                        HStack {
                            Text("Support").foregroundStyle(Palette.text)
                            Spacer()
                            Image(systemName: "arrow.up.right.square")
                                .font(.system(size: 12))
                                .foregroundStyle(Palette.textMuted)
                        }
                    }
                } header: {
                    Text("LEGAL").font(Typography.mono(10, weight: .bold)).tracking(1.4).foregroundStyle(Palette.yellow)
                } footer: {
                    Text("Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc. — this app is unofficial and unaffiliated.")
                }
            }
            .scrollContentBackground(.hidden)
            .background(Palette.bg)
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
            .confirmationDialog("Clear all captured codes?", isPresented: $confirmReset, titleVisibility: .visible) {
                Button("Clear all codes", role: .destructive) {
                    session.removeAll()
                    sessionStore.store.scheduleSave()
                }
                Button("Cancel", role: .cancel) {}
            }
        }
    }
}
