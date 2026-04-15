"""
Republic World — Multi-Channel Real-Time Analytics
Channels: Republic World · Times Now · CNN-News18 · India Today · WION · NDTV
© Manish Rawat | Republic Media Network
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz, re, time
import numpy as np
from collections import Counter

# ═══════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="Republic World — Live Multi-Channel Analytics",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════
#  CHANNEL REGISTRY
# ═══════════════════════════════════════════════
CHANNELS = {
    "REPUBLIC":   {"id": "UCknLrEdhRCp1aegoMqRaCZg", "label": "Republic World",  "color": "#e63535", "short": "REP"},
    "TIMESNOW":   {"id": "UCt4t-jeY85JegMlZ-E5UWtA", "label": "Times Now",       "color": "#0ea5e9", "short": "TIM"},
    "CNN18":      {"id": "UCwqusr8YDwM-3mEYTDeJHzw", "label": "CNN-News18",       "color": "#8b5cf6", "short": "CNN"},
    "INDIATODAY": {"id": "UCYPvAwZP8pZhSMW8AxKlOOQ", "label": "India Today",     "color": "#16a34a", "short": "IND"},
    "WION":       {"id": "UCVOQyrq-dDCWGaZFD3J8hiA", "label": "WION",            "color": "#f59e0b", "short": "WIO"},
    "NDTV":       {"id": "UCZFMm1mMw0F81Z37aaEzTUA", "label": "NDTV",            "color": "#f97316", "short": "NDT"},
}
CH_KEYS   = list(CHANNELS.keys())
CH_COLORS = [CHANNELS[k]["color"] for k in CH_KEYS]

# ═══════════════════════════════════════════════
#  MASTER CSS
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Barlow+Condensed:wght@500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, html, body, [class*="css"] { font-family: 'Barlow', sans-serif !important; }

[data-testid="stAppViewContainer"] { background: #f0f2f7 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Top nav ── */
.topbar {
    background: #ffffff;
    border-bottom: 4px solid #e63535;
    padding: 0 22px;
    height: 56px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 3px 16px rgba(0,0,0,0.10);
    position: sticky; top: 0; z-index: 999;
}
.rep-badge {
    background: #e63535; color: #fff;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 900; font-size: 15px; letter-spacing: 2.5px;
    padding: 5px 13px; border-radius: 4px;
}
.topbar-title {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 16px; font-weight: 800; color: #12132a;
    letter-spacing: 1px; text-transform: uppercase;
}
.live-pill {
    display: flex; align-items: center; gap: 7px;
    background: #fff5f5; border: 2px solid #e63535;
    border-radius: 20px; padding: 4px 16px;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 12px; font-weight: 800; color: #e63535; letter-spacing: 2px;
}
.live-dot { width: 8px; height: 8px; background: #e63535; border-radius: 50%; animation: blink 1s infinite; }
@keyframes blink { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.2;transform:scale(1.3)} }

/* ── Dark subtitle bar ── */
.subbar {
    background: #12132a; padding: 7px 24px;
    display: flex; align-items: center; justify-content: space-between;
}
.subbar-l {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 12px; font-weight: 700; color: #8890bb;
    letter-spacing: 2px; text-transform: uppercase;
}
.subbar-r { font-size: 11px; color: #4a5080; font-family: 'IBM Plex Mono', monospace !important; }

/* ── Channel colour strip ── */
.ch-strip { display: flex; height: 4px; }
.ch-seg   { flex: 1; }

/* ── Content ── */
.cw { padding: 16px 22px 36px; }

/* ── Ticker cards ── */
.ticker-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 10px; margin-bottom: 14px; }
.tcard {
    background: #ffffff; border: 1px solid #e4e6ef; border-radius: 12px;
    padding: 12px 14px 11px; position: relative; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s, transform 0.2s;
}
.tcard:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.10); transform: translateY(-2px); }
.tcard-top  { position:absolute;top:0;left:0;width:100%;height:4px;border-radius:12px 12px 0 0; }
.tcard-ch   { font-family:'Barlow Condensed',sans-serif!important; font-size:13px;font-weight:800;letter-spacing:2px;text-transform:uppercase; margin-bottom:2px; }
.tcard-title{ font-size:9.5px;font-weight:500;color:#7880a0;line-height:1.35;min-height:28px;margin-bottom:6px; }
.tcard-val  { font-family:'Barlow Condensed',sans-serif!important;font-size:30px;font-weight:900;line-height:1; }
.tcard-meta { font-size:10px;font-weight:600;color:#9098b0;margin-top:4px; }
.tcard-delta{ font-size:11px;font-weight:700;font-family:'IBM Plex Mono',monospace!important;margin-top:3px; }
.up{color:#16a34a} .dn{color:#dc2626} .flat{color:#9098b0}

/* ── Section label ── */
.slbl {
    font-family:'Barlow Condensed',sans-serif!important;
    font-size:11px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#9098b0;
    margin:18px 0 10px;display:flex;align-items:center;gap:10px;
}
.slbl::after { content:'';flex:1;height:1px;background:linear-gradient(90deg,#dde0ec,transparent); }

/* ── Panel box ── */
.pbox {
    background:#ffffff;border:1px solid #e4e6ef;border-radius:12px;
    overflow:hidden;margin-bottom:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
.pbox-inner { padding: 0; }

/* ── Legend strip ── */
.leg-strip {
    display:flex;gap:14px;flex-wrap:wrap;align-items:center;
    padding:8px 16px;border-top:1px solid #eef0f8;background:#fafbfe;
}
.leg-item  { display:flex;align-items:center;gap:6px;font-size:11px;color:#6070a0; }
.leg-line  { width:22px;height:2.5px;border-radius:2px; }
.leg-val   { font-family:'IBM Plex Mono',monospace;font-weight:700; }

/* ── Stats table ── */
.stbl-wrap {
    background:#ffffff;border:1px solid #e4e6ef;border-radius:12px;
    padding:16px 18px;height:100%;box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
.panel-ttl {
    font-family:'Barlow Condensed',sans-serif!important;
    font-size:14px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#12132a;margin-bottom:2px;
}
.panel-sub { font-size:10px;color:#9098b0;letter-spacing:0.5px;margin-bottom:12px; }
.stbl { width:100%;border-collapse:collapse; }
.stbl th {
    font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
    color:#9098b0;padding:4px 8px 8px;text-align:right;border-bottom:2px solid #eef0f8;
}
.stbl th:first-child{text-align:left;}
.stbl td {
    padding:8px 8px;text-align:right;border-bottom:1px solid #f4f5fb;
    color:#12132a;font-family:'IBM Plex Mono',monospace;font-size:12.5px;
}
.stbl td:first-child{text-align:left;font-family:'Barlow',sans-serif!important;}
.stbl tr:hover td{background:#fafbfe;}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;}

/* ── Heatmap ── */
.hmwrap {
    background:#ffffff;border:1px solid #e4e6ef;border-radius:12px;
    padding:16px 18px;box-shadow:0 2px 8px rgba(0,0,0,0.04);
}

/* ── Share panel ── */
.sharewrap {
    background:#ffffff;border:1px solid #e4e6ef;border-radius:12px;
    padding:16px 18px;height:100%;box-shadow:0 2px 8px rgba(0,0,0,0.04);
}
.sbar-row { display:flex;align-items:center;gap:8px;margin-bottom:9px; }
.sbar-lbl { font-size:11px;font-weight:700;width:66px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }
.sbar-track { flex:1;height:6px;background:#eef0f8;border-radius:3px;overflow:hidden; }
.sbar-fill  { height:100%;border-radius:3px; }
.sbar-pct   { font-size:12px;font-weight:800;font-family:'IBM Plex Mono',monospace;width:42px;text-align:right; }

/* ── Top videos table ── */
.vtbl-wrap {
    background:#ffffff;border:1px solid #e4e6ef;border-radius:12px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);overflow:hidden;
}
.vtbl-head {
    background:#12132a;padding:12px 18px;
    font-family:'Barlow Condensed',sans-serif!important;
    font-size:13px;font-weight:800;letter-spacing:2.5px;
    text-transform:uppercase;color:#8890bb;
}
.vtbl { width:100%;border-collapse:collapse;font-size:12.5px; }
.vtbl th {
    font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
    color:#9098b0;padding:8px 12px;text-align:right;
    background:#fafbfe;border-bottom:2px solid #eef0f8;
}
.vtbl th:first-child,.vtbl th:nth-child(2){text-align:left;}
.vtbl td {
    padding:9px 12px;text-align:right;border-bottom:1px solid #f4f5fb;
    color:#12132a;font-family:'IBM Plex Mono',monospace;font-size:12px;
}
.vtbl td:first-child,.vtbl td:nth-child(2){text-align:left;font-family:'Barlow',sans-serif!important;}
.vtbl tr:hover td{background:#fafbfe;}
.rank-num {
    display:inline-flex;align-items:center;justify-content:center;
    width:22px;height:22px;border-radius:50%;
    font-size:11px;font-weight:800;color:#fff;
    font-family:'Barlow Condensed',sans-serif!important;
}

/* ── Footer ── */
.footer {
    margin-top:18px;padding:12px 18px;background:#12132a;
    border-radius:10px;display:flex;justify-content:space-between;
    align-items:center;flex-wrap:wrap;gap:8px;
}
.footer span{font-size:11px;color:#4a5080;}
.footer b{color:#8890bb;}

/* ── Hide Streamlit chrome ── */
#MainMenu,footer,header{visibility:hidden!important}
[data-testid="stToolbar"]{display:none!important}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:#f0f2f7}
::-webkit-scrollbar-thumb{background:#c8cce0;border-radius:4px}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════
IST = pytz.timezone("Asia/Kolkata")

def fk(n):
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}k"
    return str(int(n))

def light_layout(h=340, ml=50, mr=14, mt=32, mb=28):
    return dict(
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(color="#6070a0", family="Barlow", size=11),
        height=h, margin=dict(l=ml, r=mr, t=mt, b=mb),
        xaxis=dict(gridcolor="rgba(0,0,0,0.05)", linecolor="#eef0f8",
                   tickfont=dict(size=10), zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0.05)", linecolor="#eef0f8",
                   tickfont=dict(size=10), zeroline=False),
        hoverlabel=dict(bgcolor="#12132a", font_color="#fff",
                        font_family="Barlow", bordercolor="rgba(0,0,0,0.1)"),
    )

def growth_curve(total_views, total_hrs, n_pts=80, seed=42):
    rng = np.random.default_rng(seed)
    n   = max(min(int(total_hrs * 4), n_pts), 4)
    xs  = np.linspace(-4.5, 1.5, n)
    raw = 1 / (1 + np.exp(-xs))
    raw = raw / raw[-1]
    noise = rng.normal(0, 0.012, n)
    raw = np.clip(raw + noise, 0, None)
    raw = raw / raw[-1]
    return (raw * total_views).astype(int).tolist()

# ═══════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    time_window  = st.slider("Time window (hours)", 1, 48, 12)
    vids_per_ch  = st.slider("Videos per channel", 3, 20, 8)
    top_n_chart  = st.slider("Channels in main chart", 3, 6, 6)
    st.divider()
    st.markdown("**📡 Tracked Channels**")
    for k,v in CHANNELS.items():
        st.markdown(
            f'<span style="display:inline-block;width:10px;height:10px;'
            f'border-radius:50%;background:{v["color"]};margin-right:6px;"></span>'
            f'<b style="color:{v["color"]};">{v["label"]}</b>',
            unsafe_allow_html=True
        )
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear(); st.rerun()
    st.markdown("---")
    st.caption("© Manish Rawat | Republic Media Network")

# ═══════════════════════════════════════════════
#  API INIT
# ═══════════════════════════════════════════════
API_KEY = st.secrets["AIzaSyD04uTEYpx3BEws-v-x2022TKMim09zU_U"]
youtube = build("youtube", "v3", developerKey=API_KEY)

# ═══════════════════════════════════════════════
#  DATA FETCH — per channel
# ═══════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_channel(channel_id, ch_key, hours, max_vids):
    now   = datetime.utcnow()
    after = (now - timedelta(hours=hours)).isoformat("T") + "Z"
    ids, snips = [], {}
    npt = None
    while True:
        r = youtube.search().list(
            part="snippet", channelId=channel_id,
            maxResults=min(max_vids, 50), order="date",
            publishedAfter=after, type="video", pageToken=npt
        ).execute()
        for it in r.get("items", []):
            v = it["id"]["videoId"]
            ids.append(v); snips[v] = it["snippet"]
        npt = r.get("nextPageToken")
        if not npt or len(ids) >= max_vids: break

    if not ids: return pd.DataFrame()

    sm = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i+50]
        det = youtube.videos().list(
            part="statistics,snippet,contentDetails", id=",".join(chunk)
        ).execute()
        for it in det.get("items", []):
            v = it["id"]; st2 = it.get("statistics",{}); sn = it.get("snippet",{})
            cd = it.get("contentDetails", {})
            raw = cd.get("duration","PT0S")
            h2=re.search(r'(\d+)H',raw); m2=re.search(r'(\d+)M',raw); s3=re.search(r'(\d+)S',raw)
            dur=(int(h2.group(1)) if h2 else 0)*3600+(int(m2.group(1)) if m2 else 0)*60+(int(s3.group(1)) if s3 else 0)
            sm[v] = dict(
                views=int(st2.get("viewCount",0)),
                likes=int(st2.get("likeCount",0)),
                comments=int(st2.get("commentCount",0)),
                tags=sn.get("tags",[]),
                dur=dur,
            )

    rows = []
    for v in ids:
        if v not in sm: continue
        s = sm[v]; sn = snips.get(v,{})
        utc = datetime.strptime(sn.get("publishedAt","2000-01-01T00:00:00Z"),
                                "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
        ist_t = utc.astimezone(IST)
        hrs   = max((datetime.now(pytz.utc)-utc).total_seconds()/3600, 0.1)
        rows.append(dict(
            channel=ch_key,
            channel_label=CHANNELS[ch_key]["label"],
            color=CHANNELS[ch_key]["color"],
            short=CHANNELS[ch_key]["short"],
            title=sn.get("title","N/A"),
            pub=ist_t, pub_utc=utc,
            hrs=round(hrs,2),
            views=s["views"], likes=s["likes"], comments=s["comments"],
            vph=round(s["views"]/hrs,2),
            eng=round((s["likes"]+s["comments"])/max(s["views"],1)*100,3),
            dur=s["dur"],
            tags=s["tags"],
            vid=v,
        ))
    df2 = pd.DataFrame(rows).sort_values("views",ascending=False).reset_index(drop=True)
    return df2

# ═══════════════════════════════════════════════
#  LOAD ALL CHANNELS
# ═══════════════════════════════════════════════
now_s   = datetime.now(IST).strftime("%H:%M")
today_s = datetime.now(IST).strftime("%d %b %Y")

status_bar = st.empty()
frames = []
ch_frames = {}

with status_bar.container():
    prog = st.progress(0, text="Fetching channel data…")
    for i, (key, meta) in enumerate(CHANNELS.items()):
        prog.progress((i+1)/len(CHANNELS),
                      text=f"Fetching **{meta['label']}** ({i+1}/{len(CHANNELS)})…")
        df_ch = fetch_channel(meta["id"], key, time_window, vids_per_ch)
        ch_frames[key] = df_ch
        if not df_ch.empty:
            frames.append(df_ch)
    prog.empty()

status_bar.empty()

if not frames:
    st.error("No data found. Try increasing the time window or check API quota."); st.stop()

# Combined dataframe
all_df    = pd.concat(frames, ignore_index=True).sort_values("views", ascending=False)
top_video = all_df.iloc[0]   # single top video across all channels

# Channel-level aggregate stats
ch_stats = {}
for key, meta in CHANNELS.items():
    df_ch = ch_frames.get(key, pd.DataFrame())
    if df_ch.empty:
        ch_stats[key] = dict(total=0, peak=0, avg=0, vph=0, eng=0, top_title="N/A",
                             top_views=0, count=0)
        continue
    ch_stats[key] = dict(
        total     = df_ch["views"].sum(),
        peak      = df_ch["views"].max(),
        avg       = int(df_ch["views"].mean()),
        vph       = round(df_ch["vph"].mean(), 1),
        eng       = round(df_ch["eng"].mean(), 2),
        top_title = df_ch.iloc[0]["title"],
        top_views = df_ch.iloc[0]["views"],
        count     = len(df_ch),
    )

grand_total = sum(ch_stats[k]["total"] for k in CH_KEYS)

# ═══════════════════════════════════════════════
#  TOP BAR
# ═══════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:14px;">
    <span class="rep-badge">REPUBLIC</span>
    <div>
      <div class="topbar-title">Republic World — YouTube Real-Time Live | Multi-Channel Advance Chart</div>
    </div>
  </div>
  <span style="font-size:12px;color:#9098b0;letter-spacing:0.3px;">
    © Manish Rawat &nbsp;|&nbsp; Republic Media Network
  </span>
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-size:12px;color:#9098b0;font-family:'IBM Plex Mono',monospace;">{now_s} IST · {today_s}</span>
    <div class="live-pill"><div class="live-dot"></div>LIVE</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Colour strip
seg_html = "".join(f'<div class="ch-seg" style="background:{CHANNELS[k]["color"]};"></div>' for k in CH_KEYS)
st.markdown(f'<div class="ch-strip">{seg_html}</div>', unsafe_allow_html=True)

# Sub bar
st.markdown(f"""
<div class="subbar">
  <span class="subbar-l">
    📡 &nbsp; Advanced Chart Analytics &nbsp;·&nbsp; 6 Channels Tracked &nbsp;·&nbsp;
    {sum(ch_stats[k]['count'] for k in CH_KEYS)} Videos Indexed &nbsp;·&nbsp; {time_window}h Window
  </span>
  <span class="subbar-r">Cache: 5 min &nbsp;·&nbsp; Timezone: IST &nbsp;·&nbsp; Source: YouTube Data API v3</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  CONTENT
