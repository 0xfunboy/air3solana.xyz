#!/usr/bin/env python3
"""
AIR3 (air3solana.xyz) static site generator.

Usage:  python3 build.py
Reads page body fragments from build/pages/*.html and emits the final
static site into ../site/ with shared header, footer and SEO tags.
No dependencies. The output is plain HTML you can also edit directly.
"""
import os, re, datetime

ROOT   = os.path.dirname(os.path.abspath(__file__))
PAGES  = os.path.join(ROOT, "pages")
OUT    = os.path.normpath(os.path.join(ROOT, "..", "site"))
DOMAIN = "https://air3solana.xyz"

# ---------------------------------------------------------------- links
L = {
    "dapp":        "https://airdapp.airewardrop.xyz",
    "airi":        "https://airi.airewardrop.xyz",
    "airtrack":    "https://airtrack.airewardrop.xyz",
    "corp":        "https://airewardrop.xyz",
    "contact":     "https://airewardrop.xyz/contact",
    "docs":        "https://airewardrop.gitbook.io/air3",
    "x":           "https://x.com/AIRewardrop",
    "tg_channel":  "https://t.me/AIRewardrop",
    "tg_comm":     "https://t.me/AIR3Community",
    "discord":     "https://discord.gg/S4f87VdsHt",
    "twitch":      "https://www.twitch.tv/airewardrop",
    "youtube":     "https://www.youtube.com/@AIRewardrop",
    "tiktok":      "https://www.tiktok.com/@airewardrop",
    "instagram":   "https://www.instagram.com/airewardrop/",
    "solscan_vault": "https://solscan.io/account/EhhE742NXcY36yPr8YJZ8zoj9nfe7MmBQ6K3gjna74EE?page_size=100#transfers",
    "solscan_token": "https://solscan.io/token/2jvsWRkT17ofmv9pkW7ofqAFWSCNyJYdykJ7kPKbmoon",
    "dexscreener":   "https://dexscreener.com/solana/2jvsWRkT17ofmv9pkW7ofqAFWSCNyJYdykJ7kPKbmoon",
    "pacifica":      "https://app.pacifica.fi/?referral=AIRewardrop",
    "terms":       "https://airewardrop.xyz/legal/terms-of-service",
    "privacy":     "https://airewardrop.xyz/legal/privacy-policy",
    "cookie":      "https://airewardrop.xyz/legal/cookie-notice",
    "manual_pdf":  "/assets/downloads/AIRTrading_User_Manual_v1.pdf",
    "ca":          "2jvsWRkT17ofmv9pkW7ofqAFWSCNyJYdykJ7kPKbmoon",
}

