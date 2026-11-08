#!/usr/bin/env python3
"""기기의 Claude Code 스킬을 스캔해 inventory/<기기명>.json 으로 저장한다.

사용: python3 skillmap/scan.py [--device 이름] [--project-root 경로 ...] [--out inventory]
스캔 위치:
  user    ~/.claude/skills/*/SKILL.md
  plugin  ~/.claude/plugins/**/skills/*/SKILL.md
  project <project-root>/**/.claude/skills/*/SKILL.md  (지정한 경우만)
"""
import argparse, hashlib, json, os, platform, re, socket, sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "__pycache__", "Library", "Applications"}


def dir_hash(d: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in d.rglob("*") if x.is_file()):
        h.update(str(p.relative_to(d)).encode())
        try:
            h.update(p.read_bytes())
        except OSError:
            h.update(b"<unreadable>")
    return h.hexdigest()[:12]


def parse_front(md: Path):
    name = desc = ""
    try:
        text = md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return name, desc
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("\"'")
            elif line.startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip("\"'")
    return name, desc[:160]


def entry(md: Path, kind: str):
    d = md.parent
    name, desc = parse_front(md)
    files = [p for p in d.rglob("*") if p.is_file()]
    return {
        "name": name or d.name,
        "kind": kind,
        "path": str(d),
        "description": desc,
        "files": len(files),
        "modified": datetime.fromtimestamp(max((p.stat().st_mtime for p in files), default=0), timezone.utc).strftime("%Y-%m-%d"),
        "hash": dir_hash(d),
        "symlink": d.is_symlink(),
    }


def walk(root: Path, kind: str, must_contain: str):
    out = []
    if not root.exists():
        return out
    for cur, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        if "SKILL.md" in files and must_contain in Path(cur).parent.as_posix():
            out.append(entry(Path(cur) / "SKILL.md", kind))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=socket.gethostname().split(".")[0])
    ap.add_argument("--project-root", action="append", default=[])
    ap.add_argument("--out", default="inventory")
    a = ap.parse_args()
    home = Path.home()
    skills = []
    skills += walk(home / ".claude" / "skills", "user", "skills")
    skills += walk(home / ".claude" / "plugins", "plugin", "skills")
    for r in a.project_root:
        skills += walk(Path(r).expanduser(), "project", ".claude/skills")
    seen, uniq = set(), []
    for s in skills:  # 중복 경로 제거
        if s["path"] not in seen:
            seen.add(s["path"]); uniq.append(s)
    data = {
        "device": a.device,
        "os": f"{platform.system()} {platform.release()}",
        "scanned_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "skills": sorted(uniq, key=lambda s: (s["name"], s["path"])),
    }
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    f = out / f"{a.device}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{a.device}: {len(uniq)}개 스킬 -> {f}")


if __name__ == "__main__":
    sys.exit(main())