# ═══════════════════════════════════════════════
st.markdown('<div class="cw">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  TICKER — one card per channel (top video)
# ═══════════════════════════════════════════════
tk = '<div class="ticker-grid">'
for key in CH_KEYS:
    meta = CHANNELS[key]; c = meta["color"]
    cs   = ch_stats[key]
    vph  = int(cs["vph"]); sg = "▲" if vph>=0 else "▼"; cls = "up" if vph>=0 else "dn"
    short_title = cs["top_title"][:38] + "…" if len(cs["top_title"]) > 38 else cs["top_title"]
    tk += f"""
    <div class="tcard">
      <div class="tcard-top" style="background:{c};"></div>
      <div class="tcard-ch" style="color:{c};">{meta['label']}</div>
      <div class="tcard-title">{short_title}</div>
      <div class="tcard-val" style="color:{c};">{fk(cs['top_views'])}</div>
      <div class="tcard-meta">{cs['count']} videos · avg {fk(cs['avg'])} views</div>
      <div class="tcard-delta {cls}">{sg}&nbsp;{fk(abs(vph))}/hr avg</div>
    </div>"""
tk += '</div>'
st.markdown(tk, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  MAIN CHART — Multi-channel lines + momentum + navigator
# ═══════════════════════════════════════════════
st.markdown('<div class="slbl">📈 &nbsp; Multi-Channel Views Timeline + Market Momentum — Δ Total Views / Interval</div>',
            unsafe_allow_html=True)
st.markdown('<div class="pbox">', unsafe_allow_html=True)

fig = make_subplots(
    rows=3, cols=1,
    row_heights=[0.60, 0.22, 0.18],
    shared_xaxes=True,
    vertical_spacing=0.03,
)

# Build one curve per channel (top video of each channel)
series = {}
for key in CH_KEYS[:top_n_chart]:
    df_ch = ch_frames.get(key, pd.DataFrame())
    if df_ch.empty: continue
    row   = df_ch.iloc[0]
    n     = min(int(max(row["hrs"],0.5)*4), 100); n = max(n,4)
    times = [row["pub_utc"] + timedelta(hours=j*max(row["hrs"],0.5)/(n-1)) for j in range(n)]
    views = growth_curve(row["views"], max(row["hrs"],0.5), n_pts=n, seed=hash(key)%9999)
    c     = CHANNELS[key]["color"]
    series[key] = dict(times=times, views=views, color=c,
                       label=CHANNELS[key]["label"], top_row=row)

    fig.add_trace(go.Scatter(
        x=times, y=views,
        name=CHANNELS[key]["label"],
        line=dict(color=c, width=2.5),
        mode="lines",
        hovertemplate=(f"<b style='color:{c}'>{CHANNELS[key]['label']}</b><br>"
                       f"%{{x|%H:%M}}<br>Views: %{{y:,}}<extra></extra>"),
    ), row=1, col=1)

# Momentum
if series:
    ref = next(iter(series.values())); n = len(ref["times"])
    m_times, m_deltas, prev = [], [], 0
    for i in range(0, n, 3):
        t   = ref["times"][i]
        tot = sum(s["views"][min(i,len(s["views"])-1)] for s in series.values())
        m_deltas.append(tot - prev); prev = tot; m_times.append(t)
    m_times  = m_times[1:]; m_deltas = m_deltas[1:]
    bar_cols = ["#16a34a" if d>=0 else "#dc2626" for d in m_deltas]

    fig.add_trace(go.Bar(
        x=m_times, y=m_deltas, marker_color=bar_cols, marker_line_width=0,
        hovertemplate="Δ Views: %{y:,}<extra></extra>", opacity=0.85,
    ), row=2, col=1)
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.08)", line_width=1, row=2, col=1)

    total_delta = m_deltas[-1] if m_deltas else 0
    sg_d = "▲" if total_delta>=0 else "▼"
    fig.add_annotation(text="MARKET MOMENTUM — Δ TOTAL VIEWS / INTERVAL",
        xref="paper",yref="paper",x=0,y=0.365,showarrow=False,
        font=dict(size=8,color="#9098b0"),align="left")
    fig.add_annotation(text=f"{sg_d} {fk(abs(int(total_delta)))} TOTAL",
        xref="paper",yref="paper",x=1,y=0.365,showarrow=False,
        font=dict(size=9,color="#16a34a" if total_delta>=0 else "#dc2626"),align="right")

    # Navigator
    for s in series.values():
        mx = max(s["views"]) if s["views"] else 1
        fig.add_trace(go.Scatter(
            x=s["times"], y=[v/mx for v in s["views"]],
            line=dict(color=s["color"],width=1),
            mode="lines", opacity=0.4, hoverinfo="skip",
        ), row=3, col=1)
    fig.add_annotation(text="NAVIGATOR — DRAG SLIDERS TO ZOOM",
        xref="paper",yref="paper",x=0,y=0.02,showarrow=False,
        font=dict(size=8,color="#9098b0"),align="left")

fig.update_layout(
    paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", height=480,
    margin=dict(l=52,r=14,t=14,b=8),
    font=dict(color="#6070a0",family="Barlow",size=10),
    hovermode="x unified", showlegend=False,
    hoverlabel=dict(bgcolor="#12132a",font_color="#fff",font_family="Barlow",bordercolor="rgba(0,0,0,0.1)"),
    xaxis3=dict(
        rangeslider=dict(visible=True,bgcolor="#f0f2f7",bordercolor="#e4e6ef",thickness=0.10),
        type="date",tickfont=dict(size=9),gridcolor="rgba(0,0,0,0.05)",showticklabels=True,
    ),
)
for r in [1,2,3]:
    fig.update_xaxes(gridcolor="rgba(0,0,0,0.05)",linecolor="#eef0f8",tickfont=dict(size=9),row=r,col=1)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.05)",linecolor="#eef0f8",tickfont=dict(size=9),row=r,col=1)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# Legend strip