# ---------------------------------------------------------------- pages
# (fragment, out path, nav id, title, description)
PAGELIST = [
    ("home",       "index.html",            "home",
     "AIR3 | Execution-Native AI Trading Agent on Solana",
     "AIR3 is a Solana AI trading product by AIRewardrop: live market intelligence, AIRTrading vault execution, AIRTrack proof and AIR3 buyback/distribution flows in one system."),
    ("product",    "product/index.html",    "product",
     "Product Suite | AIR3 Modules & Ecosystem",
     "AIR3 is a product system, not one isolated app: AIR3 Agent, AIRTrading, AIRTrack, AIRi, AIRSocial, AIRTool and AIRSponsor connected across AIRdApp on Solana."),
    ("airtrading", "airtrading/index.html", "airtrading",
     "AIRTrading | AIR3 Vault Execution on Solana",
     "AIRTrading is the AIR3 vault module: weekly Solana trading seasons, Pacifica perp execution, USDC deposits, PnL settlement, AIR3 buyback and pro-rata distribution."),
    ("airtrack",   "airtrack/index.html",   "airtrack",
     "AIRTrack | Onchain Proof Layer for AIR3 Execution",
     "AIRTrack tracks every AIR3 trade state, realized PnL and full performance history so users verify results onchain instead of trusting claims."),
    ("airi",       "airi/index.html",       "airi",
     "AIRi | Voice & Avatar Interface for AIR3",
     "AIRi turns AIR3 into a wallet-authenticated live session: 3D VRM avatar, voice input/output, market context and execution-ready UX on browser, mobile and Seeker."),
    ("live",       "live/index.html",       "live",
     "Live Agent | AIR3 24/7 Market Intelligence Channels",
     "AIR3 posts market analysis, answers commands on X, Telegram and Discord, and streams 24/7 as a live agent, routing attention into the product loop."),
    ("manual",     "manual/index.html",     "manual",
     "AIRTrading User Manual | Deposits, Seasons, Exit, Claim & Buyback",
     "Full AIRTrading guide: connect a Solana wallet, deposit USDC, follow weekly seasons, book exit, claim capital and understand the AIR3 buyback distribution."),
    ("roadmap",    "roadmap/index.html",    "roadmap",
     "Roadmap | AIR3 From Completed Launch to Scale",
     "The AIR3 launch roadmap is complete. Current focus: mainnet beta seasons, Backtest Engine validation and execution alignment, then leverage scaling, Jupiter expansion and public tiers."),
    ("token",      "token/index.html",      "token",
     "$AIR3 Token | Utility, Buyback & Flywheel",
     "$AIR3 is the access and utility asset of the AIR3 ecosystem: AIRTrading buyback/distribution, AIRTool burn-to-access, AIRSponsor segments and holder thresholds."),
    ("partners",   "partners/index.html",   "partners",
     "Partners | White-Label Agents, Sponsorship & B2B",
     "Work with AIRewardrop: white-label AI agents, partner-branded AIRi avatars, sponsored AIR3 live segments and Telegram/Discord agent deployments."),
    ("proof",      "proof/index.html",      "proof",
     "Onchain Proof | Vault, Buyback & Season Reports",
     "AIR3 results link back to the chain: Solscan vault account, buyback transactions, pro-rata AIR3 distribution and AIRTrack trade history."),
    ("faq",        "faq/index.html",        "faq",
     "FAQ | AIR3 & AIRTrading Quick Answers",
     "Quick answers about AIR3, AIRTrading deposits and seasons, exits and claims, the AIR3 buyback, risk and where to verify everything onchain."),
    ("risk",       "legal/risk.html",       "",
     "Risk Disclosure | AIR3 & AIRTrading",
     "AIR3 and AIRTrading are experimental AI-assisted trading products in mainnet beta. Understand the risks before depositing."),
    ("404",        "404.html",              "",
     "404 Signal Lost | AIR3",
     "The page you requested does not exist. Return to the AIR3 product site."),
]

NAV = [
    ("product",    "/product/",    "Product"),
    ("airtrading", "/airtrading/", "AIRTrading"),
    ("airtrack",   "/airtrack/",   "AIRTrack"),
    ("airi",       "/airi/",       "AIRi"),
    ("live",       "/live/",       "Live"),
    ("roadmap",    "/roadmap/",    "Roadmap"),
    ("token",      "/token/",      "Token"),
    ("proof",      "/proof/",      "Proof"),
]

EXT = 'target="_blank" rel="noopener noreferrer"'

# ---------------------------------------------------------------- chrome
def head(title, desc, canon):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canon}">
  <meta name="robots" content="index,follow">
  <meta name="theme-color" content="#04060b">
  <meta property="og:site_name" content="AIR3">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canon}">
  <meta property="og:image" content="{DOMAIN}/assets/img/og-air3.png">
  <meta property="og:image:secure_url" content="{DOMAIN}/assets/img/og-air3.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="AIR3: Execution-Native AI Trading Agent on Solana, by AIRewardrop">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@AIRewardrop">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{DOMAIN}/assets/img/og-air3.png">
  <meta name="twitter:image:alt" content="AIR3: Execution-Native AI Trading Agent on Solana, by AIRewardrop">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
  <link rel="manifest" href="/manifest.json">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="/assets/css/styles.css">
</head>"""

def header(active):
    links = "".join(
        f'<a class="nav-link{" active" if nid == active else ""}" href="{href}">{label}</a>'
        for nid, href, label in NAV
    )
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="hud-frame" aria-hidden="true"><i class="c1"></i><i class="c2"></i><i class="c3"></i><i class="c4"></i></div>
<header class="site-header" data-header>
  <a class="brand" href="/" aria-label="AIR3 home">
    <img class="brand-emblem" src="/assets/logos/air3-emblem.png" alt="" width="38" height="38">
    <span class="brand-text"><b>AIR<em>3</em></b><small>by AIRewardrop</small></span>
  </a>
  <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" data-menu-toggle><span></span><span></span><span></span></button>
  <nav class="site-nav" aria-label="Primary">
    {links}
    <a class="nav-link extra" href="/manual/">Deposit Guide</a>
    <a class="nav-link extra" href="/partners/">Partners</a>
    <a class="nav-link extra" href="/faq/">FAQ</a>
    <div class="nav-cta">
      <a class="btn btn-ghost" href="{L['twitch']}" {EXT}>Watch Live</a>
      <a class="btn btn-primary" href="{L['dapp']}" {EXT}>Open AIRdApp</a>
    </div>
  </nav>
  <div class="header-actions">
    <a class="btn btn-ghost btn-sm" href="{L['twitch']}" {EXT}>Watch Live</a>
    <a class="btn btn-primary btn-sm" href="{L['dapp']}" {EXT}>Open AIRdApp</a>
  </div>
</header>"""

