# PLAUD → 외부 STT(Soniox) 연동 조사 (STEP2 이전 참고자료)

> STEP1(STT=Soniox) 확정 이후, "PLAUD가 Soniox API로 직접 전사하게 만들 수 있는가?"에 대한 조사. STEP3(Drive Schema)/STEP6(n8n Workflow) 설계 시 참고.
> **v2 (2026-09-14): PLAUD 공식 MCP를 이 세션에서 실제 계정으로 테스트해 원본 오디오 추출 경로를 실증 확인. 결론 갱신.**

## 결론
**PLAUD 자체에는 서드파티 STT(Soniox 포함)를 붙이는 공식 기능은 여전히 없다.** 하지만 오디오를 "꺼내는" 공식 경로는 두 가지가 이미 존재하고, 그중 **MCP는 지금 이 세션에서 실제 계정으로 작동을 확인했다.**

- **MCP (공식, 실증됨)** — `list_files`로 녹음 목록 조회 → `get_file`로 **원본 MP3 presigned URL(S3, 24시간 유효)** 획득. 실제 사용자 PLAUD 계정에서 방금 성공. Applaud 같은 비공식 도구가 더 이상 필요 없다.
- **Plaud CLI (공식)** — 터미널에서 audio/transcript/summary를 pull하는 공식 CLI. 자동화/스크립트 워크플로우용으로 명시됨. Mac에서 cron/launchd로 정기 실행 가능.
- **Zapier (공식, 제한적)** — 트리거가 "Transcript generated" / "Summary generated" **2종뿐**. 즉 **PLAUD 자체 AI 처리가 먼저 끝나야 트리거된다.** 우리가 이 프로젝트를 시작한 이유(PLAUD 전사 한도에 의존하지 않기)와 정면으로 충돌할 수 있음 — 트리거 시점에 원본 오디오 다운로드 링크가 실제로 포함되는지는 **미확인**.

## 실측 확인 내용 (본 세션, 사용자 실제 PLAUD 계정)
- `list_files` 호출 → 최근 녹음 10건 정상 조회됨 (예: "09-02 통화: 영양진단 절차 안내 및 마감기한 공지" 등)
- `get_file`(특정 녹음, 72초짜리) 호출 → `presigned_url` 필드에 실제 S3 MP3 다운로드 링크(24시간 유효) 반환됨
- 해당 녹음의 `source_list`/`note_list`가 **비어있음** → 관찰: 이 녹음은 PLAUD 자체 전사/요약이 아직 생성되지 않은 상태로 보임. 즉 **MCP로 원본만 조회하는 행위 자체는 PLAUD 자체 전사 quota를 소모하지 않을 가능성이 높다.** (⚠️ 표본 1건 관찰, 완전 확정 아님 — PLAUD 설정에 "자동 전사" on/off가 있는지 앱에서 직접 확인 권장)

## 오디오 추출 방법 비교 (갱신)

| 방법 | 방식 | 자동화 | 우선순위 |
|---|---|---|---|
| **MCP (공식) — 1순위** | Claude/ChatGPT 등 MCP 클라이언트에서 `list_files`+`get_file` 호출, presigned URL로 오디오 다운로드 | 에이전트 기반 자동화(아래 참조) | ✅ 실증됨, 최우선 검토 |
| **Plaud CLI (공식) — 2순위** | 터미널 스크립트로 audio/transcript pull | cron/launchd로 완전 자동 | 공식 지원, MCP와 병행 검토 |
| Zapier (공식) | Transcript/Summary generated 트리거 | 완전 자동이지만 PLAUD 자체 처리 이후 발동 | ⚠️ PLAUD quota 의존 가능성 → 조건부 |
| A. 수동 export | 앱에서 직접 다운로드 → Drive 업로드 | 없음 | MVP 1건 테스트용으로만 |
| B. Applaud(비공식) | 서드파티 폴링+webhook | 완전 자동 | 공식 경로(MCP/CLI)가 확인된 이상 **불필요해짐**, 보류 |
| C. Riffado(비공식) | 동기화+자체 전사(OpenAI 호환만) | - | ❌ Soniox 미지원, 제외 |
| D. Plaud Embedded | 하드웨어 파트너용 개발자 플랫폼 | - | ❌ 목적 불일치, 제외 |

## n8n 연동 방식 — 결정 필요 (미해결)
MCP로 오디오를 실제로 받아오는 것까진 확인했지만, **이걸 n8n 워크플로우에 어떻게 연결할지는 두 가지 방식이 있고 아직 결정 안 됨**:

1. **n8n이 MCP 클라이언트로 직접 Plaud MCP 호출** — n8n에 MCP 클라이언트 노드가 있다면 가장 깔끔. 단, Plaud MCP가 n8n에서 접근 가능한 원격 엔드포인트(HTTP/SSE)를 제공하는지, 인증 방식이 무엇인지 **미확인** — `docs.plaud.ai/plaud-mcp-cli/mcp` 원문 확인 필요(네트워크 제약으로 이 세션에서 직접 열람 불가).
2. **Claude 세션이 추출 에이전트 역할** — 주기 실행되는 Claude 세션(Routine)이 MCP로 새 녹음을 폴링 → 오디오를 Drive에 업로드 → n8n 웹훅을 호출해 Soniox 전사~Notion 기록 이어받기. **이 세션에서 실제로 작동 검증된 방식이라 신뢰도 높음.**

## 리스크 (⚠️)
- ⚠️ Zapier 트리거가 PLAUD 자체 전사/요약 완료 후에만 발동 — 이 경로를 오디오 추출에 쓰면 PLAUD quota를 매 녹음마다 소모하게 될 가능성. **이 프로젝트의 핵심 전제(quota 비의존)와 충돌** → 오디오 추출 용도로는 비권장, MCP/CLI 우선.
- ⚠️ n8n이 MCP를 직접 호출 가능한지 미확인 — 확인 전까지는 "Claude 세션이 에이전트" 방식을 기본안으로 둔다.
- ⚠️ PLAUD가 녹음 업로드 시점에 자동 전사를 트리거하는지 여부(quota 소모 조건)는 표본 1건 관찰일 뿐 — 앱 설정에서 "자동 전사/자동 제목생성" 옵션 직접 확인 필요.

## 다음 액션
- [ ] `docs.plaud.ai/plaud-mcp-cli/mcp` 원문에서 MCP의 인증 방식/원격 접근 가능 여부 확인 (n8n 직접 연동 가능성 판단)
- [ ] PLAUD 앱 설정에서 자동 전사 on/off 옵션 확인
- [ ] STEP3(Drive Schema)/STEP6(n8n Workflow) 설계 시 "MCP 기반 Claude 에이전트 추출" vs "n8n MCP 클라이언트 직접 호출" 중 택1
