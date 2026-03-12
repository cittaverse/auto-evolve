#!/bin/bash
# Miniature RL Loop for Narrative Prompt Optimization
# This script simulates an environment where an AI interviews an elderly person.

echo "--- Initializing Mini-RL Engine ---"

# The initial, poorly-performing prompt
CURRENT_PROMPT="Tell me about your past."
TARGET_SCORE=0.85
MAX_ITERATIONS=3

for (( i=1; i<=$MAX_ITERATIONS; i++ ))
do
    echo "=================================================="
    echo "[Iteration $i] Current Prompt: \"$CURRENT_PROMPT\""
    
    # 1. Simulate the elderly person's response (Environment)
    # A poor prompt gets a disjointed response. A better prompt gets a more coherent one.
    # We use LLM to simulate the elderly person responding to the CURRENT_PROMPT
    SIMULATED_REPLY=$(openclaw llm "Act as an 80-year-old grandfather. Respond to this prompt: '$CURRENT_PROMPT'. If the prompt is vague (like 'tell me about your past'), give a rambling, disjointed answer jumping between different decades without explaining why things happened. If the prompt is specific and asks for chronological events and reasons, give a much more coherent, structured story." --quiet)
    
    echo ""
    echo "[Simulated Elderly Response]:"
    echo "$SIMULATED_REPLY"
    echo ""
    
    # 2. Score the response (Reward)
    # Call the v0.5 pipeline to get the JSON score
    echo "[Scoring Pipeline v0.5 Running...]"
    SCORE_JSON=$(python3 /home/node/.openclaw/workspace-hulk/PROTOTYPES/narrative_scorer/run_pipeline_v0.5.sh "$SIMULATED_REPLY" | grep -o '{.*}')
    
    # Extract the overall score for logging
    OVERALL_SCORE=$(echo $SCORE_JSON | jq '.overall_coherence' 2>/dev/null || echo "0.5")
    
    echo "[Score Received]: $OVERALL_SCORE"
    
    # 3. Check termination condition
    if (( $(echo "$OVERALL_SCORE >= $TARGET_SCORE" | bc -l) )); then
        echo ">>> SUCCESS! Target score reached. Final optimal prompt found:"
        echo ">>> \"$CURRENT_PROMPT\""
        exit 0
    fi
    
    # 4. Mutate Prompt (Policy Update)
    if [ $i -lt $MAX_ITERATIONS ]; then
        echo "[Score $OVERALL_SCORE < $TARGET_SCORE. Triggering Prompt Mutation (Brain)...]"
        NEW_PROMPT=$(python3 /home/node/.openclaw/workspace-hulk/PROTOTYPES/AReaL_Integration/prompt_mutator_v0.7.py "$CURRENT_PROMPT" "$SCORE_JSON")
        CURRENT_PROMPT="$NEW_PROMPT"
        echo "--- Mutation Complete. Proceeding to next iteration. ---"
    fi
done

echo "=================================================="
echo "Max iterations reached. Final prompt: \"$CURRENT_PROMPT\""
