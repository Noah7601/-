# STEP 4 — Claude JSON Schema

> Claude(Normalize→Understand→Render 3-Pass, STEP5에서 프롬프트 설계) 가 항상 이 형태로만 응답한다. n8n은 이 JSON을 그대로 파싱해서 Notion에 쓴다. 브리프가 요구한 9개 최상위 객체(recording, people, projects, decisions, tasks, summary, template, confidence, source_evidence)를 전부 포함.

## 핵심 원칙 — 책임 분리 (환각 방지의 절반은 설계로 막는다)
- **Claude는 ID를 절대 생성하지 않는다.** `recording_id`는 n8n이 만들어서 입력으로 넘겨주고, Claude는 그걸 그대로 echo만 한다. `decision_id`/`task_id`도 Claude 출력에 없음 — n8n이 Notion에 insert할 때 생성(STEP2 전략 그대로).
- **Decision/Task에는 evidence(transcript 발췌 + timestamp)가 필수.** 없으면 그 항목 자체를 만들지 않는다 (아래 Validation 참조).
- **배열은 비어 있어도 된다.** 개인 아이디어 녹음이면 `decisions: []`, `tasks: []`가 정상. "최소 1개는 만들어라" 같은 압박을 프롬프트에 절대 넣지 않음(STEP5에서 강제).

---

## 전체 구조 (9개 최상위 객체)

```json
{
  "recording": { ... },
  "source_evidence": { ... },
  "template": { ... },
  "confidence": { ... },
  "people": [ ... ],
  "projects": [ ... ],
  "summary": { ... },
  "decisions": [ ... ],
  "tasks": [ ... ]
}
```

## 예시 (실제 녹음 기반 — "09-17 회의: 화상회의 접속 오류로 안건 논의 불가", 6.5분)

```json
{
  "recording": {
    "recording_id": "REC-20260917-001",
    "title": "화상회의 접속 오류로 안건 논의 불가",
    "recording_type": "General Meeting",
    "duration_sec": 390,
    "recorded_at": "2026-09-16T23:59:14Z"
  },
  "source_evidence": {
    "drive_folder_id": "1xxxxxxxxxxxxxxxxxxxxxxx",
    "audio_url": "https://drive.google.com/file/d/.../view",
    "transcript_url": "https://drive.google.com/file/d/.../view",
    "transcript_source": "transcript.json"
  },
  "template": {
    "template_id": "TPL-GENERAL-01",
    "template_name": "General Meeting",
    "router_confidence": 0.58
  },
  "confidence": {
    "overall": 0.58,
    "needs_human_review": true,
    "reasons": ["화상회의 접속 오류로 실제 안건 논의가 이루어지지 않아 추출할 정보가 거의 없음"]
  },
  "people": [
    { "name": "김철수", "role": null, "organization": null, "confidence": 0.8, "mentioned_as": "철수씨" }
  ],
  "projects": [],
  "summary": {
    "executive_summary": "화상회의 접속 오류로 예정된 안건을 논의하지 못하고 다음 일정을 다시 잡기로 함.",
    "key_topics": ["화상회의 접속 오류"],
    "open_questions": ["다음 회의 일정을 언제로 잡을지"],
    "important_quotes": [],
    "follow_up": ["화상회의 재접속 후 안건 재논의"],
    "keywords": ["화상회의", "접속오류"]
  },
  "decisions": [],
  "tasks": [
    {
      "title": "화상회의 재접속 시도",
      "description": null,
      "owner": "김철수",
      "due_date": null,
      "project": null,
      "nature": "Suggested",
      "evidence": {
        "quote": "다시 한번 접속해볼게요",
        "timestamp_start": 142.0,
        "timestamp_end": 145.0,
        "speaker": "김철수"
      },
      "confidence": 0.65
    }
  ]
}
```

> 이 예시의 `nature: "Suggested"`는 의도적 — "다시 한번 접속해볼게요"는 약한 확약이라 Committed로 올리지 않음. STEP5에서 Committed 판정 기준을 명확히 정의.

---

