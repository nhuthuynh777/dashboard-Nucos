"""Tab 1 — Tổng quan"""
import streamlit as st
from helpers import kpi, kpi2, kpi_html, kpi2_html, kpi_grid, section, insight, html_table, donut, chart_legend, date_range_banner, pct_badge, badge, editable_insight
from parse_data import fmt_vnd, fmt_num


def _gen_insight(total_sp, total_plan, total_imp, plan_imp,
                 total_eng, plan_eng_kpi, total_vid, plan_vid_kpi,
                 total_msg, plan_msg_kpi, cpas_gmv, cpas_rev_plan,
                 cpas_roas, actual_gg_clk, plan_gg_total_clk,
                 vid_cpv, plan_cpv):
    from parse_data import fmt_vnd, fmt_num
    lines = []
    pace = total_sp / total_plan * 100 if total_plan else 0
    lines.append(f"Budget pace: {pace:.0f}% ({fmt_vnd(total_sp)} / {fmt_vnd(total_plan)} plan)")

    kpis = []
    if plan_eng_kpi:  kpis.append(('Engagement', total_eng, plan_eng_kpi))
    if plan_vid_kpi:  kpis.append(('Video Views', total_vid, plan_vid_kpi))
    if plan_msg_kpi:  kpis.append(('Messenger', total_msg, plan_msg_kpi))
    if plan_gg_total_clk: kpis.append(('Google Clicks', actual_gg_clk, plan_gg_total_clk))
    if kpis:
        best  = max(kpis, key=lambda x: x[1] / x[2])
        worst = min(kpis, key=lambda x: x[1] / x[2])
        lines.append(
            f"KPI tốt nhất: {best[0]} ({best[1]/best[2]*100:.0f}% vs plan).  "
            f"Cần theo dõi: {worst[0]} ({worst[1]/worst[2]*100:.0f}% vs plan)."
        )

    if cpas_roas:
        lines.append(f"CPAS ROAS: {cpas_roas:.2f}x" +
                     (f" vs plan {cpas_rev_plan / (total_sp * 0.22):.1f}x." if cpas_rev_plan else "."))
    if vid_cpv and plan_cpv:
        r = plan_cpv / vid_cpv
        if r > 1:
            lines.append(f"Video CPV {fmt_vnd(vid_cpv)} — rẻ hơn plan {r:.1f}x → hiệu quả cao, nên scale.")
        else:
            lines.append(f"Video CPV {fmt_vnd(vid_cpv)} vs plan {fmt_vnd(plan_cpv)} — cần review creative.")
    return '\n'.join(lines)


def _plan_sub(actual, plan, fmt_fn):
    """Tạo sub-text: Plan: X · Y% với màu."""
    if not plan:
        return '<span style="color:#555">Plan: —</span>'
    pct = actual / plan * 100
    clr = "#22c55e" if pct >= 90 else ("#f59e0b" if pct >= 50 else "#ef4444")
    return (f'<span style="color:#555">Plan: {fmt_fn(plan)}</span> · '
            f'<span style="color:{clr};font-weight:600">{pct:.0f}%</span>')


