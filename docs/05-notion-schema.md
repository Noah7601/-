# STEP 2 — Notion Schema (완성 + 실제 생성됨: Recordings · Projects · People · Decisions · Tasks · Template Library)

## ✅ 실제 Notion에 생성 완료 (SCOBYISLAND 워크스페이스, 2026-11-08)
컨테이너 페이지: [PLAUD Ledger](https://app.notion.com/p/4128d309896b81f99830f0e3426f9e04)

| DB | 링크 |
|---|---|
| People | https://app.notion.com/p/e15c18fc3cbd425e9609c0904499bf73 |
| Projects | https://app.notion.com/p/769f6bf4a5214116b28933227f1b06d1 |
| Template Library | https://app.notion.com/p/56f58f17a2f44c22b18121011f34454a |
| Recordings | https://app.notion.com/p/a7c59ade60de495983af5ca7f08e9924 |
| Decisions | https://app.notion.com/p/c458a081f1ba4f0781985056f1168534 |
| Tasks | https://app.notion.com/p/c8a0fc741d864aa4b596f4613cf653c8 |

아래 설계대로 전부 생성됨. Projects에는 Recording Count/Last Activity/Tasks Count 롤업, People에는 Projects 롤업(Recordings 경유)도 추가 완료.

> 워크스페이스: **SCOBYISLAND** (scobyisland@gmail.com, 확인됨). 실제 생성 가능한 수준으로 설계. V1(지금 만들 것)과 V2(나중에 추가할 것)를 구분함.

## 전역 원칙 — Unique ID 전략 (모든 DB 공통)
- **Recording ID / Decision ID / Task ID는 Notion이 아니라 n8n이 생성**한다. 형식: `PREFIX-YYYYMMDD-NNN` (NNN은 그날 해당 PREFIX 기준 일별 시퀀스).
- Notion의 네이티브 "ID" 속성(자동증가 정수)은 **쓰지 않는다** — 날짜 기반 포맷을 못 만들고, insert 전에 먼저 값이 필요하기 때문.
- 대신 **일반 텍스트(Text) 속성**으로 저장하고, n8n이 insert 전에 "이 ID가 이미 있는지" Notion API로 먼저 검색 → 있으면 update, 없으면 create.
- 이 방식 하나로 **Unique ID 전략 + Idempotency(중복 방지) 요구사항을 동시에 해결**한다.
- Template ID는 예외: 소수의 수동 관리 항목이라 사람이 직접 입력(`TPL-SALES-01` 등), 충돌 가능성 낮음.

---

## 1. Recordings (Master Ledger)

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Title | Title | 사람이 읽는 제목 (PLAUD 원제목 그대로) | V1 |
| Recording ID | Text | `REC-YYYYMMDD-NNN`, n8n 생성, 검색용 유니크 키 | V1 |
| Recorded At | Date (시간 포함) | 녹음 시작 시각 | V1 |
| Recording Type | Select | `General Meeting` `Sales Meeting` `Customer Consultation` `Phone Call` `Brainstorming` `Interview` `Personal Idea` `Project Meeting` `Other` (Template Router 01~09) | V1 |
| Status | Select | `Queued` `Transcribing` `Analyzing` `Needs Review` `Completed` `Failed` | V1 |
| Duration | Number (분) | | V1 |
| Project | Relation → Projects | | V1 |
| People | Relation → People | | V1 |
| Decisions | Relation (자동 역방향, Decisions.Source Recording에서 생성됨) | 직접 추가하지 않음 | V1 |
| Tasks | Relation (자동 역방향, Tasks.Source Recording에서 생성됨) | 직접 추가하지 않음 | V1 |
| Google Drive Audio URL | URL | | V1 |
| Transcript URL | URL | Drive 상의 transcript 파일 링크 | V1 |
| Template | Relation → Template Library | | V1 |
| Summary | Text | Executive Summary 짧은 버전(표에서 바로 보이게). 전체 내용은 페이지 본문에 | V1 |
| Keywords | Text (쉼표 구분) | ⚠️ Multi-select로 하면 태그가 끝없이 늘어나 옵션 리스트가 관리 불가능해짐 → V1은 Text, 통제된 태그 체계는 V2 | V1 |
| Claude Processed At | Date (시간 포함) | | V1 |
| Confidence | Number (0~1) | 낮으면 Status를 Needs Review로 분기 | V1 |
| Pipeline Version | Text | 예: `whisper-large-v3｜claude-sonnet-5｜prompt-v1｜tpl-v1` 한 줄로 단순화 | V1 |
| STT Engine / Claude Model / Prompt Version / Template Version (4개 분리 필드) | - | 위 Pipeline Version을 구조화된 필드로 쪼갠 버전. 지금은 과설계 | **V2** |

**페이지 본문 구조**(모든 Recording 페이지 공통, Claude가 렌더링): Executive Summary → Key Topics → Decisions → Action Items → Open Questions → Important Quotes → Follow-up → Full Transcript → Source

---

## 2. Projects

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Title | Title | 프로젝트명 | V1 |
| Status | Select | `Active` `On Hold` `Completed` `Archived` | V1 |
| Description | Text | | V1 |
| Recordings | Relation (자동 역방향, Recordings.Project에서 생성됨) | | V1 |
| People | Relation (자동 역방향, People.Projects 쪽에서 생성 — 3번 참조) | | V1 |
| Decisions | Relation (자동 역방향, Decisions.Project) | | V1 |
| Tasks | Relation (자동 역방향, Tasks.Project) | | V1 |
| Recording Count | Rollup (Recordings, Count) | | V1 |
| Last Activity | Rollup (Recordings.Recorded At, Latest) | | V1 |
| Open Tasks Count | Rollup (Tasks, 조건부 Count) | Notion 롤업은 조건 필터가 제한적 → V1은 전체 Tasks Count만, "미완료만 카운트"는 **V2**(Formula 보강 필요) | V1(단순)/V2(정교) |

---

## 3. People

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Name | Title | | V1 |
| Role/Title | Text | 예: "김대표, A사 대표" | V1 |
| Organization | Text | ⚠️ 별도 Companies DB로 분리하는 게 더 정교하지만 V1은 과설계 방지 차원에서 Text로 단순화 | V1 / 분리는 **V2** |
| Recordings | Relation → Recordings (여기가 정방향, Recordings.People의 역방향을 이게 만듦) | | V1 |
| Projects | **Rollup** (Recordings.Project 경유) | 별도 Relation을 또 만들지 않음 — People↔Projects 관계를 Relation으로 중복 관리하면 Recordings 쪽과 어긋날 위험이 있어 Rollup으로 파생시킴 | V1 |
| Decisions | Relation (자동 역방향, Decisions.People) | | V1 |
| Tasks (Owner로서) | Relation (자동 역방향, Tasks.Owner) | | V1 |

---

## 관계 지도 (어디가 "정방향"인지 — 중복 Relation 방지용)

| 정방향 Relation (직접 만드는 곳) | 역방향 (자동 생성, 손대지 않음) |
|---|---|
| Recordings.Project → Projects | Projects.Recordings |
| Recordings.People → People | People.Recordings |
| Recordings.Template → Template Library | Template Library.Recordings |
| Decisions.Project → Projects | Projects.Decisions |
| Decisions.People → People | People.Decisions |
| Decisions.Source Recording → Recordings | Recordings.Decisions |
| Tasks.Project → Projects | Projects.Tasks |
| Tasks.Owner → People | People.Tasks |
| Tasks.Source Recording → Recordings | Recordings.Tasks |

---

## 4. Decisions

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Title | Title | 짧은 결정 설명. 예: "A사 1차 제안가격 2,800만원" | V1 |
| Decision ID | Text | `DEC-YYYYMMDD-NNN`, n8n 생성 (Recording ID와 동일한 전략) | V1 |
| Decision Date | Date | | V1 |
| Project | Relation → Projects | | V1 |
| People | Relation → People | 결정에 관여/합의한 사람 | V1 |
| Source Recording | Relation → Recordings | 역추적의 핵심 | V1 |
| Evidence | Text | Transcript 발췌 또는 timestamp. "왜 이렇게 결정했지?"를 몇 년 뒤에도 답할 수 있게 하는 필드 | V1 |
| Confidence | Number (0~1) | | V1 |
| Review Status | Select | `Confirmed` `Needs Review` — 중요 결정은 사람이 확인할 Queue가 필요하다는 요구사항을 이 필드로 구현 | V1 |

## 5. Tasks

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Title | Title | 예: "수정 견적서 발송" | V1 |
| Task ID | Text | `TASK-YYYYMMDD-NNN`, n8n 생성 | V1 |
| Owner | Relation → People | | V1 |
| Due Date | Date | | V1 |
| Project | Relation → Projects | | V1 |
| Source Recording | Relation → Recordings | | V1 |
| **Nature** | Select | `Committed` `Suggested` — **가장 중요한 필드**. 대화에서 실제로 약속된 것과 Claude가 제안한 것을 반드시 구분. Claude가 Committed를 함부로 만들면 안 됨(프롬프트 규칙으로 강제, STEP5에서 다룸) | V1 |
| Status | **Status**(네이티브) | `Not Started` → `In Progress` → `Done` (+ `Blocked` 추가 가능) — Tasks는 Notion Status 타입의 전형적 용도라 Select 대신 Status 사용 | V1 |
| Evidence | Text | Transcript 발췌/timestamp (선택) | V1 |

## 6. Template Library

| Property | Notion 타입 | 설명 / 옵션 | V1/V2 |
|---|---|---|---|
| Template Name | Title | 예: "Sales Meeting" | V1 |
| Template ID | Text | 예: `TPL-SALES-01`. 소수 항목이라 **수동 입력** (n8n 자동생성 대상 아님) | V1 |
| Recording Type Match | Select | Recordings.Recording Type과 동일한 9종 목록 — Template Router가 이 필드로 매칭 | V1 |
| Output Fields | Text (여러 줄) | 템플릿이 뽑아야 할 항목 리스트. 예: "고객요구사항, Pain Points, Budget, Decision Maker, Competitors, Objections, Proposal, Next Step" | V1 |
| Version | Number | | V1 |
| Status | Select | `Active` `Draft` `Deprecated` | V1 |
| Recordings | Relation (자동 역방향, Recordings.Template) | | V1 |
| 템플릿 하나가 여러 Recording Type에 매칭 (Multi-select) | - | V1은 1 Template : 1 Type 가정. 여러 유형 매칭은 과설계 방지로 보류 | **V2** |

---

## 관계 지도 (최종, 6개 DB 전체)

| 정방향 Relation (직접 만드는 곳) | 역방향 (자동 생성, 손대지 않음) |
|---|---|
| Recordings.Project → Projects | Projects.Recordings |
| Recordings.People → People | People.Recordings |
| Recordings.Template → Template Library | Template Library.Recordings |
| Decisions.Project → Projects | Projects.Decisions |
| Decisions.People → People | People.Decisions |
| Decisions.Source Recording → Recordings | Recordings.Decisions |
| Tasks.Project → Projects | Projects.Tasks |
| Tasks.Owner → People | People.Tasks |
| Tasks.Source Recording → Recordings | Recordings.Tasks |

## 생성 순서 (Notion은 Relation 대상 DB가 먼저 존재해야 함)
1. People, Projects, Template Library (서로 의존 없음 — 먼저 생성)
2. Recordings (Project/People/Template 참조)
3. Decisions, Tasks (Project/People/Recordings 전부 참조 — 마지막)

## 자가검수
- Keywords=Text, People↔Projects=Rollup — 장기 운영 시 관리 불가능해지는 패턴을 피하려는 의도적 단순화, 모순 없음.
- Nature(Committed/Suggested)와 Status(Not Started/.../Done)를 같은 속성에 합치지 않고 분리 — "약속 여부"와 "진행 상태"는 서로 다른 축이라 섞으면 안 됨. 의도대로 분리됨.
- Review Status(Decisions)와 Status(Recordings)의 Needs Review가 중복처럼 보이지만, 전자는 "이 결정을 신뢰할 수 있는가", 후자는 "이 녹음 처리가 끝났는가"로 레이어가 다름 — 모순 아님.
- STEP2 설계 완료. STEP3(Drive Schema)·STEP4(JSON Schema)는 아직 미착수.
