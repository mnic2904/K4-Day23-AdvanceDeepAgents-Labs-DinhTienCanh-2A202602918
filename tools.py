"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json  # noqa: F401
import os  # noqa: F401
import random
import re
import threading
import time  # noqa: F401
import xml.etree.ElementTree  # noqa: F401  (arXiv answers with Atom XML)

import httpx  # noqa: F401
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again.

    PSEUDO-CODE:
      for attempt in 0 .. attempts-1:
          try: return fn()
          except RetryableError as e:
              if this was the last attempt: raise
              delay = e.retry_after if the server told us, else exponential backoff base * 2**attempt
              cap the delay at `cap` seconds; add random jitter to the exponential case
              sleep(delay)
    Use it to wrap EVERY network call below. Also treat these as retryable: HTTP 429/500/502/503/504,
    httpx.TransportError (timeouts, connection resets). Read the Retry-After header when present.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(attempts):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == attempts - 1:
                raise
            if exc.retry_after is not None:
                delay = min(cap, max(0.0, float(exc.retry_after)))
            else:
                delay = min(cap, base * (2 ** attempt))
                delay += random.uniform(0, min(base, max(0.0, cap - delay)))
            time.sleep(delay)


RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_arxiv_lock = threading.Lock()
_last_arxiv_call = 0.0


def _request(method, url, **kwargs):
    """Make one HTTP request and translate transient failures for with_retry."""
    try:
        response = httpx.request(method, url, timeout=30, **kwargs)
    except httpx.TransportError as exc:
        raise RetryableError(str(exc)) from exc
    if response.status_code in RETRYABLE_STATUS:
        value = response.headers.get("Retry-After")
        try:
            retry_after = float(value) if value else None
        except ValueError:
            retry_after = None
        raise RetryableError(f"HTTP {response.status_code}", retry_after)
    response.raise_for_status()
    return response


def _clean(value, limit=600):
    return " ".join(str(value or "").split())[:limit]


def _clamp(value, minimum, maximum, default):
    try:
        return max(minimum, min(int(value), maximum))
    except (TypeError, ValueError):
        return default


def _error(exc, secret=""):
    message = f"{type(exc).__name__}: {exc}"
    if secret:
        message = message.replace(secret, "[REDACTED]")
    return f"ERROR: {message}"


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    # PSEUDO-CODE:
    #   keep only word characters of `query` -> terms; no terms -> "NO RESULTS" (do not call the network)
    #   respect arXiv etiquette: at least 3 seconds between two arXiv calls (remember the time of the last call)
    #   GET ARXIV_URL params: search_query="all:t1 AND all:t2 ...", sortBy=submittedDate, sortOrder=descending,
    #       max_results=clamp(max_results, 1, 30)           (wrap in with_retry)
    #   parse the Atom XML: each <entry> -> {id (last part of <id> after /abs/), url, published[:10], title, summary}
    #       collapse whitespace/newlines in title and summary; cut summary to ~600 chars
    #   no entries -> "NO RESULTS"; else json.dumps(records, ensure_ascii=False)
    #   any exception -> "ERROR: <type>: <message>"
    terms = re.findall(r"[\w-]+", query or "", re.UNICODE)
    terms = [term for term in terms if term.upper() not in {"AND", "OR", "NOT"}]
    if not terms:
        return "NO RESULTS"

    def call():
        global _last_arxiv_call
        with _arxiv_lock:
            delay = 3.0 - (time.monotonic() - _last_arxiv_call)
            if delay > 0:
                time.sleep(delay)
            try:
                return _request("GET", ARXIV_URL, params={
                    "search_query": " AND ".join(f"all:{term}" for term in terms),
                    "sortBy": "submittedDate", "sortOrder": "descending", "start": 0,
                    "max_results": _clamp(max_results, 1, 30, 10),
                })
            finally:
                _last_arxiv_call = time.monotonic()

    try:
        response = with_retry(call, attempts=7, cap=60)
        root = xml.etree.ElementTree.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        records = []
        for entry in root.findall("atom:entry", ns):
            raw_id = _clean(entry.findtext("atom:id", default="", namespaces=ns))
            paper_id = re.sub(r"v\d+$", "", raw_id.rsplit("/", 1)[-1])
            if not paper_id:
                continue
            records.append({
                "id": paper_id, "url": f"https://arxiv.org/abs/{paper_id}",
                "published": _clean(entry.findtext("atom:published", default="", namespaces=ns))[:10],
                "title": _clean(entry.findtext("atom:title", default="", namespaces=ns)),
                "summary": _clean(entry.findtext("atom:summary", default="", namespaces=ns)),
            })
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:  # tools must never break an agent run
        return _error(exc)


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes. `date` is YYYY-MM-DD (empty = latest).
    `keyword` filters title/summary; there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    # PSEUDO-CODE:
    #   GET HF_DAILY_URL params: limit (clamp 1..100) and date (only when given)      (with_retry)
    #   response = list of items {"paper": {id, title, summary, upvotes, githubRepo, githubStars, publishedAt}, ...}
    #   map every item to the record shape above (skip items without paper.id); url = https://huggingface.co/papers/<id>
    #   keyword -> keep records whose title+summary contains it (case-insensitive); sort by upvotes descending
    params = {"limit": _clamp(limit, 1, 100, 30)}
    if date:
        params["date"] = date
    return _hf_papers(HF_DAILY_URL, params, keyword=keyword)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    # PSEUDO-CODE:
    #   GET HF_SEARCH_URL params: q=query, limit (clamp 1..50)                         (with_retry)
    #   same item shape as the daily endpoint; prefer paper["ai_summary"] over paper["summary"] when present
    if not (query or "").strip():
        return "NO RESULTS"
    return _hf_papers(HF_SEARCH_URL, {"q": query, "limit": _clamp(limit, 1, 50, 10)}, prefer_ai=True)


