import sys
import json
import subprocess

def get_reward(text):
    """
    Wrapper function for AReaL to get reward signals based on narrative coherence.
    Simulates passing text to run_pipeline_v0.5.sh.
    """
    if not text or not text.strip():
        return 0.0
    
    # In a real integration:
    # try:
    #     result = subprocess.run(["./run_pipeline_v0.5.sh", "--input", text], capture_output=True, text=True)
    #     # parse result.stdout for overall_coherence
    #     return float(parsed_score)
    # except Exception as e:
    #     return 0.0

    # Mock score calculation:
    mock_score = 0.8
    return float(mock_score)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text_input = sys.argv[1]
        reward = get_reward(text_input)
        print(json.dumps({"overall_coherence": reward}))
    else:
        print(json.dumps({"error": "No text provided"}))