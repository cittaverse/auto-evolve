import os
import json
import urllib.request
import base64

def extract_pdf_with_gemini(pdf_path):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY missing.")
        return

    print("Reading and encoding PDF...")
    with open(pdf_path, "rb") as f:
        pdf_data = base64.b64encode(f.read()).decode('utf-8')

    model_name = "gemini-2.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = """
    You are an expert researcher in cognitive psychology and AI. 
    Analyze this paper on the automated scoring of the Autobiographical Interview (AI) using Large Language Models.
    
    Extract and summarize the following details EXACTLY:
    1. **The Exact Prompts/Instructions**: What exact prompts or instructions did they feed to the LLM to classify internal vs. external details? Did they use Few-Shot, Zero-Shot, or Chain-of-Thought? Quote the prompt if it is provided.
    2. **LLM Models Used**: Which specific LLMs did they evaluate (e.g., GPT-4, Llama-3, etc.)? Which one performed the best?
    3. **Evaluation Metrics**: What was the agreement with human raters (e.g., Intraclass Correlation Coefficient - ICC, Pearson's r)? 
    4. **Scoring Rules/Nuances**: Did they introduce any new rules or nuances for handling edge cases in the Autobiographical Interview compared to the traditional Levine (2002) manual?
    
    Output in clear, structured Markdown (in Chinese, but keep technical terms and exact prompts in English).
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "application/pdf",
                        "data": pdf_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    
    print("Sending request to Gemini 2.5 Pro (this may take a minute due to PDF size)...")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result_json = json.loads(response.read().decode('utf-8'))
            generated_text = result_json['candidates'][0]['content']['parts'][0]['text']
            
            # Save the result
            with open("paper_extraction_result.md", "w") as out_f:
                out_f.write(generated_text)
            print("Extraction successful! Saved to paper_extraction_result.md")
            print("\n--- PREVIEW ---\n")
            print(generated_text[:1500] + "\n...\n")
            
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_msg}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_pdf_with_gemini("/home/node/.openclaw/workspace-hulk/2025_LLM_Autobiographical_Scoring.pdf")
