import os
import json
import urllib.request
import re

# ==========================================
# PHASE 1: NEURAL LAYER (LLM for Extraction ONLY)
# ==========================================
# The LLM is forbidden from scoring. It acts purely as a semantic parser.

EXTRACTION_PROMPT = """
You are an NLP entity extraction engine specialized in Autobiographical Memory.
Your ONLY job is to parse the input narrative sentence-by-sentence (or clause-by-clause) and extract specific entities.
DO NOT SCORE. DO NOT EVALUATE.

For EACH segment in the narrative, extract the following if present:
- 'time_entities': Specific dates, times, or temporal anchors (e.g., "1992", "morning").
- 'place_entities': Specific locations or spatial details (e.g., "teahouse", "corner").
- 'perceptual_entities': Sights, sounds, smells, physical sensations (e.g., "fog", "jasmine smell", "cold").
- 'action_entities': Specific actions performed during the main event (e.g., "walked in", "wore a coat").
- 'emotion_entities': Internal thoughts or feelings AT THE TIME of the event (e.g., "happy", "nervous").
- 'semantic_facts': General knowledge or historical facts not tied to the specific episodic experience (e.g., "machines make tea now").
- 'meta_comments': Comments about memory itself or present state (e.g., "I can't remember", "I am old").

OUTPUT FORMAT (JSON ONLY):
{
  "segments": [
    {
      "text": "The exact segment text",
      "time_entities": [],
      "place_entities": [],
      "perceptual_entities": [],
      "action_entities": [],
      "emotion_entities": [],
      "semantic_facts": [],
      "meta_comments": []
    }
  ]
}
"""

def neural_extract(narrative_text):
    print("[Neural Layer] Extracting entities via LLM...")
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return {"error": "DASHSCOPE_API_KEY missing."}

    model_name = "qwen3.5-plus"
    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": EXTRACTION_PROMPT + "\n\nNarrative:\n" + narrative_text}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    })
    try:
        with urllib.request.urlopen(req) as response:
            result_json = json.loads(response.read().decode('utf-8'))
            return json.loads(result_json['choices'][0]['message']['content'])
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# PHASE 2: SYMBOLIC LAYER (Deterministic Python Rules)
# ==========================================
# This is a highly simplified version of Levine's (2002) AI manual logic

def symbolic_score(extracted_data):
    print("[Symbolic Layer] Applying deterministic clinical rules...")
    scored_segments = []
    total_internal = 0
    total_external = 0
    
    # Clinical Rule Definitions (Symbolic Logic)
    for seg in extracted_data.get("segments", []):
        text = seg.get("text", "")
        reasoning_trace = []
        category = "UNASSIGNED"
        
        # Rule 1: Meta-cognitive or present-state comments are strictly EXTERNAL
        if len(seg.get("meta_comments", [])) > 0:
            category = "EXTERNAL"
            reasoning_trace.append("Rule 1 Fired: Contains meta-cognitive/present comment.")
            
        # Rule 2: General semantic facts are EXTERNAL
        elif len(seg.get("semantic_facts", [])) > 0:
            category = "EXTERNAL"
            reasoning_trace.append("Rule 2 Fired: Contains general semantic fact.")
            
        # Rule 3: If it contains specific episodic markers (time, place, perception, action, emotion), it's INTERNAL
        else:
            episodic_markers = 0
            if len(seg.get("time_entities", [])) > 0: episodic_markers += 1
            if len(seg.get("place_entities", [])) > 0: episodic_markers += 1
            if len(seg.get("perceptual_entities", [])) > 0: episodic_markers += 1
            if len(seg.get("action_entities", [])) > 0: episodic_markers += 1
            if len(seg.get("emotion_entities", [])) > 0: episodic_markers += 1
            
            if episodic_markers > 0:
                category = "INTERNAL"
                reasoning_trace.append(f"Rule 3 Fired: Contains {episodic_markers} type(s) of episodic entities.")
            else:
                # Default fallback rule
                category = "EXTERNAL"
                reasoning_trace.append("Rule 4 Fired: Fallback to External (Lacks specific episodic markers).")
                
        # Tally scores
        if category == "INTERNAL":
            total_internal += 1
        elif category == "EXTERNAL":
            total_external += 1
            
        scored_segments.append({
            "text": text,
            "category": category,
            "trace": " | ".join(reasoning_trace)
        })
        
    ratio = total_internal / (total_internal + total_external) if (total_internal + total_external) > 0 else 0
    
    return {
        "scored_segments": scored_segments,
        "summary": {
            "internal": total_internal,
            "external": total_external,
            "ratio": round(ratio, 2)
        }
    }

if __name__ == "__main__":
    sample_narrative = (
        "（叹气）那个老茶馆啊，是在1992年开业的，就在红星路那个拐角。 "
        "我记得清清楚楚，开业那天早上下了很大的雾，路都看不清。 "
        "我当时穿了件借来的灰色呢子大衣，去给老板送道贺的花篮。 "
        "现在的茶馆都是机器泡茶了，一点人情味都没有。 "
        "我刚一进门，就闻到一股很浓的茉莉花香，还听到前面有个戏台子在唱川剧。 "
        "我当时心里很高兴，因为终于帮朋友把这事办成了。 "
        "不过这都是三十多年前的事了，我这脑子，昨天中午吃啥都记不住了。"
    )
    
    print("--- CittaVerse Neuro-Symbolic Pipeline v0.2 ---")
    
    # 1. Neural Extraction
    extraction = neural_extract(sample_narrative)
    if "error" in extraction:
        print("Error in Neural Layer:", extraction["error"])
        exit()
        
    # 2. Symbolic Scoring
    final_result = symbolic_score(extraction)
    
    # 3. Output Explainable Result
    print("\n=== FINAL EXPLAINABLE SCORES ===")
    print(f"Internal Details: {final_result['summary']['internal']}")
    print(f"External Details: {final_result['summary']['external']}")
    print(f"Episodic Ratio:   {final_result['summary']['ratio']}")
    
    print("\n=== DECISION TRACE (Why did it score this way?) ===")
    for s in final_result["scored_segments"]:
        color = "\033[92m" if s["category"] == "INTERNAL" else "\033[91m"
        reset = "\033[0m"
        print(f"{color}[{s['category']}]{reset} {s['text']}")
        print(f"      └─> Trace: {s['trace']}")
