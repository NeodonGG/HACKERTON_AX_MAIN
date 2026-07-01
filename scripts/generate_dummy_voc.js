// 더미 VoC CSV 생성 스크립트 (4단계용)
// 원본 data/voc.csv(45건, 정제 후 44건) 구조/문체/용어를 참고해 행 수를 확장한 합성 데이터 생성
// 실행: node generate_dummy_voc.js > voc_dummy.csv

const TOTAL_ROWS = 200; // 원본 44건의 약 4.5배 규모 (150~300건 범위 내 중간값)

// 원본 44건 최종 분류 집계 (decisions.md [2단계] 기록 근거)
// 불만 9 / 기능요청 12 / 칭찬 8 / 일반 문의 15 (합 44) => 20.5% / 27.3% / 18.2% / 34.1%
const TYPE_WEIGHTS = [
  { type: "불만", weight: 9 / 44 },
  { type: "기능요청", weight: 12 / 44 },
  { type: "칭찬", weight: 8 / 44 },
  { type: "문의", weight: 15 / 44 },
];

const TERMS = [
  "CBAM", "CSRD", "Scope 1", "Scope 2", "Scope 3", "PCF", "ESG", "TCFD",
  "SBTi", "ISO 14064", "GWP", "IPCC", "LCA", "EU ETS", "탄소국경조정",
  "이중중요성", "탄소크레딧", "녹색채권", "탄소내재량", "온실가스",
];

