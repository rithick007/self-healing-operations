"""Pretty-print selected columns from Lemma --json record output.

Usage: ... --json | python show_rows.py col1 col2 col3
"""
import sys, json

cols = sys.argv[1:]
rows = json.load(sys.stdin).get("items", [])
for r in rows:
    if cols:
        print(" | ".join(f"{c}={r.get(c)}" for c in cols))
    else:
        print(json.dumps(r))
print(f"[{len(rows)} row(s)]")