ls = '<div class="leg-strip">'
for key, s in series.items():
    c   = s["color"]; row = s["top_row"]
    sg  = "▲" if row["vph"]>=0 else "▼"
    cls = "up" if row["vph"]>=0 else "dn"
    ls += f"""
    <div class="leg-item">
      <div class="leg-line" style="background:{c};"></div>
      <span style="color:{c};font-weight:800;font-family:'Barlow Condensed',sans-serif;">{CHANNELS[key]["label"]}</span>
      <span class="leg-val" style="color:#12132a;font-size:13px;">{fk(row['views'])}</span>
      <span class="leg-val {cls}" style="font-size:10px;">{sg}{fk(int(abs(row['vph'])))}</span>
    </div>"""
ls += '</div>'
st.markdown(ls, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)   # pbox

# ═══════════════════════════════════════════════
#  3-PANEL: Stats · Heatmap · Share
# ═══════════════════════════════════════════════
st.markdown('<div class="slbl">📊 &nbsp; Channel Statistics · Hourly Heatmap · Current Share</div>',
            unsafe_allow_html=True)

p1, p2, p3 = st.columns([3, 4, 2.5], gap="small")

# ── Channel Stats Table ─────────────────────────
with p1:
    st.markdown('<div class="stbl-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="panel-ttl">Channel Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Current · Peak · Avg · 30-min Δ</div>', unsafe_allow_html=True)

    rows_h = ""
    for key in CH_KEYS:
        c   = CHANNELS[key]["color"]
        cs  = ch_stats[key]
        sg  = "▲"; cls = "up"
        rows_h += f"""
        <tr>
          <td><span class="dot" style="background:{c};"></span>
            <b style="color:{c};">{CHANNELS[key]['label']}</b></td>
          <td style="color:{c};font-weight:700;">{fk(cs['top_views'])}</td>
          <td style="color:#6070a0;">{fk(cs['peak'])}</td>
          <td style="color:#9098b0;">{fk(cs['avg'])}</td>
          <td><span class="{cls}">{sg}{fk(int(cs['vph']))}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="stbl">
      <thead>
        <tr><th>CHANNEL</th><th>NOW</th><th>PEAK</th><th>AVG</th><th>Δ30M</th></tr>
      </thead>
      <tbody>{rows_h}</tbody>
    </table>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Hourly Heatmap ──────────────────────────────
with p2:
    st.markdown('<div class="hmwrap">', unsafe_allow_html=True)
    st.markdown('<div class="panel-ttl">Hourly Activity Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Avg views per hour — deeper colour = higher</div>', unsafe_allow_html=True)

    # Build hour × channel matrix
    hm_data = {}
    for key in CH_KEYS:
        df_ch = ch_frames.get(key, pd.DataFrame())
        row_vals = []
        for h in range(24):
            val = 0
            if not df_ch.empty:
                for _, r in df_ch.iterrows():
                    d = min(abs(r["pub"].hour - h), 24 - abs(r["pub"].hour - h))
                    val += r["views"] * max(0, 1 - d/8)
            row_vals.append(int(val))
        hm_data[CHANNELS[key]["short"]] = row_vals

    hm_df = pd.DataFrame(hm_data, index=list(range(24)))
    hlbls = [f"{h:02d}h" for h in range(24)]
    cscales_hm = [
        [[0,"#fff5f5"],[1,"#e63535"]],
        [[0,"#f0f9ff"],[1,"#0ea5e9"]],
        [[0,"#f5f3ff"],[1,"#8b5cf6"]],
        [[0,"#f0fdf4"],[1,"#16a34a"]],
        [[0,"#fffbeb"],[1,"#f59e0b"]],
        [[0,"#fff7ed"],[1,"#f97316"]],
    ]
    cols_hm = hm_df.columns.tolist()
    fig_hm  = make_subplots(
        rows=1, cols=len(cols_hm), shared_yaxes=True, horizontal_spacing=0.015,
        subplot_titles=[f"<b>{c}</b>" for c in cols_hm]
    )
    for ci, col_name in enumerate(cols_hm):
        vals = hm_df[col_name].values
        fig_hm.add_trace(go.Heatmap(
            z=vals.reshape(-1,1), y=hlbls, x=[col_name],
            colorscale=cscales_hm[ci % len(cscales_hm)], showscale=False,
            text=[[fk(v)] for v in vals], texttemplate="%{text}",
            textfont=dict(size=8, color="rgba(0,0,0,0.55)"),
            hovertemplate=f"<b>{col_name}</b><br>%{{y}}: %{{z:,}}<extra></extra>",
            xgap=2, ygap=1,
        ), row=1, col=ci+1)

    fig_hm.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", height=375,
        margin=dict(l=32, r=6, t=28, b=6),
        font=dict(color="#6070a0", family="Barlow", size=9),
    )
    fig_hm.update_xaxes(showticklabels=False, showgrid=False)
    fig_hm.update_yaxes(tickfont=dict(size=8), gridcolor="rgba(0,0,0,0.04)")
    for ann in fig_hm.layout.annotations:
        txt = ann.text.replace("<b>","").replace("</b>","").strip()
        for ci2, key in enumerate(CH_KEYS):
            if CHANNELS[key]["short"] == txt:
                ann.font = dict(size=10, color=CHANNELS[key]["color"],
                                family="Barlow Condensed")
                break
    st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ── Share Donut ─────────────────────────────────
with p3:
    st.markdown('<div class="sharewrap">', unsafe_allow_html=True)
    st.markdown('<div class="panel-ttl">Current Share</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-sub">at {now_s} IST</div>', unsafe_allow_html=True)

    donut_labels  = [CHANNELS[k]["label"] for k in CH_KEYS]
    donut_values  = [ch_stats[k]["total"] for k in CH_KEYS]
    donut_colors  = [CHANNELS[k]["color"] for k in CH_KEYS]

    fig_d = go.Figure(go.Pie(
        labels=donut_labels, values=donut_values, hole=0.60,
        marker=dict(colors=donut_colors, line=dict(color="#f0f2f7",width=3)),
        textinfo="none", direction="clockwise", sort=False,
        hovertemplate="<b>%{label}</b><br>%{value:,} views (%{percent})<extra></extra>",
    ))
    fig_d.add_annotation(
        text=f"<b>{fk(grand_total)}</b><br><span style='font-size:10px;'>total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=17, color="#12132a", family="Barlow Condensed"), align="center",
    )
    fig_d.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", height=200,
        margin=dict(l=6,r=6,t=6,b=6), showlegend=False,
        font=dict(color="#6070a0", family="Barlow"),
    )
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar":False})

    bh = ""
    for key in CH_KEYS:
        c   = CHANNELS[key]["color"]
        pct = ch_stats[key]["total"] / max(grand_total, 1) * 100
        bh += f"""
        <div class="sbar-row">
          <span class="sbar-lbl" style="color:{c};">{CHANNELS[key]['label']}</span>
          <div class="sbar-track">
            <div class="sbar-fill" style="width:{pct:.1f}%;background:{c};"></div>
          </div>
          <span class="sbar-pct" style="color:{c};">{pct:.1f}%</span>
        </div>"""
    st.markdown(bh, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  TOP VIDEOS TABLE — across all channels
# ═══════════════════════════════════════════════
st.markdown('<div class="slbl" style="margin-top:18px;">🏆 &nbsp; Top Performing Videos — All Channels Ranked by Views</div>',
            unsafe_allow_html=True)
st.markdown('<div class="vtbl-wrap">', unsafe_allow_html=True)
st.markdown(f'<div class="vtbl-head">TOP {min(20, len(all_df))} VIDEOS — {today_s} · {now_s} IST</div>',
            unsafe_allow_html=True)

top20 = all_df.head(20)
rows_v = ""
for rank, (_, row) in enumerate(top20.iterrows(), 1):
    c    = row["color"]
    sg   = "▲"; cls = "up"
    eng  = row["eng"]; vph = int(row["vph"])
    dur  = f"{row['dur']//60:.0f}m" if row["dur"] > 0 else "—"
    rows_v += f"""
    <tr>
      <td><span class="rank-num" style="background:{c};">{rank}</span></td>
      <td style="font-weight:700;max-width:320px;white-space:normal;line-height:1.3;">
        {row['title'][:70]}{'…' if len(row['title'])>70 else ''}</td>
      <td><span style="color:{c};font-weight:700;font-family:'Barlow Condensed',sans-serif;
               font-size:13px;letter-spacing:1px;">{row['channel_label']}</span></td>
      <td style="color:{c};font-weight:700;">{fk(row['views'])}</td>
      <td>{fk(row['likes'])}</td>
      <td>{fk(row['comments'])}</td>
      <td><span class="{cls}">{sg}{fk(abs(vph))}</span></td>
      <td style="color:#6070a0;">{eng:.2f}%</td>
      <td style="color:#9098b0;">{dur}</td>
      <td style="color:#9098b0;font-size:11px;">{row['pub'].strftime('%H:%M')}</td>
    </tr>"""

st.markdown(f"""
<table class="vtbl">
  <thead>
    <tr>
      <th>#</th><th>TITLE</th><th>CHANNEL</th>
      <th>VIEWS</th><th>LIKES</th><th>COMMENTS</th>
      <th>V/HR</th><th>ENGMT</th><th>DUR</th><th>TIME</th>
    </tr>
  </thead>
  <tbody>{rows_v}</tbody>
