"""리뉴어스랩 VoC 분류·인사이트 Streamlit 대시보드 (로컬 실행용).

실행: streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
TYPES = ["불만", "기능 요청", "칭찬", "일반 문의"]
RISK_KEYWORDS = ["긴급", "마비", "반려", "누락", "위험"]

TYPE_COLOR = {
    "불만": "#e63946",
    "기능 요청": "#4361ee",
    "칭찬": "#2d6a4f",
    "일반 문의": "#e9a800",
}

PRIORITY_STYLE = {
    "P0": {"bg": "#ffe0e3", "fg": "#c9323e", "border": "#e63946"},
    "P1": {"bg": "#fff3cd", "fg": "#856404", "border": "#e9a800"},
}

PROPOSALS = [
    {
        "priority": "P0",
        "title": "CBAM 신고 기한 알림 + 인증서 비용 추정/제출 현황 추적",
        "subtitle": "제도는 시행됐지만 고객이 스스로 절차를 관리할 도구가 없는 문제 해결",
        "problem": (
            "CBAM 인증서 구매 의무화는 2026년 1월부터 이미 시행 중인데도, VoC 접수 시점(2026-05~06) 기준으로 "
            "신고 기한·인증서 비용 추산·제출 양식 등 기본 절차를 확인하는 문의가 계속 발생한다. 신고 마감을 넘긴 뒤 "
            "\"수출 계약이 위험하다\"며 긴급 대응을 요청한 사례(id 045)까지 있다."
        ),
        "improvements": [
            "고객사별 CBAM 신고 기한 자동 알림 (D-day 알림)",
            "인증서 예상 비용 계산기 (EU ETS 탄소 가격 연동 추정치)",
            "제출 현황 대시보드 (완료/반려/재제출 상태 추적)",
        ],
        "evidence": [
            ("001", "신고 기한 확인"),
            ("016·041", "인증서 실구매 시점·단가 비용 추산"),
            ("025", "EU 수입업자 제출 형식 문의"),
            ("045", "신고 마감 경과 후 긴급 대응 요청"),
            ("010", "카본링크 CBAM 보고서 EU 세관 반려"),
        ],
        "scores": [
            ("비즈니스 임팩트", 45, 85),
            ("규제 긴급성", 25, 95),
            ("VoC 빈도", 30, 100),
        ],
        "total": 92.0,
        "note": None,
    },
    {
        "priority": "P1",
        "title": "협력사 탄소 데이터 일괄 수집 자동화",
        "subtitle": "2차 협력사 200여 곳으로부터 Scope 3 데이터를 걷는 병목 해결",
        "problem": (
            "1차 협력사가 2차 협력사 200여 곳으로부터 Scope 3 데이터를 걷을 때 수기 입력·개별 링크 전송에 "
            "의존하고 있어 업무 비효율과 데이터 누락 위험이 크다. 협력사 협조 저조로 데이터 수집 자체가 막히는 "
            "사례도 있다."
        ),
        "improvements": [
            "협력사 데이터 요청 일괄 발송 + 응답 진행 현황 추적",
            "표준 공문/데이터 요청 템플릿 자동 생성",
            "CSRD 이중 중요성 평가 방법론 내장 지원",
        ],
        "evidence": [
            ("008", "2차 협력사 200개 데이터 수기 입력 비효율"),
            ("018", "일괄 발송 기능 필요"),
            ("023", "협력사 협조 저조 + 공문 템플릿 요청"),
            ("013", "CSRD 이중 중요성 평가 방법론 지원 요청"),
        ],
        "scores": [
            ("비즈니스 임팩트", 45, 95),
            ("규제 긴급성", 25, 75),
            ("VoC 빈도", 30, 40),
        ],
        "total": 73.5,
        "note": "총점 격차는 CBAM 대비 규제 긴급성·VoC 빈도 원점수가 낮기 때문 (CSRD는 확대 적용 진행 단계, 관련 VoC 4건 vs CBAM 10건)",
    },
]

INSIGHTS = [
    {
        "title": "CBAM \"이미 시행 중\"인데도 절차 불확실성 문의 집중",
        "evidence_ids": ["001", "016", "025", "032", "036", "041", "045"],
        "evidence_scope": "일반 문의 15건 중 7건 (약 47%)",
        "meaning": (
            "제도는 시행됐지만 실무 가이드가 못 따라가고 있다는 신호. CBAM 인증서 구매·비용 추산 가이드를 "
            "FAQ·온보딩 콘텐츠로 즉시 배포하면 CS 대응 부담을 줄이고 신규 협력사 온보딩 전환율도 높일 수 있다. "
            "045처럼 \"긴급 대응\"을 요구하는 케이스는 계약 리스크와 직결되므로 SLA 최우선 관리 대상이다."
        ),
        "detail": (
            "VoC 접수일(2026-05~06)은 CBAM 인증서 구매 의무화 시행일(2026-01)보다 늦은 시점인데도 기본 절차 "
            "확인 문의가 계속되고 있다. industry-news.md에 따르면 CBAM은 2026년 1월부터 전환기간(보고만 의무)을 "
            "끝내고 인증서 구매가 본격 과금되기 시작했으며, 한국 대EU 수출 중 CBAM 대상 품목이 51억 달러(철강 "
            "89.3%)에 달한다. 리뉴어스랩 고객 대부분이 이 제도를 처음 겪는 실무자라는 company-info.md의 서술과도 "
            "일치한다."
        ),
    },
    {
        "title": "Scope 3(협력사) 데이터 수집 병목이 불만·기능 요청 양쪽에서 반복",
        "evidence_ids": ["008", "018", "023", "013"],
        "evidence_scope": "기능 요청(12건)의 1/3 + 관련 불만 포함 총 4건",
        "meaning": (
            "협력사 데이터 수집 자동화는 개별 기능 하나가 아니라 \"Scope 3 자동화\"라는 제품의 핵심 약속을 지키는 "
            "문제다. 이 영역의 개선 우선순위를 낮추면 CSRD 확대 적용 시점(2026년)에 고객 이탈로 직결될 위험이 있다."
        ),
        "detail": (
            "008(불만: 200개 협력사 데이터 수기 입력 비효율), 018(기능요청: 일괄 발송 기능 필요), 023(기능요청: "
            "협력사 협조 저조 + 공문 템플릿 요청), 013(기능요청: CSRD 이중중요성 평가 지원)이 모두 협력사로부터 "
            "Scope 3 데이터를 걷는 과정의 병목을 지적한다. industry-news.md에 따르면 CSRD는 2026년부터 NFRD "
            "미해당 대규모 기업까지 확대 적용되며, company-info.md는 카본링크의 핵심 타겟 영역을 \"Scope 3 자동 "
            "수집\"으로 명시한다."
        ),
    },
    {
        "title": "계산 결과 신뢰성 문제 제기가 불만의 절반 가까이",
        "evidence_ids": ["010", "014", "019", "033"],
        "evidence_scope": "불만 9건 중 4건",
        "meaning": (
            "계산 로직 공개(방법론 문서화) 또는 외부 기준과의 차이를 설명하는 검증 리포트 기능을 제공하면, 감사·"
            "인증 시즌마다 반복되는 신뢰성 문의를 줄이고 CSRD 제3자 검증 대응력도 강화할 수 있다. 방치하면 계약 "
            "갱신율(NRR) 하락으로 이어질 수 있다."
        ),
        "detail": (
            "\"카본링크 계산 결과가 외부 산정값·경쟁사 플랫폼과 다르다\" 또는 \"CBAM 보고서가 EU 세관에서 반려됐다\"는 "
            "정확성·신뢰성 문제 제기. 019는 GWP 값이 IPCC 최신 기준을 반영하지 못했다는 구체적 지적까지 포함한다. "
            "industry-news.md는 CSRD가 제3자 검증(Limited Assurance)을 의무화하고 있고, 규제 기준 변경이 \"불만·"
            "문의, 기존 데이터 재처리 요구, 신뢰도 이슈\"로 이어진다고 명시한다."
        ),
    },
]

CUSTOM_CSS = """
<style>
div[data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 2rem; }

