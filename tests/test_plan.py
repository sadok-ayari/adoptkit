import unittest
from datetime import date

from adoptkit.plan import parse_plan, validate

FULL = {
    "tool": "Weekly coverage digest",
    "owner": "Head of Communications",
    "ritual": {"name": "Monday coverage review", "cadence": "weekly",
               "moment": "first item", "participants": ["chair"]},
    "trigger": "scheduler runs at 06:00 Monday",
    "format": "one page",
    "metric": {"name": "time to decision", "target": "30 minutes", "source": "chair's log"},
    "stops": ["printing clips"],
    "failure_modes": [{"mode": "Nobody opens it", "mitigation": "first agenda item"},
                      {"mode": "Second process", "mitigation": "withdraw the old list"}],
    "start": "2026-11-12",
}


class PlanTests(unittest.TestCase):
    def test_complete_plan_has_no_problems(self):
        self.assertEqual(validate(parse_plan(FULL)), [])

    def test_empty_plan_lists_every_gap(self):
        problems = validate(parse_plan({}))
        joined = " ".join(problems)
        for field in ("tool", "owner", "ritual", "trigger", "format", "metric", "stops", "failure_modes"):
            self.assertIn(field, joined)

    def test_metric_without_target_or_source(self):
        data = dict(FULL, metric={"name": "time"})
        problems = validate(parse_plan(data))
        self.assertIn("metric.target: a number and a direction", problems)
        self.assertIn("metric.source: where the number comes from", problems)

    def test_single_failure_mode_is_not_enough(self):
        data = dict(FULL, failure_modes=[{"mode": "Nobody opens it", "mitigation": "x"}])
        self.assertIn("failure_modes: at least two, each with a mitigation", validate(parse_plan(data)))

    def test_failure_mode_needs_mitigation(self):
        data = dict(FULL, failure_modes=[{"mode": "A", "mitigation": "x"}, {"mode": "B", "mitigation": ""}])
        self.assertIn("failure_modes[B]: missing mitigation", validate(parse_plan(data)))

    def test_stops_is_mandatory(self):
        self.assertIn("stops: at least one thing the team stops doing",
                      validate(parse_plan(dict(FULL, stops=[]))))


class WeekTests(unittest.TestCase):
    def test_weeks_start_next_monday(self):
        plan = parse_plan(FULL)          # 2026-11-12 is a Thursday
        weeks = plan.weeks()
        self.assertEqual(weeks[0]["start"], "2026-11-16")
        self.assertEqual(weeks[1]["start"], "2026-11-23")

    def test_review_follows_the_configured_weeks(self):
        plan = parse_plan(dict(FULL, review_weeks=4))
        self.assertEqual(plan.weeks()[-1]["start"], "2026-12-14")

    def test_shadow_before_live(self):
        labels = [week["label"] for week in parse_plan(FULL).weeks()]
        self.assertIn("shadow", labels[0])
        self.assertIn("live", labels[1])

    def test_monday_start_is_not_pushed_a_week(self):
        plan = parse_plan(dict(FULL, start="2026-11-16"))   # already a Monday
        self.assertEqual(plan.weeks()[0]["start"], "2026-11-16")


if __name__ == "__main__":
    unittest.main()
