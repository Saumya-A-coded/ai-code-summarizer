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














# #summarizer.py
# from autogen import AssistantAgent, UserProxyAgent
# import os
# import json # Import json for parsing LLM's structured output
# import re   # Import re for regex to find JSON in LLM output
# from dotenv import load_dotenv

# load_dotenv()

# # Ensure your .env file has OPENAI_API_KEY set with your OpenAI API Key
# api_key = os.getenv("OPENAI_API_KEY")
# if api_key is None:
#     raise ValueError("OPENAI_API_KEY not found in .env. Please set your OpenAI API key.")

# # Autogen will pick this up for OpenAI models
# os.environ["OPENAI_API_KEY"] = api_key

# # ✨ FEW-SHOT EXAMPLES ✨
# # These examples guide the LLM on the desired output format and content.
# # The LLM is now explicitly asked to output JSON.
# FEW_SHOT_EXAMPLES = """
# Example 1:
# Function:
# def greet(name):
#     \"\"\"Greets the user.\"\"\"
#     return f"Hi {name}"
# JSON Summary:
# {"summary": "This function `greet(name)` takes a `name` as input and returns a personalized greeting message."}

# Example 2:
# Class:
# class Calculator:
#     def __init__(self):
#         self.result = 0

#     def add(self, a, b):
#         return a + b
# JSON Summary:
# {"summary": "The `Calculator` class initializes with a `result` of 0. It includes an `add` method that takes two numbers, `a` and `b`, and returns their sum."}

# Example 3:
# Function:
# public static void main(String[] args) {
#     System.out.println("Hello, World!");
# }
# JSON Summary:
# {"summary": "The `main` function is the entry point of a Java program. It prints 'Hello, World!' to the console."}
# """

# # 🧠 Summarizer AssistantAgent
# # Configured to use an OpenAI model (gpt-3.5-turbo) with your API key.
# summarizer = AssistantAgent(
#     name="SummarizerAgent",
#     llm_config={
#         "model": "gpt-3.5-turbo", # Using OpenAI's GPT-3.5 Turbo model
#         "api_key": api_key,
#         "temperature": 0.2, # Lower temperature for more consistent, factual summaries
#         "timeout": 600, # Increased timeout for potentially longer LLM calls
#         # IMPORTANT: Force JSON output for reliable parsing
#         "response_format": { "type": "json_object" } # This instructs the LLM to return JSON
#     },
#     # System message to strictly control the LLM's behavior
#     system_message=(
#         "You are a helpful assistant that summarizes code. "
#         "Your only task is to provide a concise summary of the given code block. "
#         "Always respond with a JSON object containing a single key 'summary'. "
#         "DO NOT generate or suggest any code, explanations outside of the JSON, or conversational filler. "
#         "DO NOT ask follow-up questions. "
#         "When you have provided the JSON summary, respond with 'TERMINATE'."
#     )
# )

# # 👤 UserProxyAgent
# # Configured for automated operation (no human input) and NO code execution.
# user = UserProxyAgent(
#     name="UserProxy",
#     human_input_mode="NEVER",
#     # Explicitly disable code execution for this summarization task
#     # Setting 'last_n_messages' to 0 and 'use_docker' to False should prevent code execution.
#     code_execution_config={"use_docker": False, "last_n_messages": 0},
#     # Ensure UserProxy also terminates correctly when it sees 'TERMINATE'
#     is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") != -1,
#     # System message to prevent UserProxy from trying to generate code or act as a conversational agent
#     system_message=(
#         "You are a proxy agent that simply relays messages. "
#         "Do NOT generate any code or engage in conversation beyond relaying the final JSON summary. "
#         "Once you receive a JSON summary from the AssistantAgent, print it and then send 'TERMINATE'."
#     )
# )

# def get_summary_from_llm(code_block_type: str, code_content: str) -> str:
#     """
#     Initiates a chat with the summarizer agent to get a summary for a code block.
#     This function handles the Autogen chat initiation and extracts the final summary
#     by expecting and parsing JSON output from the LLM, with robust fallback for text.

#     Args:
#         code_block_type (str): The type of code block (e.g., "function", "class").
#         code_content (str): The actual code snippet to be summarized.

