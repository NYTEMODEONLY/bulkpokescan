# CodeDex Pro

<p align="center">
  <strong>The Professional Pokémon TCG Code Scanner</strong><br>
  Complete your digital collection — lightning fast.
</p>

<p align="center">
  <a href="https://codedex-web.vercel.app"><strong>🌐 Try the Web App</strong></a>
   ·
  <a href="#desktop-installation"><strong>💻 Install the Desktop App</strong></a>
   ·
  <a href="https://nytemode.com"><strong>nytemode.com</strong></a>
</p>

<p align="center">
  <a href="#two-ways-to-use-it">Versions</a> ·
  <a href="#features">Features</a> ·
  <a href="#desktop-installation">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

## Two Ways To Use It

CodeDex Pro ships in two flavors that share the same design language and workflow:

| | Web | Desktop |
|---|---|---|
| **URL / Source** | [codedex-web.vercel.app](https://codedex-web.vercel.app) | This repo |
| **Install needed?** | No — open the link | Yes — Python + dependencies |
| **Best for** | Phone or laptop on the go, sharing a link, one-shot use | Power users batching hundreds of cards on a fixed webcam |
| **Stack** | Next.js + React + `qr-scanner` (browser) | PyQt5 + OpenCV (native) |
| **Privacy** | 100% local (codes never leave the browser) | 100% local (codes never leave the machine) |
| **Persistence** | `localStorage` | `~/.codedexpro/session.json` |

Pick whichever fits your workflow. The web app needs no installation and works on any modern phone or desktop browser; the desktop app is faster for marathon scanning sessions and runs without a network.

## About

CodeDex Pro is a high-performance QR code scanner for Pokémon TCG redemption codes. Scan, organize, and manage hundreds of codes at lightning speed instead of redeeming them one at a time in the official app.

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
  <img src="assets/screenshot.png" alt="CodeDex Pro Screenshot" width="800">
</p>

> Screenshot shows an earlier version. The current redesign matches the [web app](https://codedex-web.vercel.app).

## Desktop Installation

### Requirements

- Python 3.10 or newer (3.13 recommended)
- A webcam
- Pokémon TCG code cards

### macOS / Windows / Linux

```bash
# 1. Clone
git clone https://github.com/NYTEMODEONLY/codedexpro.git
cd codedexpro

# 2. Create a virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python codedexpro.py
```

The first run creates `config.json` with sensible defaults. Customize via the in-app **Settings** dialog (⌘, / Ctrl+,) or by editing the file.

## Usage

1. **Start the camera** — `Start Camera` button (or `Ctrl+L`)
2. **Scan codes** — hold cards in front of the lens, 6–12 inches away, with even lighting
3. **Manage codes** — All Codes tab for the running list, Code Blocks tab for grouped export
4. **Export** — TXT or Markdown via `Export TXT` / `Export MD`, or copy to clipboard

## Project Structure

```
src/
├── main.py              # entry — applies global QSS, opens MainWindow
├── main_window.py       # MainWindow + behavior + state + persistence
├── theme.py             # palette, typography, programmatic Pokéball icon
├── widgets.py           # CameraView, StatusIndicator, Toast, EnergyStrip, …
├── dialogs.py           # SettingsDialog, AboutDialog, AddCodeDialog
├── scanner.py           # OpenCV QR detection wrapper
└── config.py            # JSON-backed settings
```

## FAQ

**Q: Is this an official Pokémon app?**
A: No, CodeDex Pro is an unofficial, fan-made application. Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc. — this app is unaffiliated.

**Q: Is CodeDex Pro free?**
A: Yes — free, open source, MIT licensed.

**Q: Do my codes get sent anywhere?**
A: No. Both versions process codes 100% locally. Codes never touch a server.

**Q: Can I scan codes that don't have QR codes?**
A: Yes — use `Add Code` (⌘N) to enter codes manually.

**Q: Does the web app work on my iPhone?**
A: Yes — iOS Safari 15+ supports `getUserMedia()` over HTTPS, which is what Vercel provides automatically.

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
