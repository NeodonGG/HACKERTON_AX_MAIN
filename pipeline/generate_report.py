"""
VoC 파이프라인: CSV 입력 -> 정제 -> 분류 -> 집계 -> voc-report.md / voc-report.html 자동 생성

사용법:
    python pipeline/generate_report.py <입력 CSV 경로> <출력 디렉터리> [--insights <insights.md 경로>] [--proposals <proposals.md 경로>]

예:
    python pipeline/generate_report.py data/voc.csv output --insights content/insights.md --proposals content/proposals.md
"""

import argparse
import csv
import html
import re
from collections import Counter, OrderedDict
from pathlib import Path

TYPES = ["불만", "기능 요청", "칭찬", "일반 문의"]

PRAISE_STEMS = ["감사합니다", "감사드립니다", "덕분", "좋았", "만족", "인상적", "올라갔", "편하게", "줄었습니다"]
COMPLAINT_STEMS = [
    "안 됩니다", "안됩니다", "틀린", "틀렸", "오류", "반려", "끊깁니다", "마비",
    "차이납니다", "차이가 납니다", "제한적", "호환이 안", "누락됩니다",
    "불편합니다", "수정해주세요", "해결해주세요",
]
REQUEST_STEMS = ["좋겠", "기능이 필요", "서비스가 필요", "제공해", "만들어", "지원해줄", "추가해", "템플릿"]

KOREAN_DATE_RE = re.compile(r"(\d{1,2})월\s*(\d{1,2})일")
SLASH_DATE_RE = re.compile(r"(\d{4})/(\d{1,2})/(\d{1,2})")
ISO_DATE_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")


