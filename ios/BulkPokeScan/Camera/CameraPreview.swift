import AVFoundation
import SwiftUI
import UIKit

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.videoPreviewLayer.session = session
        view.videoPreviewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(_ uiView: PreviewView, context: Context) {}

    final class PreviewView: UIView {
        override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
        var videoPreviewLayer: AVCaptureVideoPreviewLayer { layer as! AVCaptureVideoPreviewLayer }

        /// Convert a tap location in view coordinates to a normalized device-of-interest
        /// point AVFoundation expects for focusPointOfInterest.
        func devicePoint(for viewPoint: CGPoint) -> CGPoint {
            videoPreviewLayer.captureDevicePointConverted(fromLayerPoint: viewPoint)
        }
    }
}