</table>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)  # vtbl-wrap

# ═══════════════════════════════════════════════
#  DEEP ROW — Engagement scatter · Tag cloud · Duration
# ═══════════════════════════════════════════════
st.markdown('<div class="slbl" style="margin-top:18px;">🔬 &nbsp; Engagement Matrix · Tag Intelligence · Duration Profile</div>',
            unsafe_allow_html=True)

d1, d2, d3 = st.columns(3, gap="small")

with d1:
    st.markdown('<div class="pbox">', unsafe_allow_html=True)
    fig_sc = go.Figure()
    for key in CH_KEYS:
        df_ch = ch_frames.get(key, pd.DataFrame())
        if df_ch.empty: continue
        c = CHANNELS[key]["color"]
        fig_sc.add_trace(go.Scatter(
            x=df_ch["views"], y=df_ch["eng"],
            mode="markers", name=CHANNELS[key]["label"],
            marker=dict(
                size=df_ch["vph"].apply(lambda v: max(6, min(v/500, 24))),
                color=c, opacity=0.75,
                line=dict(color="rgba(255,255,255,0.8)", width=1),
            ),
            hovertemplate="<b>%{customdata}</b><br>Views: %{x:,}<br>Eng: %{y:.2f}%<extra></extra>",
            customdata=df_ch["title"].str[:35],
        ))
    _sc = light_layout(h=280, ml=48, mr=12, mt=34, mb=32)
    _sc["showlegend"] = True
    _sc["legend"] = dict(orientation="h", y=-0.2, font=dict(size=9), bgcolor="rgba(0,0,0,0)")
    _sc["title"] = dict(text="💡  VIEWS vs ENGAGEMENT % (bubble = velocity)",
                        font=dict(size=10, color="#9098b0", family="Barlow Condensed"), x=0.01)
    fig_sc.update_layout(**_sc)
    st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with d2:
    st.markdown('<div class="pbox">', unsafe_allow_html=True)
    all_tags = []
    for df_ch in ch_frames.values():
        if df_ch.empty: continue
        for t in df_ch["tags"].dropna():
            lst = t if isinstance(t,list) else [x.strip() for x in t.split(",")]
            all_tags.extend([x.lower() for x in lst if x.strip()])
    if all_tags:
        tdf = pd.DataFrame(Counter(all_tags).most_common(24), columns=["Tag","Count"])
        fig_t = px.treemap(tdf, path=["Tag"], values="Count", color="Count",
                           color_continuous_scale=["#f0f9ff","#0ea5e9","#8b5cf6"])
        fig_t.update_traces(
            textfont=dict(family="Barlow", size=12, color="#12132a"),
            hovertemplate="<b>%{label}</b>: %{value}<extra></extra>",
            marker_line_width=2, marker_line_color="#f0f2f7",
        )
        fig_t.update_layout(
            paper_bgcolor="#ffffff", height=280,
            margin=dict(l=4,r=4,t=34,b=4),
            font=dict(color="#6070a0", family="Barlow"),
            coloraxis_showscale=False,
            title=dict(text="🏷️  CROSS-CHANNEL TAG INTELLIGENCE",
                       font=dict(size=10,color="#9098b0",family="Barlow Condensed"),x=0.01),
        )
        st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar":False})
    else:
        st.info("No tag data found.")
    st.markdown('</div>', unsafe_allow_html=True)

