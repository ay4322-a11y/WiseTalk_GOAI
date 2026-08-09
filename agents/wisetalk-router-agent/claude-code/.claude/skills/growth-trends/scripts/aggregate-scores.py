#!/usr/bin/env python3
"""WiseTalk Skill-10: Long-Term Trend Analysis (code-first, deterministic).

Reads historical battle-score records (the Skill-9 persistence contract, JSONL:
{"date": "YYYY-MM-DD", "logic": 0-100, "eq": 0-100, "response_speed": 0-100, "persuasion": 0-100}),
buckets them weekly (ISO Monday) or monthly (YYYY-MM-01), averages each of the
4 dimensions per bucket (integer mean, round half up), and names the weak point
(lowest average dimension; "declining" suffix when the last bucket < first bucket).

Output contract (PDF): success -> {"trend_data": {"dates": [...], "logic": [...],
"eq": [...], "response_speed": [...], "persuasion": [...]}, "weak_point": "..."}
empty/missing/all-malformed -> {"message": "No history available yet"}

Exit codes: 0 = ok (including the empty-history message); 2 = usage error.
Malformed records are skipped, never fatal, never guessed.
"""
import argparse
import datetime as dt
import json
import sys

DIMENSIONS = ["logic", "eq", "response_speed", "persuasion"]
DIMENSION_LABELS = {
    "logic": "Logic",
    "eq": "Emotional Empathy",
    "response_speed": "On-the-spot Responsiveness",
    "persuasion": "Persuasiveness",
}
EMPTY_MESSAGE = "No history available yet"


def parse_record(line):
    """Return (date, scores) or None for a malformed line."""
    try:
        rec = json.loads(line)
    except (ValueError, TypeError):
        return None
    if not isinstance(rec, dict):
        return None
    date_text = rec.get("date")
    try:
        date = dt.date.fromisoformat(date_text)
    except (TypeError, ValueError):
        return None
    scores = {}
    for key in DIMENSIONS:
        value = rec.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not (0 <= value <= 100):
            return None
        scores[key] = value
    return date, scores


def bucket_key(date, weekly):
    if weekly:
        # ISO week: Monday-start label.
        return (date - dt.timedelta(days=date.weekday())).isoformat()
    return date.strftime("%Y-%m-01")


def aggregate(records, weekly):
    """records: list of (date, scores). Returns (buckets: {label: {dim: [values]}}, ordered_labels)."""
    buckets = {}
    for date, scores in records:
        key = bucket_key(date, weekly)
        buckets.setdefault(key, {dim: [] for dim in DIMENSIONS})
        for dim in DIMENSIONS:
            buckets[key][dim].append(scores[dim])
    return buckets


def mean_half_up(values):
    return int(sum(values) / len(values) + 0.5)


def weak_point(buckets, ordered_labels):
    """Lowest average dimension across the range; tie -> fixed dimension order.
    "declining" suffix iff >= 2 buckets and last-bucket average < first-bucket average."""
    # Per-bucket averages of each dimension, then mean over buckets.
    per_bucket = {
        dim: [mean_half_up(buckets[label][dim]) for label in ordered_labels]
        for dim in DIMENSIONS
    }
    dim_means = {dim: mean_half_up(per_bucket[dim]) for dim in DIMENSIONS}
    lowest = min(DIMENSIONS, key=lambda d: dim_means[d])
    label = DIMENSION_LABELS[lowest]
    if len(ordered_labels) >= 2:
        first, last = per_bucket[lowest][0], per_bucket[lowest][-1]
        if last < first:
            label += " declining"
    return label


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="WiseTalk Skill-10: aggregate battle-score history into growth trends",
        add_help=False,
    )
    parser.add_argument("--scores", required=True, help="path to the JSONL battle-score records file")
    parser.add_argument("--range", choices=("weekly", "monthly"), default="weekly", help="bucket granularity")
    parser.add_argument("--help", action="help", help="show this help")
    args = parser.parse_args(argv)

    try:
        with open(args.scores, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        lines = []  # missing file == no history yet (graceful, per UC-002)

    records = []
    for line in lines:
        parsed = parse_record(line)
        if parsed is not None:
            records.append(parsed)

    if not records:
        print(json.dumps({"message": EMPTY_MESSAGE}))
        return 0

    buckets = aggregate(records, args.range == "weekly")
    ordered_labels = sorted(buckets.keys())

    result = {
        "trend_data": {
            "dates": ordered_labels,
            "logic": [mean_half_up(buckets[label]["logic"]) for label in ordered_labels],
            "eq": [mean_half_up(buckets[label]["eq"]) for label in ordered_labels],
            "response_speed": [mean_half_up(buckets[label]["response_speed"]) for label in ordered_labels],
            "persuasion": [mean_half_up(buckets[label]["persuasion"]) for label in ordered_labels],
        },
        "weak_point": weak_point(buckets, ordered_labels),
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
