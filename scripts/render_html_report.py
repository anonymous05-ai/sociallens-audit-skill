#!/usr/bin/env python3
"""
SocialLens Interactive Web Report Renderer
Xuất file HTML dashboard trực quan giống giao diện sociallens.co.in/reports.
"""

import html
import json
import sys
from pathlib import Path

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SocialLens Intelligence Report — {brand_name}</title>
  <style>
    :root {{
      --bg: #0b0f19;
      --surface: #121827;
      --surface-2: #1a2236;
      --border: #26314d;
      --text: #f1f5f9;
      --muted: #94a3b8;
      --accent: #6366f1;
      --accent-2: #22d3ee;
      --green: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 32px 20px 80px;
    }}
    .container {{ max-width: 1120px; margin: 0 auto; }}
    .topbar {{
      display: flex; justify-content: space-between; align-items: center;
      padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 32px;
      flex-wrap: wrap; gap: 12px;
    }}
    .logo {{ font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em; }}
    .logo span {{ color: var(--accent-2); }}
    .badge {{
      background: rgba(99, 102, 241, 0.16); color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.35);
      padding: 4px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 600;
    }}
    .hero {{
      display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px;
      background: linear-gradient(135deg, var(--surface) 0%, #161f35 100%);
      border: 1px solid var(--border); border-radius: 20px; padding: 32px; margin-bottom: 28px;
    }}
    @media (max-width: 820px) {{ .hero {{ grid-template-columns: 1fr; }} }}
    .hero h1 {{ font-size: 2rem; line-height: 1.2; margin: 10px 0 12px; }}
    .hero p {{ color: var(--muted); font-size: 0.98rem; }}
    .score-card {{
      background: var(--surface-2); border: 1px solid var(--border);
      border-radius: 16px; padding: 24px; display: flex; flex-direction: column;
      align-items: center; justify-content: center; text-align: center;
    }}
    .score-ring {{
      width: 132px; height: 132px; border-radius: 50%;
      background: conic-gradient(var(--accent-2) {score_deg}deg, #26314d 0deg);
      display: flex; align-items: center; justify-content: center; margin-bottom: 12px;
    }}
    .score-inner {{
      width: 106px; height: 106px; border-radius: 50%; background: var(--surface-2);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    .score-num {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
    .score-sub {{ font-size: 0.78rem; color: var(--muted); }}
    .grid-4 {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px;
    }}
    @media (max-width: 820px) {{ .grid-4 {{ grid-template-columns: repeat(2, 1fr); }} }}
    .kpi {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 14px; padding: 18px;
    }}
    .kpi-label {{ color: var(--muted); font-size: 0.82rem; }}
    .kpi-val {{ font-size: 1.5rem; font-weight: 700; margin-top: 4px; color: var(--accent-2); }}
    .section {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 18px; padding: 26px; margin-bottom: 24px;
    }}
    .section h2 {{ font-size: 1.25rem; margin-bottom: 18px; display: flex; align-items: center; gap: 8px; }}
    .pillar-row {{ margin-bottom: 14px; }}
    .pillar-head {{ display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 6px; }}
    .bar-bg {{ height: 10px; background: var(--surface-2); border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); border-radius: 999px; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    @media (max-width: 820px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
    .card {{
      background: var(--surface-2); border: 1px solid var(--border);
      border-radius: 14px; padding: 18px;
    }}
    .card h3 {{ font-size: 1rem; margin-bottom: 8px; color: #e2e8f0; }}
    .card p, .card li {{ font-size: 0.9rem; color: var(--muted); }}
    .card ul {{ padding-left: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); font-weight: 600; }}
    .pill {{
      display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
      background: rgba(16, 185, 129, 0.15); color: var(--green);
    }}
    .pill.warn {{ background: rgba(245, 158, 11, 0.15); color: var(--amber); }}
    .pill.bad {{ background: rgba(239, 68, 68, 0.15); color: var(--red); }}
  </style>
</head>
<body>
  <div class="container">
    <div class="topbar">
      <div class="logo">Social<span>Lens</span> // Brand Intelligence Report</div>
      <div class="badge">{industry} • Ngày báo cáo: {report_date}</div>
    </div>

    <div class="hero">
      <div>
        <span class="badge">Xếp hạng {grade} • {percentile}</span>
        <h1>{brand_name}</h1>
        <p>{executive_summary}</p>
        <div style="margin-top:16px; font-size:0.88rem; color:#cbd5e1;">
          <strong>Định vị cốt lõi:</strong> {positioning}
        </div>
      </div>
      <div class="score-card">
        <div class="score-ring">
          <div class="score-inner">
            <div class="score-num">{total_score}</div>
            <div class="score-sub">/ 100 điểm</div>
          </div>
        </div>
        <div style="font-weight:700;">Brand Social Health Score</div>
        <div style="font-size:0.82rem; color:var(--muted); margin-top:4px;">{verdict_tagline}</div>
      </div>
    </div>

    <div class="grid-4">
      <div class="kpi"><div class="kpi-label">Tổng Followers Đa Kênh</div><div class="kpi-val">{total_followers}</div></div>
      <div class="kpi"><div class="kpi-label">Weighted ER (wER)</div><div class="kpi-val">{weighted_er}</div></div>
      <div class="kpi"><div class="kpi-label">Tần suất Đăng bài</div><div class="kpi-val">{posting_cadence}</div></div>
      <div class="kpi"><div class="kpi-label">Định dạng Chủ lực</div><div class="kpi-val">{top_format}</div></div>
    </div>

    <div class="section">
      <h2>1. Điểm Thành Phần & Phân Bổ Trụ Cột Nội Dung</h2>
      <div class="grid-2">
        <div>
          <h3 style="font-size:0.95rem; color:var(--muted); margin-bottom:12px;">Chấm điểm 5 Trụ cột Sức khỏe</h3>
          {subscores_html}
        </div>
        <div>
          <h3 style="font-size:0.95rem; color:var(--muted); margin-bottom:12px;">Tỷ trọng Content Pillars (%)</h3>
          {pillars_html}
        </div>
      </div>
    </div>

    <div class="section">
      <h2>2. Phân Rã Bài Viết Thắng Lợi & Thư Viện Hook</h2>
      <div class="grid-2">
        {winning_posts_html}
      </div>
    </div>

    <div class="section">
      <h2>3. Voice-of-Customer (VoC) & Sắc Thái Cộng Đồng</h2>
      <div class="grid-2">
        <div class="card">
          <h3>Điểm chạm Khách hàng Yêu thích (Delight Triggers)</h3>
          <ul>{delights_html}</ul>
        </div>
        <div class="card">
          <h3>Rào cản Chốt đơn & Phàn nàn (Objections)</h3>
          <ul>{objections_html}</ul>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>4. Đối Chiếu Đối Thủ Cạnh Tranh (Competitor Matrix)</h2>
      <table>
        <thead>
          <tr>
            <th>Thương hiệu</th>
            <th>Followers</th>
            <th>Tần suất</th>
            <th>Weighted ER</th>
            <th>Lợi thế & Khoảng trống</th>
          </tr>
        </thead>
        <tbody>
          {competitors_html}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2>5. Lộ Trình Hành Động 30-60-90 Ngày</h2>
      <div class="grid-2">
        {roadmap_html}
      </div>
    </div>
  </div>
</body>
</html>
"""


def esc(text):
    return html.escape(str(text or ""))


def render_report(data: dict, output_path: Path):
    score = int(data.get("total_score", 72))
    score_deg = int((max(0, min(100, score)) / 100) * 360)

    subscores_html = ""
    for item in data.get("subscores", []):
        pct = int((item["score"] / item["max"]) * 100) if item.get("max") else 0
        subscores_html += f"""
        <div class="pillar-row">
          <div class="pillar-head"><span>{esc(item['name'])}</span><strong>{item['score']}/{item['max']}</strong></div>
          <div class="bar-bg"><div class="bar-fill" style="width:{pct}%"></div></div>
        </div>"""

    pillars_html = ""
    for p in data.get("content_pillars", []):
        pillars_html += f"""
        <div class="pillar-row">
          <div class="pillar-head"><span>{esc(p['name'])}</span><strong>{p['pct']}%</strong></div>
          <div class="bar-bg"><div class="bar-fill" style="width:{p['pct']}%"></div></div>
        </div>"""

    winning_posts_html = ""
    for post in data.get("winning_posts", []):
        winning_posts_html += f"""
        <div class="card">
          <span class="pill">{esc(post.get('metric', 'Viral Outlier'))}</span>
          <h3 style="margin-top:8px;">{esc(post.get('title', ''))}</h3>
          <p><strong>Hook:</strong> "{esc(post.get('hook', ''))}"</p>
          <p style="margin-top:6px;"><strong>Lý do thắng:</strong> {esc(post.get('why_it_worked', ''))}</p>
        </div>"""

    delights_html = "".join(f"<li>{esc(x)}</li>" for x in data.get("voc_delights", []))
    objections_html = "".join(f"<li>{esc(x)}</li>" for x in data.get("voc_objections", []))

    competitors_html = ""
    for c in data.get("competitors", []):
        competitors_html += f"""
        <tr>
          <td><strong>{esc(c.get('name'))}</strong></td>
          <td>{esc(c.get('followers'))}</td>
          <td>{esc(c.get('cadence'))}</td>
          <td>{esc(c.get('wer'))}</td>
          <td>{esc(c.get('edge'))}</td>
        </tr>"""

    roadmap_html = ""
    for step in data.get("roadmap", []):
        roadmap_html += f"""
        <div class="card">
          <span class="pill warn">{esc(step.get('phase', 'Phase'))}</span>
          <h3 style="margin-top:8px;">{esc(step.get('title', ''))}</h3>
          <p>{esc(step.get('action', ''))}</p>
        </div>"""

    rendered = HTML_TEMPLATE.format(
        brand_name=esc(data.get("brand_name", "Brand Audit")),
        industry=esc(data.get("industry", "Consumer Brand")),
        report_date=esc(data.get("report_date", "2026")),
        grade=esc(data.get("grade", "B")),
        percentile=esc(data.get("percentile", "Top 25%")),
        executive_summary=esc(data.get("executive_summary", "")),
        positioning=esc(data.get("positioning", "")),
        total_score=score,
        score_deg=score_deg,
        verdict_tagline=esc(data.get("verdict_tagline", "")),
        total_followers=esc(data.get("total_followers", "N/A")),
        weighted_er=esc(data.get("weighted_er", "N/A")),
        posting_cadence=esc(data.get("posting_cadence", "N/A")),
        top_format=esc(data.get("top_format", "Short Video")),
        subscores_html=subscores_html,
        pillars_html=pillars_html,
        winning_posts_html=winning_posts_html,
        delights_html=delights_html,
        objections_html=objections_html,
        competitors_html=competitors_html,
        roadmap_html=roadmap_html,
    )

    output_path.write_text(rendered, encoding="utf-8")
    print(f"Đã xuất báo cáo web tương tác tại: {output_path.resolve()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python scripts/render_html_report.py <report_data.json> [sociallens_report.html]")
        sys.exit(1)

    in_json = Path(sys.argv[1])
    out_html = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("sociallens_report.html")
    payload = json.loads(in_json.read_text(encoding="utf-8"))
    render_report(payload, out_html)
