import Foundation

enum AppConfigKey {
    static let hapticsEnabled  = "config.haptics_enabled"
    static let soundEnabled    = "config.sound_enabled"
    static let scanCooldown    = "config.scan_cooldown"
    static let torchDefaultOn  = "config.torch_default_on"
}

enum AppConfigDefault {
    static let hapticsEnabled  = true
    static let soundEnabled    = false
    static let scanCooldown    = 1.5
    static let torchDefaultOn  = false
}

enum AppInfo {
    static let appVersion = (Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String) ?? "1.0.0"
    static let buildNumber = (Bundle.main.infoDictionary?["CFBundleVersion"] as? String) ?? "1"
    static let userAgent = "BulkPokeScan-iOS/\(appVersion)"
    static let tallyURL = URL(string: "https://bulkpokescan.vercel.app/api/tally")!
}
