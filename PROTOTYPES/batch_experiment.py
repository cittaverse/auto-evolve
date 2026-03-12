import os
import json
import urllib.request
import csv
import time

def call_gemini(prompt, response_json=False):
    api_key = os.environ.get("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7 if not response_json else 0.1}
    }
    if response_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"
        
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            text = res['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text) if response_json else text
    except Exception as e:
        return {"error": str(e)} if response_json else f"Error: {str(e)}"

def generate_patient(patient_id, condition):
    prompt = f"""
    Generate a short, colloquial Chinese reminiscence narrative (about 100-150 words) 
    from a 75-year-old recalling a specific childhood festival (e.g., Spring Festival).
    Condition: {condition}. 
    If 'Healthy': Include rich specific episodic details (sights, sounds, exact actions, feelings then).
    If 'MCI': Struggle to find specific memories, rely heavily on general semantic facts about festivals back then, and complain about current poor memory (meta-cognition).
    Return ONLY the narrative text.
    """
    return call_gemini(prompt)

def neural_extract(text):
    prompt = """
    Extract entities into JSON. DO NOT SCORE.
    Keys: 
    - 'episodic_entities' (specific time/place/perception/action/emotion of the past event)
    - 'semantic_facts' (general historical facts or generic statements)
    - 'meta_comments' (evaluations of current memory or present state)
    
    Narrative:
    """ + text
    return call_gemini(prompt, response_json=True)

def symbolic_score(extracted_data):
    internal = len(extracted_data.get("episodic_entities", []))
    external = len(extracted_data.get("semantic_facts", [])) + len(extracted_data.get("meta_comments", []))
    total = internal + external
    ratio = (internal / total) if total > 0 else 0.0
    return internal, external, round(ratio, 2)

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY first.")
        exit()
        
    num_samples_per_group = 15
    results = []
    
    print(f"Starting Batch Experiment: {num_samples_per_group*2} total patients...")
    
    for group in ["Healthy", "MCI"]:
        for i in range(num_samples_per_group):
            p_id = f"{group[:1]}{(i+1):02d}"
            print(f"Processing {p_id}...")
            narrative = generate_patient(p_id, group)
            extracted = neural_extract(narrative)
            
            if "error" in extracted:
                print(f"  Error extracting {p_id}")
                continue
                
            internal, external, ratio = symbolic_score(extracted)
            
            results.append({
                "Patient_ID": p_id,
                "True_Condition": group,
                "Internal_Score": internal,
                "External_Score": external,
                "Episodic_Ratio": ratio,
                "Narrative_Snippet": narrative[:50].replace("\n", " ") + "..."
            })
            time.sleep(2) # rate limit
            
    # Save to CSV
    csv_file = "citta_simulated_trial_results.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Patient_ID", "True_Condition", "Internal_Score", "External_Score", "Episodic_Ratio", "Narrative_Snippet"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nExperiment complete! Results saved to {csv_file}")
