import sys
import json

def score_coherence(event_graph):
    """
    Scores narrative coherence based on Temporal Consistency and Causal Density.
    Expects event_graph to be a dict with 'events' (list of dicts).
    """
    events = event_graph.get('events', [])
    if not events:
        return 0.0

    total_events = len(events)
    
    # 1. Temporal Consistency
    temporal_links = 0
    for event in events:
        if event.get('temporal_anchor') or event.get('relative_time'):
            temporal_links += 1
    temporal_score = temporal_links / total_events if total_events > 0 else 0.0

    # 2. Causal Density
    causal_edges = 0
    for event in events:
        causal_edges += len(event.get('caused_by_event_ids', []))
    # Normalize (max expected edges is roughly total_events - 1 for a linear narrative)
    max_expected_edges = max(1, total_events - 1)
    causal_score = min(1.0, causal_edges / max_expected_edges)

    # 3. Overall Coherence (Weighted Average: 40% Temporal, 60% Causal)
    overall_score = (0.4 * temporal_score) + (0.6 * causal_score)
    
    return {
        "temporal_consistency": round(temporal_score, 3),
        "causal_density": round(causal_score, 3),
        "overall_coherence": round(overall_score, 3),
        "event_count": total_events
    }

if __name__ == "__main__":
    try:
        # Read JSON from stdin (piped from run_pipeline.sh)
        input_data = sys.stdin.read()
        event_graph = json.loads(input_data)
        
        results = score_coherence(event_graph)
        
        print("\n--- Narrative Coherence Score ---")
        print(f"Overall Coherence:   {results['overall_coherence']} / 1.0")
        print(f"Temporal Consistency:{results['temporal_consistency']} / 1.0")
        print(f"Causal Density:      {results['causal_density']} / 1.0")
        print(f"Events Extracted:    {results['event_count']}")
        print("---------------------------------")
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON received from standard input.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during scoring: {str(e)}", file=sys.stderr)
        sys.exit(1)