## JSON Schema (Draft-07)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ClaudeRecordingAnalysis",
  "type": "object",
  "required": ["recording", "source_evidence", "template", "confidence", "people", "projects", "summary", "decisions", "tasks"],
  "additionalProperties": false,
  "properties": {
    "recording": {
      "type": "object",
      "required": ["recording_id", "title", "recording_type", "duration_sec", "recorded_at"],
      "additionalProperties": false,
      "properties": {
        "recording_id": { "type": "string", "pattern": "^REC-\\d{8}-\\d{3}$", "description": "n8n이 입력으로 준 값을 그대로 echo. Claude가 생성하지 않음." },
        "title": { "type": "string" },
        "recording_type": { "type": "string", "enum": ["General Meeting","Sales Meeting","Customer Consultation","Phone Call","Brainstorming","Interview","Personal Idea","Project Meeting","Other"] },
        "duration_sec": { "type": "number", "minimum": 0 },
        "recorded_at": { "type": "string", "format": "date-time" }
      }
    },
    "source_evidence": {
      "type": "object",
      "required": ["drive_folder_id", "audio_url", "transcript_url", "transcript_source"],
      "additionalProperties": false,
      "properties": {
        "drive_folder_id": { "type": "string" },
        "audio_url": { "type": "string", "format": "uri" },
        "transcript_url": { "type": "string", "format": "uri" },
        "transcript_source": { "type": "string", "const": "transcript.json" }
      }
    },
    "template": {
      "type": "object",
      "required": ["template_id", "template_name", "router_confidence"],
      "additionalProperties": false,
      "properties": {
        "template_id": { "type": "string" },
        "template_name": { "type": "string" },
        "router_confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "confidence": {
      "type": "object",
      "required": ["overall", "needs_human_review", "reasons"],
      "additionalProperties": false,
      "properties": {
        "overall": { "type": "number", "minimum": 0, "maximum": 1 },
        "needs_human_review": { "type": "boolean" },
        "reasons": { "type": "array", "items": { "type": "string" } }
      }
    },
    "people": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "confidence", "mentioned_as"],
        "additionalProperties": false,
        "properties": {
          "name": { "type": "string" },
          "role": { "type": ["string", "null"] },
          "organization": { "type": ["string", "null"] },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "mentioned_as": { "type": "string", "description": "transcript 원문 표현 그대로" }
        }
      }
    },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "confidence", "mentioned_as"],
        "additionalProperties": false,
        "properties": {
          "name": { "type": "string" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "mentioned_as": { "type": "string" }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["executive_summary", "key_topics", "open_questions", "important_quotes", "follow_up", "keywords"],
      "additionalProperties": false,
      "properties": {
        "executive_summary": { "type": "string" },
        "key_topics": { "type": "array", "items": { "type": "string" } },
        "open_questions": { "type": "array", "items": { "type": "string" } },
        "important_quotes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text", "speaker", "timestamp"],
            "properties": {
              "text": { "type": "string" },
              "speaker": { "type": ["string", "null"] },
              "timestamp": { "type": "number" }
            }
          }
        },
        "follow_up": { "type": "array", "items": { "type": "string" } },
        "keywords": { "type": "array", "items": { "type": "string" } }
      }
    },
    "decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "description", "decision_date", "project", "people", "evidence", "confidence"],
        "additionalProperties": false,
        "properties": {
          "title": { "type": "string" },
          "description": { "type": "string" },
          "decision_date": { "type": ["string", "null"], "format": "date" },
          "project": { "type": ["string", "null"] },
          "people": { "type": "array", "items": { "type": "string" } },
          "evidence": { "$ref": "#/$defs/evidence" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "description", "owner", "due_date", "project", "nature", "evidence", "confidence"],
        "additionalProperties": false,
        "properties": {
          "title": { "type": "string" },
          "description": { "type": ["string", "null"] },
          "owner": { "type": ["string", "null"] },
          "due_date": { "type": ["string", "null"], "format": "date" },
          "project": { "type": ["string", "null"] },
          "nature": { "type": "string", "enum": ["Committed", "Suggested"], "description": "실제 확약 발화가 있었을 때만 Committed. STEP5 규칙으로 강제." },
          "evidence": { "$ref": "#/$defs/evidence" },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    }
  },
  "$defs": {
    "evidence": {
      "type": "object",
      "required": ["quote", "timestamp_start", "timestamp_end", "speaker"],
      "additionalProperties": false,
      "properties": {
        "quote": { "type": "string", "description": "transcript.json에서 그대로 발췌한 문장. Claude가 재구성하지 않음." },
        "timestamp_start": { "type": "number", "minimum": 0 },
        "timestamp_end": { "type": "number", "minimum": 0 },
        "speaker": { "type": ["string", "null"] }
      }
    }
  }
}
```

---

## Validation 규칙 (n8n이 Claude 응답을 받은 직후 수행 — STEP6에서 노드로 구현)
1. 위 JSON Schema로 구조 검증 → 실패하면 재시도 1회, 또 실패하면 Failed Queue
2. `recording.recording_id`가 입력으로 준 값과 **정확히 일치**하는지 확인 (Claude가 바꿔치기했으면 거부)
3. `decisions[].evidence.quote`, `tasks[].evidence.quote`가 **실제 transcript.json 안에 존재하는 문자열**인지 퍼지 매칭으로 확인 (완전 불일치 = 환각 의심 → Needs Review로 강제 전환)
4. `confidence.overall` 또는 개별 항목 confidence가 임계값(예: 0.7) 미만이면 → Notion Status를 자동으로 `Needs Review`로 설정

## Notion 매핑 (STEP2와 연결)

| JSON 경로 | Notion 대상 |
|---|---|
| `recording.*` | Recordings DB 속성 |
| `confidence.overall` | Recordings.Confidence |
| `confidence.needs_human_review` | true면 Recordings.Status = `Needs Review` |
| `template.template_id` | Recordings.Template (Relation, Template ID로 검색) |
| `summary.executive_summary` | Recordings.Summary + 페이지 본문 Executive Summary |
| `summary.key_topics/open_questions/important_quotes/follow_up` | 페이지 본문 각 섹션 |
| `people[]` | People DB upsert (이름으로 검색 후 없으면 생성) 후 Recordings.People 관계 연결 |
| `projects[]` | Projects DB upsert 후 Recordings.Project 관계 연결 |
| `decisions[]` | Decisions DB에 각각 생성 (Decision ID는 n8n 생성), Source Recording 관계 연결 |
| `tasks[]` | Tasks DB에 각각 생성 (Task ID는 n8n 생성), Nature/Status 그대로 매핑 |

## V1/V2
- V1: 위 스키마 그대로.
- V2 후보: `decisions[].superseded_by`(결정이 나중에 뒤집힌 경우 추적), `tasks[].priority`, `important_quotes[].emotion_tag` 등 — 지금은 과설계 방지로 보류.

## 다음 액션
- [ ] STEP 5 — Prompt Architecture (Normalize/Understand/Render 각 Pass의 system prompt, 환각 방지 규칙 구체화)
