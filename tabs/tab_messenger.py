"""Tab 3 — Conversion (Messenger)"""
import streamlit as st
from helpers import kpi, kpi_html, kpi_grid, section, insight, html_table, rank_badge, ad_name_cell, date_range_banner, editable_insight
from parse_data import fmt_vnd, fmt_num


def _gen_insight(msg, crm, plan_msg):
    from parse_data import fmt_vnd, fmt_num
    msg_t = msg.get('totals', {})
    lines = []
    sp = msg_t.get('spend', 0); sp_plan = plan_msg.get('budget', 0)
    if sp_plan:
        lines.append(f"Messenger: {fmt_vnd(sp)} ({sp/sp_plan*100:.0f}% plan {fmt_vnd(sp_plan)}).")
    msgs = msg_t.get('msg', 0); msg_plan = plan_msg.get('kpi', 0)
    if msg_plan:
        lines.append(f"Conversations: {fmt_num(msgs)} ({msgs/msg_plan*100:.0f}% vs plan {fmt_num(msg_plan)}).")
    cpm = msg_t.get('cost_per_msg', 0); cpm_plan = plan_msg.get('cpmsg', 0)
    rr = msg_t.get('reply_rate', 0)
    lines.append(f"Cost/Msg: {fmt_vnd(cpm)}" + (f" vs plan {fmt_vnd(cpm_plan)}." if cpm_plan else ".") +
                 (f"  Reply rate: {rr:.1f}%." if rr else ""))
    orders = crm.get('total_orders', 0); rev = crm.get('total_revenue', 0)
    kh_new = crm.get('kh_new', 0); kh_old = crm.get('kh_old', 0)
    total_kh = kh_new + kh_old
    if orders:
        lines.append(f"CRM: {orders} đơn, doanh thu {fmt_vnd(rev)}." +
                     (f"  KH mới: {kh_new/total_kh*100:.0f}%." if total_kh else ""))
    return '\n'.join(lines)


