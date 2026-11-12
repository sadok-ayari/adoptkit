from __future__ import annotations

from typing import List

from .plan import Plan


def render(plan: Plan) -> str:
    metric = plan.metric
    out = [f"# Adoption pack — {plan.tool}", ""]
    if plan.problem:
        out += [f"**The problem:** {plan.problem}", ""]
    out += [f"**Owner:** {plan.owner}" + (f" · **Sponsor:** {plan.sponsor}" if plan.sponsor else ""),
            f"**Trigger:** {plan.trigger}",
            f"**Format:** {plan.format}", ""]

    out += ["## Where it sits", ""]
    if plan.ritual:
        out.append(f"- **Ritual:** {plan.ritual.name} ({plan.ritual.cadence})")
        out.append(f"- **Moment:** {plan.ritual.moment}")
        if plan.ritual.participants:
            out.append(f"- **In the room:** {', '.join(plan.ritual.participants)}")
    out.append(f"- **First artefact:** the output is read before anything else in that ritual")

    out += ["", "## First weeks", ""]
    for week in plan.weeks():
        out.append(f"### {week['label']} ({week['start']})")
        out.append(week["work"])
        out.append("")

    out += ["## How we will know", ""]
    if metric:
        out.append(f"- **Metric:** {metric.name}")
        out.append(f"- **Target:** {metric.target}")
        out.append(f"- **Source:** {metric.source}")
    out.append(f"- **Review:** {plan.weeks()[-1]['start']}")

    out += ["", "## What we stop doing", ""]
    for item in plan.stops:
        out.append(f"- {item}")

    out += ["", "## What will go wrong", ""]
    for failure in plan.failure_modes:
        out.append(f"- **{failure.mode}** — {failure.mitigation}")

    if plan.fallback:
        out += ["", "## If it fails", "", plan.fallback]

    out += ["", "---", "",
            "_A tool is adopted when the old artefact is gone. If both run in parallel for a "
            "month, this was a demo._"]
    return "\n".join(out) + "\n"


def short_summary(plan: Plan) -> str:
    metric = plan.metric.name if plan.metric else "no metric"
    return f"{plan.tool} · owner {plan.owner} · into {plan.ritual.name if plan.ritual else 'nowhere'} · measured by {metric}"
