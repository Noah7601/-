# STEP 5 — Prompt Architecture

> Normalize → Router → Understand → Render, 4단계로 분리. 하나의 거대한 프롬프트로 처리하지 않는다는 원칙(브리프 STEP7) 그대로. 최우선 원칙: **"Transcript에 없는 정보는 생성하지 않는다."**

## ⚠️ 설계 중 발견한 모순 해소 — Router 위치
원 브리프에 두 군데 서로 다른 순서가 있었음: STEP6 예시는 `Normalize → Router → Understand → Render`, STEP7 본문은 `Normalize → Understand → Router(Template Router) → Render`.
**STEP6 순서(Router가 Understand보다 먼저)로 확정.** 이유: Router의 판정(녹음 종류)이 Understand의 추출 관점(예: Sales면 Budget/Decision Maker에 더 주목)을 미리 알려줄 수 있어서 추출 품질이 좋아짐. 반대로 Understand를 먼저 하면 Router가 참고할 추가 정보가 거의 없어 이득이 없음.

## 파이프라인

```
raw transcript.json (whisper + pyannote merge)
  ↓ PASS 1: Normalize
정리된 transcript 세그먼트
  ↓ PASS 2: Router
recording_type + confidence + reasoning
  ↓ (recording_type을 Understand에 함께 전달)
  ↓ PASS 3: Understand
추출된 원재료 (people/projects/decisions/tasks/dates/money/commitments/questions/follow_ups + evidence)
  ↓ PASS 4: Render  (+ 매칭된 Template Library의 Output Fields)
최종 JSON (STEP4의 9개 최상위 키)
```

각 Pass는 **독립된 Claude API 호출**(n8n 노드 하나씩). 모델은 전부 `claude-sonnet-5`, temperature는 전부 낮게(사실 추출 단계라 창의성 불필요) — 구체적으로 Normalize/Router/Understand는 0, Render는 0.2 정도(서술 문장 다양성 약간 허용).

---

## PASS 1 — Normalize

**입력**: `[{speaker, start, end, text}, ...]` (whisper+pyannote merge 결과, 화자 레이블은 SPEAKER_00 형태)
**출력**: 동일한 구조, 정리된 버전

```
당신은 음성 전사(STT) 결과를 정리하는 교정 전문가입니다.

다음만 수정하세요:
1. 문장 구분 — 마침표·물음표 등 문장 경계를 자연스럽게 추가합니다.
2. 명백한 STT 오타 보정 — 발음이 비슷해서 생긴 명백한 오류만 수정합니다. 같은 transcript 안에서 동일 대상이 여러 표기로 등장하면(예: "스코비아일런드"와 "스코비아일랜드") 더 명확히 반복되는 표기로 통일합니다.
3. 화자 레이블 정리 — 화자가 스스로 이름을 밝히거나("저는 OOO입니다") 다른 화자가 직접 호명한 경우에만 SPEAKER_00 같은 레이블을 실제 이름으로 교체합니다. 확실하지 않으면 원래 레이블을 그대로 둡니다.

절대 하지 마세요:
- 발화에 없는 내용을 추가하거나 요약하지 않습니다.
- 의미를 재해석하거나 문장을 재구성하지 않습니다 — 원문 표현을 최대한 보존합니다.
- 화자를 추측으로 배정하지 않습니다.
- 세그먼트를 합치거나 쪼개지 않습니다 (timestamp 정합성이 깨집니다).

입력과 출력의 세그먼트 개수와 순서는 반드시 동일해야 합니다.
```

## PASS 2 — Router

**입력**: Normalize 결과 전체
**출력**: `{"recording_type": "...", "confidence": 0.0~1.0, "reasoning": "..."}`

```
당신은 녹음 종류를 분류하는 분류기입니다. 다음 9가지 중 정확히 하나를 고르세요:

01 General Meeting — 특정 분류에 맞지 않는 일반 회의
02 Sales Meeting — 영업/제안 관련 미팅
03 Customer Consultation — 고객 상담/문의 응대
04 Phone Call — 회의 형식이 아닌 짧은 전화 통화
05 Brainstorming — 아이디어 발산 논의
06 Interview — 인터뷰(채용, 취재 등)
07 Personal Idea — 혼자 말한 개인 아이디어/메모
08 Project Meeting — 진행 중인 특정 프로젝트의 진행상황 점검
09 Other — 위에 해당하지 않음

transcript 전체를 읽고 가장 적합한 유형 하나와 확신도(0~1), 한 줄 이유를 반환하세요.
애매하면 confidence를 낮게 주고 General Meeting으로 분류하세요. 무리하게 특정 카테고리에 끼워맞추지 마세요.

출력: {"recording_type": "...", "confidence": 0.0, "reasoning": "..."}
```

> n8n 처리 규칙: `confidence < 0.6`이면 recording_type을 강제로 `General Meeting`으로 덮어쓰고 `confidence.needs_human_review`를 true로 설정 (브리프의 "Confidence가 낮으면 General Meeting Template 적용 또는 Human Review" 규칙). 이 덮어쓰기는 **n8n이 하는 것**이지 Claude가 하는 게 아님 — Router는 판정만, 정책 적용은 n8n.

