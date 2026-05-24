"""helpers.py — Shared UI components for Nucos Dashboard."""
import json
import os
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go

_INSIGHT_FILE = Path(__file__).parent / 'insight_notes.json'


def _load_insights():
    try:
        return json.loads(_INSIGHT_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_insight(tab_key, text):
    data = _load_insights()
    data[tab_key] = text
    _INSIGHT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _delete_insight(tab_key):
    data = _load_insights()
    data.pop(tab_key, None)
    _INSIGHT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _get_pin():
    try:
        return st.secrets.get('INSIGHT_PIN', '1234')
    except Exception:
        return os.environ.get('INSIGHT_PIN', '1234')

C = dict(accent='#6c63ff', green='#22c55e', yellow='#f59e0b',
         pink='#ec4899', blue='#3b82f6', red='#ef4444', purple='#a855f7')

CSS = """
<style>
  .stApp { background-color: #0f1117; color: #e2e8f0; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
  /* kpi-card dùng flex column — grid bên ngoài sẽ equalize height */
  .kpi-card { background:#181c27; border:1px solid #2a2f45; border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; }
  /* kpi-grid: render N cards cùng row, grid tự equalize height */
  .kpi-grid { display:grid; gap:12px; align-items:stretch; margin-bottom:16px; }
  .kpi-label { color:#8892a4; font-size:11px; text-transform:uppercase; letter-spacing:.6px; margin-bottom:6px; }
  .kpi-value { font-size:22px; font-weight:700; }
  .kpi-sub   { color:#8892a4; font-size:12px; margin-top:3px; }
  .prog-bg   { background:#1e2333; border-radius:4px; height:6px; overflow:hidden; margin-top:6px; }
  .prog-fill { height:100%; border-radius:4px; }
  .kpi-accent { border-top:3px solid #6c63ff; } .kpi-accent .kpi-value { color:#6c63ff; }
  .kpi-green  { border-top:3px solid #22c55e; } .kpi-green  .kpi-value { color:#22c55e; }
  .kpi-blue   { border-top:3px solid #3b82f6; } .kpi-blue   .kpi-value { color:#3b82f6; }
  .kpi-yellow { border-top:3px solid #f59e0b; } .kpi-yellow .kpi-value { color:#f59e0b; }
  .kpi-pink   { border-top:3px solid #ec4899; } .kpi-pink   .kpi-value { color:#ec4899; }
  .kpi-purple { border-top:3px solid #a855f7; } .kpi-purple .kpi-value { color:#a855f7; }
  .stTabs [data-baseweb="tab-list"] { background:#181c27; border-radius:8px; padding:3px; gap:2px; }
  .stTabs [data-baseweb="tab"] { color:#8892a4; border-radius:6px; }
  .stTabs [aria-selected="true"] { background:#2a2f45 !important; color:#6c63ff !important; }
  #MainMenu { visibility:hidden; } footer { visibility:hidden; }
</style>
"""


def kpi(label, value, sub="", color="accent", progress=None):
    prog = ""
    if progress is not None:
        pct = min(progress * 100, 100)
        prog = f'<div class="prog-bg" style="margin-top:6px"><div class="prog-fill" style="width:{pct:.1f}%;background:{C.get(color, C["accent"])}"></div></div>'
    sub_h = f'<div class="kpi-sub" style="margin-top:3px;line-height:1.4">{sub}</div>' if sub else ''
    st.markdown(f'<div class="kpi-card kpi-{color}"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value" style="margin-top:4px">{value}</div>{sub_h}{prog}</div>',
                unsafe_allow_html=True)


def badge(text, color='green'):
    cfg = {'green': ('#22c55e', 'rgba(34,197,94,.15)'), 'yellow': ('#f59e0b', 'rgba(245,158,11,.15)'),
           'red': ('#ef4444', 'rgba(239,68,68,.15)'), 'blue': ('#3b82f6', 'rgba(59,130,246,.15)')}
    tc, bg = cfg.get(color, cfg['blue'])
    return f'<span style="background:{bg};color:{tc};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600">{text}</span>'


def pct_badge(actual, plan, invert=False):
    if not plan:
        return badge('—', 'blue')
    pct = actual / plan * 100
    color = ('green' if pct <= 110 else 'red') if invert else ('green' if pct >= 90 else 'red')
    return badge(f'{pct:.0f}%', color)


def _prog_html(progress, color, plan_label=''):
    """
    Wrapper div (margin-top:auto) chứa label row + progress bar.
    Tách wrapper khỏi .prog-bg để padding không bị overflow:hidden clip.
    """
    if progress is None:
        return ''
    pct = min(progress * 100, 100)
    fill_c = C.get(color, C['accent'])
    clr = '#22c55e' if pct >= 90 else ('#f59e0b' if pct >= 50 else '#ef4444')
    label_row = (
        f'<div style="display:flex;justify-content:space-between;'
        f'margin-bottom:3px;font-size:10px;line-height:1.2">'
        f'<span style="color:#555">{plan_label}</span>'
        f'<span style="color:{clr};font-weight:600">{pct:.0f}%</span>'
        f'</div>'
    ) if plan_label else (
        f'<div style="text-align:right;margin-bottom:3px;font-size:10px;'
        f'color:{clr};font-weight:600">{pct:.0f}%</div>'
    )
    return (
        f'<div style="margin-top:auto;padding-top:6px">'   # wrapper: pushes to bottom, không bị clip
        f'{label_row}'
        f'<div class="prog-bg"><div class="prog-fill" style="width:{pct:.1f}%;background:{fill_c}"></div></div>'
        f'</div>'
    )


def kpi_html(label, value, sub='', color='accent', progress=None, plan_label=''):
    """Card HTML string — dùng trong kpi_grid()."""
    sub_h = f'<div class="kpi-sub" style="margin-top:3px;line-height:1.4">{sub}</div>' if sub else ''
    return (f'<div class="kpi-card kpi-{color}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="margin-top:4px">{value}</div>'
            f'{sub_h}{_prog_html(progress, color, plan_label)}</div>')


def kpi2_html(label, v1, v1_sub, v2, v2_sub, color='accent',
              progress=None, plan_label='', progress2=None, plan_label2=''):
    """Card 2-metric HTML — 2 cột ngang, mỗi cột có progress bar riêng."""
    s1 = f'<div class="kpi-sub" style="margin-top:3px;line-height:1.3">{v1_sub}</div>' if v1_sub else ''
    s2 = f'<div class="kpi-sub" style="margin-top:3px;line-height:1.3">{v2_sub}</div>' if v2_sub else ''
    p1 = _prog_html(progress,  color, plan_label)
    p2 = _prog_html(progress2, color, plan_label2)
    return (
        f'<div class="kpi-card kpi-{color}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div style="display:flex;flex:1;margin-top:6px">'
        f'  <div style="flex:1;min-width:0;padding-right:10px;display:flex;flex-direction:column">'
        f'    <div class="kpi-value" style="font-size:18px">{v1}</div>'
        f'    {s1}{p1}'
        f'  </div>'
        f'  <div style="flex:1;min-width:0;padding-left:10px;border-left:1px solid #2a2f45;display:flex;flex-direction:column">'
        f'    <div class="kpi-value" style="font-size:18px;color:#8892a4">{v2}</div>'
        f'    {s2}{p2}'
        f'  </div>'
        f'</div>'
        f'</div>'
    )


def kpi_grid(*card_htmls, cols=None):
    """Render list card HTML trong CSS grid — tự equalize height."""
    n = cols or len(card_htmls)
    items = ''.join(card_htmls)
    st.markdown(
        f'<div class="kpi-grid" style="grid-template-columns:repeat({n},1fr)">{items}</div>',
        unsafe_allow_html=True
    )


def insight(html, color='accent'):
    cfg = {'accent': ('#6c63ff', 'rgba(108,99,255,.08)'),
           'green':  ('#22c55e', 'rgba(34,197,94,.08)'),
           'yellow': ('#f59e0b', 'rgba(245,158,11,.08)')}
    bc, bg = cfg.get(color, cfg['accent'])
    st.markdown(f'<div style="background:{bg};border-left:3px solid {bc};border-radius:0 8px 8px 0;'
                f'padding:12px 16px;margin-top:14px;font-size:13px;color:#8892a4;line-height:1.6">{html}</div>',
                unsafe_allow_html=True)


def section(title, dot='accent'):
    dot_c = C.get(dot, C['accent'])
    st.markdown(f'<div style="font-size:14px;font-weight:600;color:#e2e8f0;margin:18px 0 10px;'
                f'display:flex;align-items:center;gap:8px">'
                f'<span style="width:8px;height:8px;border-radius:50%;background:{dot_c};display:inline-block">'
                f'</span>{title}</div>', unsafe_allow_html=True)


def rank_badge(n):
    if n == 1:
        return ('<span style="background:rgba(245,158,11,.2);color:#f59e0b;width:24px;height:24px;'
                'border-radius:50%;display:inline-flex;align-items:center;justify-content:center;'
                'font-size:11px;font-weight:700">1</span>')
    return (f'<span style="background:#1e2333;color:#8892a4;width:24px;height:24px;'
            f'border-radius:50%;display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:11px">{n}</span>')


def html_table(headers, rows, aligns=None):
    if aligns is None:
        aligns = ['left'] + ['right'] * (len(headers) - 1)
    ths = ''.join(f'<th style="color:#8892a4;font-size:11px;text-transform:uppercase;padding:8px 10px;'
                  f'text-align:{aligns[i]};border-bottom:1px solid #2a2f45">{h}</th>'
                  for i, h in enumerate(headers))
    trs = ''.join(
        '<tr>' + ''.join(
            f'<td style="padding:9px 10px;text-align:{aligns[i]};border-bottom:1px solid rgba(42,47,69,.5)">{cell}</td>'
            for i, cell in enumerate(row)
        ) + '</tr>'
        for row in rows
    )
    st.markdown(f'<table style="width:100%;border-collapse:collapse;font-size:13px">'
                f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>',
                unsafe_allow_html=True)


def pva_table(rows):
    """rows = [(label, plan_val, actual_val, fmt_fn, badge_html)]"""
    ths = ''.join(
        f'<th style="color:#8892a4;font-size:11px;text-transform:uppercase;padding:8px 10px;'
        f'text-align:{a};border-bottom:1px solid #2a2f45">{h}</th>'
        for h, a in [('Metric', 'left'), ('Plan', 'right'), ('Actual', 'right'), ('% vs Plan', 'center')]
    )
    trs = ''
    for label, pv, av, fmt_fn, bdg in rows:
        trs += (f'<tr>'
                f'<td style="padding:9px 10px;border-bottom:1px solid rgba(42,47,69,.5);font-weight:500">{label}</td>'
                f'<td style="padding:9px 10px;border-bottom:1px solid rgba(42,47,69,.5);text-align:right;color:#555">{fmt_fn(pv) if pv else "—"}</td>'
                f'<td style="padding:9px 10px;border-bottom:1px solid rgba(42,47,69,.5);text-align:right;color:#6c63ff;font-weight:600">{fmt_fn(av)}</td>'
                f'<td style="padding:9px 10px;border-bottom:1px solid rgba(42,47,69,.5);text-align:center">{bdg}</td>'
                f'</tr>')
    st.markdown(f'<table style="width:100%;border-collapse:collapse;font-size:13px">'
                f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>',
                unsafe_allow_html=True)


def donut(labels, values, colors_list):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors_list, line=dict(color='#181c27', width=3)),
        hovertemplate='%{label}<br>%{value:,.0f}₫ (%{percent})<extra></extra>',
    ))
    fig.update_layout(height=240, showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=10, r=10, t=10, b=10), font=dict(color='#e2e8f0'))
    return fig


