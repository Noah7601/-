# STEP 3 — Google Drive Schema

> Source Vault 설계. Layer 1(Audio)·Layer 2(Transcript)를 영구 보관하는 곳. 이 레이어가 살아있으면 STT나 Claude 모델이 바뀌어도 처음부터 다시 처리할 수 있다.

## 폴더 구조

```
/PLAUD Ledger/
  /2026/
    /09/
      /REC-20260902-001/
        audio.mp3
        transcript.json
        transcript.txt
        claude_output.json
        metadata.json
      /REC-20260902-002/
        ...
    /10/
      ...
```

| 레벨 | 이름 규칙 | 비고 |
|---|---|---|
| 루트 | `PLAUD Ledger` | Notion 컨테이너 페이지와 이름 통일 |
| 연도 | `YYYY` | 예: `2026` |
| 월 | `MM` | 예: `09` |
| 녹음 폴더 | `REC-YYYYMMDD-NNN` (Recording ID 그대로) | 폴더명=ID라서 사람이 봐도 바로 찾음 |

연/월로 나누는 이유: 한 폴더에 녹음이 몇 년치 쌓이면 Drive UI가 느려지고 찾기 어려워짐. 월 단위면 수백 건이 쌓여도 폴더당 항목 수가 적게 유지됨.

## 녹음 폴더 안 파일 (고정 파일명)

| 파일명 | 내용 | Layer | 용도 |
|---|---|---|---|
| `audio.<원본확장자>` | PLAUD 원본 오디오 그대로 (mp3/wav 등, presigned_url에서 받은 포맷 유지) | 1 (Source) | Source of Truth — 절대 수정 안 함 |
| `transcript.json` | whisper.cpp 결과 + pyannote 화자분리를 timestamp 기준 merge한 구조화 데이터. `[{speaker, start, end, text}, ...]` | 2 (Transcript) | Claude가 읽는 캐노니컬 포맷, 재처리의 기준점 |
| `transcript.txt` | 사람이 읽기 좋은 버전. 예: `[00:00:03] 화자1: 안녕하세요...` | 2 (Transcript) | Notion "Transcript URL"이 가리키는 대상 — 클릭하면 바로 읽힘 |
| `claude_output.json` | Claude 3-Pass 결과 전체(STEP4 JSON Schema). Notion에 들어간 것과 동일한 원본 | 3 (Intelligence) | 재처리/디버깅용 원본 보관. Notion 페이지가 깨져도 이걸로 복원 가능 |
| `metadata.json` | 아래 참조 | - | 파이프라인 메타 정보 |

**고정 파일명을 쓰는 이유**: 파일명이 매번 같아야 n8n이 "이 폴더 안의 transcript.json을 읽어라" 같은 로직을 변수 없이 짤 수 있음. 파일명에 날짜/ID를 또 넣지 않음 — 폴더명이 이미 ID라서 중복.

### metadata.json 구조
```json
{
  "recording_id": "REC-20260902-001",
  "plaud_file_id": "of_7443c22a908a1d8e9e6425906d388216",
  "title": "09-02 통화: 영양진단 절차 안내 및 마감기한 공지",
  "recorded_at": "2026-09-02T05:30:09Z",
  "duration_sec": 28,
  "drive_folder_id": "<Drive folder ID>",
  "ingested_at": "2026-09-02T05:35:00Z",
  "pipeline_version": {
    "stt_engine": "whisper.cpp-large-v3",
    "diarization": "pyannote-3.1",
    "claude_model": "claude-sonnet-5",
    "prompt_version": "v1",
    "template_version": "v1"
  },
  "status": "completed"
}
```

## Notion 필드와의 연결
- Notion **Google Drive Audio URL** → `audio.<ext>` 파일의 공유 링크 (폴더가 아니라 파일 직접 링크 — 클릭 한 번에 재생)
- Notion **Transcript URL** → `transcript.txt`의 공유 링크 (사람이 읽는 용도)
- `transcript.json`/`claude_output.json`/`metadata.json`은 Notion에 링크로 안 노출함 — n8n/Claude가 `drive_folder_id` + 고정 파일명으로 직접 읽는 내부용 파일

## Idempotency (중복 방지) — Notion과 동일한 원칙
n8n이 폴더를 만들기 전에 **`PLAUD Ledger/YYYY/MM/REC-...` 경로가 이미 있는지 먼저 검색** → 있으면 그 폴더에 파일을 업데이트, 없으면 새로 생성. Recording ID가 Notion과 Drive 양쪽에서 동일한 중복 방지 키로 작동함.

## 재처리(Reprocessing) 시 덮어쓰기 정책

| 파일 | 모델/엔진 교체 시 | 비고 |
|---|---|---|
| `audio.*` | **절대 덮어쓰지 않음** | 진짜 원본, 영구 불변 |
| `transcript.json` / `transcript.txt` | V1: 덮어씀 (어떤 엔진으로 만들었는지는 metadata.json의 stt_engine으로 추적) | V2: `transcript.v2.json`처럼 버전별로 보관하는 히스토리는 과설계 방지로 보류 |
| `claude_output.json` | V1: 덮어씀 | V2: 버전 히스토리 보류 |
| `metadata.json` | 매번 pipeline_version 갱신 | - |

## 권한 / 공유
- `PLAUD Ledger` 루트 폴더는 **비공개 유지** — 계약금액·법무상담 등 민감한 내용이 많아 로컬 Whisper로 전환한 것과 같은 이유.
- Notion에 노출되는 두 링크(`audio`, `transcript.txt`)만 "링크가 있는 사용자" 수준으로 최소 공유, 폴더 전체 공유는 하지 않음.

## ✅ 실제 Drive에 생성 완료 (2026-11-18, scobyisland@gmail.com)
사용자 결정: 기존 번호 체계(`00_INBOX_분류대기` 등)에 편입하지 않고 **독립 최상위 폴더**로 생성.

| 폴더 | 링크 |
|---|---|
| PLAUD Ledger (루트) | https://drive.google.com/drive/folders/1PmVXihV6bpq6xLwMdgL5gH6pNLob596s |
| 2026/11 | https://drive.google.com/drive/folders/1438oQQk3KBc5m03krzUs70Q_m_J1ydpE |

이후 월이 바뀌면 n8n이 Idempotency 원칙(검색 후 없으면 생성)에 따라 자동으로 새 월 폴더를 만든다.

## 다음 액션
- [ ] STEP 4 (Claude JSON Schema) 진행
