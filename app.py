"""
Nucos Media Dashboard — Main app
Upload 1 xlsx với 5 sheets: Media Plan, Facebook Raw data, Google Raw data, Google KW Raw data, Messenger Sale Data
"""
import streamlit as st
from parse_data import parse_all
from helpers import CSS
from tabs import tab_overview, tab_branding, tab_messenger, tab_cpas, tab_google

st.set_page_config(page_title="Nucos Media Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Nucos × Miss World VN 2026 — Media Dashboard")
st.markdown("---")

# ── Upload ────────────────────────────────────────────────────────────────────
with st.expander("📂 Upload File dữ liệu (.xlsx)", expanded=True):
    uploaded = st.file_uploader(
        "Upload 1 file xlsx với các sheets: Media Plan, Facebook Raw data, Google Raw data, Google KW Raw data, Messenger Sale Data",
        type=['xlsx'], label_visibility='collapsed'
    )

if not uploaded:
    st.info("Upload file xlsx để bắt đầu.")
    st.stop()

# ── Parse ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(b):
    return parse_all(b)

col_up, col_btn = st.columns([6, 1])
with col_btn:
    if st.button("🔄 Clear cache"):
        st.cache_data.clear()
        st.rerun()

with st.spinner("Đang xử lý dữ liệu..."):
    data = load_data(uploaded.read())

plan       = data.get('plan', {})
br         = data.get('branding', {})
msg        = data.get('messenger', {})
cpas       = data.get('cpas', {})
gg         = data.get('google', {})
crm        = data.get('crm', {})
ov         = data.get('overall', {})
date_range = data.get('date_range', {})
cpas_plan  = data.get('cpas_plan', {})

plan_eng = plan.get('engage', {}); plan_vid = plan.get('video', {})
plan_rch = plan.get('reach', {}); plan_msg = plan.get('messenger', {})
plan_gg_gdn    = plan.get('google_gdn', {})
plan_gg_search = plan.get('google_search', {})

# ── Debug panel ───────────────────────────────────────────────────────────────
with st.expander("🔧 Debug — Plan values (click để xem)", expanded=False):
    st.json({
        "budget_breakdown": plan.get('_debug_budget', {}),
        "cpas_plan":        cpas_plan,
        "plan_gg_gdn":      plan_gg_gdn,
        "plan_gg_search":   plan_gg_search,
        "google_totals": {
            "total_clicks": gg.get('total_clicks', 'N/A'),
            "total_imp":    gg.get('total_imp',    'N/A'),
            "google_spend": gg.get('google_spend', 'N/A'),
        },
        "sheets_in_file":   data.get('_sheets', []),
    })

unclassified = data.get('unclassified', [])
if unclassified:
    with st.expander(f"⚠️ {len(unclassified)} campaign chưa classify — click để xem tên", expanded=False):
        st.caption("Paste tên vào đây để thêm keyword vào classify_campaign() trong parse_data.py.")
        for name in unclassified:
            st.code(name)

# ── Tabs ──────────────────────────────────────────────────────────────────────
t_ov, t_brand, t_msg_tab, t_cpas, t_gg = st.tabs([
    "📊 Tổng quan", "📢 Branding (FB)", "💬 Conversion (Messenger)", "🛒 CPAS", "🔍 Google"
])

with t_ov:
    tab_overview.render(plan, br, msg, cpas, gg, crm, ov, date_range,
                        cpas_plan, plan_gg_gdn, plan_gg_search)

with t_brand:
    tab_branding.render(br, plan_eng, plan_vid, plan_rch)

with t_msg_tab:
    tab_messenger.render(msg, crm, plan_msg, date_range)

with t_cpas:
    tab_cpas.render(cpas)

with t_gg:
    tab_google.render(gg)
