# BulkPokeScan

<p align="center">
  <strong>The Professional Pokémon TCG Code Scanner</strong><br>
  Complete your digital collection — lightning fast.
</p>

<p align="center">
  <a href="https://bulkpokescan.vercel.app"><strong>🌐 Try the Web App</strong></a>
   ·
  <a href="#desktop-installation"><strong>💻 Install the Desktop App</strong></a>
   ·
  <a href="ios/README.md"><strong>📱 iOS App</strong></a>
   ·
  <a href="https://nytemode.com"><strong>nytemode.com</strong></a>
</p>

<p align="center">
  <a href="#three-ways-to-use-it">Versions</a> ·
  <a href="#features">Features</a> ·
  <a href="#desktop-installation">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

## Three Ways To Use It

BulkPokeScan ships in three flavors that share the same design language and workflow:

| | Web | Desktop | iOS |
|---|---|---|---|
| **URL / Source** | [bulkpokescan.vercel.app](https://bulkpokescan.vercel.app) | This repo (`src/`) | This repo (`ios/`) |
| **Install needed?** | No — open the link | Yes — Python + dependencies | Yes — Xcode + Apple ID |
| **Best for** | Phone or laptop on the go, sharing a link, one-shot use | Power users batching hundreds of cards on a fixed webcam | Phone-native scanning with haptics, torch, and Share Sheet export |
| **Stack** | Next.js + React + `qr-scanner` (browser) | PyQt5 + OpenCV (native) | SwiftUI + AVFoundation (native) |
| **Privacy** | 100% local (codes never leave the browser) | 100% local (codes never leave the machine) | 100% local (codes never leave the device) |
| **Persistence** | `localStorage` | `~/.bulkpokescan/session.json` | `UserDefaults` |
| **Status** | Live | Live (v1.4.2) | v0 — running on device, not yet on the App Store |

Pick whichever fits your workflow. The web app needs no installation and works on any modern phone or desktop browser; the desktop app is faster for marathon scanning sessions and runs without a network; the iOS app is the natural form factor for opening a booster pack and scanning straight from the phone you're already holding. All three report to the same shared global tally.

## About

BulkPokeScan is a high-performance QR code scanner for Pokémon TCG redemption codes. Scan, organize, and manage hundreds of codes at lightning speed instead of redeeming them one at a time in the official app.

## Features

- **Ultra-fast continuous scanning** — animated cyan reticle + scan-line sweep
- **Batch processing** — scan an entire booster box in one session
- **Pokédex-style numbering** — `#001`, `#002`, … with green/gray dots indicating scan source (camera vs manual)
- **Format-flexible export** — Numbered list / Raw / Space-separated / Comma-separated
- **Code Blocks tab** — auto-grouped into chunks of 10 for clean redemption batches
- **One-click copy + TXT/Markdown export**
- **Session persistence + Undo (⌘Z)** — never lose your work
- **Keyboard shortcuts** — ⌘N add, ⌘E export, ⌘, settings, Space scan, ⌘⇧C copy all
- **Trading-card design language** — creature-ball red + electric yellow palette, energy-type accents
- **Dark UI optimized for long sessions** — Space Grotesk + Inter Tight + JetBrains Mono typography

## Screenshot

<p align="center">
  <img src="assets/screenshot.png" alt="BulkPokeScan Screenshot" width="800">
</p>

> Screenshot shows an earlier version. The current redesign matches the [web app](https://bulkpokescan.vercel.app).

## Desktop Installation

### Requirements

- Python 3.10 or newer (3.13 recommended)
- A webcam
- Pokémon TCG code cards

### macOS / Windows / Linux

```bash
# 1. Clone
git clone https://github.com/NYTEMODEONLY/bulkpokescan.git
cd bulkpokescan

# 2. Create a virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python bulkpokescan.py
```

The first run creates `config.json` with sensible defaults. Customize via the in-app **Settings** dialog (⌘, / Ctrl+,) or by editing the file.

## Usage

1. **Start the camera** — `Start Camera` button (or `Ctrl+L`)
2. **Scan codes** — hold cards in front of the lens, 6–12 inches away, with even lighting
3. **Manage codes** — All Codes tab for the running list, Code Blocks tab for grouped export
4. **Export** — TXT or Markdown via `Export TXT` / `Export MD`, or copy to clipboard

## Project Structure

```
.
├── bulkpokescan.py          # desktop entry — applies global QSS, opens MainWindow
├── src/                     # desktop app (Python / PyQt5 / OpenCV)
│   ├── main_window.py       # MainWindow + behavior + state + persistence
│   ├── theme.py             # palette, typography, programmatic Pokéball icon
│   ├── widgets.py           # CameraView, StatusIndicator, Toast, EnergyStrip, …
│   ├── dialogs.py           # SettingsDialog, AboutDialog, AddCodeDialog
│   ├── scanner.py           # OpenCV QR detection wrapper
│   └── config.py            # JSON-backed settings
└── ios/                     # iOS app (SwiftUI / AVFoundation)
    ├── README.md            # iOS-specific build, signing, and roadmap docs
    ├── project.yml          # xcodegen project spec
    └── BulkPokeScan/        # Swift sources (Models / Views / Components / Camera / Managers / Theme)
```

## FAQ

**Q: Is this an official Pokémon app?**
A: No, BulkPokeScan is an unofficial, fan-made application. Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc. — this app is unaffiliated.

**Q: Is BulkPokeScan free?**
A: Yes — free, open source, MIT licensed.

**Q: Do my codes get sent anywhere?**
A: No. Both versions process codes 100% locally. Codes never touch a server.

**Q: Can I scan codes that don't have QR codes?**
A: Yes — use `Add Code` (⌘N) to enter codes manually.

**Q: Does the web app work on my iPhone?**
A: Yes — iOS Safari 15+ supports `getUserMedia()` over HTTPS, which is what Vercel provides automatically.

**Q: Is there a native iOS app?**
A: A SwiftUI port lives in [`ios/`](ios/README.md). It runs on physical iPhones today via Personal Team signing; TestFlight distribution is in progress now that the paid Apple Developer enrollment is approved. See the [iOS README](ios/README.md) for build instructions.

## Contributing

PRs welcome.

1. Fork
2. Create a feature branch (`git checkout -b feature/your-thing`)
3. Commit (`git commit -m "Add some thing"`)
4. Push (`git push origin feature/your-thing`)
5. Open a PR

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- Built by collectors, for collectors
- Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc.

---

<p align="center">
  Made with ❤️ by <a href="https://nytemode.com">NYTEMODE</a>
</p>
