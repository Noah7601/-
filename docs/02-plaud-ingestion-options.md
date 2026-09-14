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

## n8n 연동 방식 — 미해결 2건 확인 완료 (v3, 2026-09-14)

### 1) n8n이 MCP를 직접 호출할 수 있는가 → **가능(기술적으로 확인), 실제 연결 테스트는 아직 안 함**
- n8n에 **MCP Client Tool 노드**가 공식으로 존재. SSE/HTTP Streamable 전송을 지원하고, Bearer/개별 헤더/다중 헤더/**OAuth2** 인증을 지원함.
- Plaud MCP의 **공식 원격 엔드포인트: `https://mcp.plaud.ai/mcp`**, 인증은 OAuth(Plaud 계정으로 로그인, 별도 API 키 발급 없음). ChatGPT/Claude Web 등 MCP 클라이언트에서 "Remote MCP server URL"에 이 주소를 넣는 방식과 동일한 패턴이므로 n8n의 MCP Client Tool 노드에도 같은 방식으로 연결 시도 가능.
- ⚠️ 단, **HTTP로 연결 시 녹음 데이터가 Plaud의 US 리전 MCP 서버를 경유**함 — 영업/상담 등 민감 대화가 많은 이 프로젝트 특성상 데이터 처리 리전 이슈로 재확인.
- ⚠️ n8n의 MCP Client Tool은 구조적으로 **"AI Agent" 노드 아래 Tool로 붙는 서브노드** — 단순 HTTP Request처럼 정해진 파라미터로 결정론적 호출을 하는 게 아니라, Agent(LLM)가 어떤 도구를 어떤 인자로 호출할지 판단하는 구조. "새 녹음 오디오를 매번 정확히 같은 방식으로 가져오기"엔 Agent의 판단 변동성이 리스크가 될 수 있음 — 프롬프트를 엄격하게 고정하거나, 결정론적 대안(Plaud CLI를 Execute Command 노드로 호출)과 비교 검토 필요.
- **미검증(실제 연결 안 해봄)**: n8n에서 `https://mcp.plaud.ai/mcp` + OAuth2 credential 설정이 실제로 붙는지, Plaud가 n8n 같은 서드파티 클라이언트의 OAuth 등록을 허용하는지.

### 2) PLAUD가 자동으로 전사해서 quota를 소모하는가 → **확인됨, 끌 수 있음**
- PLAUD에는 **AutoFlow** 기능이 있음: 녹음이 동기화/업로드될 때마다 자동으로 transcript+summary를 생성 — **이때 quota가 소모됨**(수동 전사와 동일하게 카운트).
- **AutoFlow는 앱에서 토글로 끌 수 있음.** 끄면 동기화만 되고 자동 전사는 발생하지 않음 → **MCP/CLI로 원본 오디오만 뽑아내는 우리 방식과 완전히 호환됨.**
- ➜ **필수 액션**: PLAUD 앱 설정에서 AutoFlow를 꺼야 이 프로젝트의 핵심 전제("PLAUD 전사 quota 비의존")가 실제로 지켜짐. 켜둔 채로 두면 MCP로 원본만 가져와도 PLAUD 쪽에서 별도로 quota가 계속 소모됨.

## 최종 권장 (v3)
1. **지금 바로**: PLAUD 앱에서 AutoFlow 끄기 (사용자 액션, 5분)
2. **1차 시도**: n8n에 MCP Client Tool 노드 + `https://mcp.plaud.ai/mcp`(OAuth2)로 연결 테스트 → 되면 이게 가장 깔끔한 구조
3. **1차 시도가 막히면(OAuth 미지원 등)**: Plaud CLI를 n8n의 Execute Command 노드(self-hosted n8n 전제)로 감싸는 결정론적 방식, 또는 Claude 세션이 추출 에이전트 역할(Routine으로 주기 폴링 → Drive 업로드 → n8n 웹훅 인계) — 이미 이 세션에서 실증된 방식

## 리스크 (⚠️)
- ⚠️ n8n ↔ Plaud MCP 실제 연결은 아직 테스트 안 함 — OAuth2 credential 설정이 실제로 되는지 확인 필요.
- ⚠️ MCP Client Tool은 Agent 종속 구조라 완전한 결정론적 파이프라인에는 안 맞을 수 있음 — Agent 프롬프트를 엄격히 고정하거나 Plaud CLI 방식과 비교 필요.
- ⚠️ HTTP MCP 경유 시 데이터가 US 리전 서버를 지남 — Soniox(마찬가지로 해외 처리)와 함께 이 프로젝트의 "국내 민감 데이터 처리" 관점에서 누적 리스크로 인지 필요.

## 다음 액션
- [ ] (사용자) PLAUD 앱에서 AutoFlow 끄기
- [ ] n8n에 MCP Client Tool 노드로 `https://mcp.plaud.ai/mcp` 연결 실제 테스트 (n8n 인스턴스 필요 — self-hosted/cloud 여부 확인 후 진행)
- [ ] 연결 실패 시 Plaud CLI + Execute Command 노드 방식으로 폴백
- [ ] STEP3(Drive Schema)/STEP6(n8n Workflow) 설계에 확정된 방식 반영
