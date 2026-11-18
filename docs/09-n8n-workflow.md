# STEP 6 — n8n Workflow (노드 단위 설계)

> 트리거는 원 브리프의 "Google Drive Trigger"가 아니다 — 소스가 PLAUD MCP 폴링으로 바뀌었기 때문(STEP3 반영). 순서는 Cron → PLAUD 수집 → Drive 저장 → 로컬 Whisper/pyannote → Claude 4-Pass → Validate → Notion Upsert.

## ⚠️ STEP2 보정 — Plaud File ID 필드 추가 (방금 실제 Notion에도 반영함)
Recordings DB에 **Plaud File ID**(Text) 속성을 추가했다. Recording ID(`REC-YYYYMMDD-NNN`)는 날짜 기반이라 "이 PLAUD 원본 파일을 이미 처리했는지"를 판별하는 키가 될 수 없다 — 그래서 PLAUD의 안정적인 파일 id를 별도로 저장해야 한다. 이게 **1차 Idempotency 키**(PLAUD→수집 단계), Recording ID는 **2차 Idempotency 키**(Notion/Drive 쓰기 단계)로 역할이 다르다.

## 처리 방식
- **순차 처리** (Loop Over Items, batch size 1) — Claude/Notion API rate limit과 디버깅 단순성 때문에 V1은 병렬 처리 안 함.
- 외부 API 호출 노드(MCP, Drive, Claude, Notion) 전부 **Retry On Fail: 3회, 5초 지수backoff** 적용.
- 하나의 녹음이 실패해도 **배치 전체를 막지 않음** — 그 항목만 Status=Failed로 남기고 다음 항목 계속.

---

## 노드 시퀀스

