# App Store Connect Metadata — BulkPokeScan v1.0

Paste-ready bundle for the App Store Connect listing. Each section
maps to a specific ASC field. Character counts in parentheses are the
actual length (excluding the trailing whitespace) so you can confirm
you're under Apple's limits.

---

## App Information

### Name (max 30 chars)

```
BulkPokeScan: TCG Codes
```

(23 chars)

> Why this and not "BulkPokeScan: Pokémon TCG Codes"? Apple has a
> long history of rejecting third-party trademarks (Pokémon)
> in app *names*. The same word is allowed in subtitle, keywords,
> and description (nominative fair use). Avoiding it in the name
> lowers 5.2.1 rejection risk. The TCG/Codes hit serves the same
> top intent terms.

**Backup options if Apple rejects this one:**
- `BulkPokeScan – Card Codes` (24)
- `BulkPokeScan` (12 — bare wordmark, push all keyword weight to subtitle/keywords)

### Subtitle (max 30 chars)

```
Pokémon TCG Code Scanner
```

(24 chars)

> "Pokémon" with the acute accent. Apple normally allows it in
> subtitle. If Apple rejects, drop the accent (`Pokemon TCG Code Scanner`,
> still 24 chars).

### Bundle ID

```
com.nytemode.bulkpokescan
```

> Must be registered in your Developer Portal first. Different from
> the dev sideload bundle (`com.nytemode.bulkpokescan.dev`).

### SKU (private)

```
bulkpokescan-ios-v1
```

### Primary Language

```
English (U.S.)
```

---

## Categories

- **Primary:** Utilities
- **Secondary:** Productivity

> Utilities is a stronger fit than Reference or Lifestyle for a
> code-scanning tool. Productivity broadens discoverability for
> users searching for organizational tools.

---

## Pricing & Availability

- **Price tier:** Tier 5 — **$4.99 USD**
- **Availability:** All territories Apple supports (default)
- **Volume / Education discounts:** Off (v1.0)
- **Pre-order:** Off (v1.0)

> Apple maps tier 5 to local prices in every territory automatically.
> No need to set per-territory prices.

---

## Pricing & Distribution narrative (not a field — just confirmation)

- One-time purchase. **No** in-app purchases. **No** subscriptions.
- **No** family sharing for v1.0 (revisit in v1.1; family sharing
  is enabled at the App Store Connect level after v1.0 ships).

---

## Promotional Text (max 170 chars · UPDATABLE without resubmission)

```
Scan an entire booster box in minutes. 100% on-device. No subscriptions, no ads, no data collection. Built by collectors, for collectors.
```

(141 chars)

> Refresh this for sales, holidays, or new feature drops without
> needing a new app review. Don't waste it on evergreen copy that
> already lives in the description.

---

## Description (max 4000 chars)

> The first ~3 lines (~170 chars) are visible without "more" tap on
> the App Store. Front-load the value prop and the privacy hook —
> they convert at $4.99.

```
BulkPokeScan is the professional Pokémon TCG redemption-code scanner. Scan, organize, and export hundreds of codes at lightning speed — without ever sending one to a server.

Open a booster box, point the camera, and capture code after code at full speed. Codes are numbered Pokédex-style (#001, #002, …) and grouped automatically into clean blocks of 10 — exactly the batch size you need to redeem in the official Pokémon TCG Live app. Export as TXT or Markdown, or copy a block at a time straight to your clipboard.

Built for marathon scanning sessions. Built for the booster-box opener who's tired of one-at-a-time entry. Built for the privacy-conscious collector who doesn't want a third-party scanner sending their codes anywhere.

— FEATURES —

• Ultra-fast continuous QR scanning with an animated reticle
• Pokédex-style numbering with green/gray dots showing scan source (camera vs. manual entry)
• Code Blocks tab — auto-grouped into 10s for clean redemption batches
• Four export formats: numbered list, raw, space-separated, comma-separated
• TXT and Markdown file export via Share Sheet
• Manual code entry for QR codes that won't scan
• Undo with shake-to-undo gesture (50-deep stack)
• Pinch-to-zoom on the camera viewport
• Torch toggle for low-light booster pulls
• Tap-to-focus for damaged or angled codes
• Haptic feedback + capture sound (both toggleable, both respect ringer switch)
• Session persistence — your codes survive app kills, restarts, and updates
• Live worldwide scan counter (decorative; not tied to your device)
• Trading-card visual language with creature-ball red + electric yellow palette and energy-type accents
• Dark UI optimized for long sessions
• Custom typography (Space Grotesk + Inter Tight + JetBrains Mono)

— PRIVACY —

100% on-device. The QR codes you scan never leave your iPhone. No accounts. No analytics. No advertising. No data collection. The single network request the app makes is an empty increment to a worldwide counter — no payload, no scanned content, no user data, ever.

Camera access is used solely for QR detection. Frames are processed by Apple's AVFoundation framework and immediately discarded; nothing is saved or transmitted.

— PRICING —

One-time $4.99. No subscriptions. No in-app purchases. No upsells. No ads. You buy it once, you own it. Future updates are free.

— ABOUT —

BulkPokeScan is a NYTEMODE project, built by collectors, for collectors. The same codebase ships as a desktop app and a web app, all sharing one design and one global counter. Visit bulkpokescan.app for the web version.

Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc. — this app is unofficial and unaffiliated.
```

