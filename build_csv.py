"""Build the GitLab Certified CI/CD Associate question bank from files downloaded into sources/online/ (research agent,
2026-10-16) plus authored banks in banks/*.md. Usage: python -I build_csv.py  ->  data/questions.csv (bot schema).
Sources: smshack/MYNOTE practice exams (8 x 50, no licence: personal study only), rebash-academy quiz (40, MIT),
open-exam-prep sample (10). Domain = the official exam domain where the source names it, else the source."""
import csv, glob, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ON = os.path.join(HERE, "sources", "online")
OUT = os.path.join(HERE, "data", "questions.csv")
LET = "ABCDEFGH"
rows, seen = [], set()
DOMAINS = ["YAML Configuration", "Pipeline Development", "CI/CD Fundamentals", "Troubleshooting & Optimization",
           "Container & Package Management", "Security Integration", "Runner Configuration"]


KEYS = {"YAML Configuration": r"yaml|keyword|extends|anchor|include|default:|stages:|rules:|workflow",
        "Pipeline Development": r"pipeline|needs|dag|parent|child|downstream|merge request|environment|deploy|stage",
        "CI/CD Fundamentals": r"continuous|artifact|cache|variable|predefined|job|script",
        "Troubleshooting & Optimization": r"debug|fail|troubleshoot|lint|optimi|slow|parallel|retry|timeout|efficien",
        "Container & Package Management": r"docker|container|registry|package|image|dependency proxy|dind",
        "Security Integration": r"sast|dast|scan|vulnerab|security|secret detection|approval polic|code quality",
        "Runner Configuration": r"runner|executor|register|tag|concurren|shell executor|kubernetes executor"}


def dom_of(label, text=""):
    key = re.sub(r"[^a-z]", "", label.lower())
    for d in DOMAINS:
        if key and key[:8] in re.sub(r"[^a-z]", "", d.lower()):
            return d
    best, score = "CI/CD Fundamentals", 0        # source without domain headings: pick by keywords in the question
    for d, pat in KEYS.items():
        n = len(re.findall(pat, text.lower()))
        if n > score:
            best, score = d, n
    return best


def clean(s):
    return re.sub(r"[ \t]+", " ", html.unescape(s.replace("**", ""))).strip()


def add(domain, question, opts, answer, expl, source):
    # the last option of a markdown set ran on into the "---" between questions; the bots need one line per option
    opts = {L: re.split(r"\n\s*-{3,}", v)[0].strip().replace("\n", " ") for L, v in opts.items()}
    key = re.sub(r"\W+", " ", question[:120].lower()).strip()
    answer = answer.replace(" ", "")
    if key in seen or len(question) < 15 or not answer or not all(opts.get(L) for L in answer.split(",")):
        return
    seen.add(key)
    rows.append({"id": f"GL-{len(rows) + 1:04d}", "domain": domain, "question": question.strip(),
                 "options": "\n".join(f"{L}. {opts[L]}" for L in LET if opts.get(L)),
                 "correct": answer, "explanation": f"{expl.strip() or '(no explanation in source)'}\n(source: {source})"})


# 1. smshack/MYNOTE sets: "### Domain N — Name" / "**Qn.** stem (may hold a fenced yaml block)" / "A. ..." lines;
#    answer key as a table "| Q3 | A, B | why |" (set 01) or "**Q1.** B — why" lines (sets 02-08)
for f in sorted(glob.glob(os.path.join(ON, "github_smshack-MYNOTE_practice-exam-set-*-en.md"))):
    t = open(f, encoding="utf-8").read()
    qpart, _, apart = t.partition("## Answer Key")
    key = {}
    for n, ans, why in re.findall(r"^\| Q?(\d+) \| ([A-E](?:,\s*[A-E])*) \| (.*?) \|$", apart, re.M):       # table, with or without Q
        key[n] = (ans, why)
    for n, ans, why in re.findall(r"^\*\*Q(\d+)\.\*\*\s*([A-E](?:,\s*[A-E])*)\s*[—–-]\s*(.*)$", apart, re.M):   # **Q1.** B — why
        key[n] = (ans, why)
    for n, ans, why in re.findall(r"^\*\*Q(\d+)\.\s*([A-E](?:,\s*[A-E])*)\*\*\s*[—–-]\s*(.*)$", apart, re.M):   # **Q1. C** — why
        key[n] = (ans, re.sub(r"\s*\*\(Domain \d+\)\*\s*$", "", why))
    domain = ""
    for chunk in re.split(r"^(### .*)$", qpart, flags=re.M):
        if chunk.startswith("### "):
            domain = dom_of(re.sub(r"^Domain \d+\s*[—–:-]\s*", "", chunk[4:].strip()).split("(")[0]); continue
        for m in re.finditer(r"^\*\*Q(\d+)\.\*\*\s*(.*?)(?=^\*\*Q\d+\.\*\*|\Z)", chunk, re.M | re.S):
            n, body = m.groups()
            parts = re.split(r"^([A-E])\.\s+", body, flags=re.M)
            stem = parts[0].strip()
            opts = {parts[i]: clean(parts[i + 1]) for i in range(1, len(parts) - 1, 2)}
            if n in key and opts:
                add(domain if domain in DOMAINS else dom_of("", stem + " " + " ".join(opts.values())),
                    clean(re.sub(r"\n{3,}", "\n\n", stem)), opts, key[n][0], clean(key[n][1]),
                    f"smshack/MYNOTE practice exam set {os.path.basename(f)[-8:-6]} (GitHub, personal study)")

