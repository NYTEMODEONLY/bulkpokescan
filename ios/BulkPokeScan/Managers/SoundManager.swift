import AudioToolbox
import AVFoundation

@MainActor
enum SoundManager {
    /// "Tink" system sound — short, pleasant capture confirmation.
    /// See /System/Library/Audio/UISounds/ for the catalog.
    private static let captureSoundID: SystemSoundID = 1057

    /// Plays the capture sound if the user has it enabled in Settings.
    /// Respects the device mute switch (ambient audio session category).
    static func capture() {
        let enabled = UserDefaults.standard.object(forKey: AppConfigKey.soundEnabled) as? Bool
            ?? AppConfigDefault.soundEnabled
        guard enabled else { return }
        ensureAudioSession()
        AudioServicesPlaySystemSound(captureSoundID)
    }

    /// Sets the audio session to `.ambient` once so the capture sound mixes
    /// with other audio (Spotify, podcasts) and respects the silent switch.
    /// Without this, AVCaptureSession's implicit audio session config can
    /// suppress the system sound while the camera is running.
    private static var didConfigureSession = false
    private static func ensureAudioSession() {
        guard !didConfigureSession else { return }
        didConfigureSession = true
        try? AVAudioSession.sharedInstance().setCategory(.ambient, options: [.mixWithOthers])
        try? AVAudioSession.sharedInstance().setActive(true)
    }
}
