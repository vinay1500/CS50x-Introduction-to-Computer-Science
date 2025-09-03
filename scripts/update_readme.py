import os
import re
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timezone

REPO = os.getenv("GITHUB_REPOSITORY", "")  # e.g., "vinay1500/CS50x-Introduction-to-Computer-Science"
OWNER, NAME = (REPO.split("/") + ["", ""])[:2]

README = Path("README.md")
ROOT = Path(".")
START_PROGRESS = "<!-- CS50X_PROGRESS_START -->"
END_PROGRESS = "<!-- CS50X_PROGRESS_END -->"
START_BADGES = "<!-- CS50X_BADGES_START -->"
END_BADGES = "<!-- CS50X_BADGES_END -->"
START_SUMMARY = "<!-- CS50X_SUMMARY_START -->"
END_SUMMARY = "<!-- CS50X_SUMMARY_END -->"

# === EDIT THIS LIST to match your folders (left = folder name, right = display label) ===
SECTIONS = [
    ("Week 0 - Scratch", "Scratch"),
    ("Week 1 - C", "C: Basics"),
    ("Week 2 - Arrays", "Arrays"),
    ("Week 3 - Algorithms", "Algorithms"),
    ("Week 4 - Memory", "Memory"),
    ("Week 5 - Data Structures", "Data Structures"),
    ("Week 6 - Python", "Python"),
    ("Week 7 - SQL", "SQL"),
    ("Week 8 - HTML, CSS, JavaScript", "HTML, CSS, JavaScript"),
    ("Week 9 - Flask", "Flask"),
    ("Final Project", "Final Project"),
]

LANG_MAP = {
    ".c": "C",
    ".py": "Python",
    ".sql": "SQL",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".md": None,  # exclude Markdown from problem counts
}
SKIP_DIRS = {".git", ".github", "__pycache__", ".venv", "venv", ".idea", ".DS_Store"}
SKIP_FILES = {"README.md", "readme.md", "LICENSE"}

def is_countable_file(p: Path) -> bool:
    if not p.is_file():
        return False
    if p.name in SKIP_FILES:
        return False
    ext = p.suffix.lower()
    if ext in LANG_MAP:
        return LANG_MAP[ext] is not None
    return ext in {".h", ".hpp", ".txt", ".csv", ".json", ".jinja", ".j2", ".jinja2"}

def dir_nonempty(path: Path) -> bool:
    return path.exists() and any(x for x in path.rglob("*") if x.is_file())

def status_for(path: Path) -> str:
    if not path.exists():
        return "⏳ Pending"
    return "✅ Done" if dir_nonempty(path) else "🔄 In Progress"

def gh_link(owner: str, name: str, folder: str) -> str:
    encoded = quote(folder)
    if owner and name:
        return f"https://github.com/{owner}/{name}/tree/main/{encoded}"
    return f"./{folder}"

def collect_section_stats(folder: Path):
    total = 0
    by_lang = {}
    links = []
    if not folder.exists():
        return 0, {}, []
    for p in folder.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and is_countable_file(p):
            total += 1
            lang = LANG_MAP.get(p.suffix.lower(), "Other")
            if lang is None:
                lang = "Other"
            by_lang[lang] = by_lang.get(lang, 0) + 1
            rel = p.as_posix()
            links.append(f"- [{rel}](./{quote(rel)})")
    by_lang = dict(sorted(by_lang.items(), key=lambda kv: kv[1], reverse=True))
    links.sort()
    return total, by_lang, links

def build_table():
    header = "| Topic | Status | Problems Solved | Languages | Solutions |\n"
    header += "|-------|--------|------------------|-----------|-----------|"
    rows = []
    for folder, label in SECTIONS:
        section_path = ROOT / folder
        st = status_for(section_path)
        total, by_lang, _ = collect_section_stats(section_path)
        lang_str = ", ".join(f"{k} ({v})" for k, v in by_lang.items()) if by_lang else "—"
        link = gh_link(OWNER, NAME, folder)
        rows.append(f"| {label} | {st} | {total} | {lang_str} | [View]({link}) |")
    return header + "\n" + "\n".join(rows)

def build_badges():
    grand_total = 0
    lang_totals = {}
    for folder, _ in SECTIONS:
        total, by_lang, _ = collect_section_stats(ROOT / folder)
        grand_total += total
        for k, v in by_lang.items():
            lang_totals[k] = lang_totals.get(k, 0) + v
    badges = []
    badges.append(f"![Solved](https://img.shields.io/badge/Problems%20Solved-{grand_total}-success)")
    top_langs = sorted(lang_totals.items(), key=lambda kv: kv[1], reverse=True)[:3]
    for lang, cnt in top_langs:
        badges.append(f"![{lang}](https://img.shields.io/badge/{quote(lang)}-{cnt}-informational)")
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    badges.append(f"![Last Updated](https://img.shields.io/badge/Last%20Updated-{quote(now_utc)}-blue)")
    return " ".join(badges)

def build_summaries():
    parts = []
    for folder, label in SECTIONS:
        path = ROOT / folder
        st = status_for(path)
        total, by_lang, links = collect_section_stats(path)
        lang_md = ", ".join(f"**{k}**: {v}" for k, v in by_lang.items()) if by_lang else "—"
        max_links = 25
        visible_links = links[:max_links]
        more_count = max(0, len(links) - max_links)
        details = []
        details.append(f"<details><summary><strong>{label}</strong> — {st} · Problems: {total}</summary>\n")
        details.append("\n**Language Breakdown:** " + (lang_md if lang_md else "—") + "\n")
        if visible_links:
            details.append("\n**Files:**\n")
            details.append("\n".join(visible_links))
            if more_count:
                details.append(f"\n…and **{more_count} more**")
        else:
            details.append("\n_No files yet._")
        details.append("\n</details>\n")
        parts.append("".join(details))
    return "\n".join(parts)

def replace_block(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(rf"({re.escape(start_marker)})(.*)({re.escape(end_marker)})", re.DOTALL)
    replacement = f"{start_marker}\n{new_block}\n{end_marker}"
    if pattern.search(text):
        return pattern.sub(replacement, text)
    return text.rstrip() + f"\n\n{replacement}\n"

def main():
    if not README.exists():
        print("README.md not found. Exiting.")
        return
    original = README.read_text(encoding="utf-8")
    progress_md = build_table()
    badges_md = build_badges()
    summary_md = build_summaries()
    updated = original
    updated = replace_block(updated, START_BADGES, END_BADGES, badges_md)
    updated = replace_block(updated, START_PROGRESS, END_PROGRESS, progress_md)
    updated = replace_block(updated, START_SUMMARY, END_SUMMARY, summary_md)
    if updated != original:
        README.write_text(updated, encoding="utf-8")
        print("README.md updated.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()
