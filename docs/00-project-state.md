# PLAUD → Drive → STT → Claude → Notion Ledger — 프로젝트 상태

> 이 문서는 세션이 바뀌어도 이어서 작업할 수 있도록 STATE를 유지한다. 매 STEP 완료 시 갱신.

## 목표
녹음(PLAUD) → 원본 보관(Drive) → 전사(STT) → 구조화(Claude) → 영속 원장(Notion) 자동화(n8n).
Recording ID로 Audio/Transcript/Notion/Decision/Task/처리로그를 끝까지 역추적 가능하게 한다.

## 완료
- [x] STEP 1 — STT 엔진 선정 확정: **Soniox** (본 세션, `docs/01-stt-selection.md`)

## 진행중
- (없음 — 실측 테스트 및 STEP2 승인 대기)

## 결정사항 (변경 금지, 재질문 금지)
- 4계층 데이터 분리: Source(Audio) / Transcript / Intelligence(Claude 출력) / Ledger(Notion) — 모델·템플릿 교체 시 재처리 가능해야 함
- 모든 산출물은 Recording ID(`REC-YYYYMMDD-NNN`) 공유
- Task는 Committed(대화 중 확약) vs Suggested(AI 제안) 구분, AI가 임의로 확정 생성 금지
- Claude 분석은 단일 거대 프롬프트가 아닌 Normalize → Understand → Render 3-Pass로 분리
- Transcript에 없는 정보 생성 금지(환각 방지)가 최우선 원칙
- **STT 확정: Soniox** (사용자 보유 API 키 활용, 2026-09-14) — 근거·리스크는 `docs/01-stt-selection.md` 참조

## 실패한 접근 / 기각
- RTZR(Return Zero) — STEP1 1차 조사에서 추천했으나, 사용자가 Soniox API 키를 이미 보유해 기각. 제3자 벤치마크(AI-Hub CER 5.91%)는 더 신뢰도 높음 → Soniox 실측 품질이 기준 미달이면 재검토 대상으로 보류.

## 참고자료
- `docs/02-plaud-ingestion-options.md` (v3) — PLAUD 공식 MCP(`get_file`)로 원본 오디오 presigned URL 추출 검증 완료. n8n의 **MCP Client Tool 노드**로 Plaud 공식 원격 MCP(`https://mcp.plaud.ai/mcp`, OAuth2)에 직접 연결 가능함을 확인(단, 실제 연결 테스트는 아직 안 함, Agent 종속 구조라 결정론적 호출엔 한계 있을 수 있음). PLAUD는 **AutoFlow** 기능이 자동 전사/요약으로 quota를 소모하며 **토글로 끌 수 있음** — 반드시 꺼야 quota 비의존 전제가 실제로 지켜짐.
- `docs/03-architecture-v2.md` — 위 결정들을 반영한 갱신 마스터플랜. n8n은 **self-hosted Community Edition**(무료, CLI 폴백 가능) 권장. n8n 가격표는 검색 기반 미검증.

## 미해결 / 확인 필요
- n8n MCP Client Tool 노드 ↔ `https://mcp.plaud.ai/mcp` OAuth2 실제 연결 테스트 (아직 안 해봄)
- (사용자 액션) PLAUD 앱에서 AutoFlow 끄기 — **Claude는 조회 전용 MCP만 있어 대신 꺼줄 수 없음**, 아직 미완료
- (사용자 결정) n8n self-hosted 설치 환경(Mac 상시구동 / VPS 등) 미정
- n8n 가격표(Starter $20~, Pro $50~ 등)는 검색 스니펫 기반 — 공식 `n8n.io/pricing` 원문 미확인(네트워크 제약)
- ⚠️ Soniox 한국어 정확도(WER 4.3%)는 자사 발표 수치, 독립 검증 없음 → PLAUD 실제 녹음으로 사람이 직접 품질 검수 필요
- ⚠️ Soniox는 해외(미국) 리전 처리 — 영업 제안가 등 민감 비즈니스 대화의 개인정보/데이터 정책 미검증
- ⚠️ Soniox 긴 오디오(파일크기/길이) 제한 — 공식 문서 원문 미열람(네트워크 제약), 계약/스케일업 전 확인 필요
- 한국어+영어 혼합 발화 정확도 — 공식 벤치마크 없음, MVP 실측 필요
- STT 실측 테스트 결과 확인 후 STEP 2 진행 승인 대기
