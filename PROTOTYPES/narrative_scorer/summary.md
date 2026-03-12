# Narrative Coherence Scorer (v0.1)

## Overview
A Python prototype script (`narrative_scorer_v0.1.py`) was created to calculate a basic narrative coherence score. It computes the score based on two primary dimensions:
1. **Temporal Consistency (0.0 - 1.0):** Evaluates if events are recounted in chronological order based on their internal timestamps.
2. **Causal Linkage (0.0 - 1.0):** Assesses if the causal references (events stated as causes for other events) actually occurred before or concurrently with the effect event.

The **Overall Score** combines these equally (50% Temporal, 50% Causal).

## Files Created
All files are located in `/home/node/.openclaw/workspace-hulk/PROTOTYPES/narrative_scorer/`:
- `narrative_scorer_v0.1.py`: The main calculation and execution script.
- `mock_memories.json`: Mock JSON log files containing test narrative events.
- `summary.md`: This results overview.

## Test Results
Running the script on the `mock_memories.json` data yielded the following results:

- **A Coherent Morning:** Scored `1.00`. All events strictly chronological, causal dependencies valid.
- **A Disjointed Story:** Scored `0.50`. One event is out of order chronologically, and one causal reference (`e4`) does not exist.
- **Flashbacks without Logic:** Scored `0.25`. Timestamps skip forward and backward randomly, and the causes listed either haven't occurred or do not exist in the record.

## Usage
```bash
python3 /home/node/.openclaw/workspace-hulk/PROTOTYPES/narrative_scorer/narrative_scorer_v0.1.py /home/node/.openclaw/workspace-hulk/PROTOTYPES/narrative_scorer/mock_memories.json
```