"""Tab 5 — Google Ads"""
import streamlit as st
from helpers import kpi, kpi_html, kpi_grid, section, insight, html_table, editable_insight
from parse_data import fmt_vnd, fmt_num


def _gen_insight(gg):
    from parse_data import fmt_vnd, fmt_num
    gdn_data    = gg.get('gdn', [])
    search_data = gg.get('search', [])
    kw_data     = gg.get('keywords', [])
    lines = []
    gdn_sp  = sum(d['spend'] for d in gdn_data)
    gdn_imp = sum(d['imp']   for d in gdn_data)
    sem_sp  = sum(d['spend']  for d in search_data)
    sem_clk = sum(d['clicks'] for d in search_data)
    sem_imp = sum(d['imp']    for d in search_data)
    sem_ctr = sem_clk / sem_imp * 100 if sem_imp else 0
    total_sp = gdn_sp + sem_sp
    if total_sp:
        lines.append(f"Google total: {fmt_vnd(total_sp)} (GDN {fmt_vnd(gdn_sp)}, Search {fmt_vnd(sem_sp)}).")
    if sem_clk:
        lines.append(f"Search: {fmt_num(sem_clk)} clicks, CTR {sem_ctr:.1f}%.")
    if kw_data:
        top_kw = max(kw_data, key=lambda x: x['clicks'])
        lines.append(f"Top keyword: \"{top_kw['kw']}\" — {fmt_num(top_kw['clicks'])} clicks, CTR {top_kw['ctr']:.1f}%.")
        zero_conv = [k for k in kw_data if k['conv'] == 0 and k['clicks'] > 50]
        if zero_conv:
            lines.append(f"{len(zero_conv)} keyword(s) có nhiều clicks nhưng 0 conv → cân nhắc add negative.")
    return '\n'.join(lines)


def render(gg):
    gdn_data    = [d for d in gg.get('gdn', [])    if d['spend'] > 0]
    search_data = [d for d in gg.get('search', []) if d['spend'] > 0]
    kw_data     = gg.get('keywords', [])
    gdn_spend   = sum(d['spend']  for d in gdn_data)
    gdn_imp     = sum(d['imp']    for d in gdn_data)
    sem_spend   = sum(d['spend']  for d in search_data)
    sem_clk     = sum(d['clicks'] for d in search_data)
    sem_imp     = sum(d['imp']    for d in search_data)
    sem_ctr     = sem_clk / sem_imp * 100 if sem_imp else 0

    kpi_grid(
        kpi_html("💰 Total Google Spent", fmt_vnd(gdn_spend + sem_spend), "", "pink"),
        kpi_html("🖼 GDN",    fmt_vnd(gdn_spend), f"~{fmt_num(gdn_imp)} imp", "pink"),
        kpi_html("🔍 Search", fmt_vnd(sem_spend), f"{fmt_num(sem_clk)} clicks · {sem_ctr:.1f}% CTR", "pink"),
        kpi_html("🔑 Keywords tracked", str(len(kw_data)), "", "pink"),
        cols=4
    )

    sub_g = st.radio("", ["GDN Display", "Search (SEM)", "Keywords Report"],
                     horizontal=True, key='gg_sub')
    st.markdown("---")

    if sub_g == "GDN Display":
        section("GDN Campaigns", "pink")
        if gdn_data:
            html_table(
                ['Campaign', 'Spent (₫)', 'Impressions', 'CPM (₫)', 'Conv (micro)'],
                [[d['name'], f"{d['spend']:,.0f}", fmt_num(d['imp']),
                  f"{d['cpm']:,.0f}", f"{d['conv']:.1f}"] for d in gdn_data],
                aligns=['left', 'right', 'right', 'right', 'right']
            )
            insight('GDN phục vụ <strong>awareness + retarget pool</strong>. Conv là view-through, không phải direct sales.', 'accent')
        else:
            st.info("Không có dữ liệu GDN (campaign tên không chứa 'gdn').")

    elif sub_g == "Search (SEM)":
        section("Search Campaigns", "blue")
        if search_data:
            html_table(
                ['Campaign', 'Spent (₫)', 'Imp', 'Clicks', 'CTR', 'Conv', 'Avg CPC (₫)'],
                [[d['name'], f"{d['spend']:,.0f}", fmt_num(d['imp']), fmt_num(d['clicks']),
                  f'<span style="color:{"#22c55e" if d["ctr"]>5 else "#ef4444"};font-weight:600">{d["ctr"]:.1f}%</span>',
                  f"{d['conv']:.1f}", f"{d['avg_cpc']:,.0f}"] for d in search_data],
                aligns=['left', 'right', 'right', 'right', 'center', 'right', 'right']
            )
            insight(f'Search CTR <strong>{sem_ctr:.1f}%</strong> — intent audience rõ. Ưu tiên scale nếu còn budget.', 'green')
        else:
            st.info("Không có dữ liệu Search.")

    elif sub_g == "Keywords Report":
        if kw_data:
            c1, c2, c3 = st.columns(3)
            with c1: kpi("Total KW Impressions", fmt_num(sum(k['imp']    for k in kw_data)))
            with c2: kpi("Total KW Clicks",      fmt_num(sum(k['clicks'] for k in kw_data)))
            with c3: kpi("Total KW Cost",         fmt_vnd(sum(k['cost']   for k in kw_data)), color="yellow")

            section(f"Top {len(kw_data)} Keywords (by Clicks)", "accent")
            html_table(
                ['#', 'Keyword', 'Imp', 'Clicks', 'CTR', 'Cost (₫)', 'Avg CPC (₫)', 'Conv'],
                [[str(k['rank']), k['kw'], fmt_num(k['imp']), fmt_num(k['clicks']),
                  f'<span style="color:{"#22c55e" if k["ctr"]>5 else "#ef4444"};font-weight:600">{k["ctr"]:.1f}%</span>',
                  fmt_vnd(k['cost']), fmt_vnd(k['cpc']),
                  f'<span style="color:{"#22c55e" if k["conv"]>0 else "#ef4444"};font-weight:600">{k["conv"]:.1f}</span>']
                 for k in kw_data],
                aligns=['right', 'left', 'right', 'right', 'center', 'right', 'right', 'center']
            )
            insight('CTR cao + Conv > 0 → raise bid. Clicks nhiều, 0 conv → check landing page hoặc add negative keyword.', 'accent')
        else:
            st.info("Không có dữ liệu keywords.")

    editable_insight('google', _gen_insight(gg), 'pink')
