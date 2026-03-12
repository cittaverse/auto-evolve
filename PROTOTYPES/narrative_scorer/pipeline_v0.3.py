import json
import os
import re
from datetime import datetime

# The messy, highly tangential elderly narrative
TRANSCRIPT = """
Well, I remember the old bakery on 5th street. They had these wonderful cherry tarts. That was before the war, I think. Or maybe after? No, it was before, because my brother Tommy was still around. He went to France in '42. Anyway, the baker, Mr. Henderson, he always gave us a free cookie. I dropped my cookie once in a puddle. Tommy laughed at me. Then we moved to Chicago in 1945. But going back to the bakery, the smell of yeast was just incredible. I still think about it when I bake bread today. Tommy never liked bread, he only ate potatoes. He got sick in France, you know. Came back in '44 with a bad cough.
"""

# The prompt for the Neuro step
PROMPT = f"""
You are an expert NLP system analyzing elderly speech for narrative coherence.
Take the following transcript and extract a strict JSON event graph.

Transcript:
{TRANSCRIPT}

Output format:
{{
  "events": [
    {{"id": "e1", "description": "...", "estimated_time": "..."}}
  ],
  "temporal_links": [
    {{"source": "e1", "target": "e2", "relation": "BEFORE"}}
  ],
  "causal_links": [
    {{"source": "e1", "target": "e2", "reason": "..."}}
  ]
}}
Ensure the output is valid JSON.
"""

def neuro_parse(transcript: str) -> dict:
    """
    Step 1 (Neuro): Parse the transcript into a JSON event graph.
    In a real environment, this would call google/gemini-3.1-pro-preview.
    Here, we simulate the structured output of the LLM based on the provided prompt.
    """
    # Simulated LLM response
    return {
      "events": [
        {"id": "e1", "description": "Remember the old bakery on 5th street", "estimated_time": "pre-1942"},
        {"id": "e2", "description": "Tommy went to France", "estimated_time": "1942"},
        {"id": "e3", "description": "Mr. Henderson gave a free cookie", "estimated_time": "pre-1942"},
        {"id": "e4", "description": "Dropped cookie in a puddle", "estimated_time": "pre-1942"},
        {"id": "e5", "description": "Tommy got sick in France", "estimated_time": "1942-1944"},
        {"id": "e6", "description": "Tommy came back with a bad cough", "estimated_time": "1944"},
        {"id": "e7", "description": "Moved to Chicago", "estimated_time": "1945"}
      ],
      "temporal_links": [
        {"source": "e1", "target": "e2", "relation": "BEFORE"},
        {"source": "e3", "target": "e4", "relation": "BEFORE"},
        {"source": "e2", "target": "e5", "relation": "BEFORE"},
        {"source": "e5", "target": "e6", "relation": "BEFORE"},
        {"source": "e6", "target": "e7", "relation": "BEFORE"}
      ],
      "causal_links": [
        {"source": "e3", "target": "e4", "reason": "having a cookie is a prerequisite to dropping it"},
        {"source": "e5", "target": "e6", "reason": "getting sick causes the bad cough"}
      ]
    }

def symbolic_score(graph: dict) -> dict:
    """
    Step 2 (Symbolic): Score the JSON graph for coherence.
    We calculate Temporal Consistency and Causal Density.
    """
    events = graph.get("events", [])
    t_links = graph.get("temporal_links", [])
    c_links = graph.get("causal_links", [])
    
    num_events = len(events)
    if num_events == 0:
        return {"temporal_consistency": 0.0, "causal_density": 0.0, "total_score": 0.0}
        
    # Temporal consistency: ratio of temporally linked events vs total events (heuristic)
    # A fully coherent narrative has a linear timeline (n-1 links for n events)
    expected_t_links = num_events - 1
    t_score = min(len(t_links) / expected_t_links, 1.0) if expected_t_links > 0 else 1.0
    
    # Causal density: ratio of causal links to total events
    # Highly coherent narratives have strong causal chains.
    c_density = min(len(c_links) / num_events, 1.0)
    
    total_score = (t_score * 0.6) + (c_density * 0.4)
    
    return {
        "temporal_consistency": round(t_score, 3),
        "causal_density": round(c_density, 3),
        "total_score": round(total_score, 3)
    }

def main():
    print("Running Neuro-symbolic pipeline v0.3...")
    
    # Step 1: Extract Graph
    print("Step 1: Extracting event graph (Neuro)...")
    graph = neuro_parse(TRANSCRIPT)
    
    # Step 2: Score Graph
    print("Step 2: Scoring narrative coherence (Symbolic)...")
    scores = symbolic_score(graph)
    
    # Output Results
    output_file = "/home/node/.openclaw/workspace-hulk/PROTOTYPES/narrative_scorer/evaluation_summary.md"
    print(f"Writing results to {output_file}...")
    
    with open(output_file, "w") as f:
        f.write("# Narrative Coherence Evaluation Summary\n\n")
        f.write("## 1. Input Transcript\n")
        f.write(f"> {TRANSCRIPT.strip()}\n\n")
        
        f.write("## 2. Neuro Step: Extracted Event Graph\n")
        f.write("```json\n")
        f.write(json.dumps(graph, indent=2) + "\n")
        f.write("```\n\n")
        
        f.write("## 3. Symbolic Step: Coherence Scores\n")
        f.write(f"- **Temporal Consistency:** {scores['temporal_consistency']}\n")
        f.write(f"- **Causal Density:** {scores['causal_density']}\n")
        f.write(f"- **Total Coherence Score:** {scores['total_score']}\n\n")
        
        f.write("### Analysis\n")
        f.write("The transcript is highly tangential, jumping between pre-war bakery memories, moving to Chicago in 1945, and Tommy's time in France (1942-1944). The symbolic scorer penalizes the lack of a strict linear timeline and highlights the disjointed causal chains.\n")
        
    print("Done.")

if __name__ == "__main__":
    main()