def render(msg, crm, plan_msg, date_range):
    msg_t = msg.get('totals', {})

    msg_sp_pct  = msg_t.get('spend', 0) / plan_msg.get('budget', 1) * 100 if plan_msg.get('budget') else 0
    msg_kpi_pct = msg_t.get('msg', 0)   / plan_msg.get('kpi', 1)    * 100 if plan_msg.get('kpi')    else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Spent",       fmt_vnd(msg_t.get('spend', 0)),
                 f"/ {fmt_vnd(plan_msg.get('budget', 0))} plan · {msg_sp_pct:.1f}%" if plan_msg.get('budget') else "", "green")
    with c2: kpi("Msg Conversations", fmt_num(msg_t.get('msg', 0)),
                 f"/ {fmt_num(plan_msg.get('kpi', 0))} plan · {msg_kpi_pct:.1f}%" if plan_msg.get('kpi') else "")
    with c3: kpi("Msg Replied",       fmt_num(msg_t.get('replied', 0)), f"{msg_t.get('reply_rate', 0):.1f}% reply rate")
    with c4: kpi("Cost / Msg",        fmt_vnd(msg_t.get('cost_per_msg', 0)),
                 f"plan: {fmt_vnd(plan_msg.get('cpmsg', 0))}" if plan_msg.get('cpmsg') else "")
    with c5: kpi("CRM Orders",        str(crm.get('total_orders', 0)), fmt_vnd(crm.get('total_revenue', 0)), "purple")

    sub_m = st.radio("", ["Media Performance", "CRM Sales"], horizontal=True, key='msg_sub')
    st.markdown("---")

    if sub_m == "Media Performance":
        # Campaign comparison
        section("Campaign Comparison", "green")
        camps = msg.get('campaigns', [])
        if camps:
            html_table(
                ['Campaign', 'Spent (₫)', 'Imp', 'Msg', 'Replied', 'Reply Rate', 'Cost/Msg (₫)'],
                [[d['name'], f"{d['spend']:,.0f}", fmt_num(d['imp']), f"{d['msg']:,}",
                  f"{d['replied']:,}",
                  f'<span style="color:{"#22c55e" if d["reply_rate"]>=80 else "#ef4444"};font-weight:600">{d["reply_rate"]:.1f}%</span>',
                  f"{d['cost_per_msg']:,.0f}"] for d in camps],
                aligns=['left', 'right', 'right', 'right', 'right', 'center', 'right']
            )
            insight('Scale campaign có reply rate cao. Nếu ưu tiên volume → giảm cost/msg.', 'green')
        else:
            st.info("Không có dữ liệu campaign Messenger. Kiểm tra tên campaign trong file FB Raw.")

        col1, col2 = st.columns(2)
        with col1:
            section("Targeting Breakdown", "green")
            tgt = msg.get('targeting', [])
            if tgt:
                html_table(
                    ['Segment', 'Spent (₫)', 'Msg', 'Replied', 'Cost/Msg (₫)'],
                    [[d['segment'], f"{d['spend']:,.0f}", f"{d['msg']:,}",
                      f"{d['replied']:,}", f"{d['cost_per_msg']:,.0f}"] for d in tgt],
                    aligns=['left', 'right', 'right', 'right', 'right']
                )
                best = min(tgt, key=lambda x: x['cost_per_msg'])
                insight(f'<strong>{best["segment"]}</strong> cost/msg thấp nhất: <strong>{fmt_vnd(best["cost_per_msg"])}</strong>.', 'green')

        with col2:
            section("Top Ads — by Messages, Purchases & Revenue", "green")
            top_ads = msg.get('top_ads', [])
            if top_ads:
                html_table(
                    ['#', 'Ad', 'Spent (₫)', 'Msg', 'Cost/Msg', 'Purchases', 'Revenue (₫)', 'CTR'],
                    [[rank_badge(d['rank']),
                      ad_name_cell(d['name'], d['short_name']),
                      f"{d['spend']:,.0f}",
                      f"{d['msg']:,}",
                      f"{d['cost_per_msg']:,.0f}",
                      f"{d.get('purch', 0):,}",
                      f"{d.get('rev', 0):,.0f}",
                      f"{d['ctr']:.2f}%"] for d in top_ads],
                    aligns=['center', 'left', 'right', 'right', 'right', 'right', 'right', 'right']
                )
                top = top_ads[0]
                insight(
                    f'<strong>#{top["rank"]} "{top["short_name"]}"</strong>: '
                    f'{top["msg"]:,} msgs, {top.get("purch", 0)} purchases, '
                    f'{fmt_vnd(top.get("rev", 0))} revenue.',
                    'green'
                )
            else:
                st.info("Không có dữ liệu Top Ads Messenger.")

        section("AI vs Non-AI Content — Performance Comparison", "green")
        cmp = msg.get('ai_cmp', {})
        ai, non = cmp.get('ai', {}), cmp.get('non_ai', {})
        total_sp = (ai.get('spend', 0) + non.get('spend', 0)) or 1

        def _msg_row(label, d, color):
            if not d or d.get('spend', 0) == 0:
                return None
            sp_pct = d['spend'] / total_sp * 100
            return [
                f'<span style="color:{color};font-weight:600">{label}</span>',
                f'<span style="color:#8892a4">{d["count"]} ads</span>',
                f"{d['spend']:,.0f}",
                f"<span style='color:#8892a4'>{sp_pct:.0f}%</span>",
                f"{d['msg']:,}",
                f"{d['cost_per_msg']:,.0f}",
                f'<span style="color:{"#22c55e" if d["reply_rate"] >= 80 else "#ef4444"};font-weight:600">{d["reply_rate"]:.1f}%</span>',
                f"{d.get('purch', 0):,}",
                f"{d.get('rev', 0):,.0f}",
                f"{d['ctr']:.2f}%",
            ]

        rows = [r for r in [
            _msg_row('🤖 AI Content', ai,  '#6c63ff'),
            _msg_row('👤 Non-AI',     non, '#8892a4'),
        ] if r]

        if rows:
            html_table(
                ['Group', '# Ads', 'Spent (₫)', 'Spend %', 'Msg', 'Cost/Msg (₫)', 'Reply Rate', 'Purchases', 'Revenue (₫)', 'CTR'],
                rows,
                aligns=['left', 'center', 'right', 'center', 'right', 'right', 'center', 'right', 'right', 'right']
            )
            if ai.get('cost_per_msg') and non.get('cost_per_msg'):
                diff = (ai['cost_per_msg'] - non['cost_per_msg']) / non['cost_per_msg'] * 100
                better = 'rẻ hơn' if diff < 0 else 'đắt hơn'
                insight(
                    f'AI content cost/msg: <strong>{fmt_vnd(ai["cost_per_msg"])}</strong> — '
                    f'<strong>{better} {abs(diff):.0f}%</strong> so với Non-AI ({fmt_vnd(non["cost_per_msg"])}). '
                    f'AI: {ai["count"]} ads / {fmt_vnd(ai["spend"])} · '
                    f'Non-AI: {non["count"]} ads / {fmt_vnd(non["spend"])}.',
                    'accent'
                )
        else:
            st.info("Không có dữ liệu để so sánh.")

    else:  # CRM Sales
        date_range_banner(date_range)

        kh_new = crm.get('kh_new', 0); kh_old = crm.get('kh_old', 0)
        total_kh   = kh_new + kh_old
        purch_plan = plan_msg.get('purchase_plan', 0)
        gmv_plan   = plan_msg.get('gmv_plan', 0)
        total_ord  = crm.get('total_all_orders', crm.get('total_orders', 0))
        total_rev  = crm.get('total_revenue', 0)

        def _sub(actual, plan, fmt_fn):
            if not plan: return ''
            pct = actual / plan * 100
            clr = '#22c55e' if pct >= 90 else '#ef4444'
            return f'<span style="color:#555">Plan: {fmt_fn(plan)}</span> · <span style="color:{clr};font-weight:600">{pct:.0f}%</span>'

        kpi_grid(
            kpi_html("📦 CRM Orders",
                     f"{total_ord}",
                     _sub(total_ord, purch_plan, lambda x: f"{x:.0f}") or f"Đã giao: {crm.get('total_orders', 0)}",
                     "green",
                     progress=total_ord / purch_plan if purch_plan else None,
                     plan_label=f"Plan: {purch_plan:.0f}" if purch_plan else ""),
            kpi_html("💰 GMV / Doanh thu",
                     fmt_vnd(total_rev),
                     _sub(total_rev, gmv_plan, fmt_vnd),
                     "blue",
                     progress=total_rev / gmv_plan if gmv_plan else None,
                     plan_label=f"Plan: {fmt_vnd(gmv_plan)}" if gmv_plan else ""),
            kpi_html("📦 Total Qty",     f"{crm.get('total_qty', 0):.0f} sản phẩm", "", "accent"),
            kpi_html("👤 KH Mới",
                     f"{kh_new} ({kh_new/total_kh*100:.0f}%)" if total_kh else "—",
                     f"KH Cũ: {kh_old}", "yellow"),
            cols=4
        )

        col1, col2 = st.columns(2)
        with col1:
            section("Doanh thu theo Kênh", "green")
            ch = crm.get('channels', [])
            if ch:
                html_table(['Kênh', 'Đơn hàng', 'Doanh thu'],
                           [[d['channel'], f"{d['orders']:,}", fmt_vnd(d['revenue'])] for d in ch],
                           aligns=['left', 'right', 'right'])
        with col2:
            section("Sản phẩm bán chạy", "green")
            prod = crm.get('products', [])
            if prod:
                html_table(['Sản phẩm', 'Đơn', 'SL', 'Doanh thu'],
                           [[d['product'], f"{d['orders']:,}", f"{d['qty']:.0f}", fmt_vnd(d['revenue'])]
                            for d in prod[:8]],
                           aligns=['left', 'right', 'right', 'right'])

        section("CRM Sale Orders — Messenger", "green")
        orders = crm.get('orders', [])
        if orders:
            html_table(
                ['#', 'Ngày', 'Sản phẩm', 'Kênh', 'Cũ/Mới', 'Tình trạng', 'Doanh thu (₫)'],
                [[str(i + 1), o.get('date', ''), o.get('product', ''), o.get('channel', ''),
                  o.get('kh_type', ''),
                  f'<span style="background:rgba(34,197,94,.15);color:#22c55e;padding:2px 8px;border-radius:12px;font-size:11px">{o.get("status", "")}</span>',
                  fmt_vnd(o.get('revenue', 0))] for i, o in enumerate(orders)],
                aligns=['right', 'left', 'left', 'left', 'left', 'center', 'right']
            )
        else:
            st.info("Không có đơn hàng nào trong khoảng thời gian này.")

    editable_insight('messenger', _gen_insight(msg, crm, plan_msg), 'green')
