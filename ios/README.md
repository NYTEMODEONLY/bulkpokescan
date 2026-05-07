# BulkPokeScan — iOS

Native iPhone port of the BulkPokeScan desktop scanner. Same brand, same flow, same global tally — built with SwiftUI, AVFoundation, and the same `https://bulkpokescan.vercel.app/api/tally` backend used by the web and desktop apps.

## Status

**Running on device** as of 2026-05-03. Personal Team-signed builds installing to `Lobo's 15` (iPhone 15 Pro Max). All v0 features wired up:

- Camera scanning via `AVCaptureMetadataOutput` (no OpenCV needed on iOS)
- Card-based scanner UI matching the [web mobile app](https://bulkpokescan.vercel.app)
- Tab navigation: Scanner / Codes
- Manual entry, Code Blocks (groups of 10), Share Sheet export
- Session persistence via UserDefaults
- Live global tally polling
- Haptics, torch toggle, pinch-to-zoom, shake-to-undo
- Settings, About

Pending (revisit-soon):

- App icon — currently a placeholder
- Launch screen — solid ink, will get the Pokéball
- Accessibility / VoiceOver pass
- TestFlight migration — paid Apple Developer enrollment approved 2026-05-06; distribution work in progress (see [Roadmap](#roadmap))

## Architecture

| | |
|---|---|
| Language | Swift 5.9+ |
| UI | SwiftUI |
| Min iOS | 16.4 |
| Camera | `AVFoundation` (`AVCaptureSession` + `AVCaptureMetadataOutput`) |
| Persistence | `UserDefaults` (Codable JSON) |
| Network | `URLSession` (no third-party deps) |
| Project gen | `xcodegen` from [`project.yml`](./project.yml) |
| Bundle ID (dev) | `com.nytemode.bulkpokescan.dev` (Personal Team) |
| Bundle ID (prod) | `com.nytemode.bulkpokescan` (paid team) |
| Distribution (now) | Free Personal Team — 7-day device builds |
| Distribution (next) | TestFlight |

## Folder layout

```
ios/
├── README.md                  ← this file
├── project.yml                ← xcodegen project spec
├── BulkPokeScan.xcodeproj/    ← generated; safe to delete + regenerate
├── build/                     ← simulator build output (gitignored)
├── build-device/              ← device build output (gitignored)
└── BulkPokeScan/
    ├── BulkPokeScanApp.swift  @main App entry, environment wiring
    ├── Info.plist             camera usage description, dark mode, portrait
    ├── PrivacyInfo.xcprivacy  App Store privacy manifest (UserDefaults declared)
    ├── Models/
    │   ├── Code.swift         struct ScannedCode (value, source, capturedAt)
    │   ├── Session.swift      ObservableObject, codes + 50-deep undo stack
    │   └── AppConfig.swift    UserDefaults keys + AppInfo (version, tally URL)
    ├── Views/
    │   ├── RootView.swift     TabView + top bar + footer + shake handler
    │   ├── ScannerView.swift  Card with camera/Pokéball/buttons/tip strip
    │   ├── CodesView.swift    Card with All Codes / Code Blocks segmented
    │   ├── AllCodesList.swift numbered #001… list, swipe-delete, tap-copy
    │   ├── CodeBlocksList.swift  sectioned by 10 with Copy block button
    │   ├── AddCodeSheet.swift manual-entry modal
    │   ├── ExportSheet.swift  format picker → ShareLink
    │   ├── SettingsView.swift haptics, cooldown, torch default, reset
    │   └── AboutView.swift    Pokéball + EnergyStrip + version + credit
    ├── Components/
    │   ├── PokeballIcon.swift programmatic SwiftUI Canvas
    │   ├── EnergyStrip.swift  8 rotated diamonds in energy-type colors
    │   ├── Reticle.swift      pulsing corner-mark capture frame
    │   ├── ScanLine.swift     vertical sweeping cyan line
    │   ├── StatusPulse.swift  live/scanning/idle dot
    │   ├── GlobalTallyBadge.swift  cyan SCANNED count badge
    │   ├── CapturePill.swift  yellow "● n" session-count pill
    │   ├── Card.swift         shared bordered card frame + SectionTitle
    │   ├── CustomTabBar.swift bottom tabs (Scanner / Codes) with yellow underline
    │   └── Footer.swift       V1.4.2 + status dot + ABOUT + NYTEMODE
    ├── Camera/
    │   ├── CameraSession.swift   AVCaptureSession ObservableObject
    │   ├── CameraPreview.swift   UIViewRepresentable wrapping AVCaptureVideoPreviewLayer
    │   └── QRDelegate.swift      AVCaptureMetadataOutputObjectsDelegate w/ cooldown + dedup
    ├── Managers/
    │   ├── SessionStore.swift    UserDefaults persistence, 500ms debounced save
    │   ├── TallyClient.swift     URLSession poll (60s) + post on capture, silent failures
    │   └── HapticsManager.swift  UIImpactFeedbackGenerator wrapper
    ├── Theme/
    │   ├── Palette.swift         hex colors ported from src/theme.py
    │   ├── Typography.swift      Space Grotesk / Inter Tight / JetBrains Mono with system fallback
    │   └── EnergyType.swift      8 types + deterministic per-code hash
    └── Resources/
        ├── Assets.xcassets/      AppIcon (placeholder), AccentColor
        └── Fonts/                drop .ttf files here (optional)
```

## Build & run

### Simulator (no device, no signing)

iPhone 16 Pro on iOS 18.2 simulator (UDID `8E07025E-BDAD-4DCD-8194-604FF01CA440`):

```bash
cd ios
xcodebuild -project BulkPokeScan.xcodeproj -scheme BulkPokeScan -configuration Debug \
  -destination "id=8E07025E-BDAD-4DCD-8194-604FF01CA440" \
  -derivedDataPath ./build CODE_SIGNING_ALLOWED=NO build

# Install + launch
xcrun simctl boot 8E07025E-BDAD-4DCD-8194-604FF01CA440 2>/dev/null || true
open -a Simulator
xcrun simctl install 8E07025E-BDAD-4DCD-8194-604FF01CA440 \
  ./build/Build/Products/Debug-iphonesimulator/BulkPokeScan.app
xcrun simctl launch 8E07025E-BDAD-4DCD-8194-604FF01CA440 com.nytemode.bulkpokescan.dev

# Screenshot
xcrun simctl io 8E07025E-BDAD-4DCD-8194-604FF01CA440 screenshot /tmp/bulkpokescan.png

# Pre-grant camera permission to skip the system dialog
xcrun simctl privacy 8E07025E-BDAD-4DCD-8194-604FF01CA440 grant camera com.nytemode.bulkpokescan.dev
```

### Device (`Lobo's 15`)

The CLI build needs a team ID and a real provisioning profile. Easier path: open Xcode, hit Cmd-R.

```bash
open ios/BulkPokeScan.xcodeproj
# In Xcode: pick "Lobo's 15" in the device dropdown → Cmd-R
```

If you want to drive it from CLI after Xcode has cached a profile:

```bash
xcodebuild -project BulkPokeScan.xcodeproj -scheme BulkPokeScan -configuration Debug \
  -destination "id=00008130-001815403A92001C" \
  -derivedDataPath ./build-device \
  -allowProvisioningUpdates \
  -allowProvisioningDeviceRegistration \
  build
```

## Regenerating the Xcode project

When you add new Swift files, run:

```bash
cd ios && xcodegen generate
```

This recreates `BulkPokeScan.xcodeproj` from `project.yml`. **The .xcodeproj is disposable** — never edit it by hand; tweak `project.yml` instead. Xcode will reload the file automatically when xcodegen rewrites it.

## Signing setup (if doing this on a fresh Mac)

The current Mac is set up. For reference / future Macs:

1. **Xcode → Settings → Accounts** (Cmd-,) → **+** → Apple ID → sign in with the dev Apple ID. Confirm the team appears in the right pane.
2. Open `BulkPokeScan.xcodeproj`, click the blue project icon → BulkPokeScan target → **Signing & Capabilities** → set **Team** to `(Personal Team)` for dev builds, or the paid team for TestFlight/App Store.
3. **Important:** Do NOT hardcode `DEVELOPMENT_TEAM` in `project.yml`. The team ID in keychain certs (`Apple Development: <email> (TEAM_ID)`) doesn't always match the active Personal Team's ID — Xcode will fail with `error: No Account for Team "X"` even when the account is signed in. Letting Xcode write the team ID via the GUI dropdown is the only reliable way.
4. iPhone: **Settings → Privacy & Security → Developer Mode → on** → reboot.
5. First launch: tap the icon → "Untrusted Developer" → **Settings → General → VPN & Device Management → tap your Apple ID → Trust** → relaunch.

## The 7-day re-sign rhythm

Free Personal Team builds expire on-device after 7 days. To refresh: plug in iPhone, open Xcode, Cmd-R. ~10 seconds.

This goes away once we move to TestFlight on the paid team (90-day builds, wireless install).

## Optional: brand fonts

The Swift code falls back gracefully to system fonts if these aren't present, but for pixel-faithful matching to the desktop:

| Family | License | Files |
|---|---|---|
| [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) | OFL | `SpaceGrotesk-Bold.ttf`, `SpaceGrotesk-Medium.ttf` |
| [Inter Tight](https://fonts.google.com/specimen/Inter+Tight) | OFL | `InterTight-Regular.ttf`, `InterTight-SemiBold.ttf` |
| [JetBrains Mono](https://www.jetbrains.com/lp/mono/) | Apache 2.0 | `JetBrainsMono-Regular.ttf`, `JetBrainsMono-Bold.ttf` |

1. Drop the `.ttf` files into `BulkPokeScan/Resources/Fonts/`
2. Uncomment the `UIAppFonts` block in [`Info.plist`](./BulkPokeScan/Info.plist)
3. `xcodegen generate` to pick up the new resource files
4. Cmd-R

## Roadmap

### Now (v0 → v0.x)

- [ ] App icon — replace `AppIcon.appiconset` placeholder with a proper 1024×1024 master
- [ ] Launch screen — centered Pokéball on `#0B0D14` ink
- [ ] Accessibility pass — VoiceOver labels, Dynamic Type
- [ ] Performance pass — Instruments time profile at 100+ codes
- [ ] Polish small layout issues found during real-device testing

### TestFlight + App Store (paid team approved 2026-05-06)

- [ ] In Apple Developer Portal: register App ID `com.nytemode.bulkpokescan`
- [ ] In App Store Connect: create the app record (name "BulkPokeScan", SKU `bulkpokescan-ios-001`)
- [ ] In Xcode: switch bundle ID from `.dev` to production, switch Team to paid, archive
- [ ] Upload to App Store Connect → TestFlight Internal first (instant), then External (~24h beta review)

### v1.x (post-TestFlight)

- iCloud sync of session across devices
- Live Activity / Dynamic Island showing active scan count
- Lock-screen widget for total scanned
- iPad layout
- Apple Watch glance
- Siri Shortcuts ("Hey Siri, log a code")

## Source-of-truth references

| What | Where |
|---|---|
| Desktop palette | [`../src/theme.py`](../src/theme.py) |
| Desktop scanner pipeline | [`../src/scanner.py`](../src/scanner.py) |
| Desktop session + tally wiring | [`../src/main_window.py`](../src/main_window.py) |
| Energy-pip hash scheme | [`../src/widgets.py`](../src/widgets.py) |
| Web mobile design reference | [`https://bulkpokescan.vercel.app`](https://bulkpokescan.vercel.app) |
| Tally API | `https://bulkpokescan.vercel.app/api/tally` (shared web + desktop + iOS) |
| Original iOS port plan | `~/.claude/plans/based-off-of-this-elegant-rabbit.md` |

## Troubleshooting

### Build fails with "No Account for Team 'XXXXXXX'"

The hardcoded team ID doesn't match Xcode's active account. Fix:

1. In Xcode → Project navigator → BulkPokeScan target → **Signing & Capabilities**
2. Set **Team** dropdown to your Personal Team (or paid team)
3. Xcode writes the correct ID into the .pbxproj
4. Build again

If `project.yml` has a `DEVELOPMENT_TEAM:` line, remove it — let Xcode manage the team ID via the GUI.

### "Untrusted Developer" on first install

iOS → Settings → General → VPN & Device Management → tap your Apple ID → Trust. Then relaunch the app.

### `simctl install` hangs forever

Two simctl install commands running on the same device deadlock each other. Fix:

```bash
pkill -9 simctl
xcrun simctl shutdown all
killall Simulator
xcrun simctl boot <UDID>
xcrun simctl bootstatus <UDID> -b   # wait for boot complete
xcrun simctl install <UDID> <path-to-app>
```

### Camera-permission dialog blocks UI testing in simulator

`xcrun simctl privacy <UDID> grant camera <bundleID>` writes the grant to the simulator's TCC.db, but the running app caches its old state. After granting, terminate + relaunch:

```bash
xcrun simctl terminate <UDID> com.nytemode.bulkpokescan.dev
xcrun simctl launch <UDID> com.nytemode.bulkpokescan.dev
```

If the dialog persists, you can also write to TCC.db directly:

```bash
sqlite3 ~/Library/Developer/CoreSimulator/Devices/<UDID>/data/Library/TCC/TCC.db \
  "INSERT OR REPLACE INTO access (service, client, client_type, auth_value, ...)
   VALUES ('kTCCServiceCamera', '<bundleID>', 0, 2, ...);"
```

### `xcodegen` not found

`brew install xcodegen` (lives at `/opt/homebrew/bin/xcodegen`).

### Cross-file SourceKit "Cannot find type X" warnings in editor

Harmless. SourceKit analyzes Swift files in isolation when the project hasn't been opened in Xcode. The errors disappear once the file is part of the Xcode build target. If they persist *during* a build, that's a real error worth investigating.
