#!/usr/bin/env python3
"""WiseTalk Skill-11 — deterministic prompt-injection & sensitive-keyword interceptor.

DFA (Aho-Corasick) over scripts/sensitive-words.txt + a regex phrase layer.
Fail-closed by design: any non-safe outcome (bad args, missing wordlist, crash)
is reported as blocked — a false negative is worse than a false positive.

Usage:
    python dfa-filter.py --text <user message, unquoted>
    echo "<message>" | python dfa-filter.py

Output (one JSON line, the PDF's exact contract):
    Safe:    {"is_blocked": false, "clean_text": "<original message verbatim>"}
    Blocked: {"is_blocked": true, "block_reason": "Contains prohibited vocabulary or prompt injection."}

Exit codes: 0 = safe, 1 = blocked, 2 = usage error, 3 = internal error (fail-closed: 2 and 3 mean "treat as blocked").
"""

import argparse
import re
import sys
from collections import deque
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORDLIST = SCRIPT_DIR / "sensitive-words.txt"
BLOCK_REASON = "Contains prohibited vocabulary or prompt injection."

# Regex layer — phrase-level injection patterns (PDF: /ignore previous instructions|jailbreak|system prompt/i style).
# Applied to the normalized text. Keep patterns to manipulation vocabulary only (D-004): legitimate workplace
# language must never hit them.
INJECTION_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions?",
    r"ignore\s+previous\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior)\s+instructions?",
    r"forget\s+(all\s+)?(previous|prior)\s+instructions?",
    r"(reveal|show|print|output|disclose|leak)\s+(your\s+)?(system\s+)?(prompt|instructions?|system\s+message)",
    r"what\s+is\s+your\s+system\s+prompt",
    r"jailbreak",
    r"developer\s+mode",
    r"sudo\s+mode",
    r"unrestricted\s+mode",
    r"override\s+(your\s+)?(instructions?|rules?|guidelines?|prompt|guardrails?)",
    r"bypass\s+(your\s+)?(instructions?|rules?|filters?|guardrails?|safeguards?|restrictions?)",
    r"remove\s+(your\s+)?(rules?|restrictions?|limitations?|safety\s+filters?)",
    r"act\s+as\s+if\s+you\s+(are|have)\s+(no|without)\s+rules",
    r"do\s+anything\s+now",
    r"no\s+rules",
]

ZERO_WIDTH_RE = re.compile(r"[​-‍﻿]")  # zero-width space / joiners / BOM
WHITESPACE_RE = re.compile(r"\s+")
FLAG_RE = re.compile(r"^\s*(#|$)")


def normalize(text: str) -> str:
    """Deterministic normalization for matching: lowercase, strip zero-width chars, collapse whitespace."""
    return WHITESPACE_RE.sub(" ", ZERO_WIDTH_RE.sub("", text)).strip().lower()


def load_wordlist() -> list[str]:
    """Load sensitive phrases from sensitive-words.txt (one per line, '#' comments allowed)."""
    if not WORDLIST.exists():
        raise FileNotFoundError(f"wordlist not found: {WORDLIST}")
    words = []
    for raw in WORDLIST.read_text(encoding="utf-8").splitlines():
        if FLAG_RE.match(raw):
            continue
        word = normalize(raw)
        if word:
            words.append(word)
    if not words:
        raise ValueError(f"wordlist is empty: {WORDLIST}")
    return words


class AhoCorasick:
    """Aho-Corasick DFA — the canonical multi-pattern matcher: builds a trie with failure links
    from the wordlist, then scans the text in a single O(len(text)) pass (D-007)."""

    def __init__(self, patterns: list[str]):
        self.patterns = patterns
        self.go = [{}]          # trie transitions: node -> {char -> node}
        self.fail = [0]         # failure links
        self.output = [[]]      # patterns ending at each node
        for pidx, pattern in enumerate(patterns):
            self._insert(pattern, pidx)
        self._build_failures()

    def _insert(self, pattern: str, pidx: int) -> None:
        node = 0
        for ch in pattern:
            if ch not in self.go[node]:
                self.go[node][ch] = len(self.go)
                self.go.append({})
                self.fail.append(0)
                self.output.append([])
            node = self.go[node][ch]
        self.output[node].append(pidx)

    def _build_failures(self) -> None:
        queue = deque()
        for ch, node in self.go[0].items():
            self.fail[node] = 0
            queue.append(node)
        while queue:
            r = queue.popleft()
            for ch, u in self.go[r].items():
                queue.append(u)
                f = self.fail[r]
                while f and ch not in self.go[f]:
                    f = self.fail[f]
                self.fail[u] = self.go[f][ch] if ch in self.go[f] else 0
                self.output[u] = self.output[u] + self.output[self.fail[u]]

    def scan(self, text: str) -> list[int]:
        """Return the indices of all wordlist patterns that occur in text."""
        node = 0
        hits = []
        for ch in text:
            while node and ch not in self.go[node]:
                node = self.fail[node]
            node = self.go[node][ch] if ch in self.go[node] else 0
            if self.output[node]:
                hits.extend(self.output[node])
        return sorted(set(hits))


def check(text: str) -> dict:
    """Deterministic verdict. Raises on internal errors — the caller treats any raise as blocked (fail-closed)."""
    normalized = normalize(text)
    patterns = load_wordlist()
    dfa = AhoCorasick(patterns)
    if dfa.scan(normalized):
        return {"is_blocked": True, "block_reason": BLOCK_REASON}
    if re.search("|".join(INJECTION_PATTERNS), normalized, re.IGNORECASE):
        return {"is_blocked": True, "block_reason": BLOCK_REASON}
    return {"is_blocked": False, "clean_text": text}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="WiseTalk Skill-11 injection filter (deterministic, fail-closed).")
    parser.add_argument("--text", nargs=argparse.REMAINDER,
                        help="the user message, unquoted (all remaining args joined); reads stdin when absent")
    args = parser.parse_args(argv)

    if args.text:
        text = " ".join(args.text)
    else:
        text = sys.stdin.read()

    try:
        result = check(text)
    except Exception as exc:  # fail-closed: any internal failure is reported as blocked (D-003)
        print(f'{{"is_blocked": true, "block_reason": "Contains prohibited vocabulary or prompt injection."}}')
        print(f'[dfa-filter] internal error, treated as blocked: {exc}', file=sys.stderr)
        return 3

    import json
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["is_blocked"] is False else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
