# adoptkit

Write the adoption pack a tool needs before it ships. Or refuse to call it adopted.

```
$ adoptkit check --config config/plan.json
not adoptable yet:
  - stops: at least one thing the team stops doing
  - failure_modes: at least two, each with a mitigation
```

## Why

The failure mode of internal tooling is not bad software. It is good software that nobody opens. Fifteen polished plans all look the same in review: a problem, a method, a dashboard, a target. None of them says which meeting changes, who opens the output first, what stops being produced, or what happens in week one when the numbers disagree with the room.

This tool makes those answers mandatory. It validates the plan like a form, then writes the one page a team actually needs: where the tool sits in the week, the first two weeks, the metric and its source, the work it replaces, and the failure modes with a mitigation each.

## The rule it enforces

**A tool is adopted when the old artefact is gone.**

`stops` is a required field. If nothing is withdrawn, the tool is a second process, and second processes die quietly in month two when someone is busy. `check` exits 2 without it.

## Install

Python 3.9+. No dependencies.

```bash
git clone https://github.com/sadok-ayari/adoptkit.git
cd adoptkit
python -m adoptkit check --config config/plan.json
python -m adoptkit run --config config/plan.json
```

```bash
pip install -e . && adoptkit run --config config/plan.json
```

## Configuration

`config/plan.json`, eight required fields:

| Field | What it forces you to decide |
|---|---|
| `tool` | the thing being adopted, in the team's words |
| `owner` | a person, not a team |
| `ritual` | the meeting or moment it joins, with cadence and the exact moment inside it |
| `trigger` | what causes a run, in one sentence |
| `format` | one page, one screen, one paragraph |
| `metric` | what changes if this works, with a target and a named source |
| `stops` | at least one thing the team stops doing |
| `failure_modes` | at least two, each with a mitigation |

Optional: `sponsor`, `problem`, `start` (the pack schedules from the next Monday), `review_weeks`, `fallback`.

## Output

`out/adoption-pack.md`: one page. The problem, the ritual and the moment inside it, week 1 shadow, week 2 live, the review date, the metric and its source, what is withdrawn, what will go wrong, and what happens if it fails. `--json` returns the same structure for a tracker.

## How this lands in a working week

This is the tool for the thing this tool is about, so it has to pass its own test: it joins the approval step. No tool goes to a director without a pack, and `check` is the gate. The team stops accepting concept notes without a `stops` line.

## Honest limits

- **Structural, not substantive.** It cannot tell you whether the idea is good, only whether the adoption is specified. A well-formed pack for a useless tool still passes.
- **No calendar integration.** Dates come from `start`, not from a real calendar. The ritual's cadence is text: the tool cannot know that Monday 09:00 moved.
- **It cannot enforce anything.** Nothing stops a team writing a pack and then running both processes anyway. It makes the omission visible, which is all a document can do.
- **English output.** The template is fixed; wording changes mean editing `render.py`.

## Tests

```bash
python -m unittest discover -s tests   # 17 tests, offline
```

## Licence

MIT. See [LICENSE](LICENSE).