(Approximately 2,400 chars — well under the 4,000 limit.)

---

## Keywords (max 100 chars · comma-separated · NO spaces after commas)

```
qr,redemption,trading,card,game,booster,collector,collection,batch,export,offline,private,bulk,scan
```

(98 chars)

> Excluded (already in title/subtitle, would be wasted): "Pokémon",
> "TCG", "Code", "Codes", "Scanner". Apple auto-indexes those.
>
> Plurals are unnecessary — Apple matches them automatically.
>
> "qr" is a high-intent short token; "redemption" is the primary
> feature; "booster"/"collection"/"collector" capture the audience
> vocabulary; "offline"/"private" capture the privacy-first
> sub-segment.

---

## Support URL (REQUIRED)

```
https://bulkpokescan.app/support
```

## Marketing URL (optional, recommended)

```
https://bulkpokescan.app
```

## Privacy Policy URL (REQUIRED)

```
https://bulkpokescan.app/privacy
```

---

## App Privacy — Privacy Nutrition Label

The cleanest possible label: **Data Not Collected**.

### Questionnaire walkthrough

> Answer "No" to the first question and the entire questionnaire collapses.

**"Do you or your third-party partners collect data from this app?"**
→ **No**

That's the entire answer. Skip every downstream question.

### Why this is correct (defensible if App Review pushes back)

The single network request the app makes — `POST /api/tally` — is an
empty body that increments a global counter. The server stores a
single integer (`bulkpokescan:total` in Redis). No element of the
request is associated with the user's identity. The transient
rate-limit IP key (60-req/min, sliding window) auto-expires within
the window and is not associated with the user identity, the scanned
code, or any persistent record.

Per Apple's App Privacy framework: data that is not linked to user
identity AND not used for tracking does not constitute
"data collection." This app's tally request meets neither bar. The
camera frames never reach the server. The codes never reach the
server.

### If App Review asks for more detail (rare for camera apps)

> "Camera frames are processed entirely on-device by Apple's
> AVFoundation framework (`AVCaptureMetadataOutput`). The decoded
> string is stored in `UserDefaults` on the device. No frame, no
> code, and no derived data is transmitted, written to a server,
> shared with third parties, or otherwise leaves the device."

---

## Age Rating Questionnaire

Almost everything is **None**. Specific answers:

| Apple's question | Answer |
|---|---|
| Cartoon or fantasy violence | None |
| Realistic violence | None |
| Sexual content or nudity | None |
| Profanity or crude humor | None |
| Alcohol, tobacco, or drug use | None |
| Mature/suggestive themes | None |
| Simulated gambling | None |
| Horror/fear themes | None |
| Prolonged graphic violence | None |
| Sexual content or graphic violence | None |
| Medical/treatment information | None |
| Unrestricted web access | **No** |
| Gambling | None |
| Contests | No |
| Made for Kids | No |

> "Unrestricted web access" → **No** because the only outbound
> request is to a fixed first-party endpoint (`bulkpokescan.app/api/tally`).
> The app does not embed a `WKWebView` or load arbitrary URLs.

**Resulting rating:** 4+

---

## App Review Information

### Sign-in required

**No**

### Demo account

Not applicable.

### Notes for review (paste verbatim)

```
BulkPokeScan is a personal-productivity utility for Pokémon Trading Card Game collectors. It scans QR codes printed on physical TCG redemption cards (purchased at retail) and helps the user organize and export the codes for redemption in Pokémon's official apps.

Functional summary:
• Camera access is used solely for QR decoding (NSCameraUsageDescription is "BulkPokeScan uses the camera to scan QR codes on Pokémon TCG redemption cards.")
• Decoding runs entirely on-device via AVFoundation's AVCaptureMetadataOutput. No camera frames are saved, recorded, or transmitted.
• Scanned codes are stored only in the device's UserDefaults. Not synced to iCloud or any server.
• The app does not connect to or interact with any Pokémon-branded service.
• The app does not generate, validate, redeem, share, or trade codes.
• The single outbound request the app makes is POST https://bulkpokescan.app/api/tally with an empty body, which increments a worldwide counter shown on the About screen. No payload contains user data, IP-derived data, or the scanned code itself.
• No analytics SDKs, no crash reporters, no advertising IDs (IDFA), no third-party trackers.

Trademark posture:
"Pokémon" appears in the description and subtitle as a nominative reference identifying the card system this app helps users organize codes for. The app is unofficial and unaffiliated. The trademark attribution line ("Pokémon is a trademark of Nintendo, Creatures Inc., and GAME FREAK Inc. — this app is unofficial and unaffiliated.") appears in the description, in the in-app About screen, in the in-app Settings → Legal footer, and in the privacy policy at https://bulkpokescan.app/privacy.

Testing the app:
1. Launch the app.
2. Tap "Start Camera." Grant camera permission when prompted.
3. Hold any printed QR code 6–12 inches from the lens. (Pokémon TCG redemption cards work; any QR code will technically decode.)
4. The decoded code appears in the list with a number tag like "#001."
5. Switch to the "Code Blocks" tab to see codes auto-grouped in 10s.
6. Tap "Export" to save a TXT file via Share Sheet, or "Copy All" to copy.
7. Settings → Legal links open the Privacy Policy, Terms of Use, and Support pages on bulkpokescan.app.

Contact for review questions: support@nytemode.com
```