#     Returns:
#         str: The generated summary from the LLM, or a default message if no summary is found.
#     """
#     # Construct the prompt, now explicitly asking for JSON output and no code.
#     prompt = f"""
#     {FEW_SHOT_EXAMPLES}

#     Your task is to summarize the following {code_block_type}.
#     Provide the summary in a JSON object with a single key "summary".
#     DO NOT generate any code. Only output the JSON.

#     Code to summarize:
#     ```{code_block_type.lower()}
#     {code_content}
#     ```
#     JSON Summary:
#     """
    
#     print(f"\n--- Initiating chat for {code_block_type} ---")
#     print(f"Prompting LLM with (first 200 chars):\n{prompt[:200]}...")

#     # Initiate the chat and capture the result object
#     chat_result = user.initiate_chat(summarizer, message=prompt)

#     final_summary = "No summary generated." # Default value if no summary is found

#     # Check if chat_result and its history exist
#     if chat_result and chat_result.chat_history:
#         print(f"--- Chat History Length: {len(chat_result.chat_history)} ---")
#         # Iterate through the chat history in reverse to find the last *relevant* message
#         for i, msg in enumerate(reversed(chat_result.chat_history)):
#             sender = msg.get('sender', 'Unknown')
#             role = msg.get('role', 'Unknown')
#             content = msg.get('content', '').strip()

#             # Debug print for each message in history
#             print(f"  Msg {len(chat_result.chat_history) - i - 1} (Sender: {sender}, Role: {role}): {content[:100]}...")

#             # --- Primary Extraction Strategy: Look for JSON ---
#             # Use regex to robustly find a JSON object in the content, as LLMs might wrap it.
#             json_match = re.search(r'\{.*\}', content, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group(0)
#                 try:
#                     parsed_json = json.loads(json_str)
#                     if "summary" in parsed_json:
#                         final_summary = parsed_json["summary"].strip()
#                         print(f"--- LLM Summary Received and Extracted (from JSON) ---\n{final_summary}")
#                         break # Found the summary, exit loop
#                 except json.JSONDecodeError:
#                     # Not valid JSON, continue to fallback or next message
#                     print(f"  Msg {len(chat_result.chat_history) - i - 1}: Found string that looks like JSON but failed to parse. Skipping.")
#                     pass # Continue to next extraction attempt

#             # --- Secondary Extraction Strategy: Aggressive Text Filtering (if no clean JSON) ---
#             # This is a fallback if the LLM doesn't strictly adhere to JSON or wraps it poorly.
#             # Only consider messages from the AssistantAgent or those that look like direct summaries.
#             if (sender == summarizer.name or role == 'assistant') and content:
#                 # Filter out known non-summary messages
#                 if content == "TERMINATE" or content.strip('`').lower() == "terminate":
#                     continue
#                 if content.startswith("exitcode: ") and "Code output:" in content:
#                     continue
#                 if content.startswith("Example 1:") and "Now summarize the following" in content:
#                     continue
#                 if not content:
#                     continue
#                 if content.lower() in ["ok", "okay", "yes", "no", "i'm here to help.", "great! if you have any more questions or need further assistance, feel free to ask. just let me know how i can help you next."]:
#                     continue
#                 if "no code execution needed" in content.lower():
#                     continue
#                 # Filter out conversational intros that are not the summary itself
#                 if content.startswith("To summarize the ") or content.startswith("This is a method named ") or content.startswith("The provided code snippet defines"):
#                     # If it's a conversational intro, try to find the actual summary part within it
#                     if "Summary:" in content:
#                         parts = content.split("Summary:", 1)
#                         if len(parts) > 1:
#                             actual_summary = parts[1].strip()
#                             if actual_summary:
#                                 final_summary = actual_summary
#                                 print(f"--- LLM Summary Received and Extracted (from 'Summary:' in conversational text) ---\n{final_summary}")
#                                 break
#                     else: # If no "Summary:" and it's a conversational intro, skip
#                         continue