SOCIALS = [
    ("X",                  L["x"],        '<path d="M13.9 10.5 21.4 2h-1.8l-6.5 7.4L7.9 2H2l7.9 11.3L2 22.2h1.8l6.9-7.9 5.5 7.9H22l-8.1-11.7zM11.6 13.2l-.8-1.1L4.4 3.3h2.7l5.1 7.2.8 1.1 6.7 9.4H17l-5.4-7.8z" fill="currentColor" stroke="none"/>'),
    ("Telegram Channel",   L["tg_channel"], '<path d="m21.5 3.6-19 7.5c-.7.3-.7 1.2 0 1.5l4.7 1.7 1.8 5.6c.2.6 1 .8 1.5.3l2.6-2.5 4.9 3.6c.5.4 1.3.1 1.4-.5l3.1-16.1c.1-.8-.6-1.4-1.4-1.1zM8.5 13.9l9.5-6.7c.2-.2.5.1.3.3l-7.6 7.5-.3 3z" fill="currentColor" stroke="none"/>'),
    ("Telegram Community", L["tg_comm"],  '<path d="m21.5 3.6-19 7.5c-.7.3-.7 1.2 0 1.5l4.7 1.7 1.8 5.6c.2.6 1 .8 1.5.3l2.6-2.5 4.9 3.6c.5.4 1.3.1 1.4-.5l3.1-16.1c.1-.8-.6-1.4-1.4-1.1zM8.5 13.9l9.5-6.7c.2-.2.5.1.3.3l-7.6 7.5-.3 3z" fill="currentColor" stroke="none"/>'),
    ("Discord",            L["discord"],  '<path d="M19.3 5.3A16.9 16.9 0 0 0 15.1 4l-.5 1.1a15.6 15.6 0 0 0-5.2 0L8.9 4a16.9 16.9 0 0 0-4.2 1.3C2 9.4 1.3 13.4 1.6 17.3A17 17 0 0 0 6.8 20l1.1-1.8c-.6-.2-1.2-.5-1.7-.9l.4-.3a12.2 12.2 0 0 0 10.8 0l.4.3c-.5.4-1.1.7-1.7.9L17.2 20a17 17 0 0 0 5.2-2.7c.4-4.5-.7-8.4-3.1-12zM8.7 14.8c-1 0-1.8-.9-1.8-2s.8-2 1.8-2 1.9.9 1.8 2c0 1.1-.8 2-1.8 2zm6.6 0c-1 0-1.8-.9-1.8-2s.8-2 1.8-2 1.9.9 1.8 2c0 1.1-.8 2-1.8 2z" fill="currentColor" stroke="none"/>'),
    ("Twitch",             L["twitch"],   '<path d="M4.3 2 2.5 6.7v15h5.1V24h2.9l2.3-2.3h3.5l4.7-4.7V2zm15 14.1-2.7 2.7h-4.3L10 21.1v-2.3H6.4V4h12.9zM16.6 7.5v5.7h-1.9V7.5zm-5.1 0v5.7H9.6V7.5z" fill="currentColor" stroke="none"/>'),
    ("YouTube",            L["youtube"],  '<path d="M23 7.2a2.8 2.8 0 0 0-2-2C19.2 4.7 12 4.7 12 4.7s-7.2 0-9 .5a2.8 2.8 0 0 0-2 2A29.4 29.4 0 0 0 .5 12 29.4 29.4 0 0 0 1 16.8a2.8 2.8 0 0 0 2 2c1.8.5 9 .5 9 .5s7.2 0 9-.5a2.8 2.8 0 0 0 2-2 29.4 29.4 0 0 0 .5-4.8 29.4 29.4 0 0 0-.5-4.8zM9.7 15.4V8.6l6 3.4z" fill="currentColor" stroke="none"/>'),
    ("TikTok",             L["tiktok"],   '<path d="M16.8 2h-3.3v13.6a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.4a6.3 6.3 0 0 0-.9-.1 6.2 6.2 0 1 0 6.2 6.3V8.7a7.7 7.7 0 0 0 4.5 1.4V6.8A4.6 4.6 0 0 1 16.8 2z" fill="currentColor" stroke="none"/>'),
    ("Instagram",          L["instagram"],'<rect x="2.5" y="2.5" width="19" height="19" rx="5.2"/><circle cx="12" cy="12" r="4.4"/><circle cx="17.6" cy="6.4" r="1.2" fill="currentColor" stroke="none"/>'),
]

