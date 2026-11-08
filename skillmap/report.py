#!/usr/bin/env python3
"""inventory/*.json 을 합쳐 SKILLS.md (Notion 붙여넣기용 표)를 만든다.
사용: python3 skillmap/report.py [--inv inventory] [--out SKILLS.md]
"""
import argparse, json
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inv", default="inventory")
    ap.add_argument("--out", default="SKILLS.md")
    a = ap.parse_args()
    devs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(a.inv).glob("*.json"))]
    by_name = defaultdict(list)
    for d in devs:
        for s in d["skills"]:
            by_name[s["name"]].append((d["device"], s))

    L = ["# 스킬 지도", ""]
    L += ["## 기기 요약", "", "| 기기 | OS | 스킬 수 | 마지막 스캔 |", "|---|---|---|---|"]
    for d in devs:
        L.append(f"| {d['device']} | {d['os']} | {len(d['skills'])} | {d['scanned_at']} |")
    L += ["", "## 스킬별 현황", "",
          "상태: ✅ 모든 사본 동일 / ⚠️ 버전 불일치(해시 다름) / 🔁 한 기기에 중복 설치 / 1️⃣ 단일 사본", "",
          "| 스킬 | 상태 | 위치 (기기: 종류 · 해시 · 수정일) |", "|---|---|---|"]
    issues = []
    for name in sorted(by_name):
        items = by_name[name]
        hashes = {s["hash"] for _, s in items}
        per_dev = defaultdict(int)
        for dv, _ in items:
            per_dev[dv] += 1
        if len(hashes) > 1:
            st = "⚠️ 버전 불일치"; issues.append(f"- ⚠️ `{name}`: 해시 {len(hashes)}종")
        elif any(c > 1 for c in per_dev.values()):
            st = "🔁 중복"; issues.append(f"- 🔁 `{name}`: 같은 기기에 중복 설치")
        elif len(items) == 1:
            st = "1️⃣ 단일"
        else:
            st = "✅ 동일"
        where = "<br>".join(f"{dv}: {s['kind']} · `{s['hash']}` · {s['modified']}" for dv, s in items)
        L.append(f"| {name} | {st} | {where} |")
    L += ["", "## 조치 필요", ""] + (issues or ["- 없음"])
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(devs)}대, {len(by_name)}개 스킬 -> {a.out}")


if __name__ == "__main__":
    main()
