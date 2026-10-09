"""Small regression tests for deterministic lab logic. Run with: python -m unittest test_lab.py"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from check_citations import check
from research import REPORT_PATH, SOURCES_PATH, save_outputs, slugify
from tools import RetryableError, with_retry


class LabTests(unittest.TestCase):
    def test_retry_stops_without_sleeping_after_last_failure(self):
        with patch("tools.time.sleep") as sleep:
            with self.assertRaises(RetryableError):
                with_retry(lambda: (_ for _ in ()).throw(RetryableError("busy")), attempts=1)
        sleep.assert_not_called()

    def test_slugify_cannot_escape_reports(self):
        self.assertEqual(slugify("../../x"), "x")
        self.assertEqual(slugify(""), "topic")

    def test_citation_groups_ranges_and_markdown_links(self):
        sources = [{"n": 1, "url": "https://one.test"}, {"n": 2, "url": "https://two.test"}]
        report = ("# T\nClaims [1-2]. Link [1](https://ignored.test).\n## References\n"
                  "[1] One. web. https://one.test (2026-01-01)\n"
                  "[2] Two. web. https://two.test (2026-01-02)\n")
        self.assertEqual(check(report, sources), [])

    def test_save_outputs_rejects_fewer_than_three_families(self):
        sources = [{"n": 1, "url": "https://arxiv.org/abs/1", "source": "arxiv"}]
        backend = Mock()
        backend.download_files.return_value = []
        with patch("research.download", return_value={REPORT_PATH: b"report", SOURCES_PATH: json.dumps(sources).encode()}):
            with tempfile.TemporaryDirectory() as directory:
                with self.assertRaisesRegex(RuntimeError, "three source families"):
                    save_outputs(backend, "topic", [], 1, "model", Path(directory))


if __name__ == "__main__":
    unittest.main()
