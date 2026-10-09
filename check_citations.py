"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    if not isinstance(sources, list) or not sources:
        return ["no sources in sources.json"]

    problems, by_number, seen_urls = [], {}, set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            problems.append(f"source entry {index + 1} is not an object")
            continue
        number, url = source.get("n"), source.get("url")
        if isinstance(number, bool) or not isinstance(number, int):
            problems.append(f"source entry {index + 1} has non-integer n")
        elif number in by_number:
            problems.append(f"source number [{number}] is duplicated")
        else:
            by_number[number] = source
        if not isinstance(url, str) or not re.match(r"^https?://", url):
            problems.append(f"source [{number}] has invalid URL")
        elif url in seen_urls:
            problems.append(f"source URL duplicated: {url}")
        else:
            seen_urls.add(url)

    parts = re.split(r"(?m)^## References\s*$", report_text, maxsplit=1)
    body = parts[0]
    references = parts[1] if len(parts) == 2 else ""
    if len(parts) != 2:
        problems.append("missing ## References heading")

    # Ignore fenced code and Markdown links such as [1](https://...).
    clean_body = re.sub(r"```.*?```", "", body, flags=re.S)
    cited = set()
    for match in re.finditer(r"\[\s*(\d+(?:\s*[-,]\s*\d+)*)\s*\](?!\()", clean_body):
        expression = match.group(1)
        if "-" in expression and "," not in expression:
            start, end = map(int, re.split(r"\s*-\s*", expression))
            cited.update(range(min(start, end), max(start, end) + 1))
        else:
            cited.update(map(int, re.split(r"\s*,\s*", expression)))
    for number in sorted(cited - set(by_number)):
        problems.append(f"[{number}] cited but missing from sources.json")
    for number in sorted(set(by_number) - cited):
        problems.append(f"source [{number}] never cited")

    reference_lines = {}
    for line in references.splitlines():
        match = re.match(r"^\[(\d+)\]\s+", line.strip())
        if match:
            reference_lines.setdefault(int(match.group(1)), []).append(line.strip())
    for number in sorted(set(reference_lines) - set(by_number)):
        problems.append(f"reference line [{number}] has no source")
    for number, source in sorted(by_number.items()):
        lines = reference_lines.get(number, [])
        if not lines:
            problems.append(f"source [{number}] missing reference line")
            continue
        if len(lines) != 1:
            problems.append(f"source [{number}] has {len(lines)} reference lines")
            continue
        urls = re.findall(r"https?://\S+", lines[0])
        if len(urls) != 1:
            problems.append(f"reference [{number}] must contain exactly one URL")
        elif urls[0] != source.get("url"):
            problems.append(f"reference [{number}] URL does not match sources.json")
    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
