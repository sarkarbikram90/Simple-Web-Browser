# NEXUS Browser 🌌

A sci-fi browser built with Streamlit — jaw-dropping animated UI that changes theme on every page load.

## ✨ Themes (Random on Each Load)
- 🌊 **Deep Ocean** — fish, caustics, bubbles
- 🔴 **Mars Surface** — dust storms, red rocks
- 🚀 **SpaceX Launch** — rockets trail into starfield
- 🌆 **City at Night** — cars, people walking, neon windows
- 🏜️ **Sahara Desert** — dunes, heat shimmer, sun
- 🌌 **Aurora Borealis** — curtains of light, pine trees
- 🌿 **Rainforest** — light rays, falling leaves, canopy
- 🐕 **Golden Hour Park** — animated dogs running

## 🚀 Deploy to Streamlit Cloud (Free)

1. **Push to GitHub**:
```bash
git init
git add app.py requirements.txt .streamlit/config.toml
git commit -m "NEXUS Browser"
git remote add origin https://github.com/YOUR_USERNAME/nexus-browser
git push -u origin main
```

2. **Deploy on [share.streamlit.io](https://share.streamlit.io)**:
   - Connect GitHub repo
   - Set main file: `app.py`
   - Click Deploy

## 📁 File Structure
```
nexus-browser/
├── app.py                    ← rename browser_app.py to app.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## 🔧 Features
- **8 animated canvas backgrounds** — pure JS canvas, no libraries
- **Multi-tab** browsing (in-memory)
- **History & Bookmarks** (session-only)
- **Multi-engine search**: Google, DuckDuckGo, YouTube, Wikipedia, GitHub
- **Everything erased on close** — zero persistence
- **Sci-fi HUD** — Orbitron font, glowing accents, scanlines

## ⚠️ Notes
- Some sites block iframe embedding (X-Frame-Options). This is a limitation of web iframes, not the browser.
- All data is in Streamlit session state — restarting the server wipes everything.