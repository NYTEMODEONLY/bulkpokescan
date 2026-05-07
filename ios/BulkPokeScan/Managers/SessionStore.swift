import Foundation

/// Persists `Session.codes` to UserDefaults as JSON.
/// Save is debounced to 500ms after the last change to coalesce bursts.
@MainActor
final class SessionStore {
    private let defaultsKey = "com.nytemode.bulkpokescan.session.v1"
    private let defaults: UserDefaults
    private weak var session: Session?
    private var saveWorkItem: DispatchWorkItem?

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func attach(to session: Session) {
        self.session = session
        load(into: session)
    }

    func scheduleSave() {
        saveWorkItem?.cancel()
        let item = DispatchWorkItem { [weak self] in
            Task { @MainActor in self?.persist() }
        }
        saveWorkItem = item
        DispatchQueue.main.asyncAfter(deadline: .now() + .milliseconds(500), execute: item)
    }

    private func load(into session: Session) {
        guard let data = defaults.data(forKey: defaultsKey) else { return }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        guard let stored = try? decoder.decode([ScannedCode].self, from: data) else { return }
        session.replaceAll(stored)
    }

    private func persist() {
        guard let session else { return }
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(session.codes) else { return }
        defaults.set(data, forKey: defaultsKey)
    }
}
