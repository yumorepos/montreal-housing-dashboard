# 🚀 Streamlit Cloud Deployment Guide

**Target:** Deploy `montreal-housing-dashboard` to Streamlit Cloud (free tier)  
**Time:** 5 minutes  
**Output:** Live URL → add to portfolio site + GitHub profile

---

## Prerequisites ✅

- [x] GitHub repo: `https://github.com/yumorepos/montreal-housing-dashboard`
- [x] `requirements.txt` present
- [x] `app.py` is the entry point
- [x] `.streamlit/config.toml` included (dark theme)

---

## Step-by-Step Deployment

### 1. Sign in to Streamlit Cloud

Go to: **https://share.streamlit.io**

- Click **"Sign in with GitHub"**
- Authorize Streamlit Cloud to access your GitHub repos

### 2. Create New App

Click **"New app"** (top right)

Fill in the form:

| Field | Value |
|---|---|
| **Repository** | `yumorepos/montreal-housing-dashboard` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL** | `montreal-housing-dashboard` (or choose custom subdomain) |

### 3. Deploy

Click **"Deploy!"**

Streamlit Cloud will:
1. Clone the repo
2. Install dependencies from `requirements.txt`
3. Launch the app
4. Generate a public URL: `https://montreal-housing-dashboard.streamlit.app`

**Expected build time:** 1–2 minutes

### 4. Verify

Once deployed:
- Visit the app URL
- Confirm all charts render
- Test borough/year filters
- Check mobile responsiveness

---

## After Deployment

### A. Update GitHub Profile README

Add the live link to your profile:

```markdown
### 🏙️ [Montreal Housing Dashboard](https://montreal-housing-dashboard.streamlit.app)
Interactive rental market analysis across Montreal boroughs (Streamlit + Plotly)
```

File: `https://github.com/yumorepos/yumorepos/blob/main/README.md`

### B. Update Portfolio Site

Add to your projects section:

```markdown
**Montreal Housing Dashboard** — [Live Demo](https://montreal-housing-dashboard.streamlit.app) · [GitHub](https://github.com/yumorepos/montreal-housing-dashboard)
```

File: `~/portfolio-site/index.html` (or equivalent)

### C. Add Badge to Repo README

Insert at top of `README.md`:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://montreal-housing-dashboard.streamlit.app)
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Build fails on `requirements.txt` | Pin versions: `streamlit==1.32.0`, etc. |
| App crashes on startup | Check `app.py` for hardcoded paths or missing imports |
| Theme doesn't load | Verify `.streamlit/config.toml` is committed |
| Slow load times | Add Streamlit caching (`@st.cache_data`) to data generation |

---

## Next Steps

Once live:
1. Share on LinkedIn: "Just deployed an interactive housing market dashboard..."
2. Add to resume under **Projects**
3. Use in cover letters: "Recent work includes a live Streamlit dashboard analyzing Montreal rental trends..."

---

**Live URL (after deployment):** `https://montreal-housing-dashboard.streamlit.app`

**Deployment status:** ⏳ Pending (manual browser login required)
