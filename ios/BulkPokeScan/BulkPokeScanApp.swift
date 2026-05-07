import SwiftUI

@main
struct BulkPokeScanApp: App {
    @StateObject private var session = Session()
    @StateObject private var tally = TallyClient()
    @StateObject private var camera = CameraSession()
    @StateObject private var sessionStoreHolder: SessionStoreHolder

    init() {
        let store = SessionStore()
        _sessionStoreHolder = StateObject(wrappedValue: SessionStoreHolder(store: store))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(session)
                .environmentObject(tally)
                .environmentObject(camera)
                .environmentObject(sessionStoreHolder)
                .preferredColorScheme(.dark)
                .tint(Palette.red)
                .onAppear {
                    sessionStoreHolder.store.attach(to: session)
                    tally.start()
                    if UserDefaults.standard.object(forKey: AppConfigKey.torchDefaultOn) as? Bool ?? AppConfigDefault.torchDefaultOn {
                        // Defer torch-on until camera session is running
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
                            camera.torchOn = true
                        }
                    }
                }
                .onChange(of: session.codes) { _ in
                    sessionStoreHolder.store.scheduleSave()
                }
        }
    }
}
