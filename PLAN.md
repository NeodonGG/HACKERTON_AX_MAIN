# [01] 리뉴어스랩 — 프로젝트 수행 계획

> 이 파일은 새 Claude Code 세션에서도 프로젝트 맥락과 진행 계획을 그대로 이어받기 위한 문서입니다.
> 작업 시작 전 이 파일 + `CLAUDE.md` + `problem.md` + `context/*.md`를 함께 읽으세요.

## 프로젝트 개요

리뉴어스랩(탄소 데이터 자동화 플랫폼 CarbonLink 운영사)의 데이터 분석 컨설턴트 역할로,
`data/voc.csv`(고객 VoC 45건)를 분석해 4유형(불만/기능 요청/칭찬/일반 문의) 분류표, 건수·비율 집계,
CSRD·CBAM 규제 맥락의 비즈니스 인사이트 3개를 담은 리포트를 작성하는 과제.
채점은 Basic(100점) → Standard(+30점) → Challenge(+30점) 누적 구조.

**목표 레벨: Challenge (160점 만점 전체 달성)**

## 범위 확정 사항 (중요 — 재확인 없이 아래 원칙 따를 것)

1. **더미 데이터의 역할**: 원본 `data/voc.csv`(45건, 정제 후 44건)를 대체하지 않는다.
   - 핵심 분류표·집계·인사이트(Basic)는 반드시 **원본 44건 기준**으로 작성한다.
   - 더미 데이터(행 수를 늘린 합성 CSV)는 ①Standard의 "새 CSV 투입 시 파이프라인 재현성" 검증용,
     ②Challenge 기획안의 우선순위 점수 계산에 쓸 대규모 빈도 데이터 보조 근거로만 사용한다.
   - 더미 데이터 사용 사실은 리포트에 투명하게 명시한다.

2. **대시보드/HTML 관련 제약 해석**: CLAUDE.md의 "대시보드·웹 UI 구현 제외"는
   design-conversation.md 확인 결과 **Streamlit 같은 서버 기반 인터랙티브 대시보드를 배제**한다는 뜻이며,
   `output/sample-*.html` 같은 **정적 단일 HTML 파일 시각화는 오히려 각 레벨의 표준 산출물**로 설계되어 있다.
   - 따라서 이번 과제 제출물에는 `voc-report.md` 외에 **정적 HTML 시각화 리포트(`voc-report.html`)도 포함**한다.
   - Streamlit·Supabase·GitHub 배포(Track B)는 **이 과제 채점과 무관한 별도 포트폴리오 확장 작업**으로 분리했다.
     Track A(이 문서의 9단계) 완료 전까지는 Track B에 착수하지 않는다.

3. **problem.md "도전" 항목 처리**: problem.md 제출 가이드의 "도전"(구글시트 자동 기입 연동 + Skill 패키징)은 CLAUDE.md의 공식 Challenge 채점 기준(기획안 실효성+우선순위 설계)과 다른 항목이다.
   - 구글시트 자동 기입 연동은 Cowork 커넥터 전용 기능이라 Claude Code 터미널 환경에서는 수행하지 않는다(범위 제외).
   - Skill 패키징은 터미널에서도 가능하므로 추가 진행한다: `pipeline/generate_report.py`를 Claude Code Skill(`/명령`)로 감싸 "새 CSV만 넣으면 재현 가능한 형태"로 제출물에 포함한다(8단계에서 수행).

4. **제약 조건 (CLAUDE.md 원문, 5번 항목으로 일부 갱신됨)**
   - Claude Code(터미널) 또는 Cowork(채팅)만 사용, 별도 API 키 없이 대화 내에서 분류·분석 완료
   - 이메일·채널톡 실시간 연동 제외 (제공된 voc.csv만 원본 데이터로 사용)
   - ~~Streamlit 등 서버 기반 대시보드/웹 UI 구현 제외~~ → 5번 항목에서 갱신: 현장 안내로 Streamlit 배포 허용됨

5. **[갱신] 제출 기준을 CLAUDE.md 채점표 대신 problem.md "제출 가이드"로 전환, Streamlit 허용**
   - 현장에서 Streamlit 배포가 가능하다는 안내를 받아, 기존 "대시보드 제외" 제약은 더 이상 유효하지 않음.
   - 이에 따라 최종 제출물은 CLAUDE.md의 100/130/160점 채점표가 아니라 **problem.md의 제출 가이드(기본/권장/도전)** 를 기준으로 완성도를 판단한다.
   - **기본(필수)**: 분류표+인사이트 파일 1개, output/ 저장 → `output/voc-report.md`로 충족.
   - **권장**: (a) Streamlit 대시보드 또는 HTML 시각화 파일 → 기존 HTML(`voc-report.html`)에 더해 **Streamlit 대시보드를 로컬 실행 수준으로 신규 구축**(10단계). GitHub/Streamlit Cloud 배포는 이번 범위에 포함하지 않음. (b) 데이터 정제 과정 문서화 → `decisions.md`로 충족.
   - **도전**: (a) 구글시트 자동 기입 연동(Cowork 커넥터 활용) → **범위에서 제외**. 이 환경(Claude Code 터미널)에는 Cowork 커넥터도 구글시트 연동용 MCP 도구도 없어 기술적으로 수행 불가. (b) Skill 패키징 → `.claude/skills/voc-report/SKILL.md`로 충족(8단계 완료).
   - 9단계 자가 점검에서 발견했던 "노션/구글독스 공개 링크 제출(10점)" 항목은 CLAUDE.md 채점표 고유 항목이라, 이 갱신에 따라 더 이상 추적하지 않는다.

