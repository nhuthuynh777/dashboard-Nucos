"""
Nucos Media Dashboard — Main app
Upload 1 xlsx với 5 sheets: Media Plan, Facebook Raw data, Google Raw data, Google KW Raw data, Messenger Sale Data
"""
import streamlit as st
from parse_data import parse_all
from helpers import CSS, drive_download_file, drive_upload_file, _get_pin
from tabs import tab_overview, tab_branding, tab_messenger, tab_cpas, tab_google

st.set_page_config(page_title="Nucos Monthly Campaign Report - Media Dashboard", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Nucos Monthly Campaign Report - Media Dashboard")
st.markdown("---")

# ── Auto-load from Google Drive ───────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_from_drive():
    return drive_download_file()

drive_bytes = load_from_drive()
data_bytes  = drive_bytes  # None nếu chưa cấu hình Drive

# ── Upload panel (PIN protected) ──────────────────────────────────────────────
exp_title = "📂 Cập nhật dữ liệu (.xlsx)" if drive_bytes else "📂 Upload File dữ liệu (.xlsx)"
with st.expander(exp_title, expanded=not bool(drive_bytes)):
    if drive_bytes:
        st.success("☁️ Dữ liệu đã được tải từ cloud. Upload file mới để cập nhật số.")

    if not st.session_state.get('_upload_auth'):
        c_pin, c_btn, c_hint = st.columns([3, 1, 4])
        with c_pin:
            pin_input = st.text_input('', placeholder='Nhập PIN để upload...', type='password',
                                      key='_upload_pin_input', label_visibility='collapsed')
        with c_btn:
            if st.button('🔓 Xác nhận', key='_upload_pin_btn', use_container_width=True):
                if pin_input == _get_pin():
                    st.session_state['_upload_auth'] = True
                    st.rerun()
                else:
                    st.error('PIN không đúng.')
        with c_hint:
            st.caption('🔒 Chỉ owner mới có thể upload dữ liệu mới.')
    else:
        col_file, col_lock = st.columns([8, 1])
        with col_file:
            new_file = st.file_uploader(
                "Upload 1 file xlsx với các sheets: Media Plan, Facebook Raw data, Google Raw data, Google KW Raw data, Messenger Sale Data",
                type=['xlsx'], label_visibility='collapsed'
            )
        with col_lock:
            if st.button('🔒 Lock', key='_upload_lock', use_container_width=True, help='Khoá lại upload'):
                st.session_state['_upload_auth'] = False
                st.rerun()
        if new_file:
            raw = new_file.read()
            with st.spinner("Đang lưu lên Drive..."):
                ok = drive_upload_file(raw)
            if ok:
                st.success("✅ Đã lưu lên Drive! Mọi người sẽ thấy số mới khi refresh.")
            else:
                st.warning("⚠️ Chưa cấu hình Drive secrets. Dữ liệu chỉ có trong session này.")
            st.cache_data.clear()
            data_bytes = raw

if not data_bytes:
    if st.session_state.get('_upload_auth'):
        st.info("Upload file xlsx để bắt đầu.")
    else:
        st.info("🔒 Dashboard đang khoá. Nhập PIN phía trên để upload dữ liệu.")
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
    data = load_data(data_bytes)

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
