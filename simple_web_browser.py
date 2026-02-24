import streamlit as st
import streamlit.components.v1 as components
import random
import logging
from datetime import datetime

# Suppress tornado noise
logging.getLogger("tornado.access").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.ERROR)
logging.getLogger("tornado.general").setLevel(logging.ERROR)

st.set_page_config(
    page_title="Nexus Browser",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────
if "history"       not in st.session_state: st.session_state.history = []
if "bookmarks"     not in st.session_state: st.session_state.bookmarks = []
if "tabs"          not in st.session_state: st.session_state.tabs = [{"title": "New Tab", "url": ""}]
if "active_tab"    not in st.session_state: st.session_state.active_tab = 0
if "current_url"   not in st.session_state: st.session_state.current_url = ""
if "theme_idx"     not in st.session_state: st.session_state.theme_idx = random.randint(0, 7)
if "show_sidebar"  not in st.session_state: st.session_state.show_sidebar = False
if "incognito"     not in st.session_state: st.session_state.incognito = False
if "quick_nav"     not in st.session_state: st.session_state.quick_nav = ""

# ── Handle quick-nav from query params (iframe -> Streamlit bridge) ────────────
_params = st.query_params
if "goto" in _params:
    _goto = _params["goto"]
    st.query_params.clear()
    if _goto:
        st.session_state.quick_nav = _goto

THEMES = [
    {"name": "Deep Ocean",       "emoji": "🌊", "key": "ocean",   "accent": "#00c8ff", "accent2": "#0066ff", "glow": "0,200,255",   "bg": "#010810"},
    {"name": "Mars Surface",     "emoji": "🔴", "key": "mars",    "accent": "#ff5500", "accent2": "#ff2200", "glow": "255,85,0",    "bg": "#0a0200"},
    {"name": "SpaceX Launch",    "emoji": "🚀", "key": "rocket",  "accent": "#88ccff", "accent2": "#3366ff", "glow": "136,200,255", "bg": "#000208"},
    {"name": "City Streets",     "emoji": "🌆", "key": "city",    "accent": "#ffd700", "accent2": "#ff8800", "glow": "255,215,0",   "bg": "#03030a"},
    {"name": "Sahara Desert",    "emoji": "🏜️", "key": "desert",  "accent": "#ffaa44", "accent2": "#ff6600", "glow": "255,170,68",  "bg": "#080400"},
    {"name": "Aurora Borealis",  "emoji": "🌌", "key": "aurora",  "accent": "#00ff99", "accent2": "#aa00ff", "glow": "0,255,153",   "bg": "#000608"},
    {"name": "Rainforest",       "emoji": "🌿", "key": "forest",  "accent": "#22ff66", "accent2": "#00aa33", "glow": "34,255,102",  "bg": "#010a02"},
    {"name": "Golden Hour Park", "emoji": "🐕", "key": "dogs",    "accent": "#ffbb44", "accent2": "#ff7722", "glow": "255,187,68",  "bg": "#060300"},
]

# Process any pending quick_nav (from new-tab card clicks)
if st.session_state.quick_nav:
    _qurl = st.session_state.quick_nav
    st.session_state.quick_nav = ""
    navigate(_qurl)

theme = THEMES[st.session_state.theme_idx]
ACC   = theme["accent"]
ACC2  = theme["accent2"]
GLOW  = theme["glow"]
BG    = theme["bg"]

# ── Navigation Helpers ────────────────────────────────────────────────────────
def navigate(url: str):
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    st.session_state.quick_nav = ""  # clear any pending quick nav
    st.session_state.current_url = url
    t = st.session_state.active_tab
    st.session_state.tabs[t]["url"]   = url
    domain = url.replace("https://","").replace("http://","").split("/")[0]
    st.session_state.tabs[t]["title"] = domain[:20]
    if not st.session_state.incognito:
        st.session_state.history.insert(0, {"url": url, "domain": domain, "time": datetime.now().strftime("%H:%M")})
        if len(st.session_state.history) > 50:
            st.session_state.history = st.session_state.history[:50]

def do_search(q: str, engine: str = "Google"):
    urls = {
        "Google":     f"https://www.google.com/search?q={q.replace(' ','+')}",
        "DuckDuckGo": f"https://duckduckgo.com/?q={q.replace(' ','+')}",
        "Bing":       f"https://www.bing.com/search?q={q.replace(' ','+')}",
        "YouTube":    f"https://www.youtube.com/results?search_query={q.replace(' ','+')}",
        "Wikipedia":  f"https://en.wikipedia.org/w/index.php?search={q.replace(' ','+')}",
        "GitHub":     f"https://github.com/search?q={q.replace(' ','+')}",
    }
    navigate(urls.get(engine, urls["Google"]))

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
  --acc:   {ACC};
  --acc2:  {ACC2};
  --glow:  {GLOW};
  --bg:    {BG};
  --surface:  rgba(255,255,255,0.04);
  --surface2: rgba(255,255,255,0.07);
  --border:   rgba(255,255,255,0.09);
  --text:     #e8eaf0;
  --text-dim: rgba(232,234,240,0.5);
  --radius:   10px;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  height: 100vh;
  overflow: hidden;
}}

/* Strip Streamlit chrome */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="collapsedControl"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
div[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}
.element-container {{ margin: 0 !important; }}

/* Inputs */
.stTextInput > div > div > input {{
  background: rgba(255,255,255,0.06) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 24px !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: 7px 18px !important;
  transition: all 0.2s ease !important;
  caret-color: var(--acc) !important;
}}
.stTextInput > div > div > input:focus {{
  border-color: var(--acc) !important;
  background: rgba(255,255,255,0.09) !important;
  box-shadow: 0 0 0 3px rgba(var(--glow),0.12), 0 2px 12px rgba(0,0,0,0.4) !important;
  outline: none !important;
}}
.stTextInput > div > div > input::placeholder {{ color: var(--text-dim) !important; }}
.stTextInput label {{ display: none !important; }}
.stTextInput > div {{ padding: 0 !important; }}

/* Buttons */
.stButton > button {{
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  border-radius: 8px !important;
  padding: 5px 10px !important;
  transition: all 0.15s ease !important;
  white-space: nowrap !important;
  min-height: 0 !important;
  line-height: 1.4 !important;
}}
.stButton > button:hover {{
  background: var(--surface2) !important;
  border-color: var(--acc) !important;
  color: var(--acc) !important;
  box-shadow: 0 2px 12px rgba(var(--glow),0.2) !important;
  transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* Selectbox */
.stSelectbox > div > div {{
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-size: 12px !important;
  min-height: 0 !important;
}}
.stSelectbox label {{ display: none !important; }}
.stSelectbox > div {{ padding: 0 !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.15); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--acc); }}

/* Column spacing fix */
[data-testid="column"] {{ padding: 0 3px !important; }}
</style>
""", unsafe_allow_html=True)

# ── Tab Bar ───────────────────────────────────────────────────────────────────
tabs_html = ""
for i, tab in enumerate(st.session_state.tabs[:8]):
    active_cls = "tab-active" if i == st.session_state.active_tab else ""
    label = tab["title"] if tab["title"] else "New Tab"
    if len(label) > 16: label = label[:16] + "…"
    favicon = "🌐" if not tab["url"] else "🔒"
    tabs_html += f"""
    <div class="tab {active_cls}" onclick="setTab({i})">
      <span class="tab-favicon">{favicon}</span>
      <span class="tab-label">{label}</span>
      <span class="tab-close" onclick="event.stopPropagation();closeTab({i})">✕</span>
    </div>"""

st.markdown(f"""
<div id="browser-chrome">
  <div id="tab-strip">
    <div id="tabs-wrapper">{tabs_html}</div>
    <button class="new-tab-btn" title="New tab">＋</button>
    {'<div class="incognito-badge">👤 Incognito</div>' if st.session_state.incognito else ''}
  </div>