def render(plan, br, msg, cpas, gg, crm, ov, date_range,
           cpas_plan=None, plan_gg_gdn=None, plan_gg_search=None):
    eng = br.get('engage', {}); vid = br.get('video', {}); rch = br.get('reach', {})
    msg_t    = msg.get('totals', {})
    cpas_t   = cpas.get('totals', {})
    plan_eng = plan.get('engage', {}); plan_vid = plan.get('video', {})
    plan_rch = plan.get('reach', {}); plan_msg = plan.get('messenger', {})

    total_sp     = ov.get('total_spend', 0)
    brand_sp     = ov.get('branding_spend', 0)
    msg_sp       = ov.get('messenger_spend', 0)
    cpas_sp      = cpas_t.get('spend', 0)
    gdn_sp       = ov.get('gdn_spend', 0)
    sem_sp       = ov.get('search_spend', 0)
    crm_rev      = crm.get('total_revenue', 0)

    # Plan total — auto-scan + fallback sum known budgets
    total_plan   = plan.get('total_budget', 0)
    if not total_plan:
        total_plan = (plan_eng.get('budget', 0) + plan_vid.get('budget', 0) +
                      plan_rch.get('budget', 0) + plan_msg.get('budget', 0))

    # KPI values
    total_imp    = eng.get('imp', 0) + vid.get('imp', 0) + rch.get('imp', 0)
    plan_imp     = plan_eng.get('imp', 0) + plan_vid.get('imp', 0) + plan_rch.get('imp', 0)
    total_eng    = eng.get('results', 0);   plan_eng_kpi = plan_eng.get('kpi', 0)
    total_vid    = vid.get('results', 0);   plan_vid_kpi = plan_vid.get('kpi', 0)
    total_msg    = msg_t.get('msg', 0);     plan_msg_kpi = plan_msg.get('kpi', 0)
    plan_msg_gmv = plan_msg.get('gmv_plan', 0)
    cpas_gmv     = cpas_t.get('rev', 0);   cpas_roas    = cpas_t.get('roas', 0)

    cpas_plan    = cpas_plan or {}
    plan_gg_gdn  = plan_gg_gdn or {}
    plan_gg_search = plan_gg_search or {}

    gdn_data     = gg.get('gdn', []);      search_data  = gg.get('search', [])
    gdn_imp      = sum(d['imp']    for d in gdn_data)
    sem_clk      = sum(d['clicks'] for d in search_data)
    sem_imp_tot  = sum(d['imp']    for d in search_data)
    sem_ctr      = sem_clk / sem_imp_tot * 100 if sem_imp_tot else 0

    # Plan values for card 6 (CPAS)
    cpas_rev_plan  = cpas_plan.get('revenue', 0)
    cpas_roas_plan = cpas_plan.get('roas_plan', 0)

    # Plan values for card 7 (Google): sum GDN + Search
    plan_gg_total_clk = plan_gg_gdn.get('clicks', 0) + plan_gg_search.get('clicks', 0)
    plan_gg_total_imp = plan_gg_gdn.get('imp', 0)    + plan_gg_search.get('imp', 0)
    plan_gg_ctr       = plan_gg_total_clk / plan_gg_total_imp * 100 if plan_gg_total_imp else 0

    # Actual Google: đọc từ dòng Total trong sheet (chính xác hơn sum từng campaign)
    actual_gg_clk = gg.get('total_clicks', sum(d.get('clicks', 0) for d in gdn_data) + sem_clk)
    actual_gg_imp = gg.get('total_imp',    gdn_imp + sem_imp_tot)
    actual_gg_ctr = actual_gg_clk / actual_gg_imp * 100 if actual_gg_imp else 0

    date_range_banner(date_range)

    # ── Row 1: 4 cards ────────────────────────────────────────────────────────
    kpi_grid(
        kpi_html("💰 Total Spent",
                 fmt_vnd(total_sp), "",
                 "accent",
                 progress=total_sp / total_plan if total_plan else None,
                 plan_label=f"Plan: {fmt_vnd(total_plan)}" if total_plan else ""),

        kpi_html("👁 Impressions",
                 fmt_num(total_imp), "",
                 "blue",
                 progress=total_imp / plan_imp if plan_imp else None,
                 plan_label=f"Plan: {fmt_num(plan_imp)}" if plan_imp else ""),

        kpi2_html("📣 Engage & Video",
                  fmt_num(total_eng),
                  _plan_sub(total_eng, plan_eng_kpi, fmt_num),
                  fmt_num(total_vid) + " views",
                  _plan_sub(total_vid, plan_vid_kpi, fmt_num),
                  "purple",
                  progress=total_eng / plan_eng_kpi if plan_eng_kpi else None,
                  plan_label=f"Plan: {fmt_num(plan_eng_kpi)}" if plan_eng_kpi else "",
                  progress2=total_vid / plan_vid_kpi if plan_vid_kpi else None,
                  plan_label2=f"Plan: {fmt_num(plan_vid_kpi)}" if plan_vid_kpi else ""),

        kpi2_html("💬 Messenger & GMV",
                  fmt_num(total_msg) + " msgs",
                  _plan_sub(total_msg, plan_msg_kpi, fmt_num),
                  fmt_vnd(crm_rev) + " GMV",
                  f'<span style="color:#555">{crm.get("total_orders", 0)} đơn (CRM)</span>',
                  "green",
                  progress=total_msg / plan_msg_kpi if plan_msg_kpi else None,
                  plan_label=f"Plan: {fmt_num(plan_msg_kpi)}" if plan_msg_kpi else "",
                  progress2=crm_rev / plan_msg_gmv if plan_msg_gmv else None,
                  plan_label2=f"Plan GMV: {fmt_vnd(plan_msg_gmv)}" if plan_msg_gmv else ""),
        cols=4
    )

    # ── Row 2: 3 cards ────────────────────────────────────────────────────────
    denom = total_sp or 1
    spend_lines = ''.join(
        f'<div style="display:flex;justify-content:space-between;padding:3px 0;font-size:12px;border-bottom:1px solid #2a2f45">'
        f'<span style="color:#aaa">{lbl}</span>'
        f'<span style="color:#6c63ff;font-weight:600">{fmt_vnd(val)}'
        f'<span style="color:#555;font-weight:400"> ({val/denom*100:.0f}%)</span></span></div>'
        for lbl, val in [('FB Branding', brand_sp), ('FB Messenger', msg_sp),
                          ('CPAS', cpas_sp), ('GDN', gdn_sp), ('Search', sem_sp)]
    )

    kpi_grid(
        kpi2_html("🛒 CPAS",
                  fmt_vnd(cpas_gmv) + " GMV",
                  _plan_sub(cpas_gmv, cpas_rev_plan, fmt_vnd),
                  f'{cpas_roas:.2f}x ROAS',
                  _plan_sub(cpas_roas, cpas_roas_plan, lambda x: f"{x:.1f}x") if cpas_roas_plan else
                  f'<span style="color:#555">{fmt_num(cpas_t.get("purch", 0))} purchases</span>',
                  "yellow",
                  progress=cpas_gmv / cpas_rev_plan if cpas_rev_plan else None,
                  plan_label=f"Plan GMV: {fmt_vnd(cpas_rev_plan)}" if cpas_rev_plan else "",
                  progress2=cpas_roas / cpas_roas_plan if cpas_roas_plan else None,
                  plan_label2=f"Plan: {cpas_roas_plan:.1f}x" if cpas_roas_plan else ""),

        kpi2_html("🔍 Google",
                  fmt_num(actual_gg_clk) + " clicks",
                  _plan_sub(actual_gg_clk, plan_gg_total_clk, fmt_num),
                  f"{actual_gg_ctr:.2f}% CTR",
                  _plan_sub(actual_gg_ctr, plan_gg_ctr, lambda x: f"{x:.2f}%"),
                  "",
                  progress=actual_gg_clk / plan_gg_total_clk if plan_gg_total_clk else None,
                  plan_label=f"Plan: {fmt_num(plan_gg_total_clk)}" if plan_gg_total_clk else "",
                  progress2=actual_gg_ctr / plan_gg_ctr if plan_gg_ctr else None,
                  plan_label2=f"Plan: {plan_gg_ctr:.2f}%" if plan_gg_ctr else ""),

        f'<div class="kpi-card" style="border-top:3px solid #2a2f45">'
        f'<div class="kpi-label">📊 Spend Breakdown</div>'
        f'<div style="margin-top:6px">{spend_lines}</div></div>',
        cols=3
    )

    # ── Charts ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        section("Budget Allocation", "accent")
        labels = ['FB Branding', 'FB Messenger', 'FB CPAS', 'Google GDN', 'Google Search']
        values = [brand_sp, msg_sp, cpas_sp, gdn_sp, sem_sp]
        colors = ['#6c63ff', '#22c55e', '#f59e0b', '#ec4899', '#3b82f6']
        st.plotly_chart(donut(labels, values, colors), use_container_width=True)
        chart_legend(labels, [fmt_vnd(v) for v in values], colors)

    with col2:
        section("KPI Summary — Plan vs Actual", "accent")

        def row_html(label, actual, plan_val, fmt_fn):
            bdg = pct_badge(actual, plan_val) if plan_val else badge('—', 'blue')
            pv = fmt_fn(plan_val) if plan_val else '—'
            return (f'<tr>'
                    f'<td style="padding:6px 8px;border-bottom:1px solid rgba(42,47,69,.4);color:#aaa;font-size:12px">{label}</td>'
                    f'<td style="padding:6px 8px;text-align:right;border-bottom:1px solid rgba(42,47,69,.4);color:#555;font-size:12px">{pv}</td>'
                    f'<td style="padding:6px 8px;text-align:right;border-bottom:1px solid rgba(42,47,69,.4);color:#6c63ff;font-weight:600;font-size:12px">{fmt_fn(actual)}</td>'
                    f'<td style="padding:6px 8px;text-align:center;border-bottom:1px solid rgba(42,47,69,.4)">{bdg}</td></tr>')

        ths = ''.join(
            f'<th style="color:#8892a4;font-size:10px;text-transform:uppercase;padding:6px 8px;text-align:{a};border-bottom:1px solid #2a2f45">{h}</th>'
            for h, a in [('KPI', 'left'), ('Plan', 'right'), ('Actual', 'right'), ('vs Plan', 'center')]
        )
        trs = (row_html("Impressions",       total_imp,  plan_imp,     fmt_num) +
               row_html("Engagements",       total_eng,  plan_eng_kpi, fmt_num) +
               row_html("Video Views",       total_vid,  plan_vid_kpi, fmt_num) +
               row_html("Msg Conversations", total_msg,  plan_msg_kpi, fmt_num) +
               row_html("CPAS GMV",          cpas_gmv,   0,            fmt_vnd) +
               row_html("Google Clicks",     actual_gg_clk, plan_gg_total_clk, fmt_num))
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>',
            unsafe_allow_html=True
        )
        budget_pct = total_sp / total_plan * 100 if total_plan else 0
        insight(
            f'Pace <strong>{budget_pct:.0f}%</strong> budget '
            f'({fmt_vnd(total_sp)} / {fmt_vnd(total_plan)}). '
            f'CPAS ROAS <strong>{cpas_roas:.1f}x</strong>. '
            f'Video CPV {fmt_vnd(vid.get("cpv", 0))} vs plan {fmt_vnd(plan_vid.get("cpv", 0))}.',
            'accent'
        )

    auto = _gen_insight(total_sp, total_plan, total_imp, plan_imp,
                        total_eng, plan_eng_kpi, total_vid, plan_vid_kpi,
                        total_msg, plan_msg_kpi, cpas_gmv, cpas_rev_plan,
                        cpas_roas, actual_gg_clk, plan_gg_total_clk,
                        vid.get('cpv', 0), plan_vid.get('cpv', 0))
    editable_insight('overview', auto, 'accent')