def footer():
    socials = "".join(
        f'<a href="{href}" {EXT} aria-label="{name}" title="{name}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">{path}</svg></a>'
        for name, href, path in SOCIALS
    )
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="footer-brand" href="/"><img src="/assets/logos/air3-emblem.png" alt="AIR3 emblem" width="34" height="34"><b>AIR<em>3</em></b></a>
        <p class="footer-desc">AIR3 is a Solana AI trading product by AIRewardrop: live agent, vault execution, onchain tracking and product-native token utility.</p>
        <div class="social-row">{socials}</div>
        <p class="risk-note">AIR3 and AIRTrading are experimental AI-assisted trading products. Nothing on this site is financial advice. Crypto and perp trading involve substantial risk, including loss of capital. Past performance and alpha season data do not guarantee future results.</p>
      </div>
      <div class="footer-col">
        <h4>AIR3</h4>
        <a href="/product/">Product Suite</a>
        <a href="/airtrading/">AIRTrading</a>
        <a href="/airtrack/">AIRTrack</a>
        <a href="/airi/">AIRi</a>
        <a href="/live/">Live Agent</a>
        <a href="/token/">$AIR3 Token</a>
        <a href="/roadmap/">Roadmap</a>
        <a href="/manual/">Deposit Guide</a>
      </div>
      <div class="footer-col">
        <h4>Ecosystem</h4>
        <a href="{L['dapp']}" {EXT}>AIRdApp ↗</a>
        <a href="{L['airi']}" {EXT}>AIRi Live ↗</a>
        <a href="{L['airtrack']}" {EXT}>AIRTrack App ↗</a>
        <a href="{L['corp']}" {EXT}>AIRewardrop ↗</a>
        <a href="{L['docs']}" {EXT}>Docs ↗</a>
        <a href="/partners/">Partners</a>
        <a href="/proof/">Onchain Proof</a>
        <a href="/faq/">FAQ</a>
      </div>
      <div class="footer-col">
        <h4>Community</h4>
        <a href="{L['x']}" {EXT}>X / Twitter</a>
        <a href="{L['tg_channel']}" {EXT}>Telegram Channel</a>
        <a href="{L['tg_comm']}" {EXT}>Telegram Community</a>
        <a href="{L['discord']}" {EXT}>Discord</a>
        <a href="{L['twitch']}" {EXT}>Twitch</a>
        <a href="{L['youtube']}" {EXT}>YouTube</a>
        <a href="{L['tiktok']}" {EXT}>TikTok</a>
        <a href="{L['instagram']}" {EXT}>Instagram</a>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <a href="{L['terms']}" {EXT}>Terms of Service</a>
        <a href="{L['privacy']}" {EXT}>Privacy Policy</a>
        <a href="{L['cookie']}" {EXT}>Cookie Notice</a>
        <a href="/legal/risk.html">Risk Disclosure</a>
        <a href="{L['manual_pdf']}">Manual PDF</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 AIRewardrop. AIR3 is a Solana AI trading product by AIRewardrop.</span>
      <span>$AIR3 CA: <code>{L['ca']}</code></span>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/livedata.js" defer></script>
