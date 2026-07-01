---
name: voc-report
description: 리뉴어스랩 VoC CSV(id·date·channel·customer_type·content·keyword_hint 컬럼)를 정제→분류→집계해 voc-report.md/voc-report.html을 자동 생성한다. "VoC 리포트 만들어줘", "새 CSV로 리포트 재생성해줘" 같은 요청에 사용.
---

# VoC 리포트 생성 스킬

`pipeline/generate_report.py`를 감싸, 새 VoC CSV가 들어와도 정제→분류→집계→리포트(md+html) 생성을 동일한 절차로 재현하는 스킬이다.

## 입력 전제

CSV는 최소 아래 컬럼을 포함한다:
- `id`, `date`(`YYYY-MM-DD`/`YYYY/MM/DD`/`M월 D일` 혼용 가능), `channel`(결측 허용), `customer_type`, `content`, `keyword_hint`
- 이미 검증된 유형 라벨이 있다면 `type` 컬럼(불만/기능 요청/칭찬/일반 문의 중 하나)을 추가해도 된다 — 있으면 그 값을 그대로 쓰고, 없으면 규칙 기반 분류기가 자동으로 채운다.

## 절차

### 1. 리포트 생성

```
python pipeline/generate_report.py <입력 CSV 경로> <출력 디렉터리> \
  --insights content/insights.md \
  --proposals content/proposals.md \
  --decisions-summary content/decisions-summary.md \
  --pipeline-usage content/weekly-report-design.md \
  --source-label "<리포트에 표시할 원본 파일명>"
```

- `--insights`/`--proposals`/`--decisions-summary`/`--pipeline-usage`는 생략 가능(생략 시 해당 섹션은 "미입력"으로 표시됨). 새 데이터셋으로 인사이트·기획안을 새로 도출했다면 해당 내용을 담은 md 파일 경로로 교체한다.
- 원본 리뉴어스랩 데이터로 재현하려면 `data/voc.csv`(자동 규칙 기반 분류, 정확도 참고용) 또는 `output/voc-classification.csv`(검증된 수동 분류, 그래디드 제출본과 동일 결과)를 입력으로 쓴다.

### 2. 결과 확인

`<출력 디렉터리>/voc-report.md`, `voc-report.html`이 생성된다. 콘솔에 출력되는 유형별 건수·비율을 원본 분류(`output/voc-classification.csv`)와 대조해 이상 여부를 확인한다.

### 3. 새로운 날짜 형식·분류 키워드가 나오면

- 날짜 형식 인식 실패: `pipeline/generate_report.py`의 `ISO_DATE_RE`/`SLASH_DATE_RE`/`KOREAN_DATE_RE` 정규식에 실제 등장한 패턴을 추가한다(추측 금지, 실제 문자열 기준).
- 분류 오분류 발견: `PRAISE_STEMS`/`COMPLAINT_STEMS`/`REQUEST_STEMS` 키워드 리스트에 새 근거를 추가하되, 기존 44건 검증 결과(43/44=97.7% 일치, decisions.md 3단계 기록)가 깨지지 않는지 재실행해 확인한다.

## 주의

- 인사이트·기획안·우선순위 가중치는 스크립트가 자동 생성하지 않는다 — 사람이 판단해 md 파일로 작성한 뒤 인자로 전달한다.
- 분류 기준이나 우선순위 가중치를 바꿔야 하면 임의로 수정하지 않고 먼저 사용자와 합의한 뒤 `decisions.md`에 근거를 기록한다.
