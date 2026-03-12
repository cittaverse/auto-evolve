# Narrative Coherence Evaluation Summary

## 1. Input Transcript
> Well, I remember the old bakery on 5th street. They had these wonderful cherry tarts. That was before the war, I think. Or maybe after? No, it was before, because my brother Tommy was still around. He went to France in '42. Anyway, the baker, Mr. Henderson, he always gave us a free cookie. I dropped my cookie once in a puddle. Tommy laughed at me. Then we moved to Chicago in 1945. But going back to the bakery, the smell of yeast was just incredible. I still think about it when I bake bread today. Tommy never liked bread, he only ate potatoes. He got sick in France, you know. Came back in '44 with a bad cough.

## 2. Neuro Step: Extracted Event Graph
```json
{
  "events": [
    {
      "id": "e1",
      "description": "Remember the old bakery on 5th street",
      "estimated_time": "pre-1942"
    },
    {
      "id": "e2",
      "description": "Tommy went to France",
      "estimated_time": "1942"
    },
    {
      "id": "e3",
      "description": "Mr. Henderson gave a free cookie",
      "estimated_time": "pre-1942"
    },
    {
      "id": "e4",
      "description": "Dropped cookie in a puddle",
      "estimated_time": "pre-1942"
    },
    {
      "id": "e5",
      "description": "Tommy got sick in France",
      "estimated_time": "1942-1944"
    },
    {
      "id": "e6",
      "description": "Tommy came back with a bad cough",
      "estimated_time": "1944"
    },
    {
      "id": "e7",
      "description": "Moved to Chicago",
      "estimated_time": "1945"
    }
  ],
  "temporal_links": [
    {
      "source": "e1",
      "target": "e2",
      "relation": "BEFORE"
    },
    {
      "source": "e3",
      "target": "e4",
      "relation": "BEFORE"
    },
    {
      "source": "e2",
      "target": "e5",
      "relation": "BEFORE"
    },
    {
      "source": "e5",
      "target": "e6",
      "relation": "BEFORE"
    },
    {
      "source": "e6",
      "target": "e7",
      "relation": "BEFORE"
    }
  ],
  "causal_links": [
    {
      "source": "e3",
      "target": "e4",
      "reason": "having a cookie is a prerequisite to dropping it"
    },
    {
      "source": "e5",
      "target": "e6",
      "reason": "getting sick causes the bad cough"
    }
  ]
}
```

## 3. Symbolic Step: Coherence Scores
- **Temporal Consistency:** 0.833
- **Causal Density:** 0.286
- **Total Coherence Score:** 0.614

### Analysis
The transcript is highly tangential, jumping between pre-war bakery memories, moving to Chicago in 1945, and Tommy's time in France (1942-1944). The symbolic scorer penalizes the lack of a strict linear timeline and highlights the disjointed causal chains.
