# skillmap — 기기별 스킬 위치·버전 지도

## 흐름
1. 각 기기에서 `scan.py` 실행 → `inventory/<기기명>.json`
2. 이 레포에 commit·push (기기별 파일이라 충돌 없음)
3. 아무 기기에서 pull 후 `report.py` 실행 → `SKILLS.md` (Notion에 그대로 붙여넣기)

## Mac 명령
```
python3 skillmap/scan.py --device macbook --project-root ~/Projects
git add inventory && git commit -m "scan macbook" && git push
git pull && python3 skillmap/report.py
```

## 스캔 범위
| 종류 | 경로 |
|---|---|
| user | `~/.claude/skills/*/SKILL.md` |
| plugin | `~/.claude/plugins/**/skills/*/SKILL.md` |
| project | `--project-root` 아래 `**/.claude/skills/*/SKILL.md` |

## 판정
- 해시 = 스킬 폴더 전체 파일 내용의 SHA-256 앞 12자. 같으면 동일 스킬.
- ⚠️ 해시 다름 = 기기 간 버전 불일치, 🔁 같은 기기 중복, ✅ 동일, 1️⃣ 단일.

## 주의
- `inventory/*.json`에 로컬 경로(사용자명 포함)가 들어갑니다. 레포가 private인지 확인하세요.
- claude.ai 계정 스킬·Notion 스킬은 로컬 파일이 아니라 스캔 대상이 아닙니다 (미지원).
