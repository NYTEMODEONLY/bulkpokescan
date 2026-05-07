import UIKit

@MainActor
enum HapticsManager {
    static func capture() {
        guard UserDefaults.standard.object(forKey: AppConfigKey.hapticsEnabled) as? Bool ?? AppConfigDefault.hapticsEnabled else { return }
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.prepare()
        generator.impactOccurred()
    }

    static func error() {
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(.error)
    }

    /// Warning pattern — used when a scanned code is already in the session.
    /// Distinct from `capture()` so the user can feel the difference without
    /// looking at the screen.
    static func duplicate() {
        guard UserDefaults.standard.object(forKey: AppConfigKey.hapticsEnabled) as? Bool ?? AppConfigDefault.hapticsEnabled else { return }
        let generator = UINotificationFeedbackGenerator()
        generator.prepare()
        generator.notificationOccurred(.warning)
    }
}
