# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**BulkPokeScan** is a Pokémon TCG redemption-code scanner that ships in three flavors sharing one design language and one global tally counter:

| Flavor | Lives in | Stack |
|---|---|---|
| Desktop | `src/` (this repo) | Python 3.10+ · PyQt5 · OpenCV |
| iOS | `ios/BulkPokeScan/` (this repo) | Swift 5.9 · SwiftUI · AVFoundation |
| Web | separate Vercel repo | Next.js — also hosts the shared tally API |

The repo working directory is still named `pokescanbot/` for historical reasons; the product is BulkPokeScan. External infra (custom domain `bulkpokescan.app`, Vercel project, GitHub remotes, Redis keys) all use the `bulkpokescan` namespace — see "Don't break this" below.

## Common commands

### Desktop (Python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python bulkpokescan.py        # entry point
```

Settings persist to `config.json` (top level) and session state to `~/.bulkpokescan/session.json`. There are no automated tests.

### iOS

The Xcode project is **regenerated** by [xcodegen](https://github.com/yonaskolb/XcodeGen) from `ios/project.yml`. Never edit `BulkPokeScan.xcodeproj` by hand — it's disposable.

```bash
cd ios
xcodegen generate              # rebuild .xcodeproj after adding/removing Swift files
```

Simulator build (no signing required) — iPhone 16 Pro / iOS 18.2:

```bash
cd ios
xcodebuild -project BulkPokeScan.xcodeproj -scheme BulkPokeScan -configuration Debug \
  -destination "id=8E07025E-BDAD-4DCD-8194-604FF01CA440" \
  -derivedDataPath ./build CODE_SIGNING_ALLOWED=NO build

xcrun simctl boot 8E07025E-BDAD-4DCD-8194-604FF01CA440 2>/dev/null || true
open -a Simulator
xcrun simctl install 8E07025E-BDAD-4DCD-8194-604FF01CA440 \
  ./build/Build/Products/Debug-iphonesimulator/BulkPokeScan.app
xcrun simctl launch 8E07025E-BDAD-4DCD-8194-604FF01CA440 com.nytemode.bulkpokescan.dev
```

Device build (`Lobo's 15`, UDID `00008130-001815403A92001C`) is easier from Xcode (`open ios/BulkPokeScan.xcodeproj` → Cmd-R). The full CLI incantation, simctl troubleshooting (camera permission, install hangs), and TestFlight checklist live in `ios/README.md`.

## Architecture

### The shared tally is the cross-flavor link

All three flavors POST to and GET from `https://bulkpokescan.app/api/tally` to drive a single global "cards scanned worldwide" counter. This URL is baked into:

- `ios/BulkPokeScan/Models/AppConfig.swift:21`
- `src/main_window.py` (`TALLY_URL`)
- The web app (in the separate Vercel repo)

**Never store actual scanned codes server-side** — the tally is a count-only aggregate; codes stay 100% local on each client. Privacy is a feature.

### Design system flows desktop → iOS

`src/theme.py` is the source of truth for the trading-card-inspired palette (creature-ball red, electric yellow, 8 energy-type accents) and Space Grotesk / Inter Tight / JetBrains Mono typography. The iOS port hand-translated this into `ios/BulkPokeScan/Theme/Palette.swift` and `Typography.swift`. When changing brand colors, change both — they intentionally mirror.

### Brand wordmark renders two-tone

"Bulk**PokeScan**" is rendered as two adjacent labels — `"Bulk"` in `Palette.text` (white, bold) and `"PokeScan"` in `Palette.yellow` (medium). Don't merge them into a single Text/QLabel without preserving the two-tone effect. Lives in `ios/BulkPokeScan/Views/{AboutView,RootView}.swift` and `src/{main_window,dialogs}.py`.

### Desktop session model

`MainWindow` (`src/main_window.py`) owns: a `QRScanner` (OpenCV `QRCodeDetector` wrapped in `src/scanner.py`), the codes list with sources (camera vs manual), a 50-deep undo stack, debounced JSON persistence, and tally polling. Everything else (`widgets.py`, `dialogs.py`) is presentation.

### iOS session model

`Session` (`Models/Session.swift`) is the `ObservableObject` truth. `SessionStore` debounces UserDefaults writes 500ms. `CameraSession` runs `AVCaptureSession` config off the main thread (`bulkpokescan.camera.session` queue) and routes QR detections through `QRDelegate` on a dedicated `bulkpokescan.camera.metadata` queue — keeping metadata callbacks off `.main` is critical for scanner responsiveness when the UI is animating.

## Don't break this

- **`bulkpokescan.app/api/tally` URL becomes load-bearing the moment iOS ships.** As of writing, iOS hasn't shipped to TestFlight or the App Store, so the URL can still be changed cheaply. Once an App Store build is live, every shipped binary hits this exact URL forever — any future migration requires shipping an iOS update first AND accepting stale counters on old versions. The custom domain (registered through Vercel) is the canonical home; `bulkpokescan.vercel.app` 308-redirects to it. Detailed migration notes in `docs/web-to-landing-page.md`.
- **`ios/project.yml` is the source of truth** for the Xcode project — `BulkPokeScan.xcodeproj` is generated. Edits to the .xcodeproj will be wiped on next `xcodegen generate`.
- **Don't hardcode `DEVELOPMENT_TEAM`** that doesn't match the user's active Personal Team. Free Personal Teams have a team ID that often differs from the keychain cert's `Apple Development: <email> (TEAM_ID)`, and hardcoding causes `error: No Account for Team "X"` even when the account is correctly signed in. The current `project.yml` pins `Q2QT3TXJE4` for the paid team, but if anyone else builds it they'll need to clear that line and let Xcode write the team ID via Signing & Capabilities → Team dropdown.
- **Bundle IDs:** dev = `com.nytemode.bulkpokescan.dev` (Personal Team, 7-day re-sign rhythm), prod = `com.nytemode.bulkpokescan` (paid Apple Developer team, approved 2026-05-06). The `.dev` suffix is intentional — keeps the two Xcode signing profiles from colliding.
- **Repo working dir is `pokescanbot/` (still legacy)** but the git remote is now `github.com/NYTEMODEONLY/bulkpokescan.git` (renamed 2026-05-07). Don't auto-rename the working dir — that's a separate user decision because it breaks paths, IDE history, and existing terminal sessions.

## Useful pointers

- `ios/README.md` — full iOS build, signing, troubleshooting, and TestFlight checklist
- `docs/web-to-landing-page.md` — parked plan for converting the web app into a marketing landing page once iOS ships
- Memory: `~/.claude/projects/-Users-lobo-Desktop-Progress-BI2025-pokescanbot/memory/` — point-in-time project context across sessions