#                 # If it's none of the above filters, and it's from the assistant, and a reasonable length, take it.
#                 if len(content) > 10 and len(content) < 1000: # Heuristic: reasonable length for a summary
#                     final_summary = content
#                     print(f"--- LLM Summary Received and Extracted (final fallback - direct assistant content) ---\n{final_summary}")
#                     break
#             else: # Also check messages from UserProxy if they contain a summary (due to Autogen's echo behavior)
#                 if "Summary:" in content:
#                     parts = content.split("Summary:", 1)
#                     if len(parts) > 1:
#                         actual_summary = parts[1].strip()
#                         if actual_summary:
#                             final_summary = actual_summary
#                             print(f"--- LLM Summary Received and Extracted (from 'Summary:' in UserProxy message) ---\n{final_summary}")
#                             break
#                 elif len(content) > 10 and len(content) < 1000 and not (content.startswith("To summarize the ") or content.startswith("This is a method named ") or content.startswith("The provided code snippet defines")):
#                     final_summary = content
#                     print(f"--- LLM Summary Received and Extracted (final fallback - direct UserProxy content) ---\n{final_summary}")
#                     break
#     else:
#         print("--- Chat result or history is empty. No summary could be extracted. ---")

#     # Print what the function is returning for debugging purposes
#     print(f"--- get_summary_from_llm returning: '{final_summary[:100]}...' ---")
#     return final_summary


# # 🔁 Standalone test run for the summarizer module
# if __name__ == "__main__":
#     test_function_code = """
# def calculate_area(length, width):
#     \"\"\"Calculates the area of a rectangle.\"\"\"
#     return length * width
# """
#     test_class_code = """
# class Product:
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price

#     def get_details(self):
#         return f"{self.name} costs ${self.price}"
# """
#     test_java_code = """
# public class MyJavaClass {
#     public void doSomething() {
#         // Some Java code
#     }
# }
# """

#     print("--- Testing Function Summarization (Python) ---")
#     function_summary = get_summary_from_llm("function", test_function_code)
#     print(f"\nFinal Function Summary from standalone test:\n{function_summary}")

#     print("\n--- Testing Class Summarization (Python) ---")
#     class_summary = get_summary_from_llm("class", test_class_code)
#     print(f"\nFinal Class Summary from standalone test:\n{class_summary}")

#     print("\n--- Testing Class Summarization (Java) ---")
#     java_class_summary = get_summary_from_llm("class", test_java_code)
#     print(f"\nFinal Java Class Summary from standalone test:\n{java_class_summary}")










# working











# #summarizer.py
# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Ensure your .env file has OPENAI_API_KEY set with your OpenAI API Key
# api_key = os.getenv("OPENAI_API_KEY")
# if api_key is None:
#     raise ValueError("OPENAI_API_KEY not found in .env. Please set your OpenAI API key.")

# # Autogen will pick this up for OpenAI models
# os.environ["OPENAI_API_KEY"] = api_key

# # ✨ FEW-SHOT EXAMPLES ✨
# # These examples guide the LLM on the desired output format and content.
# FEW_SHOT_EXAMPLES = """
# Example 1:
# Function:
# def greet(name):
#     \"\"\"Greets the user.\"\"\"
#     return f"Hi {name}"
# Summary:
# This function `greet(name)` takes a `name` as input and returns a personalized greeting message.

# Example 2:
# Class:
# class Calculator:
#     def __init__(self):
#         self.result = 0

#     def add(self, a, b):
#         return a + b
# Summary:
# The `Calculator` class initializes with a `result` of 0. It includes an `add` method that takes two numbers, `a` and `b`, and returns their sum.

# Example 3:
# Function:
# public static void main(String[] args) {
#     System.out.println("Hello, World!");
# }
# Summary:
# The `main` function is the entry point of a Java program. It prints "Hello, World!" to the console.
# """

# # 🧠 Summarizer AssistantAgent
# # Configured to use an OpenAI model (gpt-3.5-turbo) with your API key.
# summarizer = AssistantAgent(
#     name="SummarizerAgent",
#     llm_config={
#         "model": "gpt-3.5-turbo", # Using OpenAI's GPT-3.5 Turbo model
#         "api_key": api_key,
#         "temperature": 0.2, # Lower temperature for more consistent, factual summaries
#         "timeout": 600, # Increased timeout for potentially longer LLM calls
#     }
# )

