#!/usr/bin/env python3
"""The findings ledger of the review-round skill: one Markdown file per branch.

    ledger.py init  <file> <name> <base commit> <ref> [--fixed]
    ledger.py show  <file>                      base, last round, open entries
    ledger.py base  <file> <commit>             new base after a rebase or merge
    ledger.py start <file> <kind> <scope start> <head>   prints the round number
    ledger.py worktree <file> <path>            records the worktree of the running round
    ledger.py drop  <file>                      deletes the running round (interrupted or empty)
    ledger.py add   <file> <file:line> <finding>         prints the new ID
    ledger.py set   <file> <ID> <status> [<reason>]      open, fixed, rejected or deferred
    ledger.py close <file> <next step>          delta, full or done; prints the counts
"""
import re
import sys

STATUSES = ("open", "fixed", "rejected", "deferred")
FINDINGS = ["ID", "Round", "Status", "File", "Finding", "Reason"]
ROUNDS = ["Round", "Kind", "Scope start", "Head", "Worktree", "New", "Fixed", "Rejected",
          "Deferred", "Open", "Next", "State"]


def fail(msg):
    sys.exit(f"error: {msg}")


def cell(text):
    return str(text).replace("|", "/").replace("\n", " ").strip()


def load(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    head = re.search(r"^# Review ledger: (.*)\nBase: (\S+) \(ref (\S+?)(, fixed)?\)$", text, re.M)
    if not head:
        fail(f"{path} is not a ledger of this format")
    tables = {}
    for title, columns in (("Findings", FINDINGS), ("Rounds", ROUNDS)):
        section = re.search(rf"^## {title}\n\n\|.*\n\|[-| ]+\n((?:\|.*\n)*)", text, re.M)
        rows = section.group(1).splitlines() if section else []
        tables[title] = [dict(zip(columns, (c.strip() for c in r.strip("|").split("|"))))
                         for r in rows]
    return {"name": head[1], "base": head[2], "ref": head[3], "fixed": bool(head[4]),
            "findings": tables["Findings"], "rounds": tables["Rounds"]}


def save(path, ledger):
    def table(title, columns, rows):
        lines = [f"## {title}", "", "| " + " | ".join(columns) + " |",
                 "|" + "|".join("-" * (len(c) + 2) for c in columns) + "|"]
        lines += ["| " + " | ".join(cell(r.get(c, "")) for c in columns) + " |" for r in rows]
        return "\n".join(lines) + "\n"
    fixed = ", fixed" if ledger["fixed"] else ""
    text = (f"# Review ledger: {ledger['name']}\n"
            f"Base: {ledger['base']} (ref {ledger['ref']}{fixed})\n\n"
            + table("Findings", FINDINGS, ledger["findings"]) + "\n"
            + table("Rounds", ROUNDS, ledger["rounds"]))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def running(ledger):
    rows = [r for r in ledger["rounds"] if r["State"] == "running"]
    if not rows:
        fail("no round is running")
    return rows[-1]


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 2:
        fail(__doc__)
    cmd, path, args = argv[0], argv[1], argv[2:]
    if cmd == "init":
        if len(args) < 3 or args[3:] not in ([], ["--fixed"]):
            fail("usage: init <file> <name> <base commit> <ref> [--fixed]")
        name, base, ref = args[0], args[1], args[2]
        save(path, {"name": name, "base": base, "ref": ref, "fixed": args[3:] == ["--fixed"],
                    "findings": [], "rounds": []})
        return
    ledger = load(path)
    if cmd == "show":
        fixed = ", fixed" if ledger["fixed"] else ""
        print(f"base {ledger['base']} (ref {ledger['ref']}{fixed})")
        last = ledger["rounds"][-1] if ledger["rounds"] else None
        print("last round: " + (", ".join(f"{k}={v}" for k, v in last.items()) if last else "none"))
        for f in ledger["findings"]:
            if f["Status"] == "open":
                print(f"open {f['ID']} {f['File']} {f['Finding']}")
        return
    if cmd == "base":
        ledger["base"] = args[0]
    elif cmd == "start":
        if any(r["State"] == "running" for r in ledger["rounds"]):
            fail("a round is still running; drop it first")
        kind, start, head = args
        number = len(ledger["rounds"]) + 1
        ledger["rounds"].append({"Round": number, "Kind": kind, "Scope start": start, "Head": head,
                                 "Worktree": "none", "State": "running"})
        print(number)
    elif cmd == "worktree":
        running(ledger)["Worktree"] = args[0]
    elif cmd == "drop":
        ledger["rounds"].remove(running(ledger))
    elif cmd == "add":
        number = running(ledger)["Round"]
        ids = [int(f["ID"][1:]) for f in ledger["findings"] if f["ID"][1:].isdigit()]
        new_id = f"F{max(ids, default=0) + 1}"
        ledger["findings"].append({"ID": new_id, "Round": number, "Status": "open",
                                   "File": args[0], "Finding": " ".join(args[1:]), "Reason": ""})
        print(new_id)
    elif cmd == "set":
        fid, status, reason = args[0], args[1], " ".join(args[2:])
        if status not in STATUSES:
            fail(f"status must be one of {', '.join(STATUSES)}")
        entry = next((f for f in ledger["findings"] if f["ID"] == fid), None)
        if not entry:
            fail(f"no finding {fid}")
        entry["Status"] = status
        if reason:
            entry["Reason"] = reason
    elif cmd == "close":
        if args[0] not in ("delta", "full", "done"):
            fail("next step must be delta, full or done")
        row = running(ledger)
        new = [f for f in ledger["findings"] if f["Round"] == str(row["Round"])]
        row["New"] = len(new)
        for status in STATUSES[1:]:
            row[status.capitalize()] = sum(f["Status"] == status for f in new)
        row["Open"] = sum(f["Status"] == "open" for f in ledger["findings"])
        row["Next"], row["State"] = args[0], "closed"
        print(", ".join(f"{k.lower()} {row[k]}" for k in ("New", "Fixed", "Rejected", "Deferred",
                                                           "Open")) + f"; next: {args[0]}")
    else:
        fail(f"unknown command {cmd}")
    save(path, ledger)


if __name__ == "__main__":
    main(sys.argv[1:])
