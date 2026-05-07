import SwiftUI
import UIKit

struct ScannerView: View {
    @EnvironmentObject var camera: CameraSession
    @EnvironmentObject var session: Session
    @EnvironmentObject var tally: TallyClient
    @EnvironmentObject var sessionStore: SessionStoreHolder

    @State private var captureFlash = false
    @State private var duplicateFlash = false
    @State private var duplicateAlertSuffix: String?
    @State private var showAddSheet = false
    @State private var zoomBaseline: CGFloat = 1.0

    var body: some View {
        Card { scannerCard.padding(16) }
            .padding(.horizontal, 14)
            .padding(.vertical, 14)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Palette.bg)
            .onAppear { camera.refreshPermission() }
        .onReceive(camera.didCaptureCode) { value in
            if session.add(value, source: .scan) {
                sessionStore.store.scheduleSave()
                tally.increment()
                HapticsManager.capture()
                SoundManager.capture()
                triggerFlash()
            } else if session.contains(value) {
                HapticsManager.duplicate()
                triggerDuplicateAlert(for: value)
            }
        }
        .sheet(isPresented: $showAddSheet) { AddCodeSheet() }
    }

    // MARK: - Scanner card

    private var scannerCard: some View {
        VStack(spacing: 14) {
            SectionTitle("SCANNER", trailing: AnyView(statusIndicator))
            viewfinder
            tipStrip
            buttonRow
        }
    }

    private var statusIndicator: some View {
        HStack(spacing: 8) {
            ZStack {
                Circle()
                    .stroke(camera.isRunning ? Palette.scan : Palette.textMuted, lineWidth: 1.5)
                    .frame(width: 12, height: 12)
                Circle()
                    .fill(camera.isRunning ? Palette.scan : Palette.textMuted)
                    .frame(width: 5, height: 5)
            }
            Text(camera.isRunning ? "SCANNING" : "CAMERA OFF")
                .font(Typography.mono(11, weight: .bold))
                .tracking(1.6)
                .foregroundStyle(Palette.text2)
        }
    }

    // MARK: - Viewfinder

    private var viewfinder: some View {
        ZStack {
            Color.black

            switch camera.permission {
            case .granted where camera.isRunning:
                liveContent
            case .denied:
                permissionDenied
            default:
                cameraOff
            }

            // Capture-success flash overlay
            Color.white
                .opacity(captureFlash ? 0.20 : 0)
                .allowsHitTesting(false)

            // Duplicate-detected amber flash overlay
            Palette.yellow
                .opacity(duplicateFlash ? 0.18 : 0)
                .allowsHitTesting(false)

            // "ALREADY SCANNED" banner
            if let suffix = duplicateAlertSuffix {
                duplicateBanner(suffix: suffix)
                    .transition(.opacity.combined(with: .move(edge: .top)))
                    .allowsHitTesting(false)
            }
        }
        .aspectRatio(1, contentMode: .fit)
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(duplicateAlertSuffix != nil ? Palette.yellow : Palette.border,
                        lineWidth: duplicateAlertSuffix != nil ? 2 : 1)
        )
    }

    private func duplicateBanner(suffix: String) -> some View {
        VStack {
            HStack(spacing: 8) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundStyle(Palette.yellow)
                VStack(alignment: .leading, spacing: 2) {
                    Text("ALREADY SCANNED")
                        .font(Typography.mono(11, weight: .bold))
                        .tracking(1.6)
                        .foregroundStyle(Palette.text)
                    Text("…\(suffix)")
                        .font(Typography.mono(10))
                        .foregroundStyle(Palette.text2)
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 10)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.black.opacity(0.78))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Palette.yellow.opacity(0.7), lineWidth: 1)
            )
            .padding(.top, 14)
            Spacer()
        }
    }

    private var liveContent: some View {
        ZStack {
            CameraPreview(session: camera.captureSession)
                .gesture(
                    MagnificationGesture()
                        .onChanged { value in camera.setZoom(zoomBaseline * value) }
                        .onEnded { _ in zoomBaseline = 1.0 }
                )
            Reticle()
            VStack {
                HStack {
                    Spacer()
                    torchButton
                }
                .padding(10)
                Spacer()
            }
        }
    }

    private var cameraOff: some View {
        VStack(spacing: 14) {
            PokeballIcon(monochrome: false)
                .frame(width: 130, height: 130)
                .opacity(0.32)
                .padding(.top, 30)
            Text("Camera Off")
                .font(Typography.display(22, weight: .bold))
                .foregroundStyle(Palette.text)
            Text("Press Start Camera to begin scanning Pokémon TCG codes.")
                .font(Typography.body(13))
                .foregroundStyle(Palette.text2)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
                .padding(.bottom, 30)
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var permissionDenied: some View {
        VStack(spacing: 12) {
            Image(systemName: "camera.fill")
                .font(.system(size: 38))
                .foregroundStyle(Palette.textMuted)
            Text("Camera access required")
                .font(Typography.display(18, weight: .bold))
                .foregroundStyle(Palette.text)
            Text("Enable camera access in Settings to scan codes.")
                .font(Typography.body(13))
                .foregroundStyle(Palette.text2)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
            Button {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            } label: {
                Text("Open Settings")
                    .font(Typography.body(14, weight: .semibold))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 10)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Palette.red))
            }
        }
        .padding()
    }

    // MARK: - Tip strip

    private var tipStrip: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("[TIP]")
                .font(Typography.mono(11, weight: .bold))
                .tracking(1.6)
                .foregroundStyle(Palette.yellow)
                .padding(.top, 1)
            Text("Hold the QR code 6–12 inches from the lens with even lighting for fastest captures.")
                .font(Typography.body(13))
                .foregroundStyle(Palette.text2)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface2))
        .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.border, lineWidth: 1))
    }

    // MARK: - Buttons

    private var buttonRow: some View {
        HStack(spacing: 12) {
            primaryButton
            secondaryButton
        }
    }

    private var primaryButton: some View {
        Button {
            if camera.isRunning { camera.stop() } else { camera.start() }
        } label: {
            Text(camera.isRunning ? "Stop Camera" : "Start Camera")
                .font(Typography.body(15, weight: .semibold))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(RoundedRectangle(cornerRadius: 10).fill(Palette.red))
        }
    }

    private var secondaryButton: some View {
        Button {
            showAddSheet = true
        } label: {
            Text("Add Code")
                .font(Typography.body(15, weight: .semibold))
                .foregroundStyle(camera.isRunning ? Palette.text : Palette.text2)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface2))
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.border, lineWidth: 1))
        }
    }

    private var torchButton: some View {
        Button {
            camera.torchOn.toggle()
        } label: {
            Image(systemName: camera.torchOn ? "flashlight.on.fill" : "flashlight.off.fill")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(camera.torchOn ? Palette.yellow : Palette.text2)
                .frame(width: 34, height: 34)
                .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface2.opacity(0.85)))
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.border, lineWidth: 1))
        }
    }

    private func triggerFlash() {
        withAnimation(.easeOut(duration: 0.12)) { captureFlash = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.18) {
            withAnimation(.easeOut(duration: 0.18)) { captureFlash = false }
        }
    }

    private func triggerDuplicateAlert(for value: String) {
        let suffix = String(value.suffix(6))
        withAnimation(.easeOut(duration: 0.12)) {
            duplicateFlash = true
            duplicateAlertSuffix = suffix
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.22) {
            withAnimation(.easeOut(duration: 0.22)) { duplicateFlash = false }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.6) {
            withAnimation(.easeOut(duration: 0.25)) { duplicateAlertSuffix = nil }
        }
    }
}

/// Wrapper to expose SessionStore through the environment without it
/// being itself observable.
@MainActor
final class SessionStoreHolder: ObservableObject {
    let store: SessionStore
    init(store: SessionStore) { self.store = store }
}
