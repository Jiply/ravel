"""Exercise repository discovery, history boundaries, and safe HTML rendering."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render", ROOT / "scripts/render.py")
renderer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(renderer)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve() / "demo with spaces"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Example")
        self.git("config", "user.email", "example@example.invalid")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], text=True,
            stderr=subprocess.PIPE,
        ).strip()

    def commit(self, message):
        self.git("commit", "--allow-empty", "-m", message)

    def test_subdirectory_discovery_and_read_only_rendering(self):
        message = '</script><script>alert("demo")</script> café'
        self.commit("initial")
        self.commit(message)
        nested = self.repo / "nested"
        nested.mkdir()
        dirty = self.repo / "uncommitted.txt"
        dirty.write_text("keep me", encoding="utf-8")
        before = (self.git("rev-parse", "HEAD"), self.git("status", "--porcelain"))
        data = renderer.snapshot(nested, 200)
        self.assertEqual(Path(data["repository"]), self.repo.resolve())
        self.assertEqual(data["branch"], "main")
        self.assertEqual(data["commits"][0]["subject"], message)
        output = self.repo.parent / "picker.html"
        renderer.render(data, output)
        html = output.read_text(encoding="utf-8")
        embedded = json.JSONDecoder().raw_decode(html.split("const data = ", 1)[1])[0]
        self.assertEqual(embedded, data)
        self.assertNotIn(message, html)
        self.assertNotIn("/* RAVEL_MODEL */", html)
        self.assertIn("sendFollowUpMessage", html)
        self.assertEqual(before, (self.git("rev-parse", "HEAD"), self.git("status", "--porcelain")))
        self.assertEqual(dirty.read_text(), "keep me")

    def test_first_parent_limit_merge_and_detached_head(self):
        self.commit("initial")
        self.git("checkout", "-b", "topic")
        self.commit("topic change")
        self.git("checkout", "main")
        self.commit("main change")
        self.git("merge", "--no-ff", "topic", "-m", "merge topic")
        data = renderer.snapshot(self.repo, 2)
        self.assertTrue(data["hasMore"])
        self.assertEqual([c["subject"] for c in data["commits"]], ["merge topic", "main change"])
        self.assertEqual(len(data["commits"][0]["parents"]), 2)
        self.git("checkout", "--detach")
        self.assertEqual(renderer.snapshot(self.repo, 200)["branch"], "HEAD")

    def test_output_rejects_symlink_path(self):
        self.commit("initial")
        actual = self.repo.parent / "actual"
        actual.mkdir()
        alias = self.repo.parent / "authorized"
        alias.symlink_to(actual, target_is_directory=True)
        output = alias / "ravel.html"
        with self.assertRaisesRegex(ValueError, "symlinks"):
            renderer.render(renderer.snapshot(self.repo, 200), output)
        self.assertFalse(output.exists())

    def test_output_privacy_and_reader_requirements(self):
        self.commit("initial")
        data = renderer.snapshot(self.repo, 200)
        output = self.repo / "ravel.html"
        with self.assertRaisesRegex(ValueError, "ignored"):
            renderer.render(data, output)
        (self.repo / ".git/info/exclude").write_text("ravel.html\n")
        renderer.render(data, output)
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        html = output.read_text(encoding="utf-8")
        for tag in ("<!doctype", "<html", "<head>", "<body"):
            self.assertNotIn(tag, html.lower())
        self.assertIn('id="ravel-app"', html)
        self.git("add", "-f", "ravel.html")
        with self.assertRaisesRegex(ValueError, "ignored"):
            renderer.render(data, output)
        with self.assertRaisesRegex(ValueError, "hyphenated"):
            renderer.render(data, self.repo.parent / "bad_name.html")
        data["commits"][0]["subject"] = "x" * 1_000_000
        with self.assertRaisesRegex(ValueError, "1 MB"):
            renderer.render(data, output)
        self.assertEqual(output.read_text(encoding="utf-8"), html)

    def test_empty_repository_reports_error(self):
        with self.assertRaises(ValueError):
            renderer.snapshot(self.repo, 200)


if __name__ == "__main__":
    unittest.main()