def chart_legend(labels, value_strs, colors_list):
    items = ''.join(
        f'<span style="display:inline-flex;align-items:center;gap:5px">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{c}"></span>'
        f'{l} · {v}</span>'
        for l, v, c in zip(labels, value_strs, colors_list)
    )
    st.markdown(f'<div style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center;'
                f'font-size:12px;color:#8892a4;margin-top:10px">{items}</div>', unsafe_allow_html=True)


def kpi2(label, v1, v1_sub, v2, v2_sub, color="accent", progress=None):
    """Card với 2 chỉ số — fixed height 158px cùng kpi()."""
    prog = ""
    if progress is not None:
        pct = min(progress * 100, 100)
        prog = f'<div class="prog-bg" style="margin-top:6px"><div class="prog-fill" style="width:{pct:.1f}%;background:{C.get(color, C["accent"])}"></div></div>'
    s1 = f'<div class="kpi-sub" style="margin:1px 0 4px;line-height:1.3">{v1_sub}</div>' if v1_sub else '<div style="margin-bottom:4px"></div>'
    s2 = f'<div class="kpi-sub" style="margin-top:1px;line-height:1.3">{v2_sub}</div>' if v2_sub else ''
    st.markdown(
        f'<div class="kpi-card kpi-{color}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value" style="font-size:17px;margin-top:3px">{v1}</div>'
        f'{s1}'
        f'<div class="kpi-value" style="font-size:17px;color:#8892a4">{v2}</div>'
        f'{s2}{prog}</div>',
        unsafe_allow_html=True
    )


