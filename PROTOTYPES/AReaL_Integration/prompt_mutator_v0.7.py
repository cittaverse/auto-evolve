import sys
import json
import subprocess

def mutate_prompt(current_prompt, score_data):
    """
    Calls the local LLM to reflect on the current prompt and the coherence score it produced,
    and generate a new, improved prompt designed to elicit a more coherent narrative.
    """
    try:
        # Construct the reflection prompt for the LLM
        reflection_instruction = f"""
You are an expert in Prompt Engineering and Reminiscence Therapy.
Your task is to improve a prompt that is used to interview elderly people and elicit coherent life stories.

CURRENT PROMPT BEING USED:
"{current_prompt}"

PERFORMANCE OF THIS PROMPT:
The narrative elicited by this prompt was scored by a strict Neuro-symbolic evaluator.
The scores are (out of 1.0):
- Overall Coherence: {score_data.get('overall_coherence', 'N/A')}
- Temporal Consistency (Are events ordered logically?): {score_data.get('temporal_consistency', 'N/A')}
- Causal Density (Do events clearly cause one another?): {score_data.get('causal_density', 'N/A')}

YOUR TASK:
Analyze why the current prompt might have resulted in these specific scores (especially if they are low).
Then, write a NEW, IMPROVED prompt. The new prompt must explicitly encourage the elderly person to:
1. Speak in a clear chronological order.
2. Clearly explain *why* things happened (cause and effect).

OUTPUT FORMAT:
Return ONLY the text of the new prompt. Do not include any explanations, markdown formatting, or preamble. Just the raw prompt string.
"""
        
        # Call the local LLM CLI to generate the mutation
        result = subprocess.run(
            ['openclaw', 'llm', reflection_instruction],
            capture_output=True,
            text=True,
            check=True
        )
        
        new_prompt = result.stdout.strip()
        
        # Fallback if the LLM output is empty or went wrong
        if not new_prompt:
            return current_prompt + " Please try to explain the timeline and reasons more clearly."
            
        return new_prompt

    except Exception as e:
        print(f"Mutation Error: {e}", file=sys.stderr)
        # Return the original prompt so the loop doesn't crash, just stagnates
        return current_prompt

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 prompt_mutator.py <current_prompt_string> <score_json_string>", file=sys.stderr)
        sys.exit(1)

    current_prompt = sys.argv[1]
    
    try:
        score_data = json.loads(sys.argv[2])
    except json.JSONDecodeError:
        print("Error: Invalid score JSON provided.", file=sys.stderr)
        sys.exit(1)

    # Mutate and print the new prompt to stdout (for the bash script to capture)
    mutated_prompt = mutate_prompt(current_prompt, score_data)
    print(mutated_prompt)
