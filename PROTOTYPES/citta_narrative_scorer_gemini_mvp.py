import os
import json
import urllib.request
import urllib.error

# The core prompt design based on the Autobiographical Interview (AI) coding manual
SCORING_PROMPT = """
You are an expert cognitive psychology rater trained in the Autobiographical Interview (AI) scoring manual. 
Your task is to analyze a reminiscence narrative from an older adult and evaluate its narrative quality.

INSTRUCTIONS:
1. SEGMENTATION: Break the text down into distinct "details" (meaningful units of information, roughly equivalent to clauses).
2. CLASSIFICATION: Classify EACH detail into ONE of the following two categories:
   - INTERNAL (Episodic): Details directly related to the main, specific event being described. Includes: Event actions (what happened), Perceptual details (sights, sounds), Time/Place specifics, and Emotions/Thoughts experienced AT THE TIME of the event.
   - EXTERNAL (Semantic/Other): General knowledge, facts, ongoing events, meta-comments (e.g., "I can't remember"), repetitions, or details belonging to a completely different event/timeframe.

OUTPUT FORMAT:
Return ONLY a valid JSON object with the following structure:
{
  "segments": [
    {
      "text": "the exact segment text",
      "category": "INTERNAL" or "EXTERNAL",
      "reasoning": "brief reason for classification"
    }
  ],
  "summary_scores": {
    "total_internal": <int>,
    "total_external": <int>,
    "episodic_ratio": <float> (internal / (internal + external))
  }
}
"""

def score_narrative_gemini(narrative_text, model_name="gemini-2.5-pro"):
    print(f"Analyzing narrative with Gemini... (Model: {model_name})")
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "GOOGLE_API_KEY environment variable is missing."}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": SCORING_PROMPT + "\n\nHere is the narrative to score:\n\n" + narrative_text}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result_json = json.loads(response.read().decode('utf-8'))
            # Extract the generated text from the response structure
            generated_text = result_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(generated_text)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        return {"error": f"HTTP Error {e.code}: {error_msg}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Mock Sample: An elderly person recalling their wedding day
    sample_narrative = (
        "我记得那天是1978年的秋天，天气特别冷，风刮得呼呼响。 "
        "我们当时在村东头的老房子里办的仪式。 "
        "现在那种老房子早就被拆了，现在的年轻人都喜欢去大酒店办婚礼。 "
        "我当时穿着一件红色的灯芯绒外套，心里特别紧张，手心全是汗。 "
        "我妈在旁边偷偷抹眼泪，我看着她，心里也酸酸的。 "
        "不过说实话，我现在记性越来越差了，很多细节都想不起来了。"
    )
    
    print("--- CittaVerse Narrative Scorer MVP (Gemini Edition via REST API) ---")
    print("Input Narrative:\n", sample_narrative, "\n")
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable is missing.")
        print("Please set it to run the Gemini scoring.")
    else:
        results = score_narrative_gemini(sample_narrative)
        print("=== SCORING RESULTS ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
