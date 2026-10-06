#!/usr/bin/env python3
"""Azure DevOps pull request threads for the address-review skill. Standard library only.

  info                       organization, project, repository, branch, token file presence
  pr [PR]                    the active PR of the current branch, or the given one
  threads [PR] [--all]       open threads, one block each (--all: every status)
  reply THREAD TEXT [PR]     post TEXT in thread THREAD; TEXT "-" reads stdin
  resolve THREAD [PR]        set the thread status to fixed

PR is !NNNN, NNNN or the PR URL; ids are unique across the organization. THREAD is the id shown
by "threads", with or without the T prefix. The token is read from the file that the
AZURE_DEVOPS_PAT_FILE environment variable points at (scope: Code read and write).
"""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "api-version=7.1"
TOKEN_FILE_VAR = "AZURE_DEVOPS_PAT_FILE"
DEFAULT_ORG = "exacomtech"


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def repo_coords():
    """(organization, project, repository) of origin; None when origin is not on Azure DevOps."""
    url = git("remote", "get-url", "origin")
    patterns = (
        r"https://(?:[^@/]+@)?dev\.azure\.com/([^/]+)/([^/]+)/_git/([^/]+?)(?:\.git)?/?$",
        r"git@ssh\.dev\.azure\.com:v3/([^/]+)/([^/]+)/([^/]+?)(?:\.git)?$",
        r"https://([^./]+)\.visualstudio\.com/([^/]+)/_git/([^/]+?)(?:\.git)?/?$",
    )
    for p in patterns:
        m = re.match(p, url)
        if m:
            return tuple(urllib.parse.unquote(x) for x in m.groups())
    return None


def token():
    path = os.environ.get(TOKEN_FILE_VAR)
    if not path:
        die(f"{TOKEN_FILE_VAR} is not set")
    try:
        with open(path, encoding="utf-8") as f:
            pat = f.read().strip()
    except OSError as e:
        die(f"cannot read the token file: {e}")
    if not pat:
        die(f"the token file {path} is empty")
    return pat