.rl-banner {
    background: #fff; border-radius: 12px; padding: 24px 32px; margin-bottom: 20px;
    border-left: 5px solid #4361ee; box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.rl-banner h1 { font-size: 22px; font-weight: 700; margin: 0 0 6px 0; }
.rl-banner p { font-size: 13px; color: #6c757d; margin: 0; }

.rl-section-title {
    font-size: 16px; font-weight: 700; padding: 4px 0 10px 12px; margin: 28px 0 14px 0;
    border-left: 4px solid #4361ee; border-bottom: 1px solid #e9ecef; padding-bottom: 10px;
}

.rl-card {
    background: #fff; border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06); border: 1px solid #eef0f2;
    height: 100%; box-sizing: border-box; display: flex; flex-direction: column;
}
div[data-testid="stHorizontalBlock"] { align-items: stretch; }
div[data-testid="stColumn"] { display: flex; }
div[data-testid="stColumn"] > div { width: 100%; }
details.rl-detail { margin-top: auto; padding-top: 8px; }

.rl-stat { background: #f8f9fa; border-radius: 8px; padding: 14px 16px; border-top: 3px solid; text-align: center; }
.rl-stat .rl-stat-label { font-size: 12px; font-weight: 700; color: #555; margin-bottom: 4px; }
.rl-stat .rl-stat-value { font-size: 22px; font-weight: 800; }
.rl-stat .rl-stat-pct { font-size: 12px; color: #888; }

.rl-badge { display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 6px; }

.rl-evidence-item {
    background: #f8f9fa; border-left: 3px solid #4361ee; border-radius: 0 6px 6px 0;
    padding: 7px 12px; margin-bottom: 6px; font-size: 12.5px;
}
.rl-evidence-item.risky { border-left-color: #e63946; background: #fff5f5; }
.rl-evidence-item .vid { font-weight: 700; margin-right: 6px; }

.rl-score-row { display: flex; align-items: center; gap: 10px; font-size: 12.5px; margin-bottom: 7px; }
.rl-score-row .rl-score-label { min-width: 118px; color: #444; }
.rl-score-track { background: #e9ecef; border-radius: 3px; height: 8px; flex: 1; }
.rl-score-fill { height: 100%; border-radius: 3px; background: #4361ee; }
.rl-score-val { font-weight: 700; min-width: 56px; text-align: right; color: #333; }

.rl-proposal-body { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 14px; }
.rl-prop-box { background: #f8f9fa; border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; }
.rl-prop-box-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; color: #888; margin-bottom: 8px; }
.rl-prop-box-body { font-size: 13px; color: #333; line-height: 1.6; }

details.rl-detail summary { cursor: pointer; font-size: 12.5px; color: #4361ee; font-weight: 600; margin-top: 8px; }
details.rl-detail p { font-size: 12.5px; color: #555; margin-top: 8px; line-height: 1.6; }

@media (max-width: 900px) {
    .rl-proposal-body { grid-template-columns: 1fr; }
}
</style>
"""


def badge(text: str, bg: str, fg: str) -> str:
    return f"<span class='rl-badge' style='background:{bg};color:{fg}'>{text}</span>"


def score_bar(label: str, weight: int, score: int, color: str) -> str:
    contribution = weight * score / 100
    return (
        "<div class='rl-score-row'>"
        f"<span class='rl-score-label'>{label} ({weight}%)</span>"
        f"<div class='rl-score-track'><div class='rl-score-fill' style='width:{score}%;background:{color}'></div></div>"
        f"<span class='rl-score-val'>{score}/100 · {contribution:.1f}점</span>"
        "</div>"
    )


st.set_page_config(page_title="리뉴어스랩 VoC 대시보드", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    "<div class='rl-banner'><h1>리뉴어스랩 VoC 분류·인사이트 대시보드</h1>"
    "<p>데이터: data/voc.csv 원본 44건 (정제 후) · 표에 실린 분류는 2단계에서 사람이 직접 검증한 결과이며, "
    "규칙 기반 자동 분류기(97.7% 일치, 사이드바 참고)로 만든 값이 아닙니다.</p></div>",
    unsafe_allow_html=True,
)

df = pd.read_csv(ROOT / "output" / "voc-classification.csv")
df["channel"] = df["channel"].fillna("미상")
total = len(df)

st.markdown("<div class='rl-section-title'>1. 유형별 통계</div>", unsafe_allow_html=True)
counts = df["type"].value_counts()
stat_cols = st.columns(4)
for col, t in zip(stat_cols, TYPES):
    c = int(counts.get(t, 0))
    color = TYPE_COLOR[t]
    with col:
        st.markdown(
            f"<div class='rl-stat' style='border-color:{color}'>"
            f"<div class='rl-stat-label' style='color:{color}'>{t}</div>"
            f"<div class='rl-stat-value' style='color:{color}'>{c}건</div>"
            f"<div class='rl-stat-pct'>{c / total * 100:.1f}%</div></div>",
            unsafe_allow_html=True,
        )

st.bar_chart(counts.reindex(TYPES))

st.markdown("<div class='rl-section-title'>2. VoC 유형별 분류표</div>", unsafe_allow_html=True)
filter_col, search_col = st.columns([1, 2])
with filter_col:
    selected_types = st.multiselect("유형 필터", TYPES, default=TYPES)
with search_col:
    keyword = st.text_input("내용 검색어 (예: CBAM, Scope3)")

filtered = df[df["type"].isin(selected_types)]
if keyword:
    filtered = filtered[filtered["content"].str.contains(keyword, case=False, na=False)]
st.caption(f"{len(filtered)}건 표시 중 (전체 {total}건)")
st.dataframe(filtered, width="stretch", hide_index=True)

complaint_col, request_col = st.columns(2)

with complaint_col:
    st.markdown("<div class='rl-section-title'>3. CS팀 — 지금 대응해야 할 불만</div>", unsafe_allow_html=True)
    complaints = df[df["type"] == "불만"].copy()
    complaints["긴급"] = complaints["content"].apply(lambda c: any(k in c for k in RISK_KEYWORDS))
    complaints = complaints.sort_values("긴급", ascending=False)
    urgent_n = int(complaints["긴급"].sum())
    items = []
    for _, row in complaints.iterrows():
        cls = "rl-evidence-item risky" if row["긴급"] else "rl-evidence-item"
        b = badge("긴급", "#ffe0e3", "#c9323e") if row["긴급"] else badge("일반", "#f1f3f5", "#666")
        items.append(f"<div class='{cls}'>{b} <span class='vid'>id {row['id']:03d}</span>{row['content']}</div>")
    st.markdown(
        f"<div class='rl-card'><p style='font-size:12.5px;color:#888;margin-top:0'>"
        f"불만 {len(complaints)}건 중 {urgent_n}건에 고위험 키워드({'/'.join(RISK_KEYWORDS)}) 포함</p>"
        + "".join(items)
        + "</div>",
        unsafe_allow_html=True,
    )

with request_col:
    st.markdown("<div class='rl-section-title'>4. 제품팀 — 반복 기능 요청 TOP3</div>", unsafe_allow_html=True)
    requests = df[df["type"] == "기능 요청"].copy()
    keyword_counts, keyword_ids = {}, {}
    for _, row in requests.iterrows():
        for kw in str(row["keyword_hint"]).split(","):
            kw = kw.strip()
            if not kw:
                continue
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            keyword_ids.setdefault(kw, []).append(f"{row['id']:03d}")
    top3 = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    rows = []
    max_count = top3[0][1] if top3 else 1
    for rank, (kw, count) in enumerate(top3, start=1):
        width = count / max_count * 100
        rows.append(
            "<div class='rl-score-row'>"
            f"<span class='rl-score-label'>{rank}. {kw}</span>"
            f"<div class='rl-score-track'><div class='rl-score-fill' style='width:{width}%;background:#4361ee'></div></div>"
            f"<span class='rl-score-val'>{count}건</span></div>"
            f"<div style='font-size:11.5px;color:#888;margin:-2px 0 10px 0'>근거: id {', '.join(keyword_ids[kw])}</div>"
        )
    st.markdown(
        f"<div class='rl-card'><p style='font-size:12.5px;color:#888;margin-top:0'>"
        f"기능 요청 {len(requests)}건의 keyword_hint 등장 빈도 기준</p>"
        + "".join(rows)
        + "</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='rl-section-title'>5. 탄소규제 맥락 인사이트</div>", unsafe_allow_html=True)
insight_cols = st.columns(len(INSIGHTS))
for col, insight in zip(insight_cols, INSIGHTS):
    id_badges = " ".join(badge(f"id {i}", "#f8f9fa", "#555") for i in insight["evidence_ids"])
    scope_badge = badge(f"근거 {insight['evidence_scope']}", "#eef1ff", "#4361ee")
    card_html = (
        "<div class='rl-card' style='min-height:100%'>"
        f"<p style='font-weight:700;font-size:14px'>{insight['title']}</p>"
        f"{scope_badge}"
        f"<p style='margin:10px 0 6px 0'>{id_badges}</p>"
        f"<p style='font-size:13px;line-height:1.6'><strong>비즈니스 의미</strong> — {insight['meaning']}</p>"
        "<details class='rl-detail'><summary>근거 상세 보기</summary>"
        f"<p>{insight['detail']}</p></details>"
        "</div>"
    )
    with col:
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("<div class='rl-section-title'>6. 제품 개선 기획안</div>", unsafe_allow_html=True)
st.caption("우선순위 = 비즈니스 임팩트 45% + 규제 긴급성 25% + VoC 빈도 30% (가중치 근거·민감도 분석은 사이드바 참고)")

for proposal in PROPOSALS:
    style = PRIORITY_STYLE[proposal["priority"]]
    evidence_html = "".join(
        f"<div class='rl-evidence-item'><span class='vid'>id {vid}</span>{quote}</div>"
        for vid, quote in proposal["evidence"]
    )
    scores_html = "".join(
        score_bar(name, weight, score, style["border"]) for name, weight, score in proposal["scores"]
    )
    note_html = f"<p style='font-size:11.5px;color:#888;margin-top:6px'>*{proposal['note']}</p>" if proposal["note"] else ""
    card_html = (
        f"<div class='rl-card' style='border-top:4px solid {style['border']}'>"
        "<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap'>"
        "<div>"
        f"<div style='font-size:16px;font-weight:800'>{proposal['title']}</div>"
        f"<div style='font-size:13px;color:#666;margin-top:4px'>{proposal['subtitle']}</div>"
        "</div>"
        f"<div style='text-align:center;background:{style['bg']};border-radius:10px;padding:10px 20px;min-width:90px'>"
        f"<div style='font-size:10px;font-weight:700;text-transform:uppercase;color:{style['fg']}'>Priority</div>"
        f"<div style='font-size:24px;font-weight:900;color:{style['fg']}'>{proposal['priority']}</div>"
        f"<div style='font-size:13px;font-weight:700;color:{style['fg']}'>{proposal['total']}점</div>"
        "</div></div>"
        "<div class='rl-proposal-body'>"
        "<div>"
        f"<div class='rl-prop-box'><div class='rl-prop-box-title'>문제 정의</div>"
        f"<div class='rl-prop-box-body'>{proposal['problem']}</div></div>"
        f"<div class='rl-prop-box'><div class='rl-prop-box-title'>개선 제안</div>"
        f"<div class='rl-prop-box-body'>{'<br>'.join('• ' + item for item in proposal['improvements'])}</div></div>"
        "</div>"
        "<div>"
        f"<div class='rl-prop-box'><div class='rl-prop-box-title'>근거 VoC ({len(proposal['evidence'])}건)</div>"
        f"{evidence_html}</div>"
        f"<div class='rl-prop-box'><div class='rl-prop-box-title'>우선순위 점수</div>{scores_html}{note_html}</div>"
        "</div>"
        "</div></div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)
