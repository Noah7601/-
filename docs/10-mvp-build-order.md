# STEP 7 — MVP 구축 순서

> 27개 노드를 한 번에 연결하면 뭐가 고장나도 원인을 못 찾는다. **7단계로 쪼개서, 매 단계가 독립적으로 테스트 가능하게** 간다. 목표: 5~10분 PLAUD 녹음 1건이 Audio→Transcript→Claude 분석→Notion Recording→Decision/Task까지 끝까지 성공하는 것.

## ⚠️ 테스트 녹음 추천
실제 민감한 업무 녹음(계약/자금/법무상담) 말고, **이번 MVP 테스트 전용으로 짧고 가벼운 가상 녹음을 새로 하나 만드는 걸 추천**. 파이프라인 디버깅 중에는 로그/중간 출력에 내용이 그대로 노출되는 구간이 많아서, 디버깅이 끝나기 전까지는 민감한 실제 녹음을 넣지 않는 게 안전함.

---

## M0 — 사전 설치 (맥 로컬)
- Docker + n8n (`docs/04-n8n-mac-setup.md`)
- whisper.cpp, pyannote.audio
- n8n에 자격증명 등록: Notion, Google Drive, Claude API, (나중에) Plaud MCP
- **성공 기준**: `localhost:5678` 접속되고 각 credential 테스트 연결 성공

## M1 — 오디오를 손으로 Drive에 넣기 (자동화 없이)
- 테스트 녹음(5~10분)을 PLAUD 앱에서 수동 export
- `PLAUD Ledger/2026/11/REC-20261118-001/audio.mp3`에 수동 업로드 (STEP3 구조 그대로, 폴더명만 테스트용 ID)
- **성공 기준**: Drive에 파일이 정확한 경로/이름으로 있음
- **왜 수동으로 먼저**: PLAUD MCP 연동(M6)이 아직 미해결 상태라, 그것 때문에 전체 테스트가 막히면 안 됨. 추출 자동화와 STT/Claude 품질 검증을 분리.

## M2 — whisper.cpp + pyannote 단독 실행 (n8n 없이, 터미널에서)
- `audio.mp3` → whisper.cpp(`large-v3`) → 세그먼트 확인
- 같은 파일 → pyannote → 화자 구간 확인
- 둘을 merge하는 스크립트 작성 → `transcript.json` 생성
- **성공 기준**: `transcript.json`을 열어서 사람이 직접 읽어보고 정확도·화자분리가 쓸만한지 판단 (이게 사실상 미뤄뒀던 "STT 실측 테스트")
- **실패하면**: n8n 연결은 아직 하지 않는다. whisper 모델 크기(large-v3-turbo 등) 조정하거나 pyannote 설정부터 다시 — M3로 넘어가지 않음.

## M3 — Claude 4-Pass 수동 실행 (n8n 없이, 스크립트/curl로)
- `transcript.json`을 Normalize → Router → Understand → Render 순서로 수동 호출(Python 스크립트나 curl)
- STEP4 JSON Schema로 결과 검증
- **성공 기준**: 최종 JSON이 스키마를 통과하고, `decisions[]`/`tasks[].nature`가 실제 발화와 맞는지 사람이 직접 대조
- **실패하면**: STEP5 프롬프트를 이 테스트 결과 기준으로 수정 — n8n에 아직 넣지 않는다.

## M4 — Notion에 손으로 1건 기록 (n8n 없이, Notion에서 직접 또는 Claude Code의 Notion MCP로)
- M3 결과 JSON을 가지고 Recordings/People/Projects/Decisions/Tasks에 수동 생성 + Relation 연결
- **성공 기준**: Notion 페이지들이 서로 올바르게 연결되어 있고, Decisions/Tasks에서 Source Recording을 타고 들어가면 원본까지 추적됨
- **실패하면**: STEP2 스키마나 STEP4→Notion 매핑표를 수정 — 아직 n8n 자동화로 안 간다.

## M5 — n8n으로 M1~M4를 하나로 연결 (수동 트리거)
- n8n 워크플로우를 STEP6 설계대로 구성 (Cron은 아직 끄고, "Execute Workflow" 수동 실행만)
- 같은 테스트 녹음으로 Drive 업로드 이후 전체를 한 번에 실행
- **성공 기준**: 🎯 **여기가 브리프의 목표 지점** — Audio(Drive에 있는 상태)→Transcript→Claude 분석→Notion Recording 생성→Decision/Task 추출까지 자동으로 성공
- **실패하면**: M1~M4에서 이미 검증된 각 조각을 그대로 n8n 노드로만 옮기는 것이므로, 보통 n8n 노드 연결/데이터 전달 문제. 어느 조각 로직 자체를 다시 건드리지 않는다.

## M6 — PLAUD MCP 연동 (이전부터 미해결이던 것)
- n8n MCP Client Tool → `https://mcp.plaud.ai/mcp`(OAuth2) 실제 연결 테스트
- 되면: M1(수동 업로드)을 "Plaud list_files/get_file 호출"로 교체
- 안 되면: Plaud CLI + Execute Command 노드로 폴백 (`docs/02-plaud-ingestion-options.md` 참조)
- **성공 기준**: 오디오 추출까지 완전 자동화됨 (사람이 더 이상 Drive에 손으로 안 올림)

## M7 — Cron 켜고 상시 운영
- Cron Trigger 활성화, 실제 PLAUD 계정의 새 녹음으로 운영 시작
- Failed/Needs Review 뷰를 주기적으로 확인하는 루틴만 추가
- **성공 기준**: 사용자가 "녹음하고 아무것도 안 하기"만으로 Notion에 쌓임 — 최종 목표 UX

---

## 요약 표

| 단계 | 자동화 범위 | n8n 사용 | 목적 |
|---|---|---|---|
| M0 | 없음 | 설치만 | 환경 준비 |
| M1 | 없음(수동) | 안 씀 | 오디오 확보 |
| M2 | 없음(수동) | 안 씀 | STT 품질 검증 |
| M3 | 없음(수동) | 안 씀 | 프롬프트 품질 검증 |
| M4 | 없음(수동) | 안 씀 | Notion 매핑 검증 |
| M5 | 전체(수동 트리거) | 씀 | **MVP 목표 달성** |
| M6 | PLAUD 수집까지 자동 | 씀 | 완전 자동화 |
| M7 | 전체 자동(Cron) | 씀 | 실운영 전환 |

## 자가검수 (STEP1~7 전체 마무리 점검)
- STT가 Soniox→로컬 Whisper로 바뀐 뒤 모든 후속 문서(03/06/07/08/09)가 일관되게 whisper.cpp/pyannote를 가리킴 — Soniox 잔재 없음.
- Recording ID(2차 키)와 Plaud File ID(1차 키)의 역할 구분이 STEP2/6/이 문서 전체에서 일관됨.
- M5를 "목표 지점"으로 명시해 브리프의 "Audio→Transcript→Claude 분석→Notion Recording→Decision/Task" MVP 목표와 정확히 일치시킴.

## 다음 액션
- [ ] M0부터 맥 로컬에서 시작 (이 세션은 설계까지 — 실행은 로컬 Claude Code)