def _hf_papers(url, params, keyword="", prefer_ai=False):
    try:
        items = with_retry(lambda: _request("GET", url, params=params)).json()
        records = []
        for item in items if isinstance(items, list) else []:
            paper = item.get("paper") or item
            paper_id = paper.get("id")
            if not paper_id:
                continue
            title = paper.get("title") or item.get("title") or ""
            summary = ((paper.get("ai_summary") or item.get("ai_summary")) if prefer_ai else None)
            summary = summary or paper.get("summary") or item.get("summary") or ""
            published = paper.get("publishedAt") or item.get("publishedAt") or ""
            record = {
                "id": str(paper_id), "url": f"https://huggingface.co/papers/{paper_id}",
                "published": str(published)[:10], "title": _clean(title), "summary": _clean(summary),
                "upvotes": paper.get("upvotes") or item.get("upvotes") or 0,
                "github": paper.get("githubRepo") or item.get("githubRepo") or "",
                "stars": paper.get("githubStars") or item.get("githubStars") or 0,
            }
            if not keyword or keyword.casefold() in f"{title} {summary}".casefold():
                records.append(record)
        records.sort(key=lambda value: value["upvotes"] or 0, reverse=True)
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    # PSEUDO-CODE:
    #   call the MCP tool "web_search_exa" with arguments {query, objective, numResults}
    #       (objective is REQUIRED by Exa: when empty, build one from the query)
    #   see GUIDE.md part 1.4 for how to call an MCP server over plain HTTP (JSON-RPC "tools/call") and read the answer
    #   read optional env EXA_API_KEY; when present it is sent to the Exa endpoint.
    #       (see GUIDE.md 1.4 for where it goes) => the key then appears in exception text: redact it before returning "ERROR: ..."
    #   WATCH OUT: read GUIDE.md 1.4 about how Exa signals "rate limited" on the free tier, and retry on it
    if not (query or "").strip():
        return "NO RESULTS"
    return _exa_call("web_search_exa", {
        "query": query,
        "objective": objective or f"Find reliable sources about {query}",
        "numResults": _clamp(num_results, 1, 10, 5),
    })


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page) as markdown. Long pages are truncated."""
    # PSEUDO-CODE: MCP tool "web_fetch_exa" with arguments {"urls": [url]}; truncate the text to ~12000 chars
    if not re.match(r"^https?://", url or ""):
        return "ERROR: URL must start with http:// or https://"
    return _exa_call("web_fetch_exa", {"urls": [url]})[:12000]


def _exa_call(name, arguments):
    secret = os.getenv("EXA_API_KEY", "").strip()
    endpoint = EXA_URL + (f"?exaApiKey={secret}" if secret else "")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": arguments}}

    def call():
        response = _request("POST", endpoint, json=payload, headers={
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
        })
        candidates = [line[5:].strip() for line in response.text.splitlines() if line.startswith("data:")]
        data = json.loads(candidates[-1] if candidates else response.text)
        if "error" in data:
            raise RuntimeError(data["error"])
        result = data.get("result") or {}
        meta_text = json.dumps(result.get("_meta") or {}).lower()
        content = "\n".join(part.get("text", "") for part in result.get("content", [])
                            if part.get("type") == "text").strip()
        rate_text = f"{meta_text} {content[:500].lower()}"
        if "rate limit" in rate_text or "rate_limit" in rate_text or "ratelimit" in rate_text:
            raise RetryableError("Exa rate limited")
        return content

    try:
        text = with_retry(call, attempts=7, cap=60)
        return text or "NO RESULTS"
    except Exception as exc:
        return _error(exc, secret)


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
