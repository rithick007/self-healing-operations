"""Print id | name | skill | area for records piped in as Lemma --json output."""
import sys, json

rows = json.load(sys.stdin).get("items", [])
for r in rows:
    print(
        r.get("id"),
        "|",
        r.get("customer_name") or r.get("name"),
        "|",
        r.get("skill_required") or ",".join(r.get("skills") or []),
        "|",
        r.get("area"),
        "|",
        r.get("status"),
    )