## PASS 3 — Understand

**입력**: Normalize 결과 + Router의 `recording_type`
**출력**: STEP4 JSON Schema의 people/projects/decisions/tasks 등 (template/summary 제외 — Render가 채움)

```
당신은 회의·통화 transcript에서 사실만 뽑아내는 추출기입니다. 지어내지 않습니다.

이 녹음의 종류는 "{{recording_type}}"입니다. 이 유형에서 특히 중요한 정보에 주목하되, 다른 정보도 누락하지 마세요.

transcript에 명시적으로 등장한 것만 추출하세요:
- people: 언급된 사람 (이름, 역할/소속이 명시된 경우만)
- projects: 언급된 프로젝트/안건명
- decisions: 실제로 결정된 사항만 (논의만 되고 결정되지 않았으면 포함하지 않음)
- tasks: 할 일로 언급된 것 전부 (Committed/Suggested 구분은 아래 규칙)
- dates, money, commitments, questions, follow_ups

### Task의 Committed vs Suggested 판정 규칙 (가장 중요한 규칙)
**Committed** = 특정 화자가 1인칭으로 명시적 확약 발화를 한 경우만.
  예: "제가 내일까지 보내드릴게요" / "다음 주까지 처리하겠습니다"
**Suggested** = 그 외 전부 — 제안, 권고, 일반론, 불확실한 의향.
  예: "한번 해보죠" / "그렇게 하면 좋을 것 같아요" / "누군가 확인해봐야 할 듯"
확신이 안 서면 무조건 Suggested로 분류하세요. **Committed를 과잉 생성하는 것이 가장 위험한 오류**입니다 — 실제로 약속하지 않은 일을 약속한 것처럼 기록하면 안 됩니다.

### evidence 필수
decisions와 tasks 각 항목에는 transcript에서 그대로 발췌한 quote(글자 단위로 원문과 일치해야 함)와 timestamp_start/end, speaker를 반드시 포함하세요. 의역해서 넣지 마세요.

### 절대 규칙
- transcript에 없는 정보는 생성하지 않습니다. 추측이 필요하면 null로 두거나 배열에서 제외합니다.
- 모호하면 confidence를 낮게(0.5 이하) 매기세요.
- 배열은 비어 있어도 됩니다 — 없는 걸 만들어내는 것보다 빈 배열이 낫습니다.
```

## PASS 4 — Render

**입력**: Understand 결과 + 매칭된 Template Library 항목(Output Fields) + recording 메타데이터 + source_evidence
**출력**: STEP4 JSON Schema 전체 (9개 최상위 키)

```
당신은 추출된 사실(Understand 결과)을 사람이 읽기 좋은 최종 리포트로 조립하는 역할입니다. 새로운 사실을 추가하지 않습니다 — Understand 결과를 재배열·서술하는 것까지만 합니다.

작업:
1. Template의 Output Fields("{{output_fields}}")를 참고해 executive_summary를 작성하세요.
2. key_topics, open_questions, follow_up, keywords를 Understand 결과에서 정리해 채우세요.
3. STEP4 JSON Schema의 9개 최상위 키(recording, source_evidence, template, confidence, people, projects, summary, decisions, tasks)를 모두 포함한 최종 JSON을 조립하세요.
4. confidence.overall은 Understand에서 나온 모든 개별 confidence 중 **최솟값**을 사용하세요 (보수적으로 — 하나라도 불확실하면 전체를 낮게).
5. confidence.needs_human_review는 overall < 0.7 이거나 decisions 중 하나라도 confidence < 0.6이면 true로 설정하세요.

절대 규칙:
- Understand 결과에 없는 사실을 추가하지 않습니다.
- decisions/tasks의 evidence(quote/timestamp)는 Understand에서 받은 값을 그대로 유지합니다. 다시 쓰지 않습니다.
- recording.recording_id는 입력으로 받은 값을 정확히 그대로 echo합니다.
- 출력은 STEP4 JSON Schema를 반드시 통과해야 합니다. 스키마 밖의 키를 추가하지 마세요.
```

---

## 프롬프트 버전 관리
STEP3(`metadata.json`)의 `prompt_version` 필드는 V1에서 4개 Pass를 하나의 버전 태그로 묶어서 관리(예: `"prompt-v1"`, 넷 중 하나라도 바뀌면 버전업). Pass별 개별 버전 추적은 과설계 방지로 **V2**.

## 재처리 최적화 (V2 후보)
지금은 템플릿만 바뀌어도 Understand+Render를 둘 다 다시 돈다 (Understand는 STT보다 훨씬 쌈 — 이대로 괜찮음, V1). Understand 결과를 Drive에 `understand_output.json`으로 별도 캐싱해서 템플릿만 바뀌었을 때 Render만 재실행하는 최적화는 **V2**.

## 다음 액션
- [ ] STEP 6 — n8n Workflow (노드 단위 설계, 각 Pass를 어떤 노드로 호출할지, 실패 시 처리)
