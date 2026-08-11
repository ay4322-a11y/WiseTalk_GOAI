#!/usr/bin/env python3
"""WiseTalk Skills Library sync script.

Copies the canonical skill versions from skills-library/ into every agent's
claude-code/.claude/skills/ directory. The library is the single source of
truth; agent copies must never be edited by hand (they get overwritten).

Usage:
    python skills-library/sync.py --skill <name>       sync one skill
    python skills-library/sync.py --all                sync every library skill
    python skills-library/sync.py --verify             exit non-zero if any agent copy has drifted
    python skills-library/sync.py --skill <name> --dry-run   preview without writing

Discovery:
    Library skills = folders under skills-library/ containing a SKILL.md.
    Targets = folders named <skill> under agents/*/claude-code/.claude/skills/.
    Optional sync-manifest.json may add extra targets per skill (e.g. a future
    agent that does not yet exist); entries there are merged with discovery.
"""
import argparse
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(ROOT, "skills-library")
AGENTS_DIR = os.path.join(ROOT, "agents")
MANIFEST_PATH = os.path.join(LIBRARY_DIR, "sync-manifest.json")


def library_skills():
    """Folders under skills-library/ that carry a SKILL.md."""
    if not os.path.isdir(LIBRARY_DIR):
        return []
    return sorted(
        d for d in os.listdir(LIBRARY_DIR)
        if os.path.isfile(os.path.join(LIBRARY_DIR, d, "SKILL.md"))
    )


def discovered_targets(skill):
    """Agent skill folders named <skill> that already exist."""
    if not os.path.isdir(AGENTS_DIR):
        return []
    pattern = os.path.join("claude-code", ".claude", "skills", skill)
    targets = []
    for agent in sorted(os.listdir(AGENTS_DIR)):
        candidate = os.path.join(AGENTS_DIR, agent, pattern)
        if os.path.isdir(candidate):
            targets.append(candidate)
    return targets


def manifest_targets(skill):
    """Extra targets from sync-manifest.json (relative paths, optional file)."""
    if not os.path.isfile(MANIFEST_PATH):
        return []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    entries = manifest.get(skill, {}).get("targets", [])
    return [os.path.normpath(os.path.join(ROOT, rel)) for rel in entries]


def resolve_targets(skill):
    """Union of discovered + manifest targets, deduped, existing only."""
    seen, targets = set(), []
    for target in discovered_targets(skill) + manifest_targets(skill):
        norm = os.path.normcase(os.path.abspath(target))
        if norm in seen or not os.path.isdir(target):
            continue
        seen.add(norm)
        targets.append(target)
    return sorted(targets)


def _normalized(path):
    """File bytes with line endings normalized to LF.

    Skill files are all text (.md, .py, .txt, .json). On Windows a checkout with
    core.autocrlf=true, or simply saving a library file in an editor, can leave the
    library copy CRLF while an agent copy stays LF — identical content, different
    bytes. Comparing raw bytes reported that as drift and failed a gate that is
    supposed to mean "an agent is running a stale skill". Normalizing first keeps
    every real content difference detectable while ignoring the checkout artifact.
    """
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def files_differ(src_dir, dst_dir):
    """True if any file under src_dir differs from its dst_dir counterpart, or is missing.

    Comparison is line-ending-insensitive; see _normalized().
    """
    for dirpath, _dirnames, filenames in os.walk(src_dir):
        rel = os.path.relpath(dirpath, src_dir)
        dst_sub = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        for name in filenames:
            src_file = os.path.join(dirpath, name)
            dst_file = os.path.join(dst_sub, name)
            if not os.path.isfile(dst_file):
                return True
            if _normalized(src_file) != _normalized(dst_file):
                return True
    return False


def copy_skill(src_dir, dst_dir):
    """Overwrite dst_dir with a fresh copy of src_dir. Returns number of files written."""
    if os.path.isdir(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)
    count = 0
    for _dirpath, _dirnames, filenames in os.walk(dst_dir):
        count += len(filenames)
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description="WiseTalk skills-library sync")
    parser.add_argument("--skill", help="sync a single skill by folder name")
    parser.add_argument("--all", action="store_true", help="sync every library skill")
    parser.add_argument("--verify", action="store_true", help="check for drift; exit 1 if any copy differs")
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args(argv)

    skills = [args.skill] if args.skill else (library_skills() if args.all else library_skills())
    if not skills:
        print("No library skills found under skills-library/")
        return 2

    drifted, synced, errors = [], [], []

    for skill in skills:
        src_dir = os.path.join(LIBRARY_DIR, skill)
        if not os.path.isdir(src_dir):
            print(f"[skip] {skill}: no folder in skills-library")
            continue
        targets = resolve_targets(skill)
        if not targets:
            print(f"[info] {skill}: no agent targets found (library copy only)")
            continue
        for dst_dir in targets:
            label = os.path.relpath(dst_dir, ROOT)
            if files_differ(src_dir, dst_dir):
                if args.verify:
                    drifted.append(label)
                    print(f"[drift] {skill} -> {label}")
                elif args.dry_run:
                    print(f"[would-sync] {skill} -> {label}")
                    synced.append(label)
                else:
                    count = copy_skill(src_dir, dst_dir)
                    print(f"[synced] {skill} -> {label} ({count} files)")
                    synced.append(label)
            else:
                print(f"[ok] {skill} -> {label} (in sync)")

    if args.verify:
        if drifted:
            print(f"\n{len(drifted)} agent copy/copies out of sync — run sync.py --all")
            return 1
        print("\nAll agent copies in sync.")
        return 0
    print(f"\n{len(synced)} target(s) synced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
