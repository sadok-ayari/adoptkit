from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

REQUIRED = ("tool", "owner", "ritual", "trigger", "format", "metric", "stops", "failure_modes")


@dataclass
class Ritual:
    name: str
    cadence: str
    moment: str
    participants: List[str] = field(default_factory=list)


@dataclass
class Metric:
    name: str
    target: str
    source: str


@dataclass
class FailureMode:
    mode: str
    mitigation: str


@dataclass
class Plan:
    tool: str
    owner: str
    sponsor: str = ""
    problem: str = ""
    ritual: Optional[Ritual] = None
    trigger: str = ""
    format: str = ""
    metric: Optional[Metric] = None
    stops: List[str] = field(default_factory=list)
    failure_modes: List[FailureMode] = field(default_factory=list)
    start: Optional[date] = None
    review_weeks: int = 4
    fallback: str = ""

    def weeks(self) -> List[Dict[str, str]]:
        """Two weeks: shadow, then live. A tool that goes live on day one is not adopted, it is announced."""
        base = self.start or date.today()
        first = base + timedelta(days=(7 - base.weekday()) % 7)   # next Monday
        second = first + timedelta(days=7)
        review = first + timedelta(weeks=self.review_weeks)
        return [
            {"label": "Week 1 — shadow", "start": first.isoformat(),
             "work": "Run it beside the existing process. Nobody consumes the output yet; "
                     "the owner compares it to what the team would have said anyway."},
            {"label": "Week 2 — live", "start": second.isoformat(),
             "work": "The output becomes the first artefact in the ritual. The old artefact "
                     "is withdrawn the same day, not kept \u201cfor a while\u201d."},
            {"label": f"Review — week {self.review_weeks}", "start": review.isoformat(),
             "work": f"Measure {self.metric.name if self.metric else 'the metric'} against target, "
                     "in the same room, and decide keep, change or stop."},
        ]


def parse_plan(payload: Dict[str, Any]) -> Plan:
    ritual_raw = payload.get("ritual") or {}
    metric_raw = payload.get("metric") or {}
    start = payload.get("start")
    return Plan(
        tool=payload.get("tool", ""),
        owner=payload.get("owner", ""),
        sponsor=payload.get("sponsor", ""),
        problem=payload.get("problem", ""),
        ritual=Ritual(name=ritual_raw.get("name", ""), cadence=ritual_raw.get("cadence", ""),
                      moment=ritual_raw.get("moment", ""),
                      participants=list(ritual_raw.get("participants", []))) if ritual_raw else None,
        trigger=payload.get("trigger", ""),
        format=payload.get("format", ""),
        metric=Metric(name=metric_raw.get("name", ""), target=metric_raw.get("target", ""),
                      source=metric_raw.get("source", "")) if metric_raw else None,
        stops=list(payload.get("stops", [])),
        failure_modes=[FailureMode(mode=f.get("mode", ""), mitigation=f.get("mitigation", ""))
                       for f in payload.get("failure_modes", [])],
        start=date.fromisoformat(start) if start else None,
        review_weeks=int(payload.get("review_weeks", 4)),
        fallback=payload.get("fallback", ""),
    )


def load(path: str) -> Plan:
    with open(path, encoding="utf-8") as handle:
        return parse_plan(json.load(handle))


def validate(plan: Plan) -> List[str]:
    """Every gap here is a reason the tool dies in month two."""
    problems: List[str] = []
    if not plan.tool:
        problems.append("tool: name the thing being adopted")
    if not plan.owner:
        problems.append("owner: a person, not a team")
    if not plan.ritual or not plan.ritual.name:
        problems.append("ritual: name the meeting or moment it joins")
    elif not plan.ritual.cadence:
        problems.append("ritual.cadence: weekly, monthly, on publication")
    if not plan.trigger:
        problems.append("trigger: what causes a run, in one sentence")
    if not plan.format:
        problems.append("format: one page, one screen, one paragraph")
    if not plan.metric or not plan.metric.name:
        problems.append("metric: what changes if this works")
    else:
        if not plan.metric.target:
            problems.append("metric.target: a number and a direction")
        if not plan.metric.source:
            problems.append("metric.source: where the number comes from")
    if not plan.stops:
        problems.append("stops: at least one thing the team stops doing")
    if len([f for f in plan.failure_modes if f.mode]) < 2:
        problems.append("failure_modes: at least two, each with a mitigation")
    for failure in plan.failure_modes:
        if failure.mode and not failure.mitigation:
            problems.append(f"failure_modes[{failure.mode}]: missing mitigation")
    return problems
