import AVFoundation
import Foundation

final class QRDelegate: NSObject, AVCaptureMetadataOutputObjectsDelegate {
    var cooldown: TimeInterval = 1.5
    var onDetect: ((String) -> Void)?

    private var lastCaptureAt: Date = .distantPast
    private var lastValue: String?

    func metadataOutput(_ output: AVCaptureMetadataOutput,
                        didOutput metadataObjects: [AVMetadataObject],
                        from connection: AVCaptureConnection) {
        guard let qr = metadataObjects.first as? AVMetadataMachineReadableCodeObject,
              qr.type == .qr,
              let value = qr.stringValue,
              !value.isEmpty else { return }

        let now = Date()
        if now.timeIntervalSince(lastCaptureAt) < cooldown && value == lastValue {
            return
        }

        lastCaptureAt = now
        lastValue = value
        onDetect?(value)
    }

    func resetDedup() {
        lastValue = nil
        lastCaptureAt = .distantPast
    }
}
