# PLAUD → Drive → STT → Claude → Notion Ledger — 프로젝트 상태

> 이 문서는 세션이 바뀌어도 이어서 작업할 수 있도록 STATE를 유지한다. 매 STEP 완료 시 갱신.

## 목표
녹음(PLAUD) → 원본 보관(Drive) → 전사(STT) → 구조화(Claude) → 영속 원장(Notion) 자동화(n8n).
Recording ID로 Audio/Transcript/Notion/Decision/Task/처리로그를 끝까지 역추적 가능하게 한다.

## 완료
- [x] STEP 1 — STT 엔진 선정 확정: **로컬 Whisper** (whisper.cpp/MLX, large-v3) — 2026-11-08, Soniox에서 전환. `docs/01-stt-selection.md` v4
- [x] PLAUD AutoFlow 끄기 (사용자 확인, 2026-09-14) — quota 비의존 전제 실제로 충족됨
- [x] n8n 배포 환경 결정: Mac 상시구동 self-hosted (로컬 whisper 호출 때문에 필수가 됨)

## 진행중
- (없음 — 맥 로컬에서 whisper.cpp/pyannote 설치·테스트 대기)
- STEP 2 — Notion Schema 설계 완료 (`docs/05-notion-schema.md`): Recordings/Projects/People/Decisions/Tasks/Template Library 6개 DB. 실제 Notion(워크스페이스: SCOBYISLAND, scobyisland@gmail.com)에 생성할지 승인 대기

## 결정사항 (변경 금지, 재질문 금지)
- 4계층 데이터 분리: Source(Audio) / Transcript / Intelligence(Claude 출력) / Ledger(Notion) — 모델·템플릿 교체 시 재처리 가능해야 함
- 모든 산출물은 Recording ID(`REC-YYYYMMDD-NNN`) 공유
- Task는 Committed(대화 중 확약) vs Suggested(AI 제안) 구분, AI가 임의로 확정 생성 금지
- Claude 분석은 단일 거대 프롬프트가 아닌 Normalize → Understand → Render 3-Pass로 분리
- Transcript에 없는 정보 생성 금지(환각 방지)가 최우선 원칙
- **STT 확정: 로컬 Whisper** (whisper.cpp/MLX Whisper, large-v3 또는 large-v3-turbo, 맥 로컬 실행) — 2026-11-08. 민감 비즈니스 데이터(계약금액·자금송금·법무상담)가 해외로 전송되지 않아야 한다는 이유로 Soniox에서 전환. ⚠️ 한국어 정확도는 Soniox(4.3%)/RTZR(5.91%)보다 낮음(WER 14.5~14.9%)을 감수하고 결정 — 근거는 `docs/01-stt-selection.md` v4 참조
- **화자분리**: pyannote.audio를 별도 실행해 timestamp 기준으로 whisper 결과와 merge (WhisperX는 Mac에 부적합해 비권장)

## 실패한 접근 / 기각
- RTZR(Return Zero) — STEP1 1차 조사에서 추천했으나, 사용자가 Soniox API 키를 이미 보유해 기각.
- Soniox — 정확도는 우수했으나(자체발표 WER 4.3%) 민감 비즈니스 데이터의 해외(미국) 리전 처리 리스크로 2026-11-08 기각, 로컬 Whisper로 전환.

## 참고자료
- `docs/02-plaud-ingestion-options.md` (v3) — PLAUD 공식 MCP(`get_file`)로 원본 오디오 presigned URL 추출 검증 완료. n8n의 **MCP Client Tool 노드**로 Plaud 공식 원격 MCP(`https://mcp.plaud.ai/mcp`, OAuth2)에 직접 연결 가능함을 확인(단, 실제 연결 테스트는 아직 안 함, Agent 종속 구조라 결정론적 호출엔 한계 있을 수 있음). PLAUD는 **AutoFlow** 기능이 자동 전사/요약으로 quota를 소모하며 **토글로 끌 수 있음** — 반드시 꺼야 quota 비의존 전제가 실제로 지켜짐.
- `docs/03-architecture-v2.md` — 위 결정들을 반영한 갱신 마스터플랜. n8n은 **self-hosted Community Edition**(무료, CLI 폴백 가능) 권장. n8n 가격표는 검색 기반 미검증.
- `docs/04-n8n-mac-setup.md` — Mac 상시구동 Docker 설치 가이드(docker-compose.yml 포함). 현재 설계(폴링 방식)는 인바운드 웹훅이 필요 없어 포트포워딩 불필요.

## 미해결 / 확인 필요
- (맥 로컬) whisper.cpp 또는 MLX Whisper 설치, large-v3/large-v3-turbo 실제 속도·정확도 테스트 — 아직 안 해봄
- (맥 로컬) pyannote.audio 설치 및 화자분리 merge 로직 검증 — HuggingFace 토큰 필요 여부 미확인
- n8n MCP Client Tool 노드 ↔ `https://mcp.plaud.ai/mcp` OAuth2 실제 연결 테스트 (아직 안 해봄)
- n8n이 로컬 whisper/pyannote를 호출하는 Execute Command 노드 설계 — 아직 설계 안 함
- Mac이 노트북이면 sleep/뚜껑 닫힘으로 n8n·whisper가 끊길 수 있음 — `docs/04-n8n-mac-setup.md`의 에너지 설정 확인 필요
- n8n 가격표(Starter $20~, Pro $50~ 등)는 검색 스니펫 기반 — 공식 `n8n.io/pricing` 원문 미확인(네트워크 제약)
- 한국어+영어 혼합 발화 정확도 — 공식 벤치마크 없음, MVP 실측 필요
- STT 실측 테스트 결과 확인 후 STEP 2 진행 승인 대기