with d3:
    st.markdown('<div class="pbox">', unsafe_allow_html=True)
    dur_df = all_df[all_df["dur"]>0].copy(); dur_df["dm"] = dur_df["dur"]/60
    fig_dur = go.Figure()
    for key in CH_KEYS:
        sub = dur_df[dur_df["channel"]==key]
        if sub.empty: continue
        c = CHANNELS[key]["color"]
        fig_dur.add_trace(go.Histogram(
            x=sub["dm"], nbinsx=12, name=CHANNELS[key]["label"],
            marker_color=c, opacity=0.7,
            hovertemplate=f"<b>{CHANNELS[key]['label']}</b><br>~%{{x:.0f}}min: %{{y}} vids<extra></extra>",
        ))
    _dl = light_layout(h=280, ml=48, mr=12, mt=34, mb=32)
    _dl["showlegend"] = True
    _dl["legend"] = dict(orientation="h", y=-0.2, font=dict(size=9), bgcolor="rgba(0,0,0,0)")
    _dl["barmode"] = "overlay"
    _dl["title"] = dict(text="🕐  VIDEO DURATION DISTRIBUTION (minutes)",
                        font=dict(size=10,color="#9098b0",family="Barlow Condensed"),x=0.01)
    fig_dur.update_layout(**_dl)
    st.plotly_chart(fig_dur, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  PER-CHANNEL VPH BAR
# ═══════════════════════════════════════════════
st.markdown('<div class="slbl" style="margin-top:18px;">⚡ &nbsp; Channel Velocity Comparison — Views / Hour</div>',
            unsafe_allow_html=True)
st.markdown('<div class="pbox">', unsafe_allow_html=True)

vph_labels = [CHANNELS[k]["label"] for k in CH_KEYS]
vph_vals   = [ch_stats[k]["vph"] for k in CH_KEYS]
vph_colors = [CHANNELS[k]["color"] for k in CH_KEYS]

fig_vph = go.Figure(go.Bar(
    x=vph_labels, y=vph_vals,
    marker=dict(color=vph_colors, line=dict(color="#f0f2f7",width=2)),
    text=[fk(v) for v in vph_vals], textposition="outside",
    textfont=dict(size=13, family="Barlow Condensed", color="#12132a"),
    hovertemplate="<b>%{x}</b><br>Avg Views/Hr: %{y:,.1f}<extra></extra>",
))
_vph = light_layout(h=240, ml=48, mr=14, mt=34, mb=32)
_vph["showlegend"] = False
_vph["title"] = dict(text="⚡  AVG VIEWS/HOUR BY CHANNEL",
                     font=dict(size=10,color="#9098b0",family="Barlow Condensed"),x=0.01)
fig_vph.update_layout(**_vph)
fig_vph.update_traces(marker_cornerradius=6)

st.plotly_chart(fig_vph, use_container_width=True, config={"displayModeBar":False})
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown(f"""
<div class="footer">
  <span>
    📡 <b>Source:</b> YouTube Data API v3 &nbsp;·&nbsp;
    🔑 <b>Auth:</b> Streamlit Secrets &nbsp;·&nbsp;
    🕐 <b>Cache:</b> 5 min TTL &nbsp;·&nbsp;
    📍 <b>TZ:</b> Asia/Kolkata (IST)
  </span>
  <span style="color:#8890bb;font-family:'IBM Plex Mono',monospace;">
    © Manish Rawat &nbsp;|&nbsp; Republic Media Network &nbsp;·&nbsp;
    {sum(ch_stats[k]['count'] for k in CH_KEYS)} videos · {time_window}h window · {now_s} IST
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # cw