### Contact information

- **First Name:** Lobo
- **Last Name:** Rivera
- **Phone:** (your number)
- **Email:** support@nytemode.com (or lobo.rivera@gmail.com if you prefer)

---

## What's New (per-version)

### v1.0.0 (initial release)

```
Welcome to BulkPokeScan! Scan and organize Pokémon TCG redemption codes in bulk — 100% on-device, no subscriptions, no ads, no data collection.
```

(140 chars — concise per Apple's recommendation)

---

## Screenshot Specifications

**Required size:** 6.7" iPhone — **1290 × 2796 px**.

App Store Connect uses 6.7" screenshots for all smaller screen sizes
when no others are uploaded. This is sufficient for v1.0.

**Six-screenshot composition:**

1. **Hero**
   - Capture: Scanner view with the camera viewport visible (use the
     simulator with a printed QR taped over the lens area or a
     mocked frame)
   - Overlay text: "Scan a booster box in minutes" (top, white on
     gradient red→bg)
   - Overlay subtext: "Pokémon TCG redemption codes — bulk speed"
   - Wordmark: top-left
2. **All Codes list**
   - Capture: codes view with 12–20 captured codes visible, mix of
     camera (green dot) and manual (gray dot) sources
   - Overlay: "Pokédex-style numbering" + "#001 to whatever you need"
3. **Code Blocks**
   - Capture: Code Blocks tab with two visible blocks of 10
   - Overlay: "Auto-grouped into 10s — built for redemption batches"
4. **Export sheet**
   - Capture: Share Sheet with the four format options visible
   - Overlay: "TXT, Markdown, plain — your choice"
5. **Settings (privacy hero)**
   - Capture: Settings view with toggles + Legal section visible
   - Overlay: "100% on-device" + "No accounts. No analytics. No ads."
6. **About / global tally**
   - Capture: About view with the worldwide counter rendered
   - Overlay: "Join the global scan count"

**Production approach:**

- Capture raw screenshots from the simulator at 6.7" (the build
  command in `ios/README.md` uses simulator UDID `8E07025E-…` which
  is iPhone 16 Pro / iOS 18.2 — that's a 6.3" frame, not 6.7". You
  will need to boot an iPhone 16 Pro Max simulator instead.)
- Compose marketing overlays in Figma using:
  - Background gradient: `#0B0D14` (Palette.bg) → `#161823` (Palette.surface) at 30°
  - Red accent: `#E63946` (Palette.red)
  - Yellow accent: `#FFCB05` (Palette.yellow)
  - Title font: Space Grotesk Bold 60-72pt
  - Subtitle font: Inter Tight Medium 32-40pt
  - Mono accents (energy-pip strip): JetBrains Mono Bold 16pt, tracked +0.16em uppercase

> Recommendation: a single Figma file with 6 frames at 1290×2796,
> exported as PNG. ~30 minutes of design work for a $4.99 paid app's
> conversion lever.

---

## Review checklist before hitting Submit

- [ ] App name in App Store Connect matches the production bundle ID's binary
- [ ] Privacy Policy URL returns 200 (`curl -o /dev/null -w "%{http_code}\n" https://bulkpokescan.app/privacy`)
- [ ] Support URL returns 200
- [ ] Marketing URL returns 200
- [ ] Six 1290 × 2796 screenshots uploaded
- [ ] Promotional text under 170 chars
- [ ] Description under 4000 chars
- [ ] Keywords field exactly 100 chars or fewer
- [ ] Privacy nutrition label = "Data Not Collected"
- [ ] Age rating completed (4+)
- [ ] App Review notes pasted into the field above
- [ ] Pricing tier 5 selected
- [ ] "Manually release this version" selected (not "Automatically")
- [ ] Build uploaded via Transporter / Xcode and selected for the version
- [ ] Internal Testers added (yourself) and the build is verified working on a real device
- [ ] All Required entries on the version page are green-checked
