#summarizer.py working
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure your .env file has OPENAI_API_KEY set with your OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in .env. Please set your OpenAI API key.")

# Autogen will pick this up for OpenAI models
os.environ["OPENAI_API_KEY"] = api_key

# ✨ FEW-SHOT EXAMPLES ✨
# These examples guide the LLM on the desired output format and content.
FEW_SHOT_EXAMPLES = """
Example 1:
Function:
def greet(name):
    \"\"\"Greets the user.\"\"\"
    return f"Hi {name}"
Summary:
This function `greet(name)` takes a `name` as input and returns a personalized greeting message.

Example 2:
Class:
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, a, b):
        return a + b
Summary:
The `Calculator` class initializes with a `result` of 0. It includes an `add` method that takes two numbers, `a` and `b`, and returns their sum.

Example 3:
Function:
public static void main(String[] args) {
    System.out.println("Hello, World!");
}
Summary:
The `main` function is the entry point of a Java program. It prints "Hello, World!" to the console.
"""

# 🧠 Summarizer AssistantAgent
# Configured to use an OpenAI model (gpt-3.5-turbo) with your API key.
summarizer = AssistantAgent(
    name="SummarizerAgent",
    llm_config={
        "model": "gpt-3.5-turbo", # Using OpenAI's GPT-3.5 Turbo model
        "api_key": api_key,
        "temperature": 0.2, # Lower temperature for more consistent, factual summaries
        "timeout": 600, # Increased timeout for potentially longer LLM calls
    }
)

# 👤 UserProxyAgent
# Configured for automated operation (no human input) and no code execution.
user = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False} # Set to False as we are not executing code
)

def get_summary_from_llm(code_block_type: str, code_content: str) -> str:
    """
    Initiates a chat with the summarizer agent to get a summary for a code block.
    This function handles the Autogen chat initiation and extracts the final summary
    from the conversation history by filtering out non-summary messages.

    Args:
        code_block_type (str): The type of code block (e.g., "function", "class").
        code_content (str): The actual code snippet to be summarized.

    Returns:
        str: The generated summary from the LLM, or a default message if no summary is found.
    """
    # Construct the prompt, including few-shot examples and the code to summarize.
    message = f"{FEW_SHOT_EXAMPLES}\n\nNow summarize the following {code_block_type}:\n```{code_content}```"
    print(f"\n--- Initiating chat for {code_block_type} ---")
    print(f"Prompting LLM with (first 200 chars):\n{message[:200]}...")

    # Initiate the chat and capture the result object
    chat_result = user.initiate_chat(summarizer, message=message)

    final_summary = "No summary generated." # Default value if no summary is found

    # Check if chat_result and its history exist
    if chat_result and chat_result.chat_history:
        print(f"--- Chat History Length: {len(chat_result.chat_history)} ---")
        # Iterate through the chat history in reverse to find the last *relevant* message
        for i, msg in enumerate(reversed(chat_result.chat_history)):
            sender = msg.get('sender', 'Unknown')
            role = msg.get('role', 'Unknown')
            content = msg.get('content', '').strip()

            # Debug print for each message in history
            print(f"  Msg {len(chat_result.chat_history) - i - 1} (Sender: {sender}, Role: {role}): {content[:100]}...")

            # Filter out known non-summary messages regardless of sender/role for robustness
            if content == "TERMINATE" or content.strip('`').lower() == "terminate": # Handles 'TERMINATE' or ```TERMINATE```
                continue
            if content.startswith("exitcode: ") and "Code output:" in content:
                continue
            # Filter out messages that are just echoes of the prompt or very similar to it
            if content.startswith("Example 1:") and "Now summarize the following" in content:
                continue
            # Filter out messages that are just agent's internal thoughts or empty responses
            if not content: # Empty string
                continue
            if content.lower() in ["ok", "okay", "yes", "no", "i'm here to help.", "great! if you have any more questions or need further assistance, feel free to ask. just let me know how i can help you next."]: # Simple short responses
                continue
            if "no code execution needed" in content.lower(): # Autogen internal message
                continue

            # Now, try to extract the summary. Prioritize messages from the actual summarizer agent.
            # We are looking for the actual summary content from the LLM.
            # The LLM often puts "Summary:" or similar at the start.
            if "Summary:" in content:
                # Extract content after "Summary:"
                parts = content.split("Summary:", 1)
                if len(parts) > 1:
                    actual_summary = parts[1].strip()
                    if actual_summary:
                        final_summary = actual_summary
                        print(f"--- LLM Summary Received and Extracted (from 'Summary:') ---\n{final_summary}")
                        break # Found the summary, exit loop
            elif (sender == summarizer.name or role == 'assistant') and len(content) > 10 and len(content) < 500:
                # Heuristic fallback: if it's from the assistant and looks like a summary (reasonable length)
                # and doesn't start with common intros that are not summaries.
                if not (content.startswith("To summarize the ") or content.startswith("This is a method named ") or content.startswith("The provided code snippet defines")):
                    final_summary = content
                    print(f"--- LLM Summary Received and Extracted (direct content/heuristic) ---\n{final_summary}")
                    break
            else:
                # Final fallback: if it's the last non-filtered message and contains substantial content
                # This is less ideal but catches cases where the LLM doesn't use "Summary:" or specific intros.
                if len(content) > 10: # Ensure it's not just a very short, unhelpful message
                    final_summary = content
                    print(f"--- LLM Summary Received and Extracted (final fallback) ---\n{final_summary}")
                    break

    else:
        print("--- Chat result or history is empty. No summary could be extracted. ---")

    # Print what the function is returning for debugging purposes
    print(f"--- get_summary_from_llm returning: '{final_summary[:100]}...' ---")
    return final_summary


# 🔁 Standalone test run for the summarizer module
if __name__ == "__main__":
    test_function_code = """
def calculate_area(length, width):
    \"\"\"Calculates the area of a rectangle.\"\"\"
    return length * width
"""
    test_class_code = """
class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_details(self):
        return f"{self.name} costs ${self.price}"
"""
    test_java_code = """
public class MyJavaClass {
    public void doSomething() {
        // Some Java code
    }
}
"""

    print("--- Testing Function Summarization (Python) ---")
    function_summary = get_summary_from_llm("function", test_function_code)
    print(f"\nFinal Function Summary from standalone test:\n{function_summary}")

    print("\n--- Testing Class Summarization (Python) ---")
    class_summary = get_summary_from_llm("class", test_class_code)
    print(f"\nFinal Class Summary from standalone test:\n{class_summary}")

    print("\n--- Testing Class Summarization (Java) ---")
    java_class_summary = get_summary_from_llm("class", test_java_code)
    print(f"\nFinal Java Class Summary from standalone test:\n{java_class_summary}")
