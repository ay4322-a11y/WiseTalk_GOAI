#!/usr/bin/env python3
"""WiseTalk Skill-4: MECE Logic Overlap & Omission Detection.

Deterministic checker for a list of argument points:
  1. Overlap detection  - a point whose tokens (or synonyms) are contained in
                          another point, or whose text is a verbatim substring
                          of another point, is an overlap.
  2. Omission detection  - any dimension of the fixed 4M1E library with no
                          keyword coverage across all points is reported missing.

Usage (input either as --points JSON or via stdin):
    python mece-check.py --points '["Reduce labor cost", "Cut overtime pay", "Improve efficiency"]'
    echo '{"points_list": ["A", "B"]}' | python mece-check.py

Output:
    {"is_valid": bool, "overlap_reason": str|null, "missing_dimension": str|null}
or, with fewer than 2 non-empty points:
    {"message": "Cannot perform MECE analysis"}

Exits 0 on all expected outputs (verdict or exception message); exits 2 on
input that cannot be parsed as JSON.
"""

import json
import re
import sys

# Fixed 4M1E domain library (WiseTalk spec p.4; mirrored in
# reference/wisetalk-model-catalog.md). One keyword hit in any point covers the
# dimension. English-only per D-007.
DIMENSIONS = {
    "Human": ["human", "people", "staff", "employee", "talent", "labor",
              "labour", "headcount", "skill", "team", "workforce", "personnel",
              "recruit", "hire", "employ", "analyst", "manager", "leader",
              "expert", "contractor", "training"],
    "Machine": ["machine", "equipment", "hardware", "tool", "server", "system",
                "device", "automation", "software", "infrastructure",
                "machinery", "rig", "vehicle", "fleet", "tooling"],
    "Material": ["material", "supply", "inventory", "raw", "component", "part",
                 "stock", "input", "asset", "goods", "alloy", "consumable",
                 "feedstock"],
    "Method": ["method", "process", "procedure", "workflow", "approach",
               "practice", "protocol", "guideline", "standard", "design",
               "checklist", "template", "routine", "framework", "plan"],
    "Environment": ["environment", "market", "regulation", "policy", "culture",
                    "location", "site", "context", "external", "compliance",
                    "safety", "law", "climate"],
}

# Synonym expansion: a specific term maps to the broader categories it belongs
# to. Grounds the spec's example ("labor cost" is a superset of "overtime pay").
SYNONYMS = {
    "overtime": ["labor", "labour", "hours", "time"],
    "pay": ["cost", "salary", "compensation", "wage", "income"],
    "salary": ["cost", "pay", "compensation", "income"],
    "wage": ["cost", "pay"],
    "cost": ["expense", "spend", "spending"],
    "expense": ["cost", "spend"],
    "reduce": ["cut", "lower", "decrease", "save"],
    "cut": ["reduce", "lower", "decrease"],
    "improve": ["increase", "enhance", "optimize", "boost"],
    "efficiency": ["productivity", "performance"],
    "buy": ["purchase", "acquire", "procure"],
    "hire": ["recruit", "staff", "employ"],
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "to", "of", "in", "on", "at", "for",
    "with", "by", "we", "our", "us", "it", "its", "is", "are", "be", "been",
    "being", "will", "would", "can", "could", "should", "must", "this", "that",
    "these", "those", "your", "my", "our", "as", "so", "up", "down", "out",
}

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def normalize(text):
    """Lowercase, strip punctuation, collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text):
    """Significant tokens of a point (stopwords removed)."""
    return {t for t in TOKEN_RE.findall(normalize(text)) if t not in STOPWORDS}


def expand(tokens):
    """Token set plus every synonym of each token (D-004)."""
    out = set(tokens)
    for t in tokens:
        out.update(SYNONYMS.get(t, ()))
    return out


def check_overlap(points, n):
    """First overlapping pair, or None.

    Overlap rule (D-004): point i overlaps point j when the significant tokens
    of i are all contained in the synonym-expanded set of j (either direction),
    or when point i's text is a verbatim substring of point j's text.
    """
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a_tok, b_tok = tokenize(points[i]), tokenize(points[j])
            if not a_tok or not b_tok:
                continue
            # identical token sets -> duplicates
            if a_tok == b_tok:
                return ("Point %d and Point %d are duplicates: '%s' and '%s'"
                        % (i + 1, j + 1, points[i], points[j]))
            # containment via synonym expansion
            if a_tok <= expand(b_tok):
                return ("Point %d '%s' overlaps Point %d '%s': its content is "
                        "contained in the other point."
                        % (i + 1, points[i], j + 1, points[j]))
            if b_tok <= expand(a_tok):
                return ("Point %d '%s' overlaps Point %d '%s': its content is "
                        "contained in the other point."
                        % (j + 1, points[j], i + 1, points[i]))
            # verbatim substring nesting
            a_norm, b_norm = normalize(points[i]), normalize(points[j])
            if a_norm != b_norm and (a_norm in b_norm or b_norm in a_norm):
                return ("Point %d and Point %d overlap: '%s' is a verbatim "
                        "substring of '%s'."
                        % (i + 1, j + 1, a_norm if len(a_norm) <= len(b_norm)
                           else b_norm, b_norm if len(a_norm) <= len(b_norm)
                           else a_norm))
    return None


def check_dimensions(points):
    """Comma-joined names of uncovered 4M1E dimensions, or None (D-005)."""
    covered = set()
    for p in points:
        covered.update(t for t in expand(tokenize(p)) if t in
                       {kw for kws in DIMENSIONS.values() for kw in kws})
    missing = [dim for dim, kws in DIMENSIONS.items()
               if not (covered & set(kws))]
    if not missing:
        return None
    return "%s dimension(s) missing." % ", ".join(missing)


def run(points_list):
    points = [p for p in (normalize(p) for p in points_list) if p]
    if len(points) < 2:
        return {"message": "Cannot perform MECE analysis"}
    overlap_reason = check_overlap(points, len(points))
    missing_dim = check_dimensions(points)
    return {
        "is_valid": overlap_reason is None and missing_dim is None,
        "overlap_reason": overlap_reason,
        "missing_dimension": missing_dim,
    }


def main():
    args = sys.argv[1:]
    raw = None
    if args and args[0] == "--points":
        raw = args[1] if len(args) > 1 else None
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    if not raw:
        print("Usage: python mece-check.py --points '<JSON array of points>', "
              "or pipe {'points_list': [...]} via stdin", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "Cannot parse input as JSON: %s" % e}))
        sys.exit(2)
    if isinstance(data, list):
        points_list = data
    elif isinstance(data, dict) and isinstance(data.get("points_list"), list):
        points_list = data["points_list"]
    else:
        print(json.dumps({"error": "Input must be a JSON array or "
                                   "{'points_list': [...]}"}))
        sys.exit(2)
    print(json.dumps(run(points_list), ensure_ascii=False))


if __name__ == "__main__":
    main()