| # | 노드 | 입력 | 출력 | 실패 시 |
|---|---|---|---|---|
| 1 | **Cron Trigger** (15~30분 간격) | - | 실행 시작 | - (다음 주기에 자연 재시도) |
| 2 | **MCP Client Tool: Plaud `list_files`** | - | 최근 녹음 목록 | 3회 재시도 → 계속 실패 시 알림(이메일/Slack) 후 이번 실행 중단, 다음 Cron이 자동 재시도 |
| 3 | **Notion: Recordings 조회** (Plaud File ID 전체 목록) | - | 이미 처리된 Plaud File ID 집합 | 재시도 3회 → 실패 시 이번 실행 중단(안전 쪽으로: 모르면 처리 안 함) |
| 4 | **Filter**: 2번 목록에서 3번에 없는 것만 | 목록 + 처리된 집합 | 신규 녹음 목록 | - |
| 5 | **Loop Over Items** (신규 녹음마다 아래 6~24 반복) | | | |
| 6 | **Function: Recording ID 생성** | recorded_at | `REC-YYYYMMDD-NNN` (당일 기존 개수+1을 Notion에서 조회해 NNN 결정) | Notion 조회 실패 시 재시도 3회 → 실패하면 이 항목 skip, Failed 처리(아래 "에러 처리" 참조) |
| 7 | **MCP Client Tool: Plaud `get_file`** | plaud_file_id | presigned_url (24h 유효, **다운로드 직전에 새로 호출** — list 때 값 재사용 안 함) | 재시도 3회 → 실패 시 항목 Failed |
| 8 | **HTTP Request**: 오디오 다운로드 | presigned_url | 오디오 바이너리 | 재시도 3회 → 실패 시 항목 Failed |
| 9 | **Google Drive: 폴더 검색/생성** (search-first) | Recording ID | `PLAUD Ledger/YYYY/MM/REC-.../` 폴더 id | 재시도 3회 → 실패 시 항목 Failed |
| 10 | **Google Drive: audio.<ext> 업로드** | 오디오 바이너리 + 폴더id | audio 파일 url | 재시도 3회 → 실패 시 항목 Failed |
| 11 | **Execute Command: whisper.cpp** (`large-v3`) | audio.<ext> | whisper 세그먼트(JSON, timestamp 포함) | 1회 재시도(모델 재로드) → 실패 시 항목 Failed |
| 12 | **Execute Command: pyannote.audio** | audio.<ext> | 화자 구간(speaker segments) | 1회 재시도 → **실패해도 전체를 막지 않음**: speaker=null로 두고 계속 진행(저하된 모드, 아래 참조) |
| 13 | **Function: whisper+pyannote timestamp merge** | 11+12 결과 | `transcript.json` (`[{speaker,start,end,text}]`) | 병합 로직 에러 시 speaker=null로 폴백, 경고 로그만 남기고 계속 |
| 14 | **Google Drive: transcript.json + transcript.txt 업로드** | 13 결과 | 파일 url들 | 재시도 3회 → 실패 시 항목 Failed |
| 15 | **Claude API: Normalize** (STEP5) | transcript.json | 정리된 세그먼트 | 재시도 2회(지수backoff) → 실패 시 항목 Failed |
| 16 | **Claude API: Router** (STEP5) | 15 결과 | `{recording_type, confidence, reasoning}` | 재시도 2회 → 실패 시 항목 Failed |
| 17 | **Function: Router 정책 적용** | 16 결과 | confidence<0.6이면 recording_type을 `General Meeting`으로 강제, `needs_review_hint=true` | - (로직 노드, 실패 없음) |
| 18 | **Notion: Template Library 조회** (Recording Type Match로 검색) | recording_type | 매칭된 Template(id, Output Fields) | 실패 또는 매칭 없음 → `General Meeting` 템플릿으로 폴백 |
| 19 | **Claude API: Understand** (STEP5) | 15 결과 + recording_type | people/projects/decisions/tasks 등 원재료 | 재시도 2회 → 실패 시 항목 Failed |
| 20 | **Claude API: Render** (STEP5) | 19 결과 + 18 템플릿 + 메타데이터 | STEP4 최종 JSON | 재시도 2회 → 실패 시 항목 Failed |
| 21 | **Code: JSON Schema 검증** (STEP4 Draft-07 스키마 + recording_id 일치 + evidence quote 퍼지매칭) | 20 결과 | 통과/실패 | **실패 시 Render(20번)를 에러 피드백과 함께 1회만 재시도** → 또 실패하면 항목을 Status=`Needs Review`로 Notion에 기록하고 중단(부분/오염 데이터는 절대 안 씀) |
| 22 | **Google Drive: claude_output.json + metadata.json 업로드** | 20 결과 + 파이프라인 버전 | 파일 url | 재시도 3회 → 실패해도 **Notion 기록은 계속 진행**(치명적이지 않음, 경고만) |
| 23 | **Notion: People/Projects Upsert** (이름으로 검색 후 없으면 생성) | 20 결과의 people[]/projects[] | 각 페이지 id 목록 | 재시도 3회 → 실패해도 **Recording 생성은 계속**, 해당 관계만 비워두고 Status=Needs Review로 표시 |
| 24 | **Notion: Recordings Search-then-Upsert** (Recording ID로 검색) | 모든 누적 결과 | Recordings 페이지 (Plaud File ID·Status·Confidence 포함) | 재시도 3회 → 실패 시 항목 Failed, 수동 확인 필요 |
| 25 | **Notion: Decisions 생성** (decisions[]마다 Decision ID 생성 후 검색-후-생성) | 20 결과의 decisions[] | Decisions 페이지들 | 재시도 3회 → 실패한 Decision만 skip, 나머지는 계속(부분 실패 허용) |
| 26 | **Notion: Tasks 생성** (tasks[]마다 Task ID 생성 후 검색-후-생성) | 20 결과의 tasks[] | Tasks 페이지들 | 25와 동일 |
| 27 | **Notion: Recordings Status 최종 갱신** | 모든 처리 결과 | `Completed` 또는 `Needs Review` | - |

---

## 에러 처리 정책 (브리프의 "실패 Queue" 요구사항)
**별도의 7번째 DB(Failed Queue)를 새로 만들지 않는다.** Recordings DB의 `Status = Failed` 필터 뷰 자체가 Failed Queue 역할을 한다 — 이미 있는 구조를 재사용하는 쪽이 DB를 하나 더 늘리는 것보다 낫다(과설계 방지).

| 실패 유형 | 처리 |
|---|---|
| 되돌릴 수 없는 실패 (오디오 다운로드 실패, Claude 전부 재시도 소진 등) | Recordings.Status = `Failed`, 간단한 에러 메시지를 Summary 필드에 기록 |
| 스키마 검증 실패 (환각 의심) | Recordings.Status = `Needs Review` — Failed가 아니라 Review. 데이터는 있지만 믿을 수 없다는 뜻이라 구분 |
| 부분 실패 (People/Project 연결만 실패) | Recordings.Status = `Needs Review`, Recording 자체는 생성됨 |
| pyannote 실패(화자분리만 안 됨) | 실패로 치지 않음 — speaker=null로 저하된 모드 계속 진행 (화자분리는 nice-to-have, 전사 자체가 핵심) |

**V2 후보**: 실패 건을 자동으로 n8n이 재시도하는 별도 "재처리 워크플로우"(Failed 상태인 Recording을 다시 큐에 넣기) — 지금은 사람이 Failed 뷰를 보고 수동으로 재실행. 과설계 방지.

## 다음 액션
- [ ] STEP 7 — MVP 구축 순서 (실제 테스트 가능한 최소 단위부터)