## 참고 데이터 이슈 (voc.csv, 45건 → 정제 후 44건)

- 날짜 형식 3종 혼용: `2026-05-02` / `2026/05/06` / `5월 4일` → ISO(`YYYY-MM-DD`)로 통일
- 채널 결측 2건: id 032, 035 → 임의 추정 금지, 결측 유지
- 중복행 1건: id 031 = id 001 (완전 동일) → 제거, 44건 기준 집계
- 유형 오입력 1건: id 043 — 내용은 불만(보고서 커스터마이징 제한 불만+개선요청 혼재)인데 원본 유형은 칭찬으로 잘못 태깅 → 재분류 근거 기록

## 수행 계획 (9단계)

### 1단계 — 원본 데이터 정제
- `data/voc.csv` 45건 로드 → 날짜 통일, 결측 처리, 중복 제거, 오분류 수정
- 모든 처리 판단 근거를 `decisions.md`에 기록

### 2단계 — 분류 기준 설계 및 분류
- 4유형(불만/기능 요청/칭찬/일반 문의) 판별 기준을 먼저 명문화
- 경계 케이스(불만+요청 혼합 등) 처리 원칙 수립 → decisions.md 기록
- 정제된 44건 전수 분류 → 분류표 작성

### 3단계 — 파이프라인 구축 (Standard 요건 선반영)
- CSV 경로를 입력받아 정제 → 분류 → 집계 → **`voc-report.md` + `voc-report.html`**을 함께
  자동 생성하는 스크립트 또는 Claude Code Skill(`/명령`)로 구현
- 원본 voc.csv로 먼저 정확도 검증

### 4단계 — 더미 데이터 생성
- 원본 45건의 컬럼 구조·문체·용어(CBAM/CSRD/Scope/PCF 등)를 참고해 행 수를 확장한 더미 CSV 생성
  (예: 150~300건, 4유형 분포·날짜 형식 혼용·결측·중복·오분류 비율을 원본과 유사하게 재현)
- 생성 근거(규모, 분포, 의도)를 decisions.md에 기록, 리포트에도 가공 데이터임을 명시

### 5단계 — 파이프라인 재현성 검증
- 3단계 파이프라인에 더미 CSV 입력 → md/HTML 모두 동일 품질로 자동 생성되는지 확인
- 이 결과를 리포트의 "[Standard] 파이프라인 사용법" 섹션 근거로 사용
- 주간 리포트 섹션·지표 설계(CS팀/제품팀 관점 근거 포함) 작성

### 6단계 — 인사이트 도출
- 핵심 인사이트 3개는 **원본 44건 기준**으로 CSRD·CBAM 맥락과 연결해 도출 (단순 수치 나열 금지, 비즈니스 해석 포함)
- 필요 시 더미 데이터의 대규모 패턴은 보조 근거로만 인용

### 7단계 — Challenge: 제품 개선 기획안
- 원본 VoC의 요청/불만 유형을 근거로 기획안 1~2건 작성 (문제 정의 / 근거 VoC / 개선 제안 / 우선순위)
- 우선순위 판단 프레임워크(가중치 등)는 직접 설계하고, 더미 데이터의 대규모 빈도로 보강
- 기획안 양식·우선순위 기준 설계 근거를 decisions.md에 기록

### 8단계 — 산출물 생성
- `output/voc-report.md`: `output/template.md` 형식에 맞춰 Basic~Challenge 전 섹션 작성 (제출 형식 채점의 핵심 파일)
- `output/voc-report.html`: 정적 단일 HTML 시각화 리포트 (서버/API 없는 순수 HTML/CSS/JS)
  - `output/sample-basic.html` / `sample-standard.html` / `sample-challenge.html`의 구성 요소를 참고해
    디자인은 자유롭게, 아래 내용은 반드시 포함:
    - Basic: 유형별 통계 카드, 막대 차트, 필터 가능한 분류표, 인사이트 카드, 의사결정 로그
    - Standard: 파이프라인 다이어그램, 사용법, 주간 리포트 샘플
    - Challenge: 우선순위 판단 기준(가중치), 기획안 카드(문제정의/근거VoC/우선순위 점수), 로드맵 테이블