def load_rows(csv_path: Path) -> list[dict]:
    with open(csv_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def infer_default_year(rows: list[dict]) -> str:
    years = Counter()
    for row in rows:
        m = ISO_DATE_RE.match(row["date"].strip()) or SLASH_DATE_RE.match(row["date"].strip())
        if m:
            years[m.group(1)] += 1
    return years.most_common(1)[0][0] if years else "2026"


def normalize_date(raw: str, default_year: str) -> str:
    raw = raw.strip()
    m = ISO_DATE_RE.match(raw)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    m = SLASH_DATE_RE.match(raw)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    m = KOREAN_DATE_RE.match(raw)
    if m:
        mo, d = m.groups()
        return f"{default_year}-{int(mo):02d}-{int(d):02d}"
    return raw  # 알 수 없는 형식은 원본 유지 + 이후 검토 필요


def classify(content: str) -> str:
    compact = content.replace(" ", "")

    def has_any(stems):
        return any(stem.replace(" ", "") in compact for stem in stems)

    if has_any(PRAISE_STEMS):
        return "칭찬"
    if has_any(COMPLAINT_STEMS):
        return "불만"
    if has_any(REQUEST_STEMS):
        return "기능 요청"
    return "일반 문의"


def clean_and_classify(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """정제(날짜 통일, 중복 제거) + 분류. (정제된 행 목록, 처리 로그) 반환."""
    log = []
    default_year = infer_default_year(rows)

    cleaned = []
    seen_content = {}
    for row in rows:
        content = (row.get("content") or "").strip()
        if not content:
            log.append(f"id {row.get('id')}: 콘텐츠 빈 값 -> 제외")
            continue

        key = content
        if key in seen_content:
            log.append(f"id {row.get('id')}: id {seen_content[key]}와 내용 완전 중복 -> 제외")
            continue
        seen_content[key] = row.get("id")

        row = dict(row)
        row["date"] = normalize_date(row.get("date", ""), default_year)
        row["channel"] = (row.get("channel") or "").strip()
        existing_type = (row.get("type") or "").strip()
        row["type"] = existing_type if existing_type in TYPES else classify(content)
        cleaned.append(row)

    log.append(f"날짜 형식 통일 기준 연도(원본 연도 미표기 시): {default_year}")
    has_input_type = any((r.get("type") or "").strip() in TYPES for r in rows)
    if has_input_type:
        log.append("입력 CSV에 검증된 type 컬럼이 있어 규칙 기반 분류 대신 해당 값을 그대로 사용")
    else:
        log.append("입력 CSV에 type 컬럼이 없어 규칙 기반 분류기(classify())로 자동 분류")
    return cleaned, log


def aggregate(rows: list[dict]) -> "OrderedDict[str, tuple[int, float]]":
    total = len(rows)
    counts = Counter(r["type"] for r in rows)
    result = OrderedDict()
    for t in TYPES:
        c = counts.get(t, 0)
        pct = round(c / total * 100, 1) if total else 0.0
        result[t] = (c, pct)
    return result


def read_fragment(path: str | None, fallback: str) -> str:
    if path and Path(path).exists():
        return Path(path).read_text(encoding="utf-8")
    return fallback


def render_md(rows, agg, log, insights_md, proposals_md, decisions_md, pipeline_usage_md, source_name) -> str:
    total = len(rows)
    lines = []
    lines.append("# VoC 분류·인사이트 리포트\n")
    lines.append("## 1. 데이터 개요\n")
    lines.append(f"- 원본 파일: `{source_name}`")
    lines.append(f"- 정제 후 유효 건수: {total}건\n")
    lines.append("### 데이터 정제 로그")
    for line in log:
        lines.append(f"- {line}")
    lines.append("")

    lines.append("## 2. VoC 유형별 분류표\n")
    lines.append("| id | date | channel | customer_type | type | content |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        content_short = r["content"].replace("|", "/")
        lines.append(
            f"| {r['id']} | {r['date']} | {r['channel'] or '미상'} | {r['customer_type']} | {r['type']} | {content_short} |"
        )
    lines.append("")

    lines.append("## 3. 유형별 건수·비율 요약\n")
    lines.append("| 유형 | 건수 | 비율 |")
    lines.append("|---|---|---|")
    for t, (c, pct) in agg.items():
        lines.append(f"| {t} | {c}건 | {pct}% |")
    lines.append("")

    lines.append("## 4. 탄소규제 맥락 인사이트 3개\n")
    lines.append(insights_md.strip() or "_(인사이트 내용 미입력)_")
    lines.append("")

    lines.append("## 5. 의사결정 로그 요약\n")
    lines.append(decisions_md.strip() or "_(decisions.md 참조)_")
    lines.append("")

    lines.append("---\n")
    lines.append("## [Standard] 파이프라인 사용법\n")
    lines.append(pipeline_usage_md.strip() or "_(파이프라인 사용법 미입력)_")
    lines.append("")

    lines.append("---\n")
    lines.append("## [Challenge] 제품 개선 기획안\n")
    lines.append(proposals_md.strip() or "_(기획안 내용 미입력)_")
    lines.append("")

    return "\n".join(lines)


def render_html(rows, agg, source_name) -> str:
    total = len(rows)
    stat_cards = "".join(
        f"<div class='card'><div class='num'>{c}</div><div class='label'>{html.escape(t)}</div>"
        f"<div class='pct'>{pct}%</div></div>"
        for t, (c, pct) in agg.items()
    )
    rows_html = "".join(
        f"<tr data-t='{html.escape(r['type'])}'>"
        f"<td>{html.escape(r['id'])}</td><td>{html.escape(r['date'])}</td>"
        f"<td>{html.escape(r['channel'] or '미상')}</td><td>{html.escape(r['customer_type'])}</td>"
        f"<td>{html.escape(r['type'])}</td><td>{html.escape(r['content'])}</td></tr>"
        for r in rows
    )
    filter_buttons = "".join(
        f"<button onclick=\"ft('{html.escape(t)}')\">{html.escape(t)}</button>" for t in TYPES
    )
    return f"""<section class="voc-report">
<style>
.voc-report {{ font-family: sans-serif; }}
.voc-report .cards {{ display:flex; gap:12px; flex-wrap:wrap; margin:16px 0; }}
.voc-report .card {{ border:1px solid #ddd; border-radius:8px; padding:12px 16px; min-width:120px; }}
.voc-report .card .num {{ font-size:24px; font-weight:bold; }}
.voc-report table {{ border-collapse:collapse; width:100%; margin-top:12px; }}
.voc-report th, .voc-report td {{ border:1px solid #ddd; padding:6px 8px; font-size:13px; text-align:left; }}
.voc-report button {{ margin-right:6px; padding:4px 10px; cursor:pointer; }}
</style>
<h2>VoC 분류 리포트 ({html.escape(source_name)}, 총 {total}건)</h2>
<div class="cards">{stat_cards}</div>
<div class="filters">
<button onclick="ft('all')">전체</button>{filter_buttons}
</div>
<table>
<thead><tr><th>id</th><th>date</th><th>channel</th><th>customer_type</th><th>type</th><th>content</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<script>
function ft(t) {{
  document.querySelectorAll('.voc-report tbody tr').forEach(function(tr) {{
    tr.style.display = (t === 'all' || tr.getAttribute('data-t') === t) ? '' : 'none';
  }});
}}
</script>
</section>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_dir")
    parser.add_argument("--insights", default=None)
    parser.add_argument("--proposals", default=None)
    parser.add_argument("--decisions-summary", default=None)
    parser.add_argument("--pipeline-usage", default=None)
    parser.add_argument("--source-label", default=None, help="리포트에 표시할 원본 파일명(생략 시 입력 CSV 파일명 사용)")
    args = parser.parse_args()

    src = Path(args.input_csv)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(src)
    cleaned, log = clean_and_classify(rows)
    agg = aggregate(cleaned)

    insights_md = read_fragment(args.insights, "")
    proposals_md = read_fragment(args.proposals, "")
    decisions_md = read_fragment(args.decisions_summary, "")
    pipeline_usage_md = read_fragment(args.pipeline_usage, "")

    source_label = args.source_label or src.name
    md = render_md(cleaned, agg, log, insights_md, proposals_md, decisions_md, pipeline_usage_md, source_label)
    (out_dir / "voc-report.md").write_text(md, encoding="utf-8")

    report_html = render_html(cleaned, agg, source_label)
    (out_dir / "voc-report.html").write_text(report_html, encoding="utf-8")

    print(f"정제 후 {len(cleaned)}건 처리 완료 -> {out_dir / 'voc-report.md'}, {out_dir / 'voc-report.html'}")
    for t, (c, pct) in agg.items():
        print(f"  {t}: {c}건 ({pct}%)")


if __name__ == "__main__":
    main()
