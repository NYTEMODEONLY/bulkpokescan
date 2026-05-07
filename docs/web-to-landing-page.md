# Future Plan: Convert Web App → iOS Landing Page

**Status:** parked. App is the focus right now. Revisit once iOS is on the App Store.

## Goal

Convert `bulkpokescan.app` from a full-featured web scanner into a marketing
landing page for the iOS app. The Vercel project keeps running, but the homepage
becomes "Download on the App Store" + FAQ + privacy policy + screenshots.

## Why this shape

- The Vercel project hosts **two things**: the web UI (`/`) AND the tally API
  (`/api/tally`). They're siblings in one deployment. Killing the UI does NOT
  require killing the API.
- The iOS app has `https://bulkpokescan.app/api/tally` baked into
  `ios/BulkPokeScan/Models/AppConfig.swift:21`. Every shipped App Store build
  will hit that URL forever — so the endpoint **must stay alive at that exact
  path** as long as any users have older app versions installed.
- Hosting FAQs / privacy / changelog on the web means content updates don't
  require an App Store submission + review cycle.

## ⚠️ Don't break this

- **Do NOT change the path** `/api/tally` on the Vercel project. It's the
  single source of truth for the global counter.
- **Do NOT change the domain** `bulkpokescan.app` unless you also ship
  an iOS update with the new URL AND are willing to accept that users on old
  versions will see a stale counter forever.
  - If you ever DO want to migrate the API to your own domain (e.g.
    `api.bulkpokescan.app`), do it BEFORE App Store launch, or accept fragmentation.
- **Do NOT delete the Vercel project** even if the UI goes away — the API
  function rides along with it.

## What to do when you flip the switch

1. **Strip the web UI**, replace with a simple landing page:
   - Hero: app icon, name, tagline, screenshots
   - "Download on the App Store" button (Apple's official badge SVG)
   - FAQ section
   - Privacy policy (required for App Store submission anyway)
   - Support contact (email or form)
   - Live global tally (reuse the same `/api/tally` GET — already public)
2. **Keep `/api/tally` route untouched.** Verify after deploy:
   ```
   curl https://bulkpokescan.app/api/tally
   ```
   should still return `{ "total": <n> }`.
3. **Add iOS smart-app-banner** to landing page `<head>`:
   ```html
   <meta name="apple-itunes-app" content="app-id=APP_STORE_ID_HERE">
   ```
   Safari on iPhone shows an auto-banner with "Open / View".
4. **Wire up Universal Links** so links to the landing page open the installed
   app directly:
   - Add `apple-app-site-association` JSON to the Vercel project at:
     `https://bulkpokescan.app/.well-known/apple-app-site-association`
     (must be served as `application/json`, no `.json` extension)
   - Add `Associated Domains` capability in `ios/project.yml` →
     `applinks:bulkpokescan.app`
   - Re-run `xcodegen generate`, ship update.
5. **Privacy policy URL** — App Store Connect will ask for one. Use the
   landing page URL, not a bundled in-app page (so it can be updated without
   a build).

## Optional but worth considering

- **Custom domain** for the landing page (e.g., `bulkpokescan.app`) — better SEO,
  cleaner App Store listing, future-proof if you ever migrate off Vercel.
  Migrate the API to `bulkpokescan.app/api/tally` at the same time and ship one
  iOS update to point at the new URL. Do this BEFORE App Store launch.
- **Remote config indirection** — instead of baking `tallyURL` into the iOS
  build, fetch a small config JSON on launch:
  ```
  https://bulkpokescan.app/.well-known/app-config.json
  ```
  → returns `{ "tallyURL": "..." }`. Lets you migrate the tally backend any
  time without an app update. One-time cost: an extra cold-start request.
- **Analytics on the landing page** — Plausible or Cloudflare Web Analytics
  (privacy-friendly, no cookie banner needed).

## Pointers in the code

- iOS tally URL: `ios/BulkPokeScan/Models/AppConfig.swift:21`
- iOS tally client: `ios/BulkPokeScan/Managers/TallyClient.swift` (60s poll +
  POST on capture)
- Desktop tally wiring: `src/main_window.py` (`_fetch_tally` / `_post_tally`)
- Web tally route: lives in the bulkpokescan Vercel project (separate repo: `bulkpokescan-web`)
