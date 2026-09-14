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
- `docs/02-plaud-ingestion-options.md` (v2) — PLAUD 공식 MCP(`get_file`)로 원본 오디오 presigned URL 추출을 본 세션에서 실제 계정으로 검증 완료. Applaud(비공식) 불필요해짐. Zapier는 PLAUD 자체 전사/요약 완료 후에만 트리거되어 quota 비의존 원칙과 충돌 가능 → 오디오 추출 용도로 비권장. n8n이 MCP를 직접 호출 가능한지는 미확인(Claude 세션이 추출 에이전트 역할을 하는 방식이 현재 기본안).

## 미해결 / 확인 필요
- Plaud MCP의 n8n 직접 호출 가능 여부(원격 엔드포인트/인증 방식) — `docs.plaud.ai/plaud-mcp-cli/mcp` 원문 확인 필요
- PLAUD 앱에 자동 전사 on/off 설정이 있는지 (quota 소모 조건 확정용)
- ⚠️ Soniox 한국어 정확도(WER 4.3%)는 자사 발표 수치, 독립 검증 없음 → PLAUD 실제 녹음으로 사람이 직접 품질 검수 필요
- ⚠️ Soniox는 해외(미국) 리전 처리 — 영업 제안가 등 민감 비즈니스 대화의 개인정보/데이터 정책 미검증
- ⚠️ Soniox 긴 오디오(파일크기/길이) 제한 — 공식 문서 원문 미열람(네트워크 제약), 계약/스케일업 전 확인 필요
- 한국어+영어 혼합 발화 정확도 — 공식 벤치마크 없음, MVP 실측 필요
- STT 실측 테스트 결과 확인 후 STEP 2 진행 승인 대기