// 시드 기반 의사난수 (재현성 확보)
function makeRng(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return function () {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}
const rng = makeRng(20260701);
function pick(arr) { return arr[Math.floor(rng() * arr.length)]; }
function pickInt(min, max) { return min + Math.floor(rng() * (max - min + 1)); }

// 유형별 문장 템플릿 (원본 용어/문체 참고, {term}/{n}은 치환 슬롯)
// pipeline/generate_report.py의 classify() 키워드 스템(PRAISE/COMPLAINT/REQUEST_STEMS)에
// 실제로 매칭되도록 문구를 맞춤 설계 — 그래야 5단계 파이프라인 재현성 검증에서
// 의도한 유형대로 재분류됨을 확인할 수 있음.
const TEMPLATES = {
  // COMPLAINT_STEMS 매칭: 오류/안 됩니다/반려/끊깁니다/차이가 납니다/제한적/누락됩니다/불편합니다/해결해주세요 등
  불만: [
    "카본링크 플랫폼에서 {term} 관련 계산 결과가 계속 오류로 표시됩니다. 빠른 해결이 필요합니다.",
    "{term} 데이터를 입력했는데 저장이 안 됩니다. 벌써 {n}번째 같은 문제가 발생하고 있습니다.",
    "외부 컨설팅사에서 산정한 {term} 값과 카본링크 결과가 차이가 납니다. 근거를 설명해주지 않아 해결해주세요.",
    "{term} 보고서를 제출했는데 형식 오류로 반려됐습니다. 사전 검증 기능이 없어 시간이 낭비됐습니다.",
    "API 연동이 자꾸 끊깁니다. {term} 데이터가 누락됩니다. 빨리 해결해주세요.",
    "{term} 관련 기능이 너무 제한적입니다. 실무에서 쓰기에 불편합니다.",
    "이용 중 {term} 처리 속도가 너무 느려 불편합니다. 수정해주세요.",
  ],
  // REQUEST_STEMS 매칭: 좋겠/기능이 필요/서비스가 필요/제공해/만들어/지원해줄/추가해/템플릿
  기능요청: [
    "{term} 산정 가이드 문서를 만들어 주시면 좋겠습니다.",
    "{term} 데이터를 협력사로부터 일괄 수집하는 자동화 기능을 추가해주시면 좋겠습니다.",
    "대시보드에 {term} 추세를 비교하는 차트 기능이 필요합니다.",
    "{term} 보고서를 회사 양식에 맞게 쓸 수 있는 템플릿을 제공해주시면 좋겠습니다.",
    "{term} 감축 로드맵 수립을 지원해줄 수 있는 컨설팅 서비스가 있으면 좋겠습니다.",
    "모바일에서도 {term} 데이터를 확인할 수 있는 앱을 만들어 주시면 좋겠습니다.",
    "{term}와 다른 프레임워크 데이터의 중복 입력을 줄여주는 기능이 필요합니다.",
  ],
  // PRAISE_STEMS 매칭: 감사합니다/감사드립니다/덕분/좋았/만족/인상적/올라갔/편하게/줄었습니다 (우선순위 최상단이라 다른 스템과 섞여도 칭찬으로 분류됨)
  칭찬: [
    "{term} 보고서 작성을 지원해주신 덕분에 이사회 보고를 무사히 마쳤습니다. 감사합니다.",
    "담당자분이 {term} 관련 문의에 빠르게 답변해주셔서 정말 감사합니다.",
    "온보딩 과정에서 {term} 세팅을 친절하게 안내해주셔서 정말 만족스럽습니다.",
    "카본링크 도입 이후 {term} 관련 업무 시간이 절반 이상 줄었습니다. 감사합니다.",
    "작년 대비 {term} 집계 오류가 크게 줄었습니다. 플랫폼 품질이 확실히 올라갔습니다.",
    "{term} 분석 리포트 덕분에 어디서 줄일 수 있는지 파악했습니다. 감사합니다.",
    "이번 업데이트로 {term} 화면이 훨씬 편하게 바뀌어서 좋았습니다.",
  ],
  // 위 세 스템 목록에 걸리지 않는 순수 정보 확인형 문장 -> else 분기(일반 문의)로 귀결
  문의: [
    "{term} 관련 신고 기한이 정확히 언제인지 확인하고 싶습니다.",
    "{term} 산정 방식이 이전과 달라진 것 같은데 어떤 기준이 바뀐 건지 궁금합니다.",
    "{term} 관련하여 공공기관과 민간기업에 적용되는 기준이 서로 다른지 궁금합니다.",
    "{term} 인증서 구매 절차나 예상 비용을 추산하는 방법이 궁금합니다.",
    "{term} 검증을 위한 제3자 인증 기관 목록을 알려주실 수 있나요?",
    "{term} 관련 데이터를 협력사로부터 받아야 하는데 표준 제출 양식이 있는지 궁금합니다.",
    "글로벌 고객사에서 {term} 기준 목표 설정을 요구했는데 시나리오 분석이 가능한가요?",
  ],
};

// 원본 id043처럼 불만+기능요청이 혼재된 경계 케이스 (파이프라인 분류 난이도 재현용)
// COMPLAINT_STEMS("제한적", "불편합니다")를 포함시켜, 실제 파이프라인에서도
// id043처럼 최종적으로 "불만"으로 수렴하도록 설계 (decisions.md [2단계] id043 처리 근거와 일치)
const AMBIGUOUS_TEMPLATES = [
  "{term} 보고서 커스터마이징 기능이 너무 제한적입니다. 고정된 템플릿만 써야 해서 기능 개선을 요청드립니다.",
  "{term} 계산 로직을 신뢰하기 어렵습니다. 상세 계산 근거를 확인할 수 있는 기능을 추가해주시길 요청드리는데, 현재는 제한적입니다.",
  "{term} 데이터 입력 화면이 너무 불편합니다. 더 간단한 입력 방식을 제공해주시길 요청합니다.",
];

// 문두 도입구 (콘텐츠 다양성 확보용 — 템플릿 x 용어 조합만으로는 200건 규모에서
// 우연한 완전 중복이 과도하게 발생해(원본 중복률 약 2%보다 훨씬 높아짐) 추가함)
const OPENERS = [
  "", "카본링크 사용 중 ", "최근 ", "이번 주 ", "저희 팀에서 확인해보니 ",
  "협력사 담당자와 상의한 결과, ", "실무 담당자로서 말씀드리면, ", "다시 문의드립니다. ",
];

const CHANNELS = ["이메일", "채널톡", "미팅메모"];
const CHANNEL_WEIGHTS = [0.55, 0.4, 0.05];
const CUSTOMER_TYPES = ["기타", "1차 협력사", "2차 협력사", "OEM"];
const CUSTOMER_WEIGHTS = [0.5, 0.2, 0.12, 0.18];

function weightedPick(items, weights) {
  const r = rng();
  let acc = 0;
  for (let i = 0; i < items.length; i++) {
    acc += weights[i];
    if (r <= acc) return items[i];
  }
  return items[items.length - 1];
}

function pad3(n) { return String(n).padStart(3, "0"); }

// 날짜: 2026-05-01 ~ 2026-07-15 범위, 형식 혼용 (ISO 70% / 슬래시 17% / 한글 13%)
function makeDate(dayOffset) {
  const base = new Date(2026, 4, 1); // 2026-05-01
  const d = new Date(base.getTime() + dayOffset * 86400000);
  const yyyy = d.getFullYear();
  const mm = d.getMonth() + 1;
  const dd = d.getDate();
  const mm2 = String(mm).padStart(2, "0");
  const dd2 = String(dd).padStart(2, "0");
  const r = rng();
  if (r < 0.7) return `${yyyy}-${mm2}-${dd2}`;
  if (r < 0.87) return `${yyyy}/${mm2}/${dd2}`;
  return `${mm}월 ${dd}일`;
}

function csvEscape(v) {
  if (v == null) return "";
  const s = String(v);
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

// 유형별 목표 건수 산출
const counts = {};
let assigned = 0;
TYPE_WEIGHTS.forEach((tw, i) => {
  if (i === TYPE_WEIGHTS.length - 1) {
    counts[tw.type] = TOTAL_ROWS - assigned; // 나머지 전부 (반올림 오차 보정)
  } else {
    const c = Math.round(TOTAL_ROWS * tw.weight);
    counts[tw.type] = c;
    assigned += c;
  }
});

// 순서를 뒤섞기 위한 유형 시퀀스 생성
let typeSequence = [];
Object.entries(counts).forEach(([type, c]) => {
  for (let i = 0; i < c; i++) typeSequence.push(type);
});
// Fisher-Yates shuffle (시드 rng 사용)
for (let i = typeSequence.length - 1; i > 0; i--) {
  const j = Math.floor(rng() * (i + 1));
  [typeSequence[i], typeSequence[j]] = [typeSequence[j], typeSequence[i]];
}

const rows = [];
let dayCursor = 0;

for (let i = 0; i < TOTAL_ROWS; i++) {
  const id = pad3(i + 1);
  dayCursor += rng() < 0.55 ? 0 : 1; // 날짜가 대체로 증가하되 간격 랜덤 (약 4개월 범위로 수렴)
  const date = makeDate(dayCursor);
  const channel = weightedPick(CHANNELS, CHANNEL_WEIGHTS);
  const customerType = weightedPick(CUSTOMER_TYPES, CUSTOMER_WEIGHTS);
  const type = typeSequence[i];
  const template = pick(TEMPLATES[type]);
  const term = pick(TERMS);
  const n = pickInt(2, 5);
  const opener = pick(OPENERS);
  const content = opener + template.replace("{term}", term).replace("{n}", n);
  const keywordHint = term.replace(/\s/g, "");

  rows.push({ id, date, channel, customerType, content, keywordHint, _type: type });
}

// 채널 결측 재현: 원본은 45건 중 2건 결측(약 4.4%) -> 200건 기준 약 9건
const missingChannelCount = Math.round(TOTAL_ROWS * (2 / 45));
const missingIdx = new Set();
while (missingIdx.size < missingChannelCount) {
  missingIdx.add(pickInt(0, TOTAL_ROWS - 1));
}
missingIdx.forEach((idx) => { rows[idx].channel = ""; });

// 경계 케이스(불만+기능요청 혼재) 재현: 원본 id043 사례 -> 200건 기준 3건 정도 삽입
// (중복행 생성보다 먼저 적용해야, 이후 복제되는 원본 행 내용이 최종 확정된 상태로 복사됨)
const AMBIGUOUS_COUNT = 3;
for (let k = 0; k < AMBIGUOUS_COUNT; k++) {
  const idx = pickInt(0, rows.length - 1);
  const term = pick(TERMS);
  rows[idx].content = pick(AMBIGUOUS_TEMPLATES).replace("{term}", term);
  rows[idx].keywordHint = term.replace(/\s/g, "") + ",기능개선요청";
  rows[idx]._type = "경계케이스(불만/기능요청 혼재)";
}

// 중복행 재현: 원본은 45건 중 1건 완전 중복(id031=id001) -> 200건 기준 2쌍 정도 재현
const DUP_PAIRS = 2;
const usedAsSource = new Set();
for (let k = 0; k < DUP_PAIRS; k++) {
  const dupRowIdx = rows.length - 1 - k; // 뒤쪽 몇 개 행을 복제본으로 덮어씀
  let srcIdx;
  do { srcIdx = pickInt(0, rows.length - DUP_PAIRS - 1); } while (usedAsSource.has(srcIdx));
  usedAsSource.add(srcIdx);
  rows[dupRowIdx] = {
    ...rows[srcIdx],
    id: rows[dupRowIdx].id, // id만 다르고 나머지 내용은 원본 행과 완전 동일
  };
}

// CSV 출력
const header = "id,date,channel,customer_type,content,keyword_hint";
const lines = [header];
rows.forEach((r) => {
  lines.push([
    r.id, r.date, r.channel, r.customerType, r.content, r.keywordHint,
  ].map(csvEscape).join(","));
});

process.stdout.write("﻿" + lines.join("\n") + "\n");

// 통계는 stderr로 출력 (검증용, CSV 본문과 분리)
const finalTypeCounts = {};
rows.forEach((r) => { finalTypeCounts[r._type] = (finalTypeCounts[r._type] || 0) + 1; });
console.error("=== 생성 통계 ===");
console.error("총 건수:", rows.length);
console.error("유형별 분포:", JSON.stringify(finalTypeCounts, null, 2));
console.error("채널 결측 건수:", missingChannelCount);
console.error("중복행 쌍 수:", DUP_PAIRS);
console.error("경계 케이스 건수:", AMBIGUOUS_COUNT);