# 2. rebash-academy (MIT): "### Question N" / stem / "**Options:**" / "- **A.** text" / '??? success "Reveal answer"' / "**Correct answer: A**" / text
f = os.path.join(ON, "github_rebash-academy_quizzes_cicd-fundamentals_MIT.md")
if os.path.exists(f):
    t = open(f, encoding="utf-8").read()
    section = ""
    for chunk in re.split(r"^(## .*)$", t, flags=re.M):
        if chunk.startswith("## "):
            section = chunk[3:].strip(); continue
        for m in re.finditer(r"^### Question (\d+)\n(.*?)(?=^### Question \d+|\Z)", chunk, re.M | re.S):
            body = m.group(2)
            stem = body.split("**Difficulty:**", 1)[0].strip()
            opts = {L: clean(x) for L, x in re.findall(r"^- \*\*([A-E])\.\*\* (.*)$", body, re.M)}
            am = re.search(r"\*\*Correct answer: ([A-E](?:,\s*[A-E])*)\*\*\s*\n\s*\n\s*(.*?)(?=\n\s*\*\*Related|\Z)", body, re.S)
            if opts and am:
                add(dom_of(section) if dom_of(section) in DOMAINS else "CI/CD Fundamentals", clean(stem), opts, am.group(1),
                    clean(am.group(2)), "rebash-academy CI/CD quiz (GitHub, MIT)")

# 3. open-exam-prep sample (Jina render): "N stem" / "A.text" lines / "Explanation: ..." naming the answer in prose
f = os.path.join(ON, "open-exam-prep_gitlab-cicd-associate_sample-questions_jina.md")
if os.path.exists(f):
    t = open(f, encoding="utf-8").read()
    t = t.split("## Sample GitLab CI/CD Associate Practice Questions", 1)[-1]
    for m in re.finditer(r"^(\d+) (.+?)\n\n((?:[A-D]\..*\n\n?)+)Explanation:\s*(.*?)(?=\n\n\d+ |\n## |\Z)", t, re.M | re.S):
        stem, optblock, expl = m.group(2), m.group(3), clean(m.group(4))
        opts = {L: clean(x) for L, x in re.findall(r"^([A-D])\.(.*)$", optblock, re.M)}
        el = expl.lower()
        quoted = sorted((el.find(x.lower()[:20]), L) for L, x in opts.items() if x and x.lower()[:20] in el)
        if quoted:
            ans = quoted[0][1]
        else:                                   # the option whose distinctive words the explanation uses most
            score = {L: sum(1 for w in set(re.findall(r"[a-z0-9_.\-]{4,}", x.lower())) if w in el) for L, x in opts.items()}
            best = max(score, key=score.get)
            ans = best if score[best] else ""
        if opts and ans:
            add("CI/CD Fundamentals", clean(stem), opts, ans, expl, "open-exam-prep.com sample")

# 4. Authored banks in banks/*.md (format in the SAP-C03 AGENT.md): header lines, numbered questions, answer table
for f in sorted(glob.glob(os.path.join(HERE, "banks", "*.md"))):
    t = open(f, encoding="utf-8").read()
    hdr = dict(re.findall(r"^(source|url|version): (.*)$", t.split("\n## ", 1)[0], flags=re.M))
    qpart, apart = t.split("## Answers")
    key = {n: (x, why) for n, x, why in re.findall(r"^\| (\d+) \| ([A-F](?:,[A-F])*) \| (.*?) \|$", apart, flags=re.M)}
    section = ""
    for chunk in re.split(r"^(## .*)$", qpart, flags=re.M)[1:]:
        if chunk.startswith("## "):
            section = chunk[3:].strip(); continue
        qs = re.split(r"^(\d+)\. ", chunk, flags=re.M)[1:]
        for k in range(0, len(qs), 2):
            n, body = qs[k], qs[k + 1]
            parts = re.split(r"^\s+([A-F])\. ", body, flags=re.M)
            opts = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
            if n in key:
                add(dom_of(section), parts[0].strip(), opts, key[n][0], key[n][1], hdr.get("source", os.path.basename(f)))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "domain", "question", "options", "correct", "explanation"])
    w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r["domain"] for r in rows))
print(Counter(r["explanation"].rsplit("(source: ", 1)[-1].rstrip(")") for r in rows))
print("rows:", len(rows), "multi:", sum("," in r["correct"] for r in rows), "->", OUT)
