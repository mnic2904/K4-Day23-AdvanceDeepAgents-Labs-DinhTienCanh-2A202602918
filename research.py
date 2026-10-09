"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
from collections import Counter  # noqa: F401
from pathlib import Path

from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent  # noqa: F401
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator


def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    slug = re.sub(r"[^\w]+", "-", str(topic).strip().lower(), flags=re.UNICODE).strip("-_")
    return (slug[:60].rstrip("-_") or "topic")


def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (f'Research the topic "{topic}" and produce the complete validated survey. '
            "Follow every workflow, source-diversity, sandbox-path, and citation requirement in your system prompt.")


def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    PSEUDO-CODE: walk the lead's messages; for every message with tool_calls count call["name"] (subagent_calls = the
    count of "task"); add the input/output token counts from each message's usage_metadata when present.
    (Lead messages only: subagent tokens are not included, so this undercounts the real cost.)
    elapsed_s rounded to 0.1.
    """
    calls = Counter()
    input_tokens = output_tokens = 0
    for message in messages:
        for call in getattr(message, "tool_calls", None) or (message.get("tool_calls", []) if isinstance(message, dict) else []):
            calls[call.get("name", "unknown")] += 1
        usage = getattr(message, "usage_metadata", None) or (message.get("usage_metadata", {}) if isinstance(message, dict) else {}) or {}
        input_tokens += usage.get("input_tokens", 0) or usage.get("input", 0) or 0
        output_tokens += usage.get("output_tokens", 0) or usage.get("output", 0) or 0
    return {"model": model_name, "elapsed_s": round(elapsed, 1), "subagent_calls": calls["task"],
            "tool_calls": dict(sorted(calls.items())), "tokens": {"input": input_tokens, "output": output_tokens}}


def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    PSEUDO-CODE:
      files = download(backend, [REPORT_PATH, SOURCES_PATH])
      if the report is missing/empty or sources.json is missing/invalid JSON: raise RuntimeError and WRITE NOTHING
          (a failed run must never leave an empty or half-written report behind)
      write <slug>.sources.json, <slug>.meta.json (topic + summarize(...) + n_sources + source_families: the sorted
      distinct "source" values of sources.json) and <slug>.md
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report_bytes, source_bytes = files.get(REPORT_PATH), files.get(SOURCES_PATH)
    if not report_bytes or not report_bytes.strip():
        raise RuntimeError("agent did not create a non-empty report")
    if not source_bytes:
        raise RuntimeError("agent did not create sources.json")
    try:
        sources = json.loads(source_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid sources.json: {exc}") from exc
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("sources.json must be a non-empty JSON array")
    families = {source.get("source") for source in sources if isinstance(source, dict) and source.get("source")}
    if len(families & {"arxiv", "hf-daily", "hf-search", "web"}) < 3:
        raise RuntimeError("final report must retain at least three source families")
    for source in sources:
        url = source.get("url", "") if isinstance(source, dict) else ""
        if not re.match(r"^https?://\S+$", url):
            raise RuntimeError(f"source [{source.get('n', '?')}] has an invalid URL")

    slug = slugify(topic)
    meta = {"topic": topic, **summarize(messages, elapsed, model_name), "n_sources": len(sources),
            "source_families": sorted(families)}
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{slug}.md"
    # Validate all data before any writes; replace each complete output atomically.
    outputs = {report_path: report_bytes, reports_dir / f"{slug}.sources.json": source_bytes,
               reports_dir / f"{slug}.meta.json": json.dumps(meta, ensure_ascii=False, indent=2).encode()}
    for path, content in outputs.items():
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(content)
        os.replace(temporary, path)
    return report_path


def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic).

    PSEUDO-CODE:
      empty topic -> print usage to stderr, return 2
      model = make_model(); start = time.monotonic()
      with open_sandbox() as backend:                # the sandbox is always cleaned up, even on errors
          backend.execute("mkdir -p <WORKDIR>/research/notes <WORKDIR>/report")
          upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
          agent = build_lead_agent(backend, model)
          result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                config={"recursion_limit": 1000})
          save_outputs(...); on RuntimeError print "FAILED: ..." to stderr and return 1
      print where the report was saved; return 0
    """
    topic = (topic or "").strip()
    if not topic:
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2
    try:
        model = make_model()
        model_name = getattr(model, "model_name", None) or getattr(model, "model", None) or str(model)
        started = time.monotonic()
        with open_sandbox() as backend:
            setup = backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
            if getattr(setup, "exit_code", 0) != 0:
                raise RuntimeError(f"cannot prepare sandbox: {getattr(setup, 'output', '')}")
            upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                             FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
            agent = build_lead_agent(backend, model)
            result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                  config={"recursion_limit": 1000})
            messages = result.get("messages", [])
            # Enforce deterministic formatting after the model's final edit, inside the sandbox.
            normalized = backend.execute(
                f"sed -i 's/^## Trends and Open Problems$/## Trends and open problems/' {REPORT_PATH} && "
                f"python3 {FINALIZER_PATH} && python3 {VALIDATOR_PATH} {REPORT_PATH} {SOURCES_PATH}"
            )
            if getattr(normalized, "exit_code", 1) != 0:
                raise RuntimeError(f"final citation validation failed: {getattr(normalized, 'output', '')}")
            path = save_outputs(backend, topic, messages, time.monotonic() - started, str(model_name))
        print(f"Saved report to {path}")
        return 0
    except Exception as exc:  # CLI must fail clearly and never save partial output
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