def ad_name_cell(name, short):
    return (f'<span title="{name}" style="max-width:200px;white-space:nowrap;overflow:hidden;'
            f'text-overflow:ellipsis;display:block">{short}</span>')


def date_range_banner(dr):
    if not dr or not dr.get('start'):
        return
    s = dr['start'].strftime('%d/%m/%Y')
    e = dr['end'].strftime('%d/%m/%Y')
    days = dr.get('days', '—')
    st.markdown(
        f'<div style="color:#8892a4;font-size:13px;margin-bottom:16px">'
        f'📅 Dữ liệu: <strong style="color:#e2e8f0">{s} – {e}</strong> · {days} ngày</div>',
        unsafe_allow_html=True
    )


def editable_insight(tab_key, auto_text, color='accent'):
    """
    Insight panel có thể chỉnh sửa với PIN protection.
    auto_text: plain text (newlines ok) — mặc định auto-generated.
    Text tùy chỉnh lưu trong insight_notes.json, override auto khi tồn tại.
    """
    dot_c = C.get(color, C['accent'])
    cfg = {
        'accent': ('#6c63ff', 'rgba(108,99,255,.10)'),
        'green':  ('#22c55e', 'rgba(34,197,94,.10)'),
        'yellow': ('#f59e0b', 'rgba(245,158,11,.10)'),
        'blue':   ('#3b82f6', 'rgba(59,130,246,.10)'),
        'pink':   ('#ec4899', 'rgba(236,72,153,.10)'),
    }
    bc, bg = cfg.get(color, cfg['accent'])

    edit_key   = f'_ie_editing_{tab_key}'
    pin_ok_key = f'_ie_pinok_{tab_key}'

    saved    = _load_insights().get(tab_key)
    cur_text = saved if saved else auto_text
    is_custom = bool(saved)

    # Section header
    st.markdown(
        f'<div style="font-size:14px;font-weight:600;color:#e2e8f0;margin:28px 0 10px;'
        f'display:flex;align-items:center;gap:8px">'
        f'<span style="width:8px;height:8px;border-radius:50%;background:{dot_c};'
        f'display:inline-block"></span>📝 Nhận xét tổng hợp</div>',
        unsafe_allow_html=True
    )

    # Render insight box (plain text, newlines → <br>)
    display_text = cur_text if cur_text else '_(Chưa có nhận xét — click Edit để thêm)_'
    escaped = (display_text
               .replace('&', '&amp;')
               .replace('<', '&lt;')
               .replace('>', '&gt;')
               .replace('\n', '<br>'))
    st.markdown(
        f'<div style="background:{bg};border-left:3px solid {bc};border-radius:0 8px 8px 0;'
        f'padding:14px 18px;font-size:13px;color:#c4ccd8;line-height:1.8">{escaped}</div>',
        unsafe_allow_html=True
    )

    # Source label + edit button (cùng hàng, nút rõ hơn)
    lbl = '✏️ Đã chỉnh sửa thủ công' if is_custom else '🤖 Auto-generated'
    col_src, col_btn = st.columns([5, 1])
    with col_src:
        st.caption(lbl)
    with col_btn:
        if st.button('✏️ Sửa nhận xét', key=f'ie_open_{tab_key}', use_container_width=True):
            st.session_state[edit_key]   = True
            st.session_state[pin_ok_key] = False
            st.rerun()

    if not st.session_state.get(edit_key):
        return

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    if not st.session_state.get(pin_ok_key):
        # PIN verification
        c_lbl, c_pin, c_ok, c_x = st.columns([1, 4, 1, 1])
        with c_lbl:
            st.markdown('<div style="padding-top:8px;font-size:13px;color:#8892a4">🔑 PIN:</div>',
                        unsafe_allow_html=True)
        with c_pin:
            pin_val = st.text_input('', placeholder='Nhập PIN...', type='password',
                                    key=f'ie_pin_{tab_key}', label_visibility='collapsed')
        with c_ok:
            if st.button('✓ OK', key=f'ie_pin_ok_{tab_key}'):
                if pin_val == _get_pin():
                    st.session_state[pin_ok_key] = True
                    st.rerun()
                else:
                    st.error('PIN không đúng.')
        with c_x:
            if st.button('✕', key=f'ie_pin_cancel_{tab_key}'):
                st.session_state[edit_key] = False
                st.rerun()
        return

    # Authenticated — edit mode
    new_text = st.text_area('', value=cur_text, height=150,
                             key=f'ie_ta_{tab_key}', label_visibility='collapsed')
    c_save, c_reset, c_cancel = st.columns([1, 2, 4])
    with c_save:
        if st.button('💾 Lưu', key=f'ie_save_{tab_key}'):
            _save_insight(tab_key, new_text)
            st.session_state[edit_key]   = False
            st.session_state[pin_ok_key] = False
            st.rerun()
    with c_reset:
        if st.button('↩️ Reset về auto', key=f'ie_reset_{tab_key}'):
            _delete_insight(tab_key)
            st.session_state[edit_key]   = False
            st.session_state[pin_ok_key] = False
            st.rerun()
    with c_cancel:
        if st.button('✕ Hủy', key=f'ie_cancel_{tab_key}'):
            st.session_state[edit_key]   = False
            st.session_state[pin_ok_key] = False
            st.rerun()
