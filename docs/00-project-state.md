# PLAUD → Drive → STT → Claude → Notion Ledger — 프로젝트 상태

> 이 문서는 세션이 바뀌어도 이어서 작업할 수 있도록 STATE를 유지한다. 매 STEP 완료 시 갱신.

## 목표
녹음(PLAUD) → 원본 보관(Drive) → 전사(STT) → 구조화(Claude) → 영속 원장(Notion) 자동화(n8n).
Recording ID로 Audio/Transcript/Notion/Decision/Task/처리로그를 끝까지 역추적 가능하게 한다.

## 완료
- [x] STEP 1 — STT 엔진 선정 (본 세션, `docs/01-stt-selection.md`) — **승인 대기**

## 진행중
- (없음 — STEP1 승인 대기 중)

## 결정사항 (변경 금지, 재질문 금지)
- 4계층 데이터 분리: Source(Audio) / Transcript / Intelligence(Claude 출력) / Ledger(Notion) — 모델·템플릿 교체 시 재처리 가능해야 함
- 모든 산출물은 Recording ID(`REC-YYYYMMDD-NNN`) 공유
- Task는 Committed(대화 중 확약) vs Suggested(AI 제안) 구분, AI가 임의로 확정 생성 금지
- Claude 분석은 단일 거대 프롬프트가 아닌 Normalize → Understand → Render 3-Pass로 분리
- Transcript에 없는 정보 생성 금지(환각 방지)가 최우선 원칙
- **STT 1차 후보: RTZR(Return Zero) — STEP1 근거 참조, 사용자 승인 대기**

## 실패한 접근 / 기각
- (없음)

## 미해결 / 확인 필요
- RTZR 정확한 최신 단가(원/시간) — 공식 페이지 직접 열람 필요(네트워크 제약으로 원문 fetch 불가, 검색 스니펫 기반 추정)
- 한국어+영어 혼합 발화 시 RTZR vs Naver Clova 실측 비교 (공식 문서에 벤치마크 없음 → MVP 실측 필요)
- Naver Clova Speech 정확한 시간당 단가 (콘솔 로그인 후 확인 필요, 검색으로 미확인)
- STT 선정 최종 승인 여부 (사용자 확인 대기)
