"""Tab 2 — Branding (FB)"""
import streamlit as st
from helpers import kpi_html, kpi_grid, section, insight, html_table, pva_table, rank_badge, badge, pct_badge, ad_name_cell, editable_insight
from parse_data import fmt_vnd, fmt_num


def _gen_insight(br, plan_eng, plan_vid, plan_rch):
    from parse_data import fmt_vnd, fmt_num
    eng = br.get('engage', {}); vid = br.get('video', {}); rch = br.get('reach', {})
    brand_sp   = br.get('total_spend', 0)
    total_plan = plan_eng.get('budget', 0) + plan_vid.get('budget', 0) + plan_rch.get('budget', 0)
    lines = []
    if total_plan:
        lines.append(f"FB Branding: {fmt_vnd(brand_sp)} ({brand_sp/total_plan*100:.0f}% plan {fmt_vnd(total_plan)}).")
    e_res = eng.get('results', 0); e_plan = plan_eng.get('kpi', 0)
    if e_plan:
        lines.append(f"Engagement: {fmt_num(e_res)} results ({e_res/e_plan*100:.0f}% vs plan), CPE {fmt_vnd(eng.get('cpe',0))}.")
    v_res = vid.get('results', 0); v_plan = plan_vid.get('kpi', 0)
    if v_plan:
        cpv_r = plan_vid.get('cpv', 0) / vid.get('cpv', 1) if vid.get('cpv') else 0
        lines.append(
            f"Video: {fmt_num(v_res)} ThruPlay views ({v_res/v_plan*100:.0f}% vs plan), "
            f"CPV {fmt_vnd(vid.get('cpv',0))}" +
            (f" — rẻ hơn plan {cpv_r:.1f}x." if cpv_r > 1 else ".")
        )
    r_res = rch.get('results', 0); r_plan = plan_rch.get('kpi', 0)
    if r_plan:
        lines.append(f"Reach: {fmt_num(r_res)} users ({r_res/r_plan*100:.0f}% vs plan), CPM {fmt_vnd(rch.get('cpm',0))}.")
    total_imp = eng.get('imp',0) + vid.get('imp',0) + rch.get('imp',0)
    if total_imp:
        avg_cpm = round(brand_sp / total_imp * 1000)
        lines.append(f"Tổng imp: {fmt_num(total_imp)}, avg CPM: {fmt_vnd(avg_cpm)}.")
    return '\n'.join(lines)


