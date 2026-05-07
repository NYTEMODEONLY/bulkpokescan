@preconcurrency import AVFoundation
import Combine
import UIKit

@MainActor
final class CameraSession: NSObject, ObservableObject {
    enum Permission { case unknown, granted, denied }

    @Published private(set) var permission: Permission = .unknown
    @Published private(set) var isRunning = false
    @Published private(set) var hasConfigured = false
    @Published var torchOn = false {
        didSet { applyTorch() }
    }

    // AVFoundation objects are configured on `sessionQueue` (a serial dispatch
    // queue), which provides the thread-safety contract AVCaptureSession
    // requires. Marking them nonisolated lets us touch them from those
    // background closures without main-actor hops.
    nonisolated(unsafe) let captureSession = AVCaptureSession()
    nonisolated(unsafe) private let metadataOutput = AVCaptureMetadataOutput()
    nonisolated(unsafe) private let qrDelegate: QRDelegate
    private let sessionQueue = DispatchQueue(label: "bulkpokescan.camera.session")
    /// Dedicated queue for QR metadata delegate callbacks. Keeping this OFF
    /// the main thread is critical for scanner responsiveness: when the UI is
    /// busy animating an overlay (e.g., duplicate-detected alert), main-thread
    /// metadata callbacks would queue behind the animation work and feel laggy.
    private let metadataQueue = DispatchQueue(label: "bulkpokescan.camera.metadata")
    private var videoDevice: AVCaptureDevice?

    let didCaptureCode = PassthroughSubject<String, Never>()

    override init() {
        self.qrDelegate = QRDelegate()
        super.init()
        qrDelegate.onDetect = { [weak self] value in
            Task { @MainActor in self?.didCaptureCode.send(value) }
        }
    }

    /// Refreshes `permission` from the system without prompting.
    /// Called on appear so the UI reflects current state.
    func refreshPermission() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:           permission = .granted
        case .denied, .restricted:  permission = .denied
        case .notDetermined:        permission = .unknown
        @unknown default:           permission = .denied
        }
    }

    /// Asks for camera access if needed, then starts the capture session.
    func start() {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            permission = .granted
            startSession()
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                Task { @MainActor in
                    guard let self else { return }
                    self.permission = granted ? .granted : .denied
                    if granted { self.startSession() }
                }
            }
        case .denied, .restricted:
            permission = .denied
        @unknown default:
            permission = .denied
        }
    }

    func stop() {
        sessionQueue.async { [captureSession] in
            if captureSession.isRunning { captureSession.stopRunning() }
        }
        Task { @MainActor in
            self.isRunning = false
            if self.torchOn { self.torchOn = false }
        }
    }

    func setCooldown(_ seconds: TimeInterval) {
        qrDelegate.cooldown = seconds
    }

    func resetDedup() {
        qrDelegate.resetDedup()
    }

    func setFocus(at devicePoint: CGPoint) {
        guard let device = videoDevice, device.isFocusPointOfInterestSupported else { return }
        do {
            try device.lockForConfiguration()
            device.focusPointOfInterest = devicePoint
            if device.isFocusModeSupported(.autoFocus) {
                device.focusMode = .autoFocus
            }
            if device.isExposurePointOfInterestSupported {
                device.exposurePointOfInterest = devicePoint
                device.exposureMode = .autoExpose
            }
            device.unlockForConfiguration()
        } catch {}
    }

    func setZoom(_ factor: CGFloat) {
        guard let device = videoDevice else { return }
        let clamped = max(1.0, min(factor, min(device.activeFormat.videoMaxZoomFactor, 6.0)))
        do {
            try device.lockForConfiguration()
            device.videoZoomFactor = clamped
            device.unlockForConfiguration()
        } catch {}
    }

    private func startSession() {
        sessionQueue.async { [weak self] in
            guard let self else { return }
            if self.captureSession.isRunning {
                Task { @MainActor in self.isRunning = true }
                return
            }
            if !self.captureSession.inputs.isEmpty {
                // Already configured; just start.
                self.captureSession.startRunning()
                Task { @MainActor in self.isRunning = true }
                return
            }
            self.captureSession.beginConfiguration()
            self.captureSession.sessionPreset = .high

            guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
                  let input = try? AVCaptureDeviceInput(device: device),
                  self.captureSession.canAddInput(input) else {
                self.captureSession.commitConfiguration()
                return
            }
            self.captureSession.addInput(input)
            Task { @MainActor in self.videoDevice = device }

            if self.captureSession.canAddOutput(self.metadataOutput) {
                self.captureSession.addOutput(self.metadataOutput)
                self.metadataOutput.setMetadataObjectsDelegate(self.qrDelegate, queue: self.metadataQueue)
                self.metadataOutput.metadataObjectTypes = [.qr]
            }

            self.captureSession.commitConfiguration()
            self.captureSession.startRunning()

            Task { @MainActor in
                self.isRunning = true
                self.hasConfigured = true
            }
        }
    }

    private func applyTorch() {
        guard let device = videoDevice, device.hasTorch else { return }
        do {
            try device.lockForConfiguration()
            device.torchMode = torchOn ? .on : .off
            device.unlockForConfiguration()
        } catch {}
    }
}
