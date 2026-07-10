# AIR3solana.xyz — Product Site

Static product website for **AIR3**, the execution-native AI trading agent on Solana by **AIRewardrop**.
Rebuilt July 2026 with the mission-control design language of the AIRTrading season reports
(red HUD frame, blue glowing panels, mono data readouts, starfield backdrop) and live vault
telemetry pulled from the AIRdApp backend.

## Layout

```
air3solana.xyz/
├── site/                  ← THE DEPLOYABLE SITE (upload this folder as web root)
│   ├── index.html            Home: Twitch live frame in the hero + live vault telemetry
│   ├── product/              Product suite (modules + ecosystem map)
│   ├── airtrading/           Vault protocol, live telemetry, Backtest Engine, rules, risk
│   ├── airtrack/             Proof layer with live performance strip
│   ├── airi/                 AIRi voice/avatar interface (YouTube demo autoplay loop)
│   ├── airifica/             Legacy redirect → /airi/ (hackathon-era name)
│   ├── live/                 24/7 agent channels + embedded Twitch stream
│   ├── manual/               AIRTrading User Manual v1 (web version, live values, video step)
│   ├── roadmap/              Completed milestones + scaling doctrine (toward 10x)
│   ├── token/                $AIR3 utility, flywheel, CA
│   ├── partners/             B2B, white-label, deployed agents (AIR3, PolarAI on Base, LAIR)
│   ├── proof/                Solscan vault, buyback, season reports
│   ├── faq/                  Accordion FAQ
│   ├── legal/risk.html       Product risk disclosure (ToS/Privacy/Cookie link to airewardrop.xyz)
│   ├── 404.html              "Signal lost"
│   ├── sitemap.xml · robots.txt · manifest.json · favicon.png
│   └── assets/
│       ├── css/styles.css    Design system (single file, no framework)
│       ├── js/main.js        Menu, copy-CA, scroll reveal, TOC scrollspy (no deps)
│       ├── js/livedata.js    Live telemetry from the AIRdApp API (see below)
│       ├── logos/            air3-emblem.png / air3-lockup.png (transparent, from brand art)
│       ├── icons/            favicon set + apple-touch
│       ├── img/og-air3.png   OG/social card 1200×630
│       ├── video/manual-connect-720p.mp4   Manual step-1 walkthrough loop
│       └── downloads/AIRTrading_User_Manual_v1.pdf
│
├── build/                 ← OPTIONAL generator (edit shared header/footer once)
│   ├── build.py              python3 build/build.py → regenerates site/*.html + sitemap
│   └── pages/*.html          Per-page <main> content fragments ({{key}} = link registry)
│
└── AIR3solana_site_rebuild_plan.md   Original planning doc
```

## Live data (livedata.js)

Vault and tracking numbers are never hardcoded. `assets/js/livedata.js` reads the same
backend the dApp uses (per `AIRTRACK_AIRTRADING_DATA_SOURCES.md`):

- `GET https://airdapp.airewardrop.xyz/api/auto-trading/read-model` → vault capital, PnL,
  season stats, buyback routed, cutoff timestamp (one coherent snapshot)
- `GET https://airdapp.airewardrop.xyz/api/reports` → AIRTrack all-time totals and realized PnL

Behaviour: refresh on page visit with a 5-minute `localStorage` cache; on API failure the
last valid snapshot keeps being served (never zeros); the "Season Ends In" countdown ticks
client-side from `cutoffAt`. Elements are bound via `data-live="key"` attributes on the
Home, AIRTrading, AIRTrack and Manual pages.

## Embeds

- **Twitch** (home hero + /live/): `player.twitch.tv` with `parent=air3solana.xyz`,
  `www.air3solana.xyz`, `localhost`, `127.0.0.1`. If the production domain ever changes,
  update the `parent` params in `build/pages/home.html` and `live.html`.
- **YouTube** (AIRi hero): autoplay, muted, looped via `playlist=` param. Do not add
  `referrerpolicy="no-referrer"` to YouTube iframes: it breaks embedding (error 153).

## Two ways to edit

1. **Direct**: every file in `site/` is plain HTML/CSS/JS; edit and deploy.
2. **Generated**: edit `build/pages/*.html` (content) or `build/build.py`
   (header, footer, nav, link registry, SEO meta), then run:

   ```bash
   python3 build/build.py
   ```

   All links (dApp, AIRi, socials, Solscan, CA, legal) live in the `L = {...}`
   dict at the top of `build.py`: change once, propagates everywhere.

## Deploy

Any static host (Netlify, Cloudflare Pages, GitHub Pages, nginx). Publish the
`site/` folder as the web root. `404.html` is picked up automatically by most hosts.

Local preview:
```bash
cd site && python3 -m http.server 8080
```

## Content rules baked in

- No em dashes anywhere. House style: commas, colons, parentheses.
- AIRifica is the retired hackathon-era name: the module is **AIRi** everywhere,
  with `/airifica/` redirecting to `/airi/` and two historical mentions kept on purpose.
- dApp values are authoritative for limits/thresholds, repeated on every surface.
- No yield promises; leverage is framed as controlled scaling toward 10x on a
  strategy validated by the Backtest Engine.
- No wallet connection on the product site; wallet actions live in AIRdApp/AIRi.
- All external links use `rel="noopener noreferrer"`.
- Terms/Privacy/Cookie point to airewardrop.xyz/legal/*; Risk Disclosure is local.
