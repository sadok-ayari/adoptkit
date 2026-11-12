import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from adoptkit import cli, render
from adoptkit.plan import parse_plan, validate

PLAN = {
    "tool": "Weekly coverage digest",
    "owner": "Head of Communications",
    "sponsor": "Director",
    "problem": "Ninety minutes of clips, no decision.",
    "ritual": {"name": "Monday coverage review", "cadence": "weekly, Monday 09:00",
               "moment": "first item", "participants": ["chair", "media officer"]},
    "trigger": "scheduler runs at 06:00 Monday",
    "format": "one page",
    "metric": {"name": "time to decision", "target": "30 minutes", "source": "chair's log"},
    "stops": ["printing clips"],
    "failure_modes": [{"mode": "Nobody opens it", "mitigation": "first agenda item"},
                      {"mode": "Second process", "mitigation": "withdraw the old list"}],
    "start": "2026-11-12",
    "fallback": "Revert for two weeks, then diagnose.",
}


class RenderTests(unittest.TestCase):
    def test_renders_every_section(self):
        markdown = render.render(parse_plan(PLAN))
        for heading in ("Where it sits", "First weeks", "How we will know",
                        "What we stop doing", "What will go wrong", "If it fails"):
            self.assertIn(heading, markdown)

    def test_names_the_owner_and_metric(self):
        markdown = render.render(parse_plan(PLAN))
        self.assertIn("Head of Communications", markdown)
        self.assertIn("30 minutes", markdown)

    def test_says_the_old_artefact_goes(self):
        markdown = render.render(parse_plan(PLAN))
        self.assertIn("printing clips", markdown)
        self.assertIn("withdrawn", markdown)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def write(self, payload):
        path = os.path.join(self.dir.name, "plan.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        return path

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_check_ok(self):
        code, out, _ = self.run_cli("check", "--config", self.write(PLAN))
        self.assertEqual(code, 0)
        self.assertIn("ok:", out)

    def test_check_refuses_an_incomplete_plan(self):
        data = dict(PLAN, owner="", stops=[])
        code, _, err = self.run_cli("check", "--config", self.write(data))
        self.assertEqual(code, 2)
        self.assertIn("not adoptable yet", err)
        self.assertIn("owner", err)

    def test_run_writes_the_pack(self):
        out_dir = os.path.join(self.dir.name, "out")
        code, out, _ = self.run_cli("run", "--config", self.write(PLAN), "--out", out_dir, "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["ritual"], "Monday coverage review")
        self.assertTrue(os.path.exists(os.path.join(out_dir, "adoption-pack.md")))

    def test_missing_file_exits_two(self):
        code, _, err = self.run_cli("check", "--config", os.path.join(self.dir.name, "nope.json"))
        self.assertEqual(code, 2)
        self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