# # 👤 UserProxyAgent
# # Configured for automated operation (no human input) and no code execution.
# user = UserProxyAgent(
#     name="UserProxy",
#     human_input_mode="NEVER",
#     code_execution_config={"use_docker": False} # Set to False as we are not executing code
# )

# def get_summary_from_llm(code_block_type: str, code_content: str) -> str:
#     """
#     Initiates a chat with the summarizer agent to get a summary for a code block.
#     This function handles the Autogen chat initiation and extracts the final summary
#     from the conversation history by filtering out non-summary messages.

#     Args:
#         code_block_type (str): The type of code block (e.g., "function", "class").
#         code_content (str): The actual code snippet to be summarized.

#     Returns:
#         str: The generated summary from the LLM, or a default message if no summary is found.
#     """
#     # Construct the prompt, including few-shot examples and the code to summarize.
#     message = f"{FEW_SHOT_EXAMPLES}\n\nNow summarize the following {code_block_type}:\n```{code_content}```"
#     print(f"\n--- Initiating chat for {code_block_type} ---")
#     print(f"Prompting LLM with (first 200 chars):\n{message[:200]}...")

#     # Initiate the chat and capture the result object
#     chat_result = user.initiate_chat(summarizer, message=message)

#     final_summary = "No summary generated." # Default value if no summary is found

#     # Check if chat_result and its history exist
#     if chat_result and chat_result.chat_history:
#         print(f"--- Chat History Length: {len(chat_result.chat_history)} ---")
#         # Iterate through the chat history in reverse to find the last *relevant* assistant message
#         for i, msg in enumerate(reversed(chat_result.chat_history)):
#             sender = msg.get('sender', 'Unknown')
#             role = msg.get('role', 'Unknown')
#             content = msg.get('content', '').strip()

#             # Debug print for each message in history
#             print(f"  Msg {len(chat_result.chat_history) - i - 1} (Sender: {sender}, Role: {role}): {content[:100]}...")

#             # We are looking for a message from the 'SummarizerAgent' (assistant)
#             # that contains the actual summary.
#             if (role == 'assistant' or sender == summarizer.name) and content:
#                 # Filter out common non-summary messages from the assistant
#                 if content == "TERMINATE":
#                     continue
#                 # If the assistant is repeating the prompt or a very long message that looks like the prompt
#                 if content.startswith("Example 1:") and "Now summarize the following" in content:
#                     continue
#                 # If it's a message from the UserProxy related to code execution (e.g., exitcode)
#                 # This can sometimes be misattributed or appear in the history in a confusing way
#                 if content.startswith("exitcode: ") and "Code output:" in content:
#                     continue

#                 # If we reach here, this message is likely the actual summary from the assistant.
#                 # The LLM often puts "Summary:" or similar at the start.
#                 if "Summary:" in content:
#                     # Extract content after "Summary:"
#                     parts = content.split("Summary:", 1)
#                     if len(parts) > 1:
#                         actual_summary = parts[1].strip()
#                         if actual_summary:
#                             final_summary = actual_summary
#                             print(f"--- LLM Summary Received and Extracted (from 'Summary:') ---\n{final_summary}")
#                             break # Found the summary, exit loop
#                 elif len(content) > 10 and len(content) < 500: # Heuristic: reasonable length for a summary
#                     # This is a fallback if "Summary:" isn't present but it looks like a summary
#                     final_summary = content
#                     print(f"--- LLM Summary Received and Extracted (direct content/heuristic) ---\n{final_summary}")
#                     break
#                 else:
#                     # If it's an assistant message but doesn't fit the above,
#                     # it might still be a summary if it's the last one.
#                     # This is a fallback.
#                     final_summary = content
#                     print(f"--- LLM Summary Received and Extracted (fallback to last assistant message) ---\n{final_summary}")
#                     break
#     else:
#         print("--- Chat result or history is empty. No summary could be extracted. ---")

#     # Print what the function is returning for debugging purposes
#     print(f"--- get_summary_from_llm returning: '{final_summary[:100]}...' ---")
#     return final_summary


