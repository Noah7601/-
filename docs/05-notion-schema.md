# STEP 2 — Notion Schema (1/2: Recordings · Projects · People)

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

> Decisions/Tasks DB 설계는 다음 배치에서 이어서 작성.

## 자가검수
- Keywords를 Multi-select로 안 하고 Text로 내린 것, People↔Projects를 Relation 대신 Rollup으로 내린 것 — 둘 다 "장기 운영시 관리 불가능해지는 패턴"을 피하려는 의도적 단순화. 모순 없음.
- 아직 Decisions/Tasks/Template Library 미작성 — 다음 배치 대상.
