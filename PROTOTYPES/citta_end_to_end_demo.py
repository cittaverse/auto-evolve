import os
import json
import urllib.request
import time

def call_bailian(prompt, response_json=False):
    """调用阿里云百炼 Qwen3.5-Plus 模型"""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        return f"Error: DASHSCOPE_API_KEY missing."
    
    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    payload = {
        "model": "qwen3.5-plus",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1 if response_json else 0.7
    }
    if response_json:
        payload["response_format"] = {"type": "json_object"}
        
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    })
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            text = res['choices'][0]['message']['content']
            return json.loads(text) if response_json else text
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# PHASE 1: MOCK DATA GENERATION (The "Patients")
# ==========================================
# We use LLM to simulate two distinct elderly patients based on clinical profiles.
def generate_mock_narrative(profile_type):
    print(f"\n[Phase 1] 正在生成虚拟患者语料: {profile_type}...")
    if profile_type == "Healthy":
        sys_prompt = "你是一位75岁认知健康的中国老人。请用口语化的中文回忆一次你20多岁时看露天电影的具体经历。要求：包含具体的视觉、听觉细节，明确的时间地点，以及当时的感受。字数150字左右。"
    else:
        sys_prompt = "你是一位75岁、带有早期阿尔茨海默症（认知衰退）倾向的中国老人。请用口语化的中文回忆年轻时看电影的经历。要求：偏离具体事件，大量使用通用常识（比如那时候电影很少），频繁抱怨自己记性不好（元认知），缺乏具体的时间地点和细节，车轱辘话来回说。字数150字左右。"
    
    return call_bailian(sys_prompt, response_json=False)

# ==========================================
# PHASE 2: NEURAL LAYER (LLM for Extraction ONLY)
# ==========================================
def neural_extract(narrative_text):
    print("[Phase 2] Neural Layer: 正在使用大模型进行非结构化实体的盲提取 (不打分)...")
    prompt = """
    You are an NLP entity extraction engine. Parse the input narrative and extract specific entities.
    DO NOT SCORE. DO NOT EVALUATE. Output ONLY valid JSON.
    
    Extract these arrays of strings if present in the text:
    - 'episodic_entities': Specific dates, times, locations, sights, sounds, smells, or actions tied to a single specific past event.
    - 'semantic_facts': General knowledge, historical background, or generic statements not tied to a specific episodic memory.
    - 'meta_comments': Comments about memory itself, present state, or "I forget/I don't know".
    
    Format:
    {
      "episodic_entities": ["[Entity 1]", "[Entity 2]"],
      "semantic_facts": [],
      "meta_comments": []
    }
    
    Narrative to parse:
    """ + narrative_text
    
    return call_bailian(prompt, response_json=True)

# ==========================================
# PHASE 3: SYMBOLIC LAYER (Deterministic Python Rules)
# ==========================================
def symbolic_score(extracted_data):
    print("[Phase 3] Symbolic Layer: 正在通过 Python 临床规则引擎计算最终得分...")
    
    episodic_count = len(extracted_data.get("episodic_entities", []))
    semantic_count = len(extracted_data.get("semantic_facts", []))
    meta_count = len(extracted_data.get("meta_comments", []))
    
    # Levine (2002) Simplified Logic:
    # Internal Score = count of distinct episodic details
    # External Score = count of semantic facts + meta-cognitive comments
    internal_score = episodic_count
    external_score = semantic_count + meta_count
    
    total = internal_score + external_score
    ratio = (internal_score / total) if total > 0 else 0
    
    return {
        "internal": internal_score,
        "external": external_score,
        "ratio": round(ratio, 2)
    }

# ==========================================
# RUN FULL DEMO PIPELINE
# ==========================================
if __name__ == "__main__":
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("ERROR: DASHSCOPE_API_KEY missing.")
        exit()

    print("="*60)
    print("🚀 CITTA-VERSE NEURO-SYMBOLIC END-TO-END DEMO 🚀")
    print("="*60)
    
    profiles = ["Healthy", "MCI (Cognitive Decline)"]
    
    for profile in profiles:
        print(f"\n{'='*40}\n>>> TESTING PROFILE: {profile}\n{'='*40}")
        
        # 1. Generate Data
        narrative = generate_mock_narrative(profile)
        print(f"\n【患者口述原始文本】:\n\033[96m{narrative}\033[0m\n")
        
        # 2. Neural Extraction
        extracted_json = neural_extract(narrative)
        print("\n【Neural层: 提取出的结构化实体】:")
        print(json.dumps(extracted_json, indent=2, ensure_ascii=False))
        
        # 3. Symbolic Scoring
        scores = symbolic_score(extracted_json)
        print(f"\n【Symbolic层: 最终可解释得分】:")
        print(f"  🟢 Internal Details (情景细节): {scores['internal']}")
        print(f"  🔴 External Details (外部/废话): {scores['external']}")
        print(f"  🧮 Episodic Ratio (情景专注度):   \033[93m{scores['ratio']}\033[0m")
        
        if scores['ratio'] > 0.6:
            print("  ➡️ [诊断结论]: 情景记忆丰富，网络连结健康。")
        else:
            print("  ➡️ [诊断结论]: 叙事显著语义化，缺乏具体时空锚点，存在认知衰退特征。")
        
        time.sleep(2) # brief pause between profiles