</body>
</html>"""

# ---------------------------------------------------------------- build
def build():
    written = []
    for frag, out, nav, title, desc in PAGELIST:
        src = os.path.join(PAGES, frag + ".html")
        with open(src, encoding="utf-8") as f:
            body = f.read()
        # allow {{key}} link substitution inside fragments
        body = re.sub(r"\{\{(\w+)\}\}", lambda m: L[m.group(1)], body)
        canon = DOMAIN + "/" + out.replace("index.html", "")
        if out == "404.html":
            canon = DOMAIN + "/404.html"
        extra = ""
        if frag == "home":
            extra = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "AIR3",
    "url": "https://air3solana.xyz",
    "logo": "https://air3solana.xyz/assets/icons/icon-512.png",
    "description": "Execution-native AI trading agent on Solana by AIRewardrop.",
    "parentOrganization": { "@type": "Organization", "name": "AIRewardrop", "url": "https://airewardrop.xyz" },
    "sameAs": [
      "https://x.com/AIRewardrop",
      "https://t.me/AIRewardrop",
      "https://t.me/AIR3Community",
      "https://www.twitch.tv/airewardrop",
      "https://www.youtube.com/@AIRewardrop",
      "https://www.tiktok.com/@airewardrop",
      "https://www.instagram.com/airewardrop/"
    ]
  }
  </script>"""
        if frag == "faq":
            extra = """
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      { "@type": "Question", "name": "What is AIR3?",
        "acceptedAnswer": { "@type": "Answer", "text": "AIR3 is an execution-native AI trading agent on Solana built by AIRewardrop. It combines live market intelligence, social distribution, AIRTrading vault execution, AIRTrack proof, AIRi voice/avatar interaction and AIR3 buyback/distribution flows in one product system." } },
      { "@type": "Question", "name": "What is AIRTrading?",
        "acceptedAnswer": { "@type": "Answer", "text": "The vault-based autotrading module: users deposit USDC into a shared on-chain vault, the AIR3 agent executes approved perp trades on Pacifica, and results settle weekly at the end of each season." } },
      { "@type": "Question", "name": "What is AIRTrack?",
        "acceptedAnswer": { "@type": "Answer", "text": "The proof layer: it records trade states (pending, open, closed, discarded), realized PnL and full performance history so users can verify what happened instead of trusting claims." } },
      { "@type": "Question", "name": "What is AIRi?",
        "acceptedAnswer": { "@type": "Answer", "text": "The embodied interface layer: a wallet-authenticated voice, chat and 3D avatar session with market context and execution-ready UX, in browser and mobile." } },
      { "@type": "Question", "name": "Can I lose money with AIRTrading?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes. The agent trades perps and seasons can close in loss. Losses reduce the season index and therefore your capital. Only deposit what you can afford to risk." } },
      { "@type": "Question", "name": "How does the AIR3 buyback work?",
        "acceptedAnswer": { "@type": "Answer", "text": "At settlement, 1% of positive weekly PnL goes to treasury (minimum $0.10); the remainder buys AIR3 on the market if it reaches the $5 minimum swap threshold. Bought AIR3 splits 50% to users pro rata and 50% to treasury." } },
      { "@type": "Question", "name": "How will leverage scale?",
        "acceptedAnswer": { "@type": "Answer", "text": "In controlled steps toward 10x, on a strategy validated by the AIR3 Backtest Engine against real execution data. As live and simulated results converge, size steps up." } },
      { "@type": "Question", "name": "Where can I verify AIR3 results onchain?",
        "acceptedAnswer": { "@type": "Answer", "text": "The vault account is public on Solscan, every trade lives in AIRTrack, and weekly season reports link back to onchain transfers wherever possible." } }
    ]
  }
  </script>"""
        html = (
            head(title, desc, canon).replace("</head>", extra + "\n</head>")
            + "\n<body>\n" + header(nav)
            + '\n<main id="main">\n' + body + "\n</main>\n"
            + footer()
        )
        dest = os.path.join(OUT, out)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(html)
        written.append(out)

    # legacy redirect: /airifica/ (hackathon-era name) -> /airi/
    rdir = os.path.join(OUT, "airifica")
    os.makedirs(rdir, exist_ok=True)
    with open(os.path.join(rdir, "index.html"), "w", encoding="utf-8") as f:
        f.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                '<title>AIRi | AIR3</title>'
                '<link rel="canonical" href="https://air3solana.xyz/airi/">'
                '<meta http-equiv="refresh" content="0; url=/airi/">'
                '</head><body><p>AIRifica is now <a href="/airi/">AIRi</a>.</p></body></html>\n')

    # sitemap
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{DOMAIN}/{o.replace('index.html','')}</loc><lastmod>{today}</lastmod></url>"
        for _, o, *_ in [(p[0], p[1]) for p in PAGELIST]
        if o not in ("404.html",)
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')

    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")

    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        f.write("""{
  "name": "AIR3 | AI Trading Agent on Solana",
  "short_name": "AIR3",
  "description": "Execution-native AI trading agent on Solana by AIRewardrop.",
  "start_url": "/",
  "display": "browser",
  "background_color": "#04060b",
  "theme_color": "#04060b",
  "icons": [
    { "src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
""")
    print(f"Built {len(written)} pages + sitemap.xml + robots.txt + manifest.json → {OUT}")
    for w in written:
        print("  ·", w)

if __name__ == "__main__":
    build()
