# PLAUD → 외부 STT(Soniox) 연동 조사 (STEP2 이전 참고자료)

> STEP1(STT=Soniox) 확정 이후, "PLAUD가 Soniox API로 직접 전사하게 만들 수 있는가?"에 대한 조사. STEP3(Drive Schema)/STEP6(n8n Workflow) 설계 시 참고.

## 결론
**PLAUD 자체에는 서드파티 STT(Soniox 포함)를 붙이는 공식 기능이 없다.** 추측하신 대로 맞음. 공식 Public API도 아직 없음(2026년 현재 "Plaud Embedded"는 하드웨어 파트너용 리서치 프리뷰이며 자체 전사 엔진만 사용 — 우리 목적과 다름).

**해결 방법은 원래 설계 그대로: PLAUD의 전사 기능은 아예 쓰지 않고, 원본 오디오만 꺼내서 우리 파이프라인(n8n)에서 Soniox를 직접 호출한다.** "PLAUD-Soniox 연동"이 아니라 "PLAUD 오디오 추출 자동화 + Soniox 호출"이 정답.

## 오디오 추출(PLAUD → Drive) 방법 비교

| 방법 | 방식 | 자동화 | 리스크 |
|---|---|---|---|
| **A. 수동 export (MVP 권장)** | PLAUD 앱에서 오디오 파일을 직접 내보내 Drive에 업로드 | 없음(사람이 함) | 없음. 가장 안전, 즉시 가능 |
| **B. Applaud (오픈소스)** | 10분마다 PLAUD 클라우드를 폴링해 오디오/트랜스크립트/요약을 로컬 디스크에 자동 동기화, 새 녹음 시 webhook 발사 → n8n 트리거 | 완전 자동 | ⚠️ 비공식 서드파티 도구 — PLAUD 계정 인증(세션 기반) 필요, 이용약관 위반/계정 정지 가능성 확인 안 됨. Mac에서는 launchd로 상시 실행 필요 |
| **C. Riffado (오픈소스)** | PLAUD 클라우드 동기화 + 자체 전사까지 수행 | 완전 자동(단, 전사도 대신함) | ❌ **Soniox 미지원** — OpenAI 호환(`baseURL`) 엔진만 지원(OpenAI/Groq/Azure 등). Soniox는 자체 API 스펙이라 호환 안 됨. 제외 |
| **D. Plaud Embedded (공식)** | Device SDK + 자체 Transcription API로 완전히 별도 제품을 만드는 개발자 플랫폼 | 해당 없음 | ❌ 목적 불일치(하드웨어 파트너용), 승인 필요, 리서치 프리뷰 단계라 이번 프로젝트엔 부적합 |

## 권장 순서
1. **MVP(1건 테스트)는 A(수동 export)로 시작** — 자동화 이슈를 STT 정확도 검증과 분리해서 확인.
2. 파이프라인이 검증되면 **B(Applaud)로 자동화 검토** — 단, 도입 전 PLAUD 이용약관에서 비공식 API 접근/자동화 관련 조항 확인 필요(⚠️ 미검증).
3. C(Riffado), D(Plaud Embedded)는 이번 프로젝트 목적과 맞지 않아 제외.

## 리스크 (⚠️)
- ⚠️ Applaud는 PLAUD 공식이 아닌 서드파티 오픈소스 — 계정 인증 방식과 PLAUD 이용약관 위반 여부가 확인되지 않음. 자동화 도입 전 반드시 확인.
- ⚠️ PLAUD 공식 Public API가 없으므로, 향후 PLAUD가 정책을 바꾸면(비공식 접근 차단 등) B 방식이 깨질 수 있음 — Drive를 Source of Truth로 삼는 현재 설계(원본 분리 원칙)가 이 리스크에 대한 방어책.

## 다음 액션
- [ ] STEP3(Drive Schema) 설계 시 이 문서를 반영해 "오디오 추출 방식"을 폴더 구조와 함께 확정
- [ ] Applaud 도입 여부는 STEP6(n8n Workflow) 단계에서 재논의
