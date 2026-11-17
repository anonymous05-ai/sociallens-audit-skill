#!/usr/bin/env python3
"""
SocialLens Quantitative Analyzer
Đọc file CSV hoặc JSON chứa dữ liệu bài đăng mạng xã hội, tính toán Weighted ER,
Viral Outliers, phân bổ định dạng, khung giờ vàng và xuất ra audit_metrics.json.
"""

import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_number(val):
    if val is None or val == "":
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = str(val).strip().lower().replace(",", "")
    try:
        if cleaned.endswith("k"):
            return float(cleaned[:-1]) * 1_000
        if cleaned.endswith("m"):
            return float(cleaned[:-1]) * 1_000_000
        return float(cleaned)
    except ValueError:
        return 0.0


def load_records(file_path: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else data.get("posts", [])
    elif suffix == ".csv":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    else:
        raise ValueError(f"Định dạng không hỗ trợ: {suffix}. Hãy dùng .csv hoặc .json")


def analyze_posts(records, default_followers=10000):
    if not records:
        return {"error": "File dữ liệu trống."}

    enriched = []
    format_stats = defaultdict(lambda: {"count": 0, "total_wer": 0.0, "total_views": 0.0})
    day_stats = defaultdict(lambda: {"count": 0, "total_wer": 0.0})

    for idx, row in enumerate(records, start=1):
        # Chuẩn hóa tên cột linh hoạt
        norm = {k.strip().lower(): v for k, v in row.items()}
        platform = norm.get("platform") or norm.get("channel") or "Social"
        fmt = norm.get("format") or norm.get("type") or norm.get("post_type") or "Post"
        caption = norm.get("caption") or norm.get("text") or norm.get("title") or f"Post #{idx}"
        url = norm.get("url") or norm.get("link") or ""
        date_str = norm.get("date") or norm.get("created_at") or norm.get("published_at") or ""

        followers = parse_number(norm.get("followers")) or default_followers
        likes = parse_number(norm.get("likes") or norm.get("reactions"))
        comments = parse_number(norm.get("comments"))
        shares = parse_number(norm.get("shares") or norm.get("reposts"))
        saves = parse_number(norm.get("saves") or norm.get("bookmarks"))
        views = parse_number(norm.get("views") or norm.get("plays") or norm.get("impressions"))

        raw_eng = likes + comments + shares + saves
        weighted_eng = (likes * 1.0) + (comments * 3.0) + (shares * 5.0) + (saves * 5.0)

        er_pct = (raw_eng / followers) * 100 if followers > 0 else 0.0
        wer_pct = (weighted_eng / followers) * 100 if followers > 0 else 0.0

        day_name = "Unknown"
        if date_str:
            for fmt_dt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(date_str[:19], fmt_dt)
                    day_name = dt.strftime("%A")
                    break
                except ValueError:
                    continue

        item = {
            "id": idx,
            "platform": platform,
            "format": fmt,
            "date": date_str,
            "day_of_week": day_name,
            "caption_preview": caption[:140].replace("\n", " "),
            "url": url,
            "followers": int(followers),
            "likes": int(likes),
            "comments": int(comments),
            "shares": int(shares),
            "saves": int(saves),
            "views": int(views),
            "er_pct": round(er_pct, 3),
            "wer_pct": round(wer_pct, 3),
        }
        enriched.append(item)

        format_stats[fmt]["count"] += 1
        format_stats[fmt]["total_wer"] += wer_pct
        format_stats[fmt]["total_views"] += views

        if day_name != "Unknown":
            day_stats[day_name]["count"] += 1
            day_stats[day_name]["total_wer"] += wer_pct

    wers = [p["wer_pct"] for p in enriched]
    ers = [p["er_pct"] for p in enriched]
    median_wer = statistics.median(wers) if wers else 0.0
    avg_wer = statistics.mean(wers) if wers else 0.0
    avg_er = statistics.mean(ers) if ers else 0.0

    for p in enriched:
        p["viral_multiplier"] = round(p["wer_pct"] / median_wer, 2) if median_wer > 0 else 1.0
        p["is_viral_outlier"] = p["viral_multiplier"] >= 2.5

    sorted_posts = sorted(enriched, key=lambda x: x["wer_pct"], reverse=True)

    format_breakdown = {
        k: {
            "post_count": v["count"],
            "share_pct": round((v["count"] / len(enriched)) * 100, 1),
            "avg_wer_pct": round(v["total_wer"] / v["count"], 3),
            "avg_views": int(v["total_views"] / v["count"]),
        }
        for k, v in format_stats.items()
    }

    best_days = sorted(
        [
            {"day": d, "posts": s["count"], "avg_wer_pct": round(s["total_wer"] / s["count"], 3)}
            for d, s in day_stats.items()
        ],
        key=lambda x: x["avg_wer_pct"],
        reverse=True,
    )

    return {
        "summary": {
            "total_posts_analyzed": len(enriched),
            "avg_standard_er_pct": round(avg_er, 3),
            "avg_weighted_er_pct": round(avg_wer, 3),
            "median_weighted_er_pct": round(median_wer, 3),
            "viral_outliers_count": sum(1 for p in enriched if p["is_viral_outlier"]),
        },
        "format_breakdown": format_breakdown,
        "best_posting_days": best_days,
        "top_5_winning_posts": sorted_posts[:5],
        "bottom_3_underperforming_posts": sorted_posts[-3:] if len(sorted_posts) >= 3 else [],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python scripts/analyze_social_data.py <file.csv|file.json> [followers_mặc_định]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    followers_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    records = load_records(input_path)
    result = analyze_posts(records, default_followers=followers_arg)

    out_path = Path("audit_metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
