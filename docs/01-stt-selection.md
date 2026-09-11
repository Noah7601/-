# STEP 1 — STT 엔진 선정

## 결론
**1차 추천: RTZR (Return Zero / VITO STT)**
근거: 한국어 정확도 1위(회의·상담 시나리오 특화), 화자분리·timestamp 내장, 4시간/2GB 긴 파일 지원, REST API(비동기 job) + n8n 연동 용이, 국내 데이터 처리, 10시간 무료 체험으로 즉시 검증 가능.

**차선(백업/비교 대상): Naver Clova Speech Recognition (CSR)**
정확도 근접(상담 시나리오 4.91% CER로 오히려 RTZR보다 우위), 화자분리(`speakerCountMin/Max`)·timestamp 지원. 단가 확인 안 됨(콘솔 로그인 필요) → RTZR과 병행 실측 후 택1 권장.

**제외: OpenAI Whisper/gpt-4o-transcribe, Google Cloud STT, Deepgram**
사유는 아래 비교표 참조. Deepgram은 한국어가 code-switching 지원 언어 목록에 없어 1차 제외.

---

## 비교표

| 기준 | RTZR (Return Zero) | Naver Clova Speech | OpenAI Whisper/gpt-4o-transcribe | Google Cloud STT (Chirp) | Deepgram Nova-3 |
|---|---|---|---|---|---|
| 한국어 정확도 (CER, AI-Hub 벤치마크) | **5.91%** (1위, 회의/상담 특화) | 7.52% (상담만 4.91%로 최고) | 11.39% | 11.50% | 미검증(한국어 벤치마크 없음) |
| 한/영 혼합 처리 | 공식 벤치마크 없음 — 실측 필요 | 공식 벤치마크 없음 — 실측 필요 | 강점으로 알려짐(다국어 code-switch), 단 한국어 자체 정확도 낮음 | 미확인 | 한국어가 멀티링구얼 code-switch 지원 언어(10개)에 미포함 |
| 화자분리 | O (기본 제공) | O (`speakerCountMin/Max`) | O (`gpt-4o-transcribe-diarize`, 화자 겹침 시 품질 저하 명시) | O (별도 과금 추정) | O (사전녹음 무료, 스트리밍 별도과금) |
| Timestamp | O | O (문장 자동분절+timestamp) | O | O | O |
| 긴 회의 처리 | 최대 4시간/2GB, 배치+스트리밍 | 장문 인식용 별도 API 있음 | 파일당 25MB 제한 → 청킹 필요(추정) | 제한 확인 안 됨 | 제한 확인 안 됨 |
| API 형태 | REST, 비동기 job(제출→폴링) | REST | REST, 동기 | REST/gRPC | REST/WS |
| n8n 연동 | HTTP Request + 폴링(Wait 노드)로 구현 용이 | HTTP Request로 용이 | HTTP Request로 매우 용이(가장 단순) | HTTP Request, gRPC는 n8n에서 번거로움 | HTTP Request로 용이 |
| 가격 | 검색 기준 약 ₩1,000/시간(개인/스타트업), 볼륨 할인, **10시간 무료 체험** | 종량제, 정확한 단가 미확인(콘솔 확인 필요) | $0.006/분(gpt-4o-transcribe), diarize 모델은 토큰과금 | 표준 $0.016/분 수준(검색 기준), diarization 추가과금 추정 | $0.0043/분(배치), diarization 배치 무료 |
| 데이터 처리(개인정보) | 국내(한국) 리전 — 민감 상담/영업 대화에 유리 | 국내(한국) 리전 | 해외(미국) 전송 | 해외(아시아 리전 선택 가능) | 해외 |
| 향후 교체 용이성 | REST 표준 → Transcript만 잘 저장하면 교체 쉬움 | 동일 | 동일 | 동일 | 동일 |

## 왜 RTZR인가 (근거)
1. **이 프로젝트의 핵심 시나리오(회의·상담·영업통화)에서 벤치마크 1위** — AI-Hub 테스트셋 기준 평균 CER 5.91%, 특히 상담/회의 카테고리 특화.
2. **PLAUD 녹음 특성과 정합** — 4시간/2GB까지 단일 파일 처리, 배치+스트리밍 모두 지원 → 긴 회의도 청킹 없이 처리 가능(추정: 공식 스펙 기준, 실측 필요).
3. **화자분리·timestamp가 기본 제공** — Decision/Task의 Evidence(timestamp) 추적 요구사항을 추가 조합 없이 충족.
4. **n8n 연동 부담이 낮음** — REST API이므로 HTTP Request 노드 + 폴링 구조로 표준 구현 가능.
5. **국내 리전 처리** — 영업 제안가, 고객 정보 등 민감한 비즈니스 대화가 많은 본 프로젝트 특성상 국내 처리가 유리.
6. **즉시 검증 가능** — 10시간 무료 체험으로 MVP(5~10분 녹음 테스트)에 별도 비용 없이 착수 가능.

## 리스크 / 미검증 항목 (⚠️)
- ⚠️ 한/영 혼합 발화 정확도는 RTZR 공식 문서에 벤치마크 없음 → **MVP 1차 테스트에서 실제 PLAUD 녹음으로 RTZR vs Clova 직접 비교 필요**.
- ⚠️ 정확한 최신 단가는 네트워크 제약으로 공식 가격 페이지 원문을 직접 열람하지 못했다(검색 스니펫 기반). 계약/결제 전 `https://developers.rtzr.ai/docs/en/pricing/` 직접 확인 필수. **미검증**.
- ⚠️ Naver Clova 단가는 콘솔 로그인 후에만 확인 가능해 비교표에 정확한 숫자를 채우지 못했다. **미검증**.

## 다음 액션
- [ ] 사용자 승인: RTZR을 V1 STT로 확정할지 결정
- [ ] 승인 시 RTZR 계정 생성 → 10시간 무료 체험으로 실제 PLAUD 녹음 1건 테스트(한/영 혼합 구간 포함) 후 확정
- [ ] 승인되면 STEP 2 (Notion Schema) 진행
