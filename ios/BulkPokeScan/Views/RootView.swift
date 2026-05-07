import SwiftUI
import UIKit

struct RootView: View {
    @EnvironmentObject var session: Session
    @EnvironmentObject var camera: CameraSession
    @State private var tab: AppTab = .scanner
    @State private var showSettings = false
    @State private var showAbout = false

    var body: some View {
        VStack(spacing: 0) {
            topBar
            Group {
                switch tab {
                case .scanner: ScannerView()
                case .codes:   CodesView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Palette.bg)
            CustomTabBar(selection: $tab, codesCount: session.codes.count)
        }
        .background(Palette.bg)
        .sheet(isPresented: $showSettings) { SettingsView() }
        .sheet(isPresented: $showAbout) { AboutView() }
        .onShake { session.undo() }
        .onChange(of: tab) { newTab in
            if newTab != .scanner { camera.stop() }
        }
    }

    private var topBar: some View {
        VStack(spacing: 0) {
            HStack(spacing: 12) {
                PokeballIcon()
                    .frame(width: 36, height: 36)
                    .shadow(color: Palette.red.opacity(0.30), radius: 10, x: 0, y: 0)
                HStack(spacing: 0) {
                    Text("Bulk")
                        .font(Typography.display(22, weight: .bold))
                        .foregroundStyle(Palette.text)
                    Text("PokeScan")
                        .font(Typography.display(22, weight: .medium))
                        .foregroundStyle(Palette.yellow)
                }
                .lineLimit(1)
                .fixedSize(horizontal: true, vertical: false)
                Spacer(minLength: 6)
                iconButton(systemName: "info") { showAbout = true }
                iconButton(systemName: "gearshape.fill") { showSettings = true }
            }
            .padding(.horizontal, 14)
            .padding(.top, 8)
            .padding(.bottom, 12)
            Rectangle()
                .fill(Palette.border)
                .frame(height: 1)
        }
        .background(Palette.bg)
    }

    private func iconButton(systemName: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: systemName)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(Palette.text2)
                .frame(width: 38, height: 38)
                .background(RoundedRectangle(cornerRadius: 10).fill(Palette.surface2))
                .overlay(RoundedRectangle(cornerRadius: 10).stroke(Palette.border, lineWidth: 1))
        }
    }
}

// MARK: - Shake-to-undo

extension View {
    func onShake(_ action: @escaping () -> Void) -> some View {
        background(ShakeDetector(action: action))
    }
}

private struct ShakeDetector: UIViewControllerRepresentable {
    let action: () -> Void

    func makeUIViewController(context: Context) -> ShakeViewController {
        ShakeViewController(action: action)
    }

    func updateUIViewController(_ vc: ShakeViewController, context: Context) {
        vc.action = action
    }
}

private final class ShakeViewController: UIViewController {
    var action: () -> Void

    init(action: @escaping () -> Void) {
        self.action = action
        super.init(nibName: nil, bundle: nil)
        view.backgroundColor = .clear
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) not used") }

    override var canBecomeFirstResponder: Bool { true }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        becomeFirstResponder()
    }

    override func motionEnded(_ motion: UIEvent.EventSubtype, with event: UIEvent?) {
        if motion == .motionShake { action() }
    }
}