def call(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Authorization", "Basic " + base64.b64encode(f":{token()}".encode()).decode())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        die(f"{method} {url}\nHTTP {e.code}: {e.read().decode(errors='replace')[:500]}")
    if not raw.lstrip().startswith(b"{"):  # a sign-in page means the token was not accepted
        die(f"Azure DevOps returned no JSON; check the token in {TOKEN_FILE_VAR}")
    return json.loads(raw)


def parse_pr(arg):
    """PR number from !NNNN, NNNN or a PR URL."""
    m = re.search(r"pullrequest/(\d+)", arg) or re.fullmatch(r"!?(\d+)", arg)
    if not m:
        die(f"not a PR id or URL: {arg}")
    return int(m.group(1))


class Pr:
    """A pull request and the REST base of its repository (repository.url from the API)."""

    def __init__(self, arg):
        coords = repo_coords()
        if arg:
            org = coords[0] if coords else DEFAULT_ORG
            data = call("GET", f"https://dev.azure.com/{urllib.parse.quote(org)}/_apis/git/pullrequests/{parse_pr(arg)}?{API}")
        else:
            if not coords:
                die("origin is not an Azure DevOps remote; give the PR number")
            branch = git("branch", "--show-current")
            if not branch:
                die("detached HEAD; give the PR number")
            org, project, repo = (urllib.parse.quote(x) for x in coords)
            ref = urllib.parse.quote(f"refs/heads/{branch}", safe="")
            res = call("GET", f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullrequests?searchCriteria.sourceRefName={ref}&searchCriteria.status=active&{API}")
            prs = res.get("value", [])
            if not prs:
                die(f"no active pull request for branch {branch}")
            if len(prs) > 1:
                die("several active pull requests for this branch: " + ", ".join(f"!{p['pullRequestId']}" for p in prs))
            data = prs[0]
        self.id = data["pullRequestId"]
        self.data = data
        self.threads_url = f"{data['repository']['url']}/pullRequests/{self.id}/threads"

    def line(self):
        p = self.data
        src = p["sourceRefName"].removeprefix("refs/heads/")
        dst = p["targetRefName"].removeprefix("refs/heads/")
        return f"!{self.id} {p['title']}  ({p['repository']['name']}, {src} -> {dst}, {p['status']})"


def location(thread):
    ctx = thread.get("threadContext")
    if not ctx:
        return "(general)"
    path = (ctx.get("filePath") or "").lstrip("/")
    for side, note in (("right", ""), ("left", " (old side)")):
        start = ctx.get(f"{side}FileStart")
        if not start:
            continue
        end = ctx.get(f"{side}FileEnd") or start
        lines = str(start["line"]) if end["line"] == start["line"] else f"{start['line']}-{end['line']}"
        return f"{path}:{lines}{note}"
    return path


def text_comments(thread):
    return [c for c in thread.get("comments", []) if c.get("commentType") != "system" and not c.get("isDeleted")]


def threads(pr, show_all):
    res = call("GET", f"{pr.threads_url}?{API}")
    print(pr.line())
    shown = 0
    for t in res.get("value", []):
        comments = text_comments(t)
        if t.get("isDeleted") or not comments:
            continue
        if not show_all and t.get("status") not in ("active", "pending"):
            continue
        shown += 1
        print(f"\nT{t['id']} {t.get('status', '?')}  {location(t)}")
        for c in comments:
            author = c.get("author", {}).get("displayName", "?")
            when = (c.get("publishedDate") or "")[:16].replace("T", " ")
            body = (c.get("content") or "").rstrip().replace("\n", "\n    ")
            print(f"  {author} {when}: {body}")
    print(f"\n{shown} thread(s) shown")


def thread_id(arg):
    m = re.fullmatch(r"T?(\d+)", arg or "")
    if not m:
        die(f"not a thread id: {arg}")
    return int(m.group(1))


def reply(pr, tid, text):
    body = {"content": text, "parentCommentId": 1, "commentType": 1}
    c = call("POST", f"{pr.threads_url}/{tid}/comments?{API}", body)
    print(f"replied in T{tid} (comment {c['id']})")


def resolve(pr, tid):
    call("PATCH", f"{pr.threads_url}/{tid}?{API}", {"status": "fixed"})
    print(f"T{tid} set to fixed")


def main(argv):
    cmd = argv[0] if argv else "help"
    args = argv[1:]
    if cmd == "info":
        org, project, repo = repo_coords() or (DEFAULT_ORG, "(origin is not on Azure DevOps)", "-")
        print(f"organization: {org}\nproject: {project}\nrepository: {repo}\nbranch: {git('branch', '--show-current') or '(detached)'}")
        path = os.environ.get(TOKEN_FILE_VAR)
        state = "not set" if not path else f"{path} ({'readable' if os.path.isfile(path) else 'missing file'})"
        print(f"{TOKEN_FILE_VAR}: {state}")
    elif cmd == "pr":
        print(Pr(args[0] if args else None).line())
    elif cmd == "threads":
        show_all = "--all" in args
        rest = [a for a in args if a != "--all"]
        threads(Pr(rest[0] if rest else None), show_all)
    elif cmd == "reply" and len(args) >= 2:
        text = sys.stdin.read().strip() if args[1] == "-" else args[1]
        if not text:
            die("empty reply")
        reply(Pr(args[2] if len(args) > 2 else None), thread_id(args[0]), text)
    elif cmd == "resolve" and args:
        resolve(Pr(args[1] if len(args) > 1 else None), thread_id(args[0]))
    else:
        print(__doc__.strip())
        sys.exit(0 if cmd in ("help", "-h", "--help") else 2)


if __name__ == "__main__":
    main(sys.argv[1:])
