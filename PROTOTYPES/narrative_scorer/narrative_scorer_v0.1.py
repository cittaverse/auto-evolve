import json
import sys

def calculate_coherence(events):
    """
    Calculates a basic narrative coherence score based on temporal consistency and causal linkage.
    """
    if not events:
        return {"temporal_consistency": 0.0, "causal_linkage": 0.0, "overall_score": 0.0}
    
    # 1. Temporal Consistency
    # Check if events are recounted in chronological order
    temporal_score = 0
    total_transitions = len(events) - 1
    
    for i in range(total_transitions):
        prev_time = events[i].get("timestamp", 0)
        curr_time = events[i+1].get("timestamp", 0)
        
        if curr_time >= prev_time:
            temporal_score += 1
            
    temporal_consistency = (temporal_score / total_transitions) if total_transitions > 0 else 1.0
    
    # 2. Causal Linkage
    # Check if the causes referenced by an event actually occurred before it
    valid_causes = 0
    total_causes = 0
    
    # Dictionary mapping event ID to its timestamp
    event_times = {e["id"]: e.get("timestamp", 0) for e in events}
    
    for event in events:
        causes = event.get("causes", [])
        curr_time = event.get("timestamp", 0)
        
        for cause_id in causes:
            total_causes += 1
            # A valid cause must exist and must have happened before or at the same time as the current event
            if cause_id in event_times and event_times[cause_id] <= curr_time:
                valid_causes += 1
                
    causal_linkage = (valid_causes / total_causes) if total_causes > 0 else 1.0
    
    # Overall Score (Weighted 50/50 for this prototype)
    overall_score = (temporal_consistency * 0.5) + (causal_linkage * 0.5)
    
    return {
        "temporal_consistency": temporal_consistency,
        "causal_linkage": causal_linkage,
        "overall_score": overall_score
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python narrative_scorer_v0.1.py <mock_data.json>")
        return
        
    try:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        return
        
    print(f"--- Narrative Coherence Scorer v0.1 ---\n")
    for narrative in data.get("narratives", []):
        print(f"Title: {narrative['title']}")
        results = calculate_coherence(narrative["events"])
        print(f"  Temporal Consistency: {results['temporal_consistency']:.2f} (Chronological order of telling)")
        print(f"  Causal Linkage:       {results['causal_linkage']:.2f} (Valid cause-effect relationships)")
        print(f"  Overall Score:        {results['overall_score']:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    main()
