import gradio as gr
import openai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def generate_and_select_best_response(prompt, model_generation, api_key):
    try:
        # Set the OpenAI API key from user input
        openai.api_key = api_key
        
        max_tokens = 4096
        n_responses = 10
        
        # Generate multiple detailed responses using the specified model
        logging.info(f"Generating {n_responses} responses using model: {model_generation}")
        
        completions = openai.ChatCompletion.create(
            model=model_generation,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=n_responses
        )

        if not completions.choices:
            logging.error("No responses received from OpenAI")
            return "Error: No responses received from OpenAI"

        # Score each response
        scored_responses = []
        for idx, choice in enumerate(completions.choices):
            response_text = choice.message['content']
            score = ask_gpt_to_score(prompt, response_text, api_key)
            scored_responses.append((response_text, score))
            logging.info(f"Response {idx + 1}: Score = {score}, Response = {response_text}")

        # Select the best response based on the highest score
        best_response_text, best_score = max(scored_responses, key=lambda x: x[1])
        logging.info(f"Best response selected: Score = {best_score}, Response = {best_response_text}")

        # Ask for detailed reasoning why this response is the best
        detailed_reasoning = ask_gpt_for_detailed_reasoning(prompt, best_response_text, api_key)
        logging.info(f"Reasoning for best response: {detailed_reasoning}")

        # Ask for feedback on the best response to further refine it
        feedback = ask_gpt_for_feedback(best_response_text, api_key)
        logging.info(f"Feedback on best response: {feedback}")

        return f"Best Response:\n{best_response_text}\n\nReasoning:\n{detailed_reasoning}\n\nFeedback:\n{feedback}"
    
    except Exception as e:
        logging.error(f"Error in processing: {str(e)}")
        return f"Error: {str(e)}"

def ask_gpt_to_score(prompt, response_text, api_key):
    # Use the provided API key for the scoring request
    openai.api_key = api_key

    scoring_prompt = f"On a scale of 0 to 100, score this response for its relevance, completeness, and coherence.\n\nPrompt: {prompt}\n\nResponse: {response_text}\n\nScore:"
    scoring_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": scoring_prompt}],
        max_tokens=10
    )
    try:
        score_text = scoring_response.choices[0].message['content'].strip()
        score = int(score_text)
    except ValueError:
        score = 0  # Default score if parsing fails
    return score

def ask_gpt_for_detailed_reasoning(prompt, best_response_text, api_key):
    # Use the provided API key for the reasoning request
    openai.api_key = api_key

    reasoning_prompt = f"Explain in detail why the following response is the best answer to the prompt:\n\nPrompt: {prompt}\n\nResponse: {best_response_text}\n\nDetailed Reasoning:"
    reasoning_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": reasoning_prompt}],
        max_tokens=150
    )
    reasoning_text = reasoning_response.choices[0].message['content'].strip()
    return reasoning_text

def ask_gpt_for_feedback(response_text, api_key):
    # Use the provided API key for the feedback request
    openai.api_key = api_key

    feedback_prompt = f"Provide feedback and potential improvements for the following response:\n\nResponse: {response_text}\n\nFeedback:"
    feedback_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": feedback_prompt}],
        max_tokens=100
    )
    feedback_text = feedback_response.choices[0].message['content'].strip()
    return feedback_text

# Define Gradio components
with gr.Blocks() as demo:
    gr.Markdown("# OpenAI GPT-3.5 and GPT-4 Enhanced Response Generator with Detailed Reasoning and Feedback")
    
    with gr.Row():
        api_key_input = gr.Textbox(label="OpenAI API Key:", placeholder="Enter your OpenAI API key here...", type="password")
        prompt_input = gr.Textbox(label="Enter your prompt here:", lines=4, placeholder="Type your question...")
        model_generation = gr.Dropdown(choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"], label="Model for Generation", value="gpt-3.5-turbo")
        
    generate_button = gr.Button("Generate, Select Best Response, and Explain Reasoning")
    response_output = gr.Textbox(label="Best Response with Detailed Reasoning and Feedback", lines=15)

    def handle_generate(prompt, model_gen, api_key):
        return generate_and_select_best_response(prompt, model_gen, api_key)

    generate_button.click(handle_generate, [prompt_input, model_generation, api_key_input], response_output)

# Launch the Gradio interface
demo.launch()
