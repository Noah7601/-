# 아키텍처 v2 — STT/Ingestion 확정 반영 갱신 플랜

> STEP1(STT) + PLAUD 연동 조사(MCP/Zapier/AutoFlow) 결과를 반영한 갱신 마스터플랜. STEP2(Notion Schema) 진행 전 최종 정렬용.

## ⚠️ 먼저: AutoFlow는 내가 끌 수 없음
가진 Plaud MCP 툴(`list_files`/`get_file`/`get_note`/`get_transcript`/`get_current_user`)은 **조회 전용**이라 설정 변경 권한이 없음. **AutoFlow는 사용자가 PLAUD 앱에서 직접 꺼야 함.**

- 위치(공식 지원문서 기준, 앱 버전에 따라 메뉴명 다를 수 있음): PLAUD 앱 → **설정(Settings)** → **AutoFlow** → 전역 토글 off, 또는 개별 AutoFlow 항목별 토글 off
- 안 보이면: 공식 문서 `support.plaud.ai` "AutoFlow" 문서를 직접 열어서 확인 필요(이 세션에서는 네트워크 제약으로 원문 열람 불가)
- **미완료 상태**: 꺼졌는지 내가 검증할 방법이 없음(설정 조회 API 없음) → 껐으면 알려주면 STATE에 완료로 기록

## 갱신된 파이프라인

```
PLAUD (녹음, AutoFlow OFF)
  ↓ [n8n: MCP Client Tool 노드 → https://mcp.plaud.ai/mcp (OAuth2)]
원본 오디오 (presigned URL, 24h)
  ↓ [n8n: Drive 업로드]
Google Drive (Source Vault)
  ↓ [n8n: HTTP Request → Soniox API]
Transcript (화자분리+timestamp 포함)
  ↓ [n8n: Claude 호출 — Normalize→Understand→Render]
Structured JSON
  ↓ [n8n: Notion API]
Notion Ledger (Recordings/Projects/People/Decisions/Tasks)
```

## n8n 배포 방식 — **Self-hosted (Community Edition) 권장**

| 항목 | Self-hosted (Community) | Cloud (Starter) |
|---|---|---|
| 비용 | **무료**(서버 비용만) | $20/월(연간)~, 2,500 executions/월 |
| 실행 횟수 제한 | 없음 | 있음(초과 시 요금 상승) |
| Plaud CLI 폴백(Execute Command 노드) | **가능** | 불가(로컬 명령 실행 환경 없음) |
| MCP Client Tool 노드 | 가능 | 가능 |
| 운영 부담 | 서버 직접 관리 필요(업데이트/보안) | n8n이 관리 |

**권장 이유**: ① MCP Client Tool 연결이 막히면 Plaud CLI 폴백이 필요한데 이건 self-hosted에서만 가능 ② 개인 프로젝트라 executions가 많지 않아도 무료가 유리 ③ 이미 Mac을 주력으로 쓰므로 Mac mini/저가 VPS에 상시 구동 가능.

⚠️ **가격은 검색 스니펫 기반**(n8n.io 공식 페이지 직접 열람 불가 — 네트워크 제약). 계약/가입 전 `n8n.io/pricing` 직접 확인 필요. **미검증**.

| 플랜 | 가격(검색 기준) | executions/월 |
|---|---|---|
| Self-hosted Community | 무료 | 무제한 |
| Cloud Starter | $20/월(연간), $24(월간) | 2,500 |
| Cloud Pro | $50/월(연간), $60(월간) | 10,000 |
| Cloud Business | $667/월(연간), $800(월간) | 40,000 |
| Enterprise | 별도 협의 | 무제한 |

## 확정/변경 사항 요약
- STT: **Soniox** (STEP1)
- PLAUD 오디오 추출: **n8n MCP Client Tool → `https://mcp.plaud.ai/mcp`(OAuth2)**가 1차안, 실패 시 **Plaud CLI + Execute Command 노드** 폴백
- n8n 배포: **Self-hosted Community Edition**(무료, executions 무제한, CLI 폴백 가능)
- PLAUD AutoFlow: **꺼야 함(사용자 액션, 미완료)**

## 다음 액션
- [ ] (사용자) PLAUD 앱에서 AutoFlow 끄기 → 완료되면 알려주기
- [ ] (사용자) n8n self-hosted 설치 환경 결정 (Mac 상시구동 / VPS 등)
- [ ] n8n에 MCP Client Tool 노드로 `https://mcp.plaud.ai/mcp` 연결 실제 테스트
- [ ] 연결 실패 시 Plaud CLI 폴백 검토
- [ ] 위 항목 정리되면 STEP2(Notion Schema)로 진행
