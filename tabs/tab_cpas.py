"""Tab 4 — CPAS"""
import streamlit as st
from helpers import kpi, section, insight, html_table, rank_badge, ad_name_cell, editable_insight
from parse_data import fmt_vnd, fmt_num


def _gen_insight(cpas):
    from parse_data import fmt_vnd, fmt_num
    t = cpas.get('totals', {})
    lines = []
    sp = t.get('spend', 0); rev = t.get('rev', 0); roas = t.get('roas', 0)
    purch = t.get('purch', 0); cpa = t.get('cpa', 0)
    if sp:
        lines.append(f"CPAS Spend: {fmt_vnd(sp)}, Revenue: {fmt_vnd(rev)}, ROAS: {roas:.2f}x.")
    if purch:
        lines.append(f"Purchases: {fmt_num(purch)}, Cost/Purchase: {fmt_vnd(cpa)}.")
    adsets = cpas.get('adsets', [])
    if adsets:
        best = max(adsets, key=lambda x: x['roas'])
        worst = min(adsets, key=lambda x: x['roas'])
        lines.append(f"Best adset: {best['name']} (ROAS {best['roas']:.1f}x). Cần cải thiện: {worst['name']} (ROAS {worst['roas']:.1f}x).")
    top_ads = cpas.get('top_ads', [])
    if top_ads:
        top = top_ads[0]
        lines.append(f"Star creative: #{top['rank']} \"{top['short_name']}\" — {top['purch']} purchases, ROAS {top['roas']:.1f}x.")
    return '\n'.join(lines)


def render(cpas):
    cpas_t = cpas.get('totals', {})

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Spent",       fmt_vnd(cpas_t.get('spend', 0)), color="yellow")
    with c2: kpi("Purchases",         fmt_num(cpas_t.get('purch', 0)))
    with c3: kpi("Revenue",           fmt_vnd(cpas_t.get('rev', 0)), color="blue")
    with c4: kpi("ROAS",              f"{cpas_t.get('roas', 0):.2f}x", color="green")
    with c5: kpi("Cost per Purchase", fmt_vnd(cpas_t.get('cpa', 0)))

    col1, col2 = st.columns(2)
    with col1:
        section("Adset / Targeting Breakdown", "yellow")
        adsets = cpas.get('adsets', [])
        if adsets:
            html_table(
                ['Adset', 'Spend (₫)', 'Purchases', 'Revenue', 'ROAS', 'CPA (₫)'],
                [[d['name'], f"{d['spend']:,.0f}", f"{d['purch']:,}",
                  fmt_vnd(d['rev']), f"{d['roas']:.1f}x", f"{d['cpa']:,.0f}"] for d in adsets],
                aligns=['left', 'right', 'right', 'right', 'right', 'right']
            )
            best = max(adsets, key=lambda x: x['roas'])
            insight(f'<strong>{best["name"]}</strong> ROAS <strong>{best["roas"]:.1f}x</strong> — scale lên.', 'yellow')
        else:
            st.info("Không có dữ liệu CPAS adsets.")

    with col2:
        section("Top Ads — by Purchases", "yellow")
        top_ads = cpas.get('top_ads', [])
        if top_ads:
            html_table(
                ['#', 'Ad', 'Spend (₫)', 'Purchases', 'Revenue', 'ROAS', 'CTR'],
                [[rank_badge(d['rank']),
                  ad_name_cell(d['name'], d['short_name']),
                  f"{d['spend']:,.0f}", f"{d['purch']:,}",
                  fmt_vnd(d['rev']), f"{d['roas']:.1f}x", f"{d['ctr']:.2f}%"] for d in top_ads],
                aligns=['center', 'left', 'right', 'right', 'right', 'right', 'right']
            )
            top = top_ads[0]
            insight(
                f'<strong>#{top["rank"]} "{top["short_name"]}"</strong> — {top["purch"]} purchases, ROAS {top["roas"]:.1f}x. Star creative.',
                'green'
            )
        else:
            st.info("Không có dữ liệu CPAS top ads.")

    editable_insight('cpas', _gen_insight(cpas), 'yellow')