# # 🔁 Standalone test run for the summarizer module
# if __name__ == "__main__":
#     test_function_code = """
# def calculate_area(length, width):
#     \"\"\"Calculates the area of a rectangle.\"\"\"
#     return length * width
# """
#     test_class_code = """
# class Product:
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price

#     def get_details(self):
#         return f"{self.name} costs ${self.price}"
# """
#     test_java_code = """
# public class MyJavaClass {
#     public void doSomething() {
#         // Some Java code
#     }
# }
# """

#     print("--- Testing Function Summarization (Python) ---")
#     function_summary = get_summary_from_llm("function", test_function_code)
#     print(f"\nFinal Function Summary from standalone test:\n{function_summary}")

#     print("\n--- Testing Class Summarization (Python) ---")
#     class_summary = get_summary_from_llm("class", test_class_code)
#     print(f"\nFinal Class Summary from standalone test:\n{class_summary}")

#     print("\n--- Testing Class Summarization (Java) ---")
#     java_class_summary = get_summary_from_llm("class", test_java_code)
#     print(f"\nFinal Java Class Summary from standalone test:\n{java_class_summary}")







# #summarizer.py
# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Ensure your .env file has OPENAI_API_KEY set with your OpenAI API Key
# api_key = os.getenv("OPENAI_API_KEY")
# if api_key is None:
#     raise ValueError("OPENAI_API_KEY not found in .env. Please set your OpenAI API key.")

# # Autogen will pick this up for OpenAI models
# os.environ["OPENAI_API_KEY"] = api_key

# # ✨ FEW-SHOT EXAMPLES ✨
# # These examples guide the LLM on the desired output format and content.
# FEW_SHOT_EXAMPLES = """
# Example 1:
# Function:
# def greet(name):
#     \"\"\"Greets the user.\"\"\"
#     return f"Hi {name}"
# Summary:
# This function `greet(name)` takes a `name` as input and returns a personalized greeting message.

# Example 2:
# Class:
# class Calculator:
#     def __init__(self):
#         self.result = 0

#     def add(self, a, b):
#         return a + b
# Summary:
# The `Calculator` class initializes with a `result` of 0. It includes an `add` method that takes two numbers, `a` and `b`, and returns their sum.

# Example 3:
# Function:
# public static void main(String[] args) {
#     System.out.println("Hello, World!");
# }
# Summary:
# The `main` function is the entry point of a Java program. It prints "Hello, World!" to the console.
# """

# # 🧠 Summarizer AssistantAgent
# # Configured to use an OpenAI model (gpt-3.5-turbo) with your API key.
# summarizer = AssistantAgent(
#     name="SummarizerAgent",
#     llm_config={
#         "model": "gpt-3.5-turbo", # Using OpenAI's GPT-3.5 Turbo model
#         "api_key": api_key,
#         "temperature": 0.2, # Lower temperature for more consistent, factual summaries
#         "timeout": 600, # Increased timeout for potentially longer LLM calls
#     }
# )

# # 👤 UserProxyAgent
# # Configured for automated operation (no human input) and no code execution.
# user = UserProxyAgent(
#     name="UserProxy",
#     human_input_mode="NEVER",
#     code_execution_config={"use_docker": False} # Set to False as we are not executing code
# )

# def get_summary_from_llm(code_block_type: str, code_content: str) -> str:
#     """
#     Initiates a chat with the summarizer agent to get a summary for a code block.
#     This function handles the Autogen chat initiation and extracts the final summary
#     from the conversation history.

#     Args:
#         code_block_type (str): The type of code block (e.g., "function", "class").
#         code_content (str): The actual code snippet to be summarized.

#     Returns:
#         str: The generated summary from the LLM, or a default message if no summary is found.
#     """
#     # Construct the prompt, including few-shot examples and the code to summarize.
#     # Using triple backticks for the code content helps the LLM differentiate code from instructions.
#     message = f"{FEW_SHOT_EXAMPLES}\n\nNow summarize the following {code_block_type}:\n```{code_content}```"
#     print(f"\n--- Initiating chat for {code_block_type} ---")
#     print(f"Prompting LLM with (first 200 chars):\n{message[:200]}...")

