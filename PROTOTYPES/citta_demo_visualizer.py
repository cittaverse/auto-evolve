import os
import json
import urllib.request

# The refined prompt for DEMO/Visualization purposes
# We want the LLM to explicitly highlight text to show non-experts HOW it works.
DEMO_PROMPT = """
You are the "CittaVerse Narrative Evaluator", an AI trained in the Autobiographical Interview (AI) clinical manual.
Your goal is to analyze an elderly person's reminiscence narrative and provide a visualizable, transparent scoring breakdown.

INSTRUCTIONS:
1. SEGMENTATION: Break the text down into distinct "details" (clauses).
2. CLASSIFICATION: Classify EACH detail into ONE of two categories:
   - INTERNAL (Episodic): Specific event details (actions, sights, sounds, time, place, emotions AT THAT TIME).
   - EXTERNAL (Semantic/Other): General knowledge, facts, ongoing events, meta-comments ("I forget"), repetitions, or off-topic events.
3. VISUALIZATION TAGS: Wrap the text segment in markdown-like tags: 
   - <int>text</int> for INTERNAL
   - <ext>text</ext> for EXTERNAL

OUTPUT FORMAT:
Return ONLY a valid JSON object with the following structure:
{
  "visual_narrative": "The full narrative with <int> and <ext> tags applied to every segment.",
  "segments": [
    {
      "text": "the exact segment text",
      "category": "INTERNAL" or "EXTERNAL",
      "reasoning": "A short, non-academic explanation of WHY it's classified this way (for a general audience)."
    }
  ],
  "summary_scores": {
    "total_internal": <int>,
    "total_external": <int>,
    "episodic_ratio": <float>
  },
  "clinical_insight": "A 2-sentence summary of what this ratio means for this person's memory health."
}
"""

def score_narrative_qwen_demo(narrative_text):
    print("--- CittaVerse Visualizer Engine Starting ---")
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return {"error": "DASHSCOPE_API_KEY environment variable is missing."}

    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    payload = {
        "model": "qwen3.5-plus",
        "messages": [
            {"role": "user", "content": DEMO_PROMPT + "\n\nHere is the narrative to score:\n\n" + narrative_text}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            result_json = json.loads(response.read().decode('utf-8'))
            generated_text = result_json['choices'][0]['message']['content']
            return json.loads(generated_text)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # A richer, more complex clinical mock sample
    sample_narrative = (
        "（叹气）那个老茶馆啊，是在1992年开业的，就在红星路那个拐角。 "
        "我记得清清楚楚，开业那天早上下了很大的雾，路都看不清。 "
        "我当时穿了件借来的灰色呢子大衣，去给老板送道贺的花篮。 "
        "现在的茶馆都是机器泡茶了，一点人情味都没有。 "
        "我刚一进门，就闻到一股很浓的茉莉花香，还听到前面有个戏台子在唱川剧。 "
        "我当时心里很高兴，因为终于帮朋友把这事办成了。 "
        "不过这都是三十多年前的事了，我这脑子，昨天中午吃啥都记不住了。"
    )
    
    results = score_narrative_qwen_demo(sample_narrative)
    
    if "error" in results:
        print("Error:", results["error"])
    else:
        print("\n=== 1. VISUALIZED NARRATIVE (For UI Demo) ===")
        print(results.get("visual_narrative", ""))
        
        print("\n=== 2. SCORES ===")
        scores = results.get("summary_scores", {})
        print(f"Internal Details (Episodic): {scores.get('total_internal')}")
        print(f"External Details (Semantic): {scores.get('total_external')}")
        print(f"Episodic Ratio: {scores.get('episodic_ratio')} (Higher = More Vivid/Healthy Memory)")
        
        print("\n=== 3. AI CLINICAL INSIGHT ===")
        print(results.get("clinical_insight", ""))
        
        print("\n=== 4. EXPLANATION LOG (Sample) ===")
        for seg in results.get("segments", [])[:3]: # Just show first 3
            print(f"[{seg['category']}] \"{seg['text']}\" -> {seg['reasoning']}")