</div>
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
#browser-chrome {{
  position:relative;z-index:200;
  background:rgba(10,11,18,0.97);
  backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(255,255,255,0.07);
}}
#tab-strip {{
  display:flex;align-items:flex-end;
  padding:8px 12px 0;gap:2px;height:42px;
  background:rgba(6,7,12,0.9);
}}
#tabs-wrapper {{
  display:flex;align-items:flex-end;gap:2px;flex:1;
  overflow-x:auto;scrollbar-width:none;
}}
#tabs-wrapper::-webkit-scrollbar{{display:none;}}
.tab {{
  display:flex;align-items:center;gap:6px;
  padding:6px 12px 7px;height:34px;
  min-width:100px;max-width:200px;
  border-radius:8px 8px 0 0;
  background:rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.06);border-bottom:none;
  cursor:pointer;transition:background 0.15s;
  font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:500;
  color:rgba(232,234,240,0.45);white-space:nowrap;overflow:hidden;
}}
.tab:hover{{background:rgba(255,255,255,0.07);color:rgba(232,234,240,0.8);}}
.tab-active{{
  background:rgba(16,18,28,0.99)!important;
  color:#e8eaf0!important;
  border-color:rgba(255,255,255,0.1)!important;
  box-shadow:0 -2px 0 {ACC} inset;
}}
.tab-favicon{{font-size:11px;flex-shrink:0;}}
.tab-label{{flex:1;overflow:hidden;text-overflow:ellipsis;}}
.tab-close{{
  flex-shrink:0;width:16px;height:16px;
  display:flex;align-items:center;justify-content:center;
  border-radius:50%;font-size:9px;
  color:rgba(232,234,240,0.35);transition:all 0.12s;
}}
.tab-close:hover{{background:rgba(255,255,255,0.12);color:#fff;}}
.new-tab-btn {{
  width:28px;height:28px;border-radius:6px;margin-bottom:1px;
  background:transparent;border:1px solid rgba(255,255,255,0.08);
  color:rgba(232,234,240,0.45);font-size:16px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:all 0.15s;flex-shrink:0;
}}
.new-tab-btn:hover{{background:rgba(255,255,255,0.1);color:#fff;border-color:{ACC};}}
.incognito-badge{{
  display:flex;align-items:center;gap:4px;margin-left:10px;margin-bottom:4px;
  background:rgba(150,80,255,0.12);border:1px solid rgba(150,80,255,0.25);
  border-radius:20px;padding:2px 10px;
  font-family:'Plus Jakarta Sans',sans-serif;font-size:11px;
  color:#cc99ff;font-weight:500;white-space:nowrap;
}}
</style>
""", unsafe_allow_html=True)

# ── Navigation Bar ────────────────────────────────────────────────────────────
current_url = st.session_state.current_url
is_secure   = current_url.startswith("https://")
lock_icon   = "🔒" if (is_secure and current_url) else ("🔓" if current_url else "🌐")
lock_color  = "#22cc66" if is_secure else ("#ffaa00" if current_url else "#666")

c_back, c_fwd, c_reload, c_home, c_lock, c_url, c_bkm, c_ext = st.columns([
    0.35, 0.35, 0.35, 0.35, 0.22, 6.5, 0.45, 0.45
])

with c_back:
    if st.button("←", key="btn_back", help="Go back"):
        if len(st.session_state.history) > 1:
            st.session_state.history.pop(0)
            prev = st.session_state.history[0]["url"] if st.session_state.history else ""
            if prev: navigate(prev)
            st.rerun()

with c_fwd:
    st.button("→", key="btn_fwd", help="Go forward")

with c_reload:
    if st.button("↺", key="btn_reload", help="Reload"):
        st.rerun()

with c_home:
    if st.button("⌂", key="btn_home", help="Home"):
        st.session_state.current_url = ""
        st.session_state.tabs[st.session_state.active_tab]["url"] = ""
        st.session_state.tabs[st.session_state.active_tab]["title"] = "New Tab"
        st.rerun()

with c_lock:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;height:38px;font-size:14px;color:{lock_color};"
         title="{'Secure' if is_secure else 'Not secure'}">
      {lock_icon}
    </div>""", unsafe_allow_html=True)

with c_url:
    url_val = st.text_input("URL", value=current_url, key="url_bar",
                             placeholder="Search or enter web address",
                             label_visibility="collapsed")

with c_bkm:
    is_bookmarked = any(b["url"] == current_url for b in st.session_state.bookmarks)
    if st.button("★" if is_bookmarked else "☆", key="btn_bkm", help="Bookmark"):
        if current_url and not is_bookmarked:
            domain = current_url.replace("https://","").replace("http://","").split("/")[0]
            st.session_state.bookmarks.insert(0, {"url": current_url, "domain": domain[:20]})
        elif is_bookmarked:
            st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b["url"] != current_url]
        st.rerun()

with c_ext:
    if st.button("⋮", key="btn_sidebar", help="Sidebar"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
        st.rerun()

# Handle URL bar input
if url_val != current_url and url_val:
    if " " not in url_val and "." in url_val:
        navigate(url_val)
    else:
        do_search(url_val)
    st.rerun()

# ── Search & Tools Bar ────────────────────────────────────────────────────────
sa, sb, sc, sd, se, sf = st.columns([1.1, 4.2, 0.9, 0.8, 0.8, 0.9])

with sa:
    engine = st.selectbox("eng", ["Google","DuckDuckGo","Bing","YouTube","Wikipedia","GitHub"],
                           key="engine_sel", label_visibility="collapsed")
with sb:
    srch = st.text_input("search", key="search_bar",
                          placeholder=f"  🔍  Search with {engine}…",
                          label_visibility="collapsed")
with sc:
    search_clicked = st.button("Search →", key="btn_search")
with sd:
    if st.button("🕶 Incognito", key="btn_incog"):
        st.session_state.incognito = not st.session_state.incognito
        st.rerun()
with se:
    if st.button("🗑 Clear", key="btn_clear"):
        st.session_state.history   = []
        st.session_state.bookmarks = []
        st.session_state.tabs      = [{"title":"New Tab","url":""}]
        st.session_state.active_tab = 0
        st.session_state.current_url = ""
        st.rerun()
with sf:
    theme_names = [f"{t['emoji']} {t['name']}" for t in THEMES]
    new_theme = st.selectbox("theme", theme_names, index=st.session_state.theme_idx,
                              key="theme_sel", label_visibility="collapsed")
    new_idx = theme_names.index(new_theme)
    if new_idx != st.session_state.theme_idx:
        st.session_state.theme_idx = new_idx
        st.rerun()

if (search_clicked or srch) and srch:
    do_search(srch, engine)
    st.rerun()

# Accent line separator
st.markdown(f"""
<div style="height:2px;
  background:linear-gradient(90deg,transparent 0%,{ACC} 30%,{ACC2} 70%,transparent 100%);
  opacity:0.45;margin:0;">
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS SCRIPTS
# ═══════════════════════════════════════════════════════════════════════════════
CANVAS_SCRIPTS = {
"ocean": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();window.addEventListener('resize',resize);
let t=0;
const fish=Array.from({length:22},()=>({x:Math.random()*2000,y:60+Math.random()*400,sp:0.5+Math.random()*1.8,d:Math.random()>0.5?1:-1,s:0.6+Math.random()*1.2,col:`hsl(${175+Math.random()*60},75%,${45+Math.random()*30}%)`}));
const bubbles=Array.from({length:50},()=>({x:Math.random()*2000,y:Math.random()*600,r:1+Math.random()*3.5,sp:0.2+Math.random()*0.7}));
const jellyfish=Array.from({length:4},()=>({x:Math.random()*1800+100,y:100+Math.random()*200,oy:100+Math.random()*200,phase:Math.random()*Math.PI*2}));
function draw(){
  t+=0.007;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  let g=ctx.createLinearGradient(0,0,0,h);
  g.addColorStop(0,'#000d1f');g.addColorStop(0.5,'#001428');g.addColorStop(1,'#000810');
  ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
  for(let i=0;i<8;i++){
    ctx.beginPath();ctx.ellipse(w*(0.05+i*0.13)+Math.sin(t*0.8+i)*25,h*0.25+Math.cos(t*0.6+i)*18,35+Math.sin(t+i*0.7)*12,12+Math.cos(t+i)*4,t*0.08+i*0.4,0,Math.PI*2);
    ctx.strokeStyle=`rgba(0,180,255,${0.03+Math.abs(Math.sin(t+i))*0.05})`;ctx.lineWidth=1.5;ctx.stroke();
  }
  for(let x=0;x<w;x+=3){
    const wy=h*0.12+Math.sin(x*0.012+t)*6+Math.sin(x*0.02+t*1.5)*3;
    ctx.fillStyle=`rgba(0,160,255,${0.06+Math.sin(x*0.01+t)*0.02})`;ctx.fillRect(x,wy,2,2);
  }
  for(let i=0;i<5;i++){
    let rg=ctx.createLinearGradient(w*(0.15+i*0.18),0,w*(0.2+i*0.18),h*0.8);
    rg.addColorStop(0,`rgba(0,150,255,${0.06+Math.sin(t+i)*0.02})`);rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.moveTo(w*(0.12+i*0.18),0);ctx.lineTo(w*(0.22+i*0.18),0);ctx.lineTo(w*(0.18+i*0.18),h*0.7);ctx.closePath();
    ctx.fillStyle=rg;ctx.fill();
  }
  jellyfish.forEach((j,ji)=>{
    j.y=j.oy+Math.sin(t*0.5+j.phase)*30;
    const pulse=0.85+Math.sin(t*2+j.phase)*0.15;
    ctx.save();ctx.translate(j.x,j.y);
    let jg=ctx.createRadialGradient(0,0,0,0,0,28*pulse);
    jg.addColorStop(0,'rgba(180,100,255,0.5)');jg.addColorStop(0.6,'rgba(100,50,255,0.2)');jg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.ellipse(0,0,28*pulse,18*pulse,0,Math.PI,Math.PI*2);ctx.fillStyle=jg;ctx.fill();
    for(let k=0;k<6;k++){
      ctx.beginPath();ctx.moveTo(-15+k*6,0);ctx.bezierCurveTo(-15+k*6+Math.sin(t*2+k)*8,20,-15+k*6+Math.sin(t*1.5+k)*6,40,-15+k*6+Math.sin(t+k)*10,55+ji*5);
      ctx.strokeStyle=`rgba(180,100,255,${0.2+Math.sin(t+k)*0.1})`;ctx.lineWidth=1;ctx.stroke();
    }
    ctx.restore();
  });
  fish.forEach(f=>{
    f.x+=f.sp*f.d;if(f.x>w+60)f.x=-60;if(f.x<-60)f.x=w+60;
    ctx.save();ctx.translate(f.x,f.y+Math.sin(t*1.8+f.x*0.008)*4);ctx.scale(f.d*f.s,f.s);
    ctx.fillStyle=f.col;
    ctx.beginPath();ctx.ellipse(0,0,16,6,0,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.moveTo(-16,0);ctx.lineTo(-26,-8);ctx.lineTo(-26,8);ctx.closePath();ctx.fill();
    ctx.beginPath();ctx.arc(8,0,2,0,Math.PI*2);ctx.fillStyle='rgba(0,0,0,0.6)';ctx.fill();
    ctx.restore();
  });
  bubbles.forEach(b=>{
    b.y-=b.sp;if(b.y<-10)b.y=h+10;
    ctx.beginPath();ctx.arc(b.x+Math.sin(t*0.5+b.x*0.01)*3,b.y,b.r,0,Math.PI*2);
    ctx.strokeStyle='rgba(120,210,255,0.25)';ctx.lineWidth=1;ctx.stroke();
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"mars": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const rocks=Array.from({length:30},()=>({x:Math.random(),y:0.52+Math.random()*0.48,rx:8+Math.random()*35,ry:4+Math.random()*15,col:`hsl(${8+Math.random()*18},${35+Math.random()*25}%,${12+Math.random()*18}%)`}));
const dust=Array.from({length:80},()=>({x:Math.random(),y:0.3+Math.random()*0.7,r:0.5+Math.random()*2.5,sp:0.0003+Math.random()*0.001,a:Math.random()}));
const craters=Array.from({length:8},()=>({x:Math.random(),y:0.6+Math.random()*0.35,r:15+Math.random()*40}));
function draw(){
  t+=0.004;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  let sky=ctx.createLinearGradient(0,0,0,h*0.55);
  sky.addColorStop(0,'#0f0200');sky.addColorStop(0.6,'#250800');sky.addColorStop(1,'#4a1500');
  ctx.fillStyle=sky;ctx.fillRect(0,0,w,h*0.55);
  let sg=ctx.createRadialGradient(w*0.7,h*0.18,5,w*0.7,h*0.18,h*0.4);
  sg.addColorStop(0,'rgba(255,160,30,0.35)');sg.addColorStop(0.4,'rgba(255,80,0,0.1)');sg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=sg;ctx.fillRect(0,0,w,h);
  ctx.beginPath();ctx.arc(w*0.7,h*0.18,18,0,Math.PI*2);ctx.fillStyle='#ffcc40';ctx.fill();
  let atm=ctx.createLinearGradient(0,h*0.42,0,h*0.6);
  atm.addColorStop(0,'rgba(0,0,0,0)');atm.addColorStop(0.5,'rgba(255,80,20,0.12)');atm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm;ctx.fillRect(0,h*0.42,w,h*0.18);
  let grd=ctx.createLinearGradient(0,h*0.52,0,h);
  grd.addColorStop(0,'#2a0800');grd.addColorStop(0.3,'#1e0600');grd.addColorStop(1,'#0d0200');
  ctx.fillStyle=grd;ctx.fillRect(0,h*0.52,w,h*0.48);
  ctx.beginPath();ctx.moveTo(0,h);
  for(let x=0;x<=w;x+=8){ctx.lineTo(x,h*0.56-Math.sin(x*0.004+0.5)*h*0.06-Math.sin(x*0.009+1.2)*h*0.03);}
  ctx.lineTo(w,h);ctx.closePath();ctx.fillStyle='#1a0400';ctx.fill();
  craters.forEach(cr=>{
    ctx.beginPath();ctx.ellipse(cr.x*w,cr.y*h,cr.r,cr.r*0.45,0,0,Math.PI*2);
    ctx.strokeStyle='rgba(80,20,0,0.6)';ctx.lineWidth=2;ctx.stroke();
  });
  rocks.forEach(r=>{
    ctx.beginPath();ctx.ellipse(r.x*w,r.y*h,r.rx,r.ry,0.15,0,Math.PI*2);
    ctx.fillStyle=r.col;ctx.fill();
  });
  dust.forEach(d=>{
    d.x+=d.sp;if(d.x>1.05)d.x=-0.05;
    d.a=0.08+Math.abs(Math.sin(t*1.5+d.x*10))*0.25;
    ctx.beginPath();ctx.arc(d.x*w,d.y*h,d.r,0,Math.PI*2);
    ctx.fillStyle=`rgba(200,90,30,${d.a})`;ctx.fill();
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"rocket": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const stars=Array.from({length:250},()=>({x:Math.random(),y:Math.random(),r:0.4+Math.random()*1.4,a:Math.random()}));
const rockets=[
  {x:0.35,y:1.1,sp:0.0012,s:1.1,trail:[]},
  {x:0.62,y:1.3,sp:0.0008,s:0.75,trail:[]},
  {x:0.18,y:1.5,sp:0.0006,s:0.55,trail:[]},
];
function drawRocket(ctx,x,y,s){
  ctx.save();ctx.translate(x,y);ctx.scale(s,s);
  ctx.beginPath();ctx.moveTo(-7,14);ctx.lineTo(7,14);ctx.lineTo(5,20);ctx.lineTo(-5,20);ctx.closePath();ctx.fillStyle='#aabbcc';ctx.fill();
  ctx.beginPath();ctx.roundRect(-6,-20,12,34,3);ctx.fillStyle='#d8e8f0';ctx.fill();
  ctx.beginPath();ctx.roundRect(-6,0,12,8,1);ctx.fillStyle='#cc3333';ctx.fill();
  ctx.beginPath();ctx.moveTo(0,-32);ctx.lineTo(-6,-20);ctx.lineTo(6,-20);ctx.closePath();ctx.fillStyle='#e8f0f8';ctx.fill();
  ctx.beginPath();ctx.moveTo(-6,8);ctx.lineTo(-16,22);ctx.lineTo(-6,16);ctx.closePath();ctx.fillStyle='#aabbcc';ctx.fill();
  ctx.beginPath();ctx.moveTo(6,8);ctx.lineTo(16,22);ctx.lineTo(6,16);ctx.closePath();ctx.fillStyle='#aabbcc';ctx.fill();
  ctx.beginPath();ctx.arc(0,-8,4,0,Math.PI*2);ctx.fillStyle='rgba(100,200,255,0.7)';ctx.fill();
  ctx.restore();
}
function draw(){
  t+=0.008;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  ctx.fillStyle='rgba(0,2,10,0.18)';ctx.fillRect(0,0,w,h);
  if(t<0.12){ctx.fillStyle='#000208';ctx.fillRect(0,0,w,h);}
  stars.forEach(s=>{
    s.a=0.3+Math.abs(Math.sin(t*1.5+s.x*20+s.y*15))*0.7;
    ctx.beginPath();ctx.arc(s.x*w,s.y*h,s.r,0,Math.PI*2);
    ctx.fillStyle=`rgba(255,255,255,${s.a})`;ctx.fill();
  });
  let eg=ctx.createRadialGradient(w*0.5,h*1.1,h*0.1,w*0.5,h*1.1,h*0.7);
  eg.addColorStop(0,'rgba(30,90,220,0.45)');eg.addColorStop(0.4,'rgba(20,60,180,0.15)');eg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=eg;ctx.fillRect(0,h*0.5,w,h*0.5);
  ctx.beginPath();ctx.arc(w*0.5,h*1.35,h*0.55,Math.PI,Math.PI*2);
  ctx.strokeStyle='rgba(80,160,255,0.3)';ctx.lineWidth=2;ctx.stroke();
  rockets.forEach(r=>{
    r.y-=r.sp;if(r.y<-0.25){r.y=1.2;r.trail=[];}
    const rx=r.x*w,ry=r.y*h;
    r.trail.push({x:rx,y:ry});if(r.trail.length>100)r.trail.shift();
    for(let i=0;i<4;i++){
      ctx.beginPath();ctx.ellipse(rx+(Math.random()-0.5)*4*r.s,ry+22*r.s+i*8*r.s,r.s*(3-i*0.5),r.s*(18+i*10),0,0,Math.PI*2);
      ctx.fillStyle=['rgba(255,255,160,0.9)','rgba(255,140,20,0.65)','rgba(255,60,0,0.4)','rgba(180,30,0,0.15)'][i];ctx.fill();
    }
    r.trail.forEach((p,i)=>{
      const prog=i/r.trail.length;
      ctx.beginPath();ctx.arc(p.x,p.y,r.s*(0.5+prog*2.5),0,Math.PI*2);
      ctx.fillStyle=`rgba(80,160,255,${prog*0.12})`;ctx.fill();
    });
    drawRocket(ctx,rx,ry,r.s);
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"city": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0,buildings,cars,people,raindrops;
function init(){
  const w=c.width,h=c.height;
  buildings=Array.from({length:22},(_,i)=>({
    x:i*(w/20)-20,w:28+Math.random()*55,h:h*0.18+Math.random()*h*0.55,
    col:`hsl(220,${15+Math.random()*10}%,${7+Math.random()*5}%)`,
    wins:Array.from({length:60},()=>({lit:Math.random()>0.35,flicker:Math.random()>0.9,hue:40+Math.random()*30}))
  }));
  cars=Array.from({length:14},()=>({x:Math.random(),sp:0.0008+Math.random()*0.0025,lane:Math.floor(Math.random()*4),col:Math.random()>0.5?'#ffdd00':'#ff4422',w:26+Math.random()*10}));
  people=Array.from({length:10},()=>({x:Math.random(),sp:0.0002+Math.random()*0.0006,d:Math.random()>0.5?1:-1,bob:Math.random()*Math.PI*2}));
  raindrops=Array.from({length:120},()=>({x:Math.random(),y:Math.random(),sp:0.008+Math.random()*0.015,len:6+Math.random()*14}));
}
init();
function draw(){
  t+=0.009;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  if(!buildings)init();
  ctx.fillStyle='#030308';ctx.fillRect(0,0,w,h);
  ctx.beginPath();ctx.arc(w*0.82,h*0.09,22,0,Math.PI*2);
  let mg=ctx.createRadialGradient(w*0.82,h*0.09,0,w*0.82,h*0.09,22);mg.addColorStop(0,'#fff8e0');mg.addColorStop(1,'#ffe090');
  ctx.fillStyle=mg;ctx.fill();
  let mh=ctx.createRadialGradient(w*0.82,h*0.09,22,w*0.82,h*0.09,100);mh.addColorStop(0,'rgba(255,240,180,0.12)');mh.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mh;ctx.fillRect(0,0,w,h);
  buildings.forEach(b=>{
    ctx.fillStyle=b.col;ctx.fillRect(b.x,h-b.h,b.w,b.h);
    ctx.beginPath();ctx.moveTo(b.x+b.w/2,h-b.h);ctx.lineTo(b.x+b.w/2,h-b.h-12);ctx.strokeStyle='rgba(255,255,255,0.12)';ctx.lineWidth=1;ctx.stroke();
    ctx.beginPath();ctx.arc(b.x+b.w/2,h-b.h-13,2,0,Math.PI*2);ctx.fillStyle=`rgba(255,50,50,${0.5+Math.sin(t*2+b.x)*0.5})`;ctx.fill();
    let wi=0;
    for(let row=0;row<Math.floor(b.h/18);row++){
      for(let col=0;col<Math.floor(b.w/14);col++){
        const win=b.wins[wi%b.wins.length];
        const wx=b.x+3+col*14,wy=h-b.h+6+row*18;
        if(wy>h-4)continue;
        if(win.lit){ctx.fillStyle=win.flicker&&Math.random()>0.98?'rgba(255,120,0,0.9)':`hsla(${win.hue},80%,62%,0.85)`;ctx.fillRect(wx,wy,9,11);}
        else{ctx.fillStyle='rgba(0,0,0,0.5)';ctx.fillRect(wx,wy,9,11);}
        wi++;
      }
    }
  });
  ctx.fillStyle='#0e0e16';ctx.fillRect(0,h*0.74,w,h*0.26);
  for(let i=0;i<4;i++){const ly=h*0.76+i*h*0.06;for(let x=-60;x<w+60;x+=55){ctx.fillStyle='rgba(255,210,0,0.2)';ctx.fillRect((x+t*80)%w,ly,30,2);}}
  raindrops.forEach(r=>{r.y+=r.sp;if(r.y>1)r.y=-0.05;ctx.beginPath();ctx.moveTo(r.x*w,r.y*h);ctx.lineTo(r.x*w-1.5,r.y*h+r.len);ctx.strokeStyle='rgba(150,200,255,0.12)';ctx.lineWidth=0.8;ctx.stroke();});
  cars.forEach(car=>{
    car.x+=car.sp;if(car.x>1.08)car.x=-0.06;
    const cx=car.x*w,cy=h*0.755+car.lane*h*0.062;
    let beam=ctx.createLinearGradient(cx+car.w,cy,cx+car.w+120,cy);beam.addColorStop(0,'rgba(255,245,200,0.35)');beam.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=beam;ctx.fillRect(cx+car.w,cy-16,120,32);
    ctx.beginPath();ctx.roundRect(cx,cy-6,car.w,12,3);ctx.fillStyle=car.col;ctx.fill();
    [cx+4,cx+car.w-5].forEach(wx=>{ctx.beginPath();ctx.arc(wx,cy+6,4,0,Math.PI*2);ctx.fillStyle='#111';ctx.fill();});
    ctx.beginPath();ctx.arc(cx+2,cy,3,0,Math.PI*2);ctx.fillStyle='rgba(255,30,0,0.9)';ctx.fill();
  });
  people.forEach(p=>{
    p.x+=p.sp*p.d;if(p.x>1.02)p.x=-0.02;if(p.x<-0.02)p.x=1.02;p.bob+=0.08;
    const px=p.x*w,py=h*0.74-2+Math.sin(p.bob)*1.5;
    ctx.fillStyle='rgba(3,3,12,0.95)';
    ctx.beginPath();ctx.arc(px,py-16,5,0,Math.PI*2);ctx.fill();
    ctx.fillRect(px-3,py-11,6,13);
    ctx.beginPath();ctx.moveTo(px,py+2);ctx.lineTo(px-3,py+13+Math.sin(p.bob)*5);ctx.lineWidth=3;ctx.strokeStyle='rgba(3,3,12,0.95)';ctx.stroke();
    ctx.beginPath();ctx.moveTo(px,py+2);ctx.lineTo(px+3,py+13-Math.sin(p.bob)*5);ctx.stroke();
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"desert": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const mirages=Array.from({length:4},(_,i)=>({x:0.15+i*0.22,phase:Math.random()*Math.PI*2}));
const dunes=[{yBase:0.50,amp:0.07,freq:0.004,col:'#1e0800'},{yBase:0.55,amp:0.05,freq:0.006,col:'#280b00'},{yBase:0.60,amp:0.04,freq:0.008,col:'#321000'},{yBase:0.65,amp:0.03,freq:0.01,col:'#3c1400'},{yBase:0.70,amp:0.02,freq:0.012,col:'#461800'}];
const particles=Array.from({length:60},()=>({x:Math.random(),y:0.35+Math.random()*0.5,r:0.5+Math.random()*2,sp:0.0003+Math.random()*0.001,a:Math.random()*0.3}));
function draw(){
  t+=0.005;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  let sky=ctx.createLinearGradient(0,0,0,h*0.55);sky.addColorStop(0,'#080100');sky.addColorStop(0.4,'#180500');sky.addColorStop(0.8,'#3a1000');sky.addColorStop(1,'#5a2200');
  ctx.fillStyle=sky;ctx.fillRect(0,0,w,h*0.55);
  const sx=w*0.65,sy=h*0.22;
  let sunG=ctx.createRadialGradient(sx,sy,8,sx,sy,h*0.35);sunG.addColorStop(0,'rgba(255,210,60,0.8)');sunG.addColorStop(0.15,'rgba(255,130,0,0.35)');sunG.addColorStop(0.4,'rgba(255,60,0,0.12)');sunG.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=sunG;ctx.fillRect(0,0,w,h);
  ctx.beginPath();ctx.arc(sx,sy,16,0,Math.PI*2);ctx.fillStyle='#fffde0';ctx.fill();
  dunes.forEach((d,di)=>{
    ctx.beginPath();ctx.moveTo(0,h);
    for(let x=0;x<=w;x+=5){ctx.lineTo(x,h*d.yBase+Math.sin(x*d.freq+t*200*d.amp)*h*d.amp+Math.sin(x*d.freq*1.8+t*160*d.amp+1)*h*d.amp*0.4);}
    ctx.lineTo(w,h);ctx.closePath();ctx.fillStyle=d.col;ctx.fill();
  });
  mirages.forEach(m=>{
    const alpha=0.06+Math.abs(Math.sin(t*0.6+m.phase))*0.1;
    let mg=ctx.createLinearGradient(m.x*w-60,0,m.x*w+60,0);mg.addColorStop(0,'rgba(0,0,0,0)');mg.addColorStop(0.4,`rgba(80,160,255,${alpha})`);mg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=mg;ctx.fillRect(m.x*w-60,h*0.5,120,12);
  });
  particles.forEach(p=>{p.x+=p.sp;if(p.x>1.05)p.x=-0.05;p.a=0.05+Math.abs(Math.sin(t*2+p.x*8))*0.2;ctx.beginPath();ctx.arc(p.x*w,p.y*h,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(200,90,30,${p.a})`;ctx.fill();});
  requestAnimationFrame(draw);
}
draw();
})();
""",
"aurora": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const stars=Array.from({length:220},()=>({x:Math.random(),y:Math.random()*0.85,r:0.3+Math.random()*1.3,a:Math.random()}));
const trees=Array.from({length:16},(_,i)=>({x:i/15,h:0.08+Math.random()*0.12}));
const layers=[
  {cols:['rgba(0,255,120,0)','rgba(0,255,120,0.14)','rgba(0,255,120,0)'],yB:0.28,amp:0.1,freq:0.004,sp:1},
  {cols:['rgba(0,180,255,0)','rgba(0,180,255,0.1)','rgba(0,180,255,0)'],yB:0.22,amp:0.12,freq:0.005,sp:0.7},
  {cols:['rgba(150,0,255,0)','rgba(150,0,255,0.09)','rgba(150,0,255,0)'],yB:0.35,amp:0.08,freq:0.006,sp:1.3},
];
function draw(){
  t+=0.003;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  ctx.fillStyle='#000507';ctx.fillRect(0,0,w,h);
  stars.forEach(s=>{s.a=0.2+Math.abs(Math.sin(t*1.2+s.x*20+s.y*10))*0.8;ctx.beginPath();ctx.arc(s.x*w,s.y*h,s.r,0,Math.PI*2);ctx.fillStyle=`rgba(255,255,255,${s.a})`;ctx.fill();});
  layers.forEach(l=>{
    for(let x=0;x<w;x+=4){
      const wave=Math.sin(x*l.freq+t*l.sp)*h*l.amp+Math.sin(x*l.freq*2+t*l.sp*1.4)*h*l.amp*0.4;
      const yT=h*l.yB+wave,yB=yT+h*0.25;
      let cg=ctx.createLinearGradient(0,yT,0,yB);cg.addColorStop(0,l.cols[0]);cg.addColorStop(0.4,l.cols[1]);cg.addColorStop(1,l.cols[2]);
      ctx.fillStyle=cg;ctx.fillRect(x,yT,5,yB-yT);
    }
  });
  for(let i=0;i<6;i++){
    const sx=w*(0.08+i*0.16)+Math.sin(t*0.4+i)*w*0.04;
    let vg=ctx.createLinearGradient(sx,0,sx+30,h*0.65);const hue=120+i*40;
    vg.addColorStop(0,`hsla(${hue},100%,60%,0)`);vg.addColorStop(0.3,`hsla(${hue},100%,60%,${0.08+Math.sin(t+i)*0.04})`);vg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=vg;ctx.fillRect(sx,0,30,h*0.65);
  }
  let snow=ctx.createLinearGradient(0,h*0.85,0,h);snow.addColorStop(0,'#020d08');snow.addColorStop(1,'#041208');
  ctx.fillStyle=snow;ctx.fillRect(0,h*0.85,w,h*0.15);
  trees.forEach(tr=>{
    const tx=tr.x*w,ty=h*0.85,th=tr.h*h;
    ctx.fillStyle='#010a04';
    ctx.beginPath();ctx.moveTo(tx,ty-th);ctx.lineTo(tx-10,ty-th*0.55);ctx.lineTo(tx-7,ty-th*0.55);ctx.lineTo(tx-14,ty-th*0.2);ctx.lineTo(tx-5,ty-th*0.2);ctx.lineTo(tx-8,ty);ctx.lineTo(tx+8,ty);ctx.lineTo(tx+5,ty-th*0.2);ctx.lineTo(tx+14,ty-th*0.2);ctx.lineTo(tx+7,ty-th*0.55);ctx.lineTo(tx+10,ty-th*0.55);ctx.closePath();ctx.fill();
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"forest": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const leaves=Array.from({length:70},()=>({x:Math.random(),y:Math.random(),vx:(Math.random()-0.5)*0.001,vy:0.0004+Math.random()*0.0009,r:2+Math.random()*5,angle:Math.random()*Math.PI*2,spin:(Math.random()-0.5)*0.04,col:`hsl(${95+Math.random()*55},${45+Math.random()*35}%,${15+Math.random()*18}%)`}));
const rays=Array.from({length:10},(_,i)=>({x:0.05+i*0.11,w:0.015+Math.random()*0.025,phase:Math.random()*Math.PI*2}));
const fireflies=Array.from({length:18},()=>({x:Math.random(),y:0.4+Math.random()*0.5,phase:Math.random()*Math.PI*2,sp:0.0002+Math.random()*0.0004}));
function draw(){
  t+=0.005;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  ctx.fillStyle='#010802';ctx.fillRect(0,0,w,h);
  rays.forEach((r,ri)=>{
    const alpha=0.04+Math.sin(t*0.5+r.phase)*0.025;
    let rg=ctx.createLinearGradient(r.x*w,0,(r.x+0.05)*w,h*0.75);
    rg.addColorStop(0,'rgba(120,255,80,0)');rg.addColorStop(0.1,`rgba(120,255,80,${alpha})`);rg.addColorStop(0.5,`rgba(80,200,60,${alpha*0.6})`);rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.moveTo(r.x*w,0);ctx.lineTo((r.x+r.w)*w,0);ctx.lineTo((r.x+r.w*0.6)*w,h*0.75);ctx.lineTo((r.x-r.w*0.1)*w,h*0.75);ctx.closePath();ctx.fillStyle=rg;ctx.fill();
  });
  for(let x=-20;x<w+20;x+=22){
    ctx.beginPath();ctx.ellipse(x,Math.sin(x*0.04+t*0.3)*h*0.03-8,20+Math.sin(x*0.03)*8,16+Math.cos(x*0.05)*6,0,0,Math.PI*2);
    ctx.fillStyle=`hsl(${105+Math.sin(x*0.02+t)*12},${40+Math.sin(x)*15}%,${8+Math.cos(x*0.03)*3}%)`;ctx.fill();
  }
  for(let x=-10;x<w+10;x+=16){
    ctx.beginPath();ctx.ellipse(x,h*0.15+Math.sin(x*0.03+t*0.2)*h*0.04,14+Math.sin(x*0.04)*5,12,0,0,Math.PI*2);
    ctx.fillStyle=`hsl(${110+Math.cos(x*0.02)*10},${35+Math.sin(x)*12}%,${7+Math.cos(x*0.02)*2}%)`;ctx.fill();
  }
  leaves.forEach(l=>{
    l.x+=l.vx+Math.sin(t*0.4+l.y*5)*0.0002;l.y+=l.vy;l.angle+=l.spin;
    if(l.y>1.05){l.y=-0.05;l.x=Math.random();}
    ctx.save();ctx.translate(l.x*w,l.y*h);ctx.rotate(l.angle);ctx.beginPath();ctx.ellipse(0,0,l.r,l.r*0.5,0,0,Math.PI*2);ctx.fillStyle=l.col;ctx.fill();ctx.restore();
  });
  let floor=ctx.createLinearGradient(0,h*0.72,0,h);floor.addColorStop(0,'rgba(0,8,1,0)');floor.addColorStop(0.3,'rgba(0,15,3,0.85)');floor.addColorStop(1,'#000b02');
  ctx.fillStyle=floor;ctx.fillRect(0,h*0.72,w,h*0.28);
  fireflies.forEach(f=>{
    f.phase+=0.02;f.x+=Math.sin(f.phase*1.3)*f.sp;f.y+=Math.cos(f.phase)*f.sp*0.5;
    if(f.x<0)f.x=1;if(f.x>1)f.x=0;
    const alpha=Math.max(0,Math.sin(f.phase*2)*0.5+0.5);
    let fg=ctx.createRadialGradient(f.x*w,f.y*h,0,f.x*w,f.y*h,8);fg.addColorStop(0,`rgba(200,255,100,${alpha*0.9})`);fg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=fg;ctx.fillRect(f.x*w-8,f.y*h-8,16,16);
  });
  requestAnimationFrame(draw);
}
draw();
})();
""",
"dogs": """
(function(){
const c=document.getElementById('bg');const ctx=c.getContext('2d');
function resize(){c.width=c.offsetWidth;c.height=c.offsetHeight;}resize();
let t=0;
const dogs=Array.from({length:5},(_,i)=>({x:0.1+i*0.18,sp:0.0006+Math.random()*0.0012,d:Math.random()>0.5?1:-1,col:`hsl(${22+Math.random()*28},${45+Math.random()*25}%,${30+Math.random()*20}%)`,s:0.8+Math.random()*0.5,bound:Math.random()*Math.PI*2,bsp:0.08+Math.random()*0.06}));
const grasses=Array.from({length:100},()=>({x:Math.random(),h:0.01+Math.random()*0.025,sway:Math.random()*Math.PI*2}));
const birds=Array.from({length:7},()=>({x:Math.random(),y:0.05+Math.random()*0.2,sp:0.0003+Math.random()*0.0006,flap:Math.random()*Math.PI*2}));
function drawDog(x,y,s,col,d,t){
  ctx.save();ctx.translate(x,y);ctx.scale(d*s,s);
  ctx.beginPath();ctx.ellipse(0,16,18,4,0,0,Math.PI*2);ctx.fillStyle='rgba(0,0,0,0.25)';ctx.fill();
  ctx.beginPath();ctx.ellipse(0,-6,20,9,0,0,Math.PI*2);ctx.fillStyle=col;ctx.fill();
  ctx.beginPath();ctx.ellipse(19,-12,9,8,0.25,0,Math.PI*2);ctx.fillStyle=col;ctx.fill();
  ctx.beginPath();ctx.ellipse(26,-12,5,4,0,0,Math.PI*2);ctx.fillStyle=`hsl(22,40%,22%)`;ctx.fill();
  ctx.beginPath();ctx.arc(28,-11,1.5,0,Math.PI*2);ctx.fillStyle='#111';ctx.fill();
  ctx.save();ctx.translate(20,-18);ctx.rotate(0.3);ctx.beginPath();ctx.ellipse(0,0,4,8,0,0,Math.PI*2);ctx.fillStyle=`hsl(22,40%,20%)`;ctx.fill();ctx.restore();
  ctx.beginPath();ctx.arc(22,-14,2,0,Math.PI*2);ctx.fillStyle='#1a0a00';ctx.fill();
  ctx.save();ctx.translate(-18,-8);ctx.rotate(Math.sin(t*4)*0.5);ctx.beginPath();ctx.moveTo(0,0);ctx.quadraticCurveTo(-8,-15,-4,-22);ctx.lineWidth=4;ctx.strokeStyle=col;ctx.lineCap='round';ctx.stroke();ctx.restore();
  const lk=Math.sin(t*5)*8;
  [[-8,0],[-2,0],[6,0],[12,0]].forEach(([lx],i)=>{
    ctx.beginPath();ctx.moveTo(lx,-1);ctx.lineTo(lx+(i%2===0?lk:-lk),14);ctx.lineWidth=4;ctx.strokeStyle=col;ctx.lineCap='round';ctx.stroke();
  });
  ctx.restore();
}
function draw(){
  t+=0.009;c.width=c.offsetWidth;c.height=c.offsetHeight;
  const w=c.width,h=c.height;
  let sky=ctx.createLinearGradient(0,0,0,h*0.65);sky.addColorStop(0,'#04020a');sky.addColorStop(0.3,'#100408');sky.addColorStop(0.7,'#280a02');sky.addColorStop(1,'#3d1200');
  ctx.fillStyle=sky;ctx.fillRect(0,0,w,h*0.65);
  const sx=w*0.72,sy=h*0.42;
  let sg=ctx.createRadialGradient(sx,sy,12,sx,sy,h*0.45);sg.addColorStop(0,'rgba(255,210,80,0.7)');sg.addColorStop(0.1,'rgba(255,140,0,0.4)');sg.addColorStop(0.3,'rgba(255,60,0,0.15)');sg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=sg;ctx.fillRect(0,0,w,h);
  ctx.beginPath();ctx.arc(sx,sy,20,0,Math.PI*2);ctx.fillStyle='#fff5cc';ctx.fill();
  let grd=ctx.createLinearGradient(0,h*0.62,0,h);grd.addColorStop(0,'#0e0600');grd.addColorStop(0.4,'#090400');grd.addColorStop(1,'#040200');
  ctx.fillStyle=grd;ctx.fillRect(0,h*0.62,w,h*0.38);
  grasses.forEach(g=>{
    const gx=g.x*w,gy=h*0.625;const sway=Math.sin(t*1.5+g.sway)*g.h*h*0.4;
    ctx.beginPath();ctx.moveTo(gx,gy);ctx.lineTo(gx+sway,gy-g.h*h);ctx.strokeStyle=`hsl(${95+Math.sin(gx)*15},40%,16%)`;ctx.lineWidth=1.5;ctx.stroke();
  });
  birds.forEach(b=>{
    b.x+=b.sp;b.flap+=0.12;if(b.x>1.05)b.x=-0.05;
    const bx=b.x*w,by=b.y*h,wing=Math.sin(b.flap)*8;
    ctx.beginPath();ctx.moveTo(bx-12,by+wing);ctx.quadraticCurveTo(bx,by,bx+12,by+wing);ctx.strokeStyle='rgba(0,0,0,0.65)';ctx.lineWidth=1.5;ctx.stroke();
  });
  dogs.forEach(d=>{
    d.x+=d.sp*d.d;if(d.x>1.06)d.x=-0.06;if(d.x<-0.06)d.x=1.06;d.bound+=d.bsp;
    const bounce=Math.abs(Math.sin(d.bound))*12;
    drawDog(d.x*w,h*0.635-bounce*d.s,d.s,d.col,d.d,t);
  });
  requestAnimationFrame(draw);
}
draw();
})();
"""
}

# ── NEW TAB PAGE ──────────────────────────────────────────────────────────────
QUICK_SITES = [
    ("🔍","Google","https://google.com"),("📰","Reddit","https://reddit.com"),
    ("▶️","YouTube","https://youtube.com"),("💻","GitHub","https://github.com"),
    ("📖","Wikipedia","https://en.wikipedia.org"),("🎵","Spotify","https://open.spotify.com"),
    ("📊","Finance","https://finance.yahoo.com"),("🌤","Weather","https://weather.com"),
]

def render_new_tab():
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
    script = CANVAS_SCRIPTS[theme["key"]]
    quick_cards = "".join(
        f'<div class="qcard" onclick="goTo(\'{url}\')">'
        f'<div class="qicon">{icon}</div>'
        f'<div class="qlabel">{name}</div></div>'
        for icon, name, url in QUICK_SITES
    )
    html = f"""<!DOCTYPE html><html><head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:{BG};overflow:hidden;width:100%;height:100vh;font-family:'Plus Jakarta Sans',sans-serif;}}
#bg{{position:fixed;top:0;left:0;width:100%;height:100%;}}
.ui{{position:fixed;top:0;left:0;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;pointer-events:none;}}
.header{{text-align:center;}}
.eyebrow{{font-size:11px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:{ACC};opacity:0.65;margin-bottom:10px;font-family:'JetBrains Mono',monospace;}}
.greeting{{font-size:36px;font-weight:700;color:#e8eaf0;letter-spacing:-0.5px;line-height:1.15;}}
.greeting em{{color:{ACC};font-style:normal;}}
.datetime{{font-size:13px;color:rgba(232,234,240,0.35);margin-top:8px;font-weight:400;}}
.badge{{display:inline-flex;align-items:center;gap:8px;margin-top:14px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:5px 16px;font-size:11.5px;font-weight:600;letter-spacing:1.5px;color:{ACC};text-transform:uppercase;backdrop-filter:blur(12px);}}
.qgrid{{display:grid;grid-template-columns:repeat(8,72px);gap:8px;pointer-events:all;}}
.qcard{{display:flex;flex-direction:column;align-items:center;gap:5px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:14px 8px;cursor:pointer;transition:all 0.18s cubic-bezier(.34,1.56,.64,1);backdrop-filter:blur(16px);}}
.qcard:hover{{background:rgba(255,255,255,0.1);border-color:rgba(255,255,255,0.18);transform:translateY(-4px) scale(1.04);box-shadow:0 12px 32px rgba(0,0,0,0.5),0 0 0 1px {ACC}33;}}
.qcard:active{{transform:translateY(-1px) scale(1);}}
.qicon{{font-size:22px;}}
.qlabel{{font-size:10px;font-weight:600;color:rgba(232,234,240,0.45);letter-spacing:0.2px;white-space:nowrap;}}
.vignette{{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;background:radial-gradient(ellipse at 50% 50%,transparent 40%,rgba(0,0,0,0.6) 100%);}}
.hint{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);font-size:10px;color:rgba(232,234,240,0.2);letter-spacing:3px;font-family:'JetBrains Mono',monospace;pointer-events:none;text-transform:uppercase;}}
</style>
</head><body>
<canvas id="bg"></canvas>
<div class="vignette"></div>
<div class="ui">
  <div class="header">
    <div class="eyebrow">Nexus Browser · Neural Edition</div>
    <div class="greeting">{greeting},<br><em>Explorer.</em></div>
    <div class="datetime">{datetime.now().strftime("%A, %B %d, %Y  ·  %H:%M")}</div>
    <div class="badge">{theme['emoji']}&nbsp; {theme['name']}</div>
  </div>
  <div class="qgrid">{quick_cards}</div>
</div>
<div class="hint">Type a URL or use the search bar above</div>
<script>
function goTo(url){{
  var base = window.top.location.href.split('?')[0];
  window.top.location.href = base + '?goto=' + encodeURIComponent(url);
}}
{script}
</script>
</body></html>"""
    components.html(html, height=520, scrolling=False)


def render_viewport():
    url = st.session_state.current_url
    html = f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:{BG};height:520px;overflow:hidden;}}
.wrap{{width:100%;height:520px;position:relative;}}
iframe{{width:100%;height:520px;border:none;display:block;background:#fff;}}
.progress{{position:absolute;top:0;left:0;right:0;height:2.5px;z-index:10;
  background:linear-gradient(90deg,{ACC},{ACC2});
  animation:prog 1.2s cubic-bezier(.4,0,.2,1) forwards;}}
@keyframes prog{{from{{width:0;opacity:1;}}to{{width:100%;opacity:0;}}}}
.corner{{position:absolute;width:10px;height:10px;z-index:10;}}
.tl{{top:0;left:0;border-top:2px solid {ACC};border-left:2px solid {ACC};}}
.tr{{top:0;right:0;border-top:2px solid {ACC};border-right:2px solid {ACC};}}
.bl{{bottom:0;left:0;border-bottom:2px solid {ACC};border-left:2px solid {ACC};}}
.br{{bottom:0;right:0;border-bottom:2px solid {ACC};border-right:2px solid {ACC};}}
</style></head><body>
<div class="wrap">
  <div class="progress"></div>
  <div class="corner tl"></div><div class="corner tr"></div>
  <div class="corner bl"></div><div class="corner br"></div>
  <iframe src="{url}"
    sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-presentation"
    loading="lazy" referrerpolicy="no-referrer">
  </iframe>
</div></body></html>"""
    components.html(html, height=524, scrolling=False)


# ── LAYOUT: optional sidebar + content ───────────────────────────────────────
if st.session_state.show_sidebar:
    sidebar_col, content_col = st.columns([1.6, 8.4])
    with sidebar_col:
        bkm_html = "".join(
            f'<div class="si"><span>🔖</span><span class="st">{b["domain"]}</span></div>'
            for b in st.session_state.bookmarks[:12]
        ) or '<div class="se">No bookmarks</div>'
        hist_html = "".join(
            f'<div class="si"><span class="stm">{h["time"]}</span><span class="st">{h["domain"][:18]}</span></div>'
            for h in st.session_state.history[:15]
        ) or '<div class="se">No history</div>'
        st.markdown(f"""
        <div style="background:rgba(10,11,18,0.97);border-right:1px solid rgba(255,255,255,0.07);
          height:550px;overflow-y:auto;padding:12px 8px;font-family:'Plus Jakarta Sans',sans-serif;">
          <div class="sh">🔖 Bookmarks <span class="sc">{len(st.session_state.bookmarks)}</span></div>
          <div style="margin-bottom:16px;">{bkm_html}</div>
          <div class="sh">🕐 History <span class="sc">{len(st.session_state.history)}</span></div>
          <div style="margin-bottom:16px;">{hist_html}</div>
          <div class="sh">⚙️ Session</div>
          <div class="si"><span>Tabs</span><b style="color:#e8eaf0">{len(st.session_state.tabs)}</b></div>
          <div class="si"><span>Mode</span><b style="color:{'#cc99ff' if st.session_state.incognito else '#22cc66'}">{'Incognito' if st.session_state.incognito else 'Normal'}</b></div>
          <div class="si"><span>Theme</span><b style="color:{ACC}">{theme['emoji']} {theme['name']}</b></div>
          <div class="si"><span>Storage</span><b style="color:#ffaa44">Memory</b></div>
        </div>
        <style>
        .sh{{font-size:10.5px;font-weight:700;letter-spacing:1px;color:{ACC};text-transform:uppercase;
          padding:6px 8px 6px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:6px;
          display:flex;align-items:center;justify-content:space-between;}}
        .sc{{background:rgba(255,255,255,0.08);border-radius:10px;padding:1px 7px;font-size:10px;color:rgba(232,234,240,0.5);}}
        .si{{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:5px 8px;
          border-radius:6px;font-size:11.5px;color:rgba(232,234,240,0.55);transition:background 0.1s;}}
        .si:hover{{background:rgba(255,255,255,0.05);}}
        .st{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;text-align:right;color:rgba(232,234,240,0.7);}}
        .stm{{font-size:10px;color:{ACC};font-weight:600;flex-shrink:0;font-family:'JetBrains Mono',monospace;}}
        .se{{color:rgba(232,234,240,0.2);font-size:11px;padding:8px;text-align:center;}}
        </style>
        """, unsafe_allow_html=True)
    with content_col:
        if not st.session_state.current_url: render_new_tab()
        else: render_viewport()
else:
    if not st.session_state.current_url: render_new_tab()
    else: render_viewport()

# ── STATUS BAR ────────────────────────────────────────────────────────────────
url_disp = st.session_state.current_url
if len(url_disp) > 80: url_disp = url_disp[:80] + "…"
sec = "🔒 Secure" if st.session_state.current_url.startswith("https") else ("🌐 New Tab" if not st.session_state.current_url else "⚠️ Not Secure")
mode = "👤 Incognito — no history saved" if st.session_state.incognito else "💾 Session only · All data clears on close"

st.markdown(f"""
<div style="position:fixed;bottom:0;left:0;right:0;height:22px;
  background:rgba(6,7,12,0.97);border-top:1px solid rgba(255,255,255,0.06);
  display:flex;align-items:center;justify-content:space-between;padding:0 16px;
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(232,234,240,0.3);z-index:999;backdrop-filter:blur(20px);">
  <span style="color:{ACC};opacity:0.8;white-space:nowrap;">{sec}</span>
  <span style="flex:1;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:0 24px;">
    {url_disp or "Nexus Browser · New Tab"}
  </span>
  <span style="white-space:nowrap;">{mode}</span>
</div>
""", unsafe_allow_html=True)