#     # Initiate the chat and capture the result object
#     chat_result = user.initiate_chat(summarizer, message=message)

#     final_summary = "No summary generated." # Default value if no summary is found

#     # Check if chat_result and its history exist
#     if chat_result and chat_result.chat_history:
#         print(f"--- Chat History Length: {len(chat_result.chat_history)} ---")
#         # Iterate through the chat history in reverse to find the last assistant message
#         for i, msg in enumerate(reversed(chat_result.chat_history)):
#             # Debug print for each message in history
#             print(f"  Msg {len(chat_result.chat_history) - i - 1} (Sender: {msg.get('sender', 'Unknown')}, Role: {msg.get('role', 'Unknown')}): {msg.get('content', '')[:100]}...")

#             # Check if the message is from the assistant and contains content
#             if msg.get('role') == 'assistant' or msg.get('sender') == summarizer.name:
#                 summary_content = msg.get('content', '').strip()
#                 if summary_content: # Ensure the content is not empty
#                     final_summary = summary_content
#                     print(f"--- LLM Summary Received and Extracted ---\n{final_summary}")
#                     break # Found the summary, exit the loop

#     else:
#         print("--- Chat result or history is empty. No summary could be extracted. ---")

#     # Print what the function is returning for debugging purposes
#     print(f"--- get_summary_from_llm returning: '{final_summary[:100]}...' ---")
#     return final_summary


# # 🔁 Standalone test run for the summarizer module
# if __name__ == "__main__":
#     test_function_code = """
# def calculate_area(length, width):
#     \"\"\"Calculates the area of a rectangle.\"\"\"
#     return length * width
# """
#     test_class_code = """
# class Product:
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price

#     def get_details(self):
#         return f"{self.name} costs ${self.price}"
# """
#     test_java_code = """
# public class MyJavaClass {
#     public void doSomething() {
#         // Some Java code
#     }
# }
# """

#     print("--- Testing Function Summarization (Python) ---")
#     function_summary = get_summary_from_llm("function", test_function_code)
#     print(f"\nFinal Function Summary from standalone test:\n{function_summary}")

#     print("\n--- Testing Class Summarization (Python) ---")
#     class_summary = get_summary_from_llm("class", test_class_code)
#     print(f"\nFinal Class Summary from standalone test:\n{class_summary}")

#     print("\n--- Testing Class Summarization (Java) ---")
#     java_class_summary = get_summary_from_llm("class", test_java_code)
#     print(f"\nFinal Java Class Summary from standalone test:\n{java_class_summary}")



# #summariser.py
# from autogen import AssistantAgent, UserProxyAgent
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Securely fetch your API key
# api_key = os.getenv("OPENAI_API_KEY")
# if api_key is None:
#     raise ValueError("OPENAI_API_KEY not found in .env")

# # Assign key for Autogen usage
# os.environ["OPENAI_API_KEY"] = api_key

# # ✨ FEW-SHOT EXAMPLES ✨
# FEW_SHOT_EXAMPLES = """
# Example 1:
# Function:
# def greet(name):
#     return f"Hi {name}"
# Summary:
# This function returns a greeting message with the input name.

# Example 2:
# Class:
# class Calculator:
#     def __init__(self):
#         self.result = 0
# Summary:
# This class defines a simple calculator with an initial result of zero.
# """

# # 🧠 Summarizer AssistantAgent
# summarizer = AssistantAgent(
#     name="SummarizerAgent",
#     llm_config={
#         "api_key": api_key,
#         "model": "gpt-3.5-turbo",
#         "temperature": 0.2
#     }
# )

# # 👤 UserProxyAgent
# user = UserProxyAgent(
#     name="UserProxy",
#     human_input_mode="NEVER",
#     code_execution_config={"use_docker": False}
# )

# # 🔁 For testing in standalone run
# if __name__ == "__main__":
#     test_code = """
# def add(a, b):
#     return a + b
# """
#     # 🪄 Prompt with few-shot examples
#     message = f"{FEW_SHOT_EXAMPLES}\n\nNow summarize the following function:\n{test_code}"
#     user.initiate_chat(summarizer, message=message)