def render(br, plan_eng, plan_vid, plan_rch):
    eng = br.get('engage', {}); vid = br.get('video', {}); rch = br.get('reach', {})
    brand_total = br.get('total_spend', 0)
    total_plan  = plan_eng.get('budget', 0) + plan_vid.get('budget', 0) + plan_rch.get('budget', 0)
    total_imp   = eng.get('imp', 0) + vid.get('imp', 0) + rch.get('imp', 0)
    total_rch   = eng.get('reach', 0) + vid.get('reach', 0) + rch.get('reach', 0)
    avg_cpm     = round(brand_total / total_imp * 1000) if total_imp else 0

    bp = brand_total / total_plan if total_plan else None
    kpi_grid(
        kpi_html("💰 Total Spent", fmt_vnd(brand_total), "", "blue",
                 progress=bp,
                 plan_label=f"Plan: {fmt_vnd(total_plan)}" if total_plan else ""),
        kpi_html("👁 Impressions",  fmt_num(total_imp),  "", "blue"),
        kpi_html("📡 Total Reach",  fmt_num(total_rch),  "", "blue"),
        kpi_html("📊 Avg CPM",      fmt_vnd(avg_cpm),    "", "blue"),
        cols=4
    )

    t_eng, t_vid, t_rch, t_tgt, t_content = st.tabs(
        ["📣 Engagement", "🎬 Video", "👁 Reach", "🎯 Targeting", "📋 Content"]
    )

    with t_eng:
        section("Engagement Campaign — Plan vs Actual", "blue")
        st.caption("Results = post_engagement (FB objective KPI)")
        ctr_plan_eng = plan_eng.get('ctr_plan', 0)
        pva_table([
            ("Budget (₫)",            plan_eng.get('budget', 0), eng.get('spend', 0),   fmt_vnd, pct_badge(eng.get('spend', 0),   plan_eng.get('budget', 0))),
            ("Engagements (Results)", plan_eng.get('kpi', 0),    eng.get('results', 0), fmt_num, pct_badge(eng.get('results', 0), plan_eng.get('kpi', 0))),
            ("CPE (₫)",               plan_eng.get('cpe', 0),    eng.get('cpe', 0),     fmt_vnd, pct_badge(eng.get('cpe', 0),     plan_eng.get('cpe', 0), invert=True)),
            ("CTR — Clicks(all)/Imp", ctr_plan_eng, eng.get('ctr', 0), lambda x: f"{x:.2f}%",
             pct_badge(eng.get('ctr', 0), ctr_plan_eng) if ctr_plan_eng else badge('—', 'blue')),
            ("Impressions",           plan_eng.get('imp', 0),    eng.get('imp', 0),     fmt_num, pct_badge(eng.get('imp', 0),    plan_eng.get('imp', 0))),
            ("Reach",                 0, eng.get('reach', 0), fmt_num, badge('—', 'blue')),
        ])
        ep = eng.get('spend', 0) / plan_eng.get('budget', 1) * 100 if plan_eng.get('budget') else 0
        insight(
            f'Budget <strong>{ep:.1f}%</strong>. '
            f'CPE <strong>{fmt_vnd(eng.get("cpe", 0))}</strong> vs plan {fmt_vnd(plan_eng.get("cpe", 0))}. '
            f'CTR(all) <strong>{eng.get("ctr", 0):.2f}%</strong>.',
            'yellow' if ep < 70 else 'green'
        )

    with t_vid:
        section("Video Campaign — Plan vs Actual", "blue")
        st.caption("Results = ThruPlay (video_thruplay_watched)")
        vtr_plan = plan_vid.get('vtr_plan', 0)
        pva_table([
            ("Budget (₫)",      plan_vid.get('budget', 0), vid.get('spend', 0),   fmt_vnd, pct_badge(vid.get('spend', 0),   plan_vid.get('budget', 0))),
            ("ThruPlay Views",  plan_vid.get('kpi', 0),    vid.get('results', 0), fmt_num, pct_badge(vid.get('results', 0), plan_vid.get('kpi', 0))),
            ("CPV (₫)",         plan_vid.get('cpv', 0),    vid.get('cpv', 0),     fmt_vnd, pct_badge(vid.get('cpv', 0),     plan_vid.get('cpv', 0), invert=True)),
            ("VTR — Views/Imp", vtr_plan, vid.get('ctr', 0), lambda x: f"{x:.2f}%",
             pct_badge(vid.get('ctr', 0), vtr_plan) if vtr_plan else badge('—', 'blue')),
            ("Impressions",     plan_vid.get('imp', 0),    vid.get('imp', 0),     fmt_num, pct_badge(vid.get('imp', 0),    plan_vid.get('imp', 0))),
            ("Reach",           0, vid.get('reach', 0), fmt_num, badge('—', 'blue')),
        ])
        ratio = plan_vid.get('cpv', 0) / vid.get('cpv', 1) if vid.get('cpv') else 0
        insight(
            f'ThruPlay <strong>{fmt_num(vid.get("results", 0))} views</strong>. '
            f'CPV <strong>{fmt_vnd(vid.get("cpv", 0))}</strong> vs plan {fmt_vnd(plan_vid.get("cpv", 0))}'
            + (f' — rẻ hơn <strong>{ratio:.1f}x</strong>.' if ratio > 1 else '.'),
            'green'
        )

    with t_rch:
        section("Reach Campaign — Plan vs Actual", "blue")
        st.caption("Results = Reach (unique users)")
        pva_table([
            ("Budget (₫)",  plan_rch.get('budget', 0), rch.get('spend', 0),   fmt_vnd, pct_badge(rch.get('spend', 0),   plan_rch.get('budget', 0))),
            ("Reach",       plan_rch.get('kpi', 0),    rch.get('results', 0), fmt_num, pct_badge(rch.get('results', 0), plan_rch.get('kpi', 0))),
            ("Impressions", plan_rch.get('imp', 0),    rch.get('imp', 0),     fmt_num, pct_badge(rch.get('imp', 0),    plan_rch.get('imp', 0))),
            ("CPM (₫)",     plan_rch.get('cpm', 0),    rch.get('cpm', 0),     fmt_vnd, pct_badge(rch.get('cpm', 0),    plan_rch.get('cpm', 0), invert=True)),
        ])
        insight(
            f'Reach <strong>{fmt_num(rch.get("results", 0))}</strong> vs plan {fmt_num(plan_rch.get("kpi", 0))}. '
            f'CPM {fmt_vnd(rch.get("cpm", 0))} vs plan {fmt_vnd(plan_rch.get("cpm", 0))}.',
            'green' if rch.get('results', 0) >= plan_rch.get('kpi', 0) else 'yellow'
        )

    with t_tgt:
        section("Targeting Analysis — All Branding Campaigns", "blue")
        tgt = br.get('targeting', [])
        if tgt:
            html_table(
                ['Segment', 'Spent (₫)', 'Impressions', 'CTR (all)', 'CPM (₫)'],
                [[d['segment'], f"{d['spend']:,.0f}", fmt_num(d['imp']),
                  f"{d['ctr']:.2f}%", f"{d['cpm']:,.0f}"] for d in tgt],
                aligns=['left', 'right', 'right', 'right', 'right']
            )
            best_ctr = max(tgt, key=lambda x: x['ctr'])
            best_cpm = min(tgt, key=lambda x: x['cpm'])
            insight(
                f'<strong>{best_ctr["segment"]}</strong> CTR cao nhất ({best_ctr["ctr"]:.2f}%). '
                f'<strong>{best_cpm["segment"]}</strong> CPM thấp nhất ({fmt_vnd(best_cpm["cpm"])}).',
                'accent'
            )
        else:
            st.info("Không có dữ liệu targeting.")

    with t_content:
        section("Top Engagement Ads — by Post Engagements", "blue")
        eng_ads = br.get('engage_ads', [])
        if eng_ads:
            html_table(
                ['#', 'Ad Name', 'Spent (₫)', 'Imp', 'Engagements', 'CPE (₫)', 'CTR'],
                [[rank_badge(d['rank']), ad_name_cell(d['name'], d['short_name']),
                  f"{d['spend']:,.0f}", fmt_num(d['imp']), f"{d['results']:,}",
                  f"{d['cpe']:,.0f}", f"{d['ctr']:.2f}%"] for d in eng_ads],
                aligns=['center', 'left', 'right', 'right', 'right', 'right', 'right']
            )
            top = eng_ads[0]
            insight(f'<strong>#{top["rank"]} "{top["short_name"]}"</strong> — {top["results"]:,} engagements, CPE {fmt_vnd(top["cpe"])}, CTR {top["ctr"]:.2f}%.', 'green')
        else:
            st.info("Không có dữ liệu Engagement ads.")

        section("Top Video Ads — by ThruPlay Views", "blue")
        vid_ads = br.get('video_ads', [])
        if vid_ads:
            html_table(
                ['#', 'Ad Name', 'Spent (₫)', 'Imp', 'ThruPlay Views', 'CPV (₫)', 'CTR'],
                [[rank_badge(d['rank']), ad_name_cell(d['name'], d['short_name']),
                  f"{d['spend']:,.0f}", fmt_num(d['imp']), f"{d['results']:,}",
                  f"{d['cpv']:,.0f}", f"{d['ctr']:.2f}%"] for d in vid_ads],
                aligns=['center', 'left', 'right', 'right', 'right', 'right', 'right']
            )
            top = vid_ads[0]
            insight(f'<strong>#{top["rank"]} "{top["short_name"]}"</strong> — {top["results"]:,} views, CPV {fmt_vnd(top["cpv"])}.', 'green')
        else:
            st.info("Không có dữ liệu Video ads.")

        # --- AI vs Non-AI comparison ---
        section("AI vs Non-AI Content — Performance Comparison", "blue")

        def _cmp_table(cmp, result_label, cost_label):
            ai  = cmp.get('ai', {})
            non = cmp.get('non_ai', {})
            total_sp = (ai.get('spend', 0) + non.get('spend', 0)) or 1

            def _row(label, d, color):
                if not d or d.get('spend', 0) == 0:
                    return None
                sp_pct = d['spend'] / total_sp * 100
                return [
                    f'<span style="color:{color};font-weight:600">{label}</span>',
                    f'<span style="color:#8892a4">{d["count"]} ads</span>',
                    f"{d['spend']:,.0f}",
                    f"<span style='color:#8892a4'>{sp_pct:.0f}%</span>",
                    fmt_num(d['imp']),
                    f"{d['results']:,}",
                    f"{d['cost_per_result']:,.0f}",
                    f"{d['ctr']:.2f}%",
                ]

            rows = [r for r in [
                _row('🤖 AI Content', ai,  '#6c63ff'),
                _row('👤 Non-AI',     non, '#8892a4'),
            ] if r]

            if not rows:
                return

            html_table(
                ['Group', '# Ads', 'Spent (₫)', 'Spend %', 'Imp', result_label, cost_label, 'Avg CTR'],
                rows,
                aligns=['left', 'center', 'right', 'center', 'right', 'right', 'right', 'right']
            )

            if ai.get('cost_per_result') and non.get('cost_per_result'):
                diff = (ai['cost_per_result'] - non['cost_per_result']) / non['cost_per_result'] * 100
                better = 'rẻ hơn' if diff < 0 else 'đắt hơn'
                insight(
                    f'AI content {cost_label.lower()}: <strong>{fmt_vnd(ai["cost_per_result"])}</strong> — '
                    f'<strong>{better} {abs(diff):.0f}%</strong> so với Non-AI ({fmt_vnd(non["cost_per_result"])}). '
                    f'AI: {ai["count"]} ads / {fmt_vnd(ai["spend"])} · '
                    f'Non-AI: {non["count"]} ads / {fmt_vnd(non["spend"])}.',
                    'accent'
                )

        engage_cmp = br.get('engage_ai_cmp', {})
        video_cmp  = br.get('video_ai_cmp', {})

        has_engage = engage_cmp.get('ai', {}).get('spend', 0) > 0 or engage_cmp.get('non_ai', {}).get('spend', 0) > 0
        has_video  = video_cmp.get('ai',  {}).get('spend', 0) > 0 or video_cmp.get('non_ai',  {}).get('spend', 0) > 0

        if has_engage:
            st.caption("Engagement Objective")
            _cmp_table(engage_cmp, 'Engagements', 'CPE (₫)')
        if has_video:
            st.caption("Video Objective")
            _cmp_table(video_cmp, 'ThruPlay Views', 'CPV (₫)')
        if not has_engage and not has_video:
            st.info("Không có dữ liệu để so sánh.")

    editable_insight('branding', _gen_insight(br, plan_eng, plan_vid, plan_rch), 'blue')
