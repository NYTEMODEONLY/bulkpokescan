import Foundation

/// Mirrors the desktop's tally wiring (src/main_window.py:_fetch_tally / _post_tally).
/// Polls every 60s, increments on capture, fails silently.
@MainActor
final class TallyClient: ObservableObject {
    @Published private(set) var globalTotal: Int?

    private let pollInterval: TimeInterval = 60
    private var pollTimer: Timer?

    func start() {
        Task { await self.fetch() }
        pollTimer?.invalidate()
        pollTimer = Timer.scheduledTimer(withTimeInterval: pollInterval, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in await self?.fetch() }
        }
    }

    func stop() {
        pollTimer?.invalidate()
        pollTimer = nil
    }

    func increment() {
        Task { await self.post() }
    }

    private func fetch() async {
        var req = URLRequest(url: AppInfo.tallyURL)
        req.httpMethod = "GET"
        req.setValue(AppInfo.userAgent, forHTTPHeaderField: "User-Agent")
        req.cachePolicy = .reloadIgnoringLocalCacheData
        do {
            let (data, _) = try await URLSession.shared.data(for: req)
            if let obj = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let total = obj["total"] as? Int {
                globalTotal = total
            }
        } catch {
            // Silent failure — counter stays stale until next poll
        }
    }

    private func post() async {
        var req = URLRequest(url: AppInfo.tallyURL)
        req.httpMethod = "POST"
        req.setValue(AppInfo.userAgent, forHTTPHeaderField: "User-Agent")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = "{}".data(using: .utf8)
        do {
            let (data, _) = try await URLSession.shared.data(for: req)
            if let obj = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let total = obj["total"] as? Int {
                globalTotal = total
            }
        } catch {
            // Silent failure
        }
    }
}