- Skill 패키징(problem.md "도전" 항목 대응): `pipeline/generate_report.py`를 Claude Code Skill(`/명령`)로 감싸
  새 CSV 경로만 지정하면 정제→분류→집계→리포트가 재현되도록 패키징

### 9단계 — 자가 점검
- CLAUDE.md 채점 기준(분류 정확도/집계/인사이트/제출형식 + Standard/Challenge 가산 항목) 대조 점검
- decisions.md에 주요 판단 근거 누락 없는지 확인
- md/HTML 두 산출물 모두 완성됐는지 최종 확인
- (점검 결과 "노션/구글독스 공개 링크" 갭 발견 → 5번 범위 확정 사항에 따라 problem.md 제출 가이드로 전환, 해당 갭은 더 이상 추적하지 않기로 함)

### 10단계 — Streamlit 대시보드 구축 (권장 항목, 로컬 실행)
- `dashboard/app.py` 작성: `output/voc-classification.csv`를 읽어 voc-report.md/.html과 동일한 내용을 표시
  - 유형별 통계, 필터 가능한 분류표, 인사이트 3개, Challenge 우선순위 프레임워크·기획안 2건
- `streamlit run dashboard/app.py`로 로컬 정상 구동까지 확인 (배포는 범위 외)
- 구축 근거·구성 결정을 decisions.md에 기록

## 진행 상태 체크리스트

- [x] 1단계 — 원본 데이터 정제 (`data/voc_cleaned.csv`, 44건, decisions.md 기록 완료)
- [x] 2단계 — 분류 기준 설계 및 분류 (`output/voc-classification.csv`, 44건 분류 완료, decisions.md 기록 완료)
- [x] 3단계 — 파이프라인 구축 (`pipeline/generate_report.py`, 원본 데이터 검증 43/44건=97.7% 일치, decisions.md 기록 완료)
- [x] 4단계 — 더미 데이터 생성 (`data/voc_dummy.csv`, 200건, `scripts/generate_dummy_voc.js`, 파이프라인 실행 검증 완료, decisions.md 기록 완료)
- [x] 5단계 — 파이프라인 재현성 검증 (더미 200건 재현 확인, `content/weekly-report-design.md` 작성, decisions.md 기록 완료)
- [x] 6단계 — 인사이트 도출 (`content/insights.md` 3개 작성, decisions.md 기록 완료)
- [x] 7단계 — Challenge 기획안 (`content/proposals.md`, 우선순위 프레임워크 + 기획안 2건 + 가중치 근거 보강 + 민감도 분석, decisions.md 기록 완료)
- [x] 8단계 — 산출물 생성 (`output/voc-report.md`, `output/voc-report.html`, `.claude/skills/voc-report/SKILL.md`, decisions.md 기록 완료)
- [x] 9단계 — 자가 점검 (problem.md 제출 가이드 대조, 노션/구글독스 링크 갭은 5번 갱신에 따라 추적 종료)
- [x] 10단계 — Streamlit 대시보드 구축 (`dashboard/app.py`, 로컬 구동 검증 완료, decisions.md 기록 완료)

## 완료된 후속 항목 (2026-07-01)

- **구글시트 자동 기입 연동 (problem.md 도전 항목)**: `mcp-gsheets`를 user 스코프로 재등록 후 새 세션에서 도구 로드 확인, `output/voc-classification.csv`(44건)를 스프레드시트 `1HB-bSWh1XamvMlWEz4W8zD2qwtPLBQ7bDKK_P8wE2b0`(시트명 `시트1`, `A1:G45`)에 기입 완료.
- **노션 공개 링크 제출 (CLAUDE.md 채점표 "제출 형식" 10점 보완)**: `output/voc-report.md` 전체를 Notion 페이지에 마크다운 붙여넣기로 옮기고, 2절 분류표는 중복을 피해 위 구글시트 링크로 대체. 페이지: https://www.notion.so/VoC-39021ff9e2678010b8bce7abfabb7905 — **단, "웹에 게시" 공개 설정 및 시크릿 창에서의 접근 가능 여부는 사용자가 직접 최종 확인 필요** (WebFetch로는 Notion의 클라이언트 렌더링 특성상 자동 검증이 안 됨).

## 별도 트랙 (현재 착수 보류)

**Track B — 포트폴리오 확장 (채점 무관, Track A 완료 후 진행)**
- Supabase 적재, GitHub 레포 구성 후 Streamlit Community Cloud 배포(공개 URL 확보)
- 10단계에서 만든 로컬 Streamlit 대시보드(`dashboard/app.py`)를 그대로 재사용해 배포까지 확장하는 것으로 범위 축소(신규 대시보드를 별도로 만들 필요 없음)
- 별도 디렉토리로 분리해 이 과제 제출 폴더(`output/`)와 섞이지 않도록 관리
