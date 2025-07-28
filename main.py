import os
import json
# Import the specific function from summarizer.py that handles LLM interaction.
# This function encapsulates the Autogen agents and their conversation.
from summarizer import get_summary_from_llm
from parser import read_all_code_files

def summarize_all_code(input_folder: str, output_file: str):
    """
    Orchestrates the process of reading code files, extracting code blocks,
    generating summaries for each block using an LLM, and saving the
    structured summaries to a JSON file.

    Args:
        input_folder (str): The path to the directory containing the code files.
        output_file (str): The path to the JSON file where summaries will be saved.
    """
    print(f"Starting codebase summarization from: {input_folder}")
    all_code_files_data = read_all_code_files(input_folder)

    if not all_code_files_data:
        print(f"No code files found in {input_folder} or parsing failed. Exiting.")
        return

    # This list will hold the final structured data with summaries for all files
    summarized_project_data = []

    for file_data in all_code_files_data:
        filename = file_data["filename"]
        # Use filepath if available from parser, fallback to filename
        filepath = file_data.get("filepath", filename)
        file_blocks_with_summaries = [] # To store blocks for the current file with their summaries

        print(f"\n--- Processing file: {filename} (Path: {filepath}) ---")
        if not file_data["blocks"]:
            print(f"No code blocks extracted from {filename}. Adding file with empty blocks.")
            # Add file info even if no blocks, to keep the output structure consistent
            summarized_project_data.append({
                "filename": filename,
                "filepath": filepath,
                "blocks": []
            })
            continue # Move to the next file

        for block in file_data["blocks"]:
            block_type = block["type"]
            block_name = block["name"]
            block_code = block["code"]

            print(f"🧠 Summarizing {block_type} `{block_name}` from {filename}...")

            # Call the get_summary_from_llm function to get the summary.
            # This function includes the few-shot examples in its internal prompt.
            summary_text = get_summary_from_llm(block_type, block_code)

            print("✅ Summary Generated:")
            print(summary_text)

            # Add the generated summary to the current block dictionary
            block["summary"] = summary_text
            file_blocks_with_summaries.append(block)

        # After processing all blocks in a file, add the file's data
        # (now including all block summaries) to the main project data list.
        summarized_project_data.append({
            "filename": filename,
            "filepath": filepath,
            "blocks": file_blocks_with_summaries
        })

    # Ensure the output directory exists before attempting to write the file
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")

    # Save the complete structured data (with all summaries) to the JSON file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summarized_project_data, f, indent=2)
        print(f"\n✅ All summaries successfully saved to: {output_file}")
    except IOError as e:
        print(f"❌ Error saving summaries to {output_file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving to {output_file}: {e}")


if __name__ == "__main__":
    # Define the input code folder and the output JSON file path
    input_folder = "input_code"
    output_file = "output/summary.json"

    # Call the main summarization function
    summarize_all_code(input_folder, output_file)






# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary using the summarizer agent.
#     Extracts the latest assistant message from chat history.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             # CASE 1: Object-based history
#             if hasattr(msg, "role") and msg.role == "assistant":
#                 return msg.content.strip()
#             # CASE 2: Dict-based history (fallback)
#             if isinstance(msg, dict) and msg.get("role") == "assistant":
#                 return msg.get("content", "").strip()

#     return "⚠️ No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Reads all code blocks, generates summaries, and saves to JSON.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Summary Generated:")
#             print(summary_text)

#             # ✅ Save correct summary
#             block["summary"] = summary_text

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All summaries saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)

# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary using the summarizer agent.
#     Extracts the latest assistant message from chat history.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             # CASE 1: Object-based history
#             if hasattr(msg, "role") and msg.role == "assistant":
#                 return msg.content.strip()
#             # CASE 2: Dict-based history (fallback)
#             if isinstance(msg, dict) and msg.get("role") == "assistant":
#                 return msg.get("content", "").strip()

#     return "⚠️ No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Reads all code blocks, generates summaries, and saves to JSON.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Summary Generated:")
#             print(summary_text)

#             # ✅ Save correct summary
#             block["summary"] = summary_text

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open("output/summary.md", "w", encoding="utf-8") as f:
#         for file in all_code:
#             f.write(f"# {file['filename']}\n\n")
#             for block in file["blocks"]:
#                 f.write(f"## {block['type'].capitalize()}: {block['name']}\n\n")
#                 f.write("```code\n" + block['code'] + "\n```\n\n")
#                 f.write("**Summary:**\n" + block.get("summary", "Not available") + "\n\n---\n")


#     print(f"\n✅ All summaries saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)
















# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary by initiating a chat with the summarizer agent.
#     Extracts the latest assistant response from the chat history.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     # ✅ Properly extract actual summary from assistant
#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             if isinstance(msg, dict) and msg.get("role") == "assistant":
#                 return msg["content"].strip()
#             elif hasattr(msg, "role") and msg.role == "assistant":
#                 return msg.content.strip()

#     return "No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Reads all code, summarizes each block using LLM, and saves to output JSON.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             # ✅ Save actual summary to the block
#             block["summary"] = summary_text

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)



# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary using the SummarizerAgent and extracts the assistant's reply.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     # 🔍 Extract the latest assistant response from chat history
#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
#                 return msg["content"].strip()

#     return "No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Parses code files and summarizes each block (function/class) using LLM.
#     Saves results to structured JSON.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             block["summary"] = summary_text  # ✅ Save actual summary to block

#     # 💾 Write the updated summaries to output JSON
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)


# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files


# def generate_summary(prompt):
#     """
#     Generates a summary by initiating a chat with the summarizer agent.
#     Extracts the latest assistant response from the chat history.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             if msg.get("role") == "user" and msg.get("content", "").strip():
#                 # Skip user prompts
#                 continue
#             if msg.get("role") == "assistant" and msg.get("content"):
#                 return msg["content"].strip()
#     return "No summary generated"


# def summarize_all_code(input_folder, output_file):
#     """
#     Summarizes all function and class blocks from files in the input folder.
#     Saves the output to a structured JSON file.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             block["summary"] = summary_text  # ✅ Store summary

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")


# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)



# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Sends prompt to the LLM agent and extracts assistant's final response.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     # ✅ Walk backwards in chat history to get latest assistant message
#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             if hasattr(msg, "role") and msg.role == "assistant":
#                 return msg.content.strip()
#     return "No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Loops over parsed code blocks, summarizes each, and writes final JSON output.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]

#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             # ✅ Attach the summary to this block
#             block["summary"] = summary_text

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)


# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary by chatting with the SummarizerAgent.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     # ✅ Extract assistant's message from chat history
#     history = getattr(result, "chat_history", [])
#     for msg in reversed(history):
#         if isinstance(msg, dict):
#             if msg.get("role") == "assistant":
#                 return msg.get("content", "").strip()
#         elif hasattr(msg, "role") and msg.role == "assistant":
#             return msg.content.strip()

#     return "No summary generated"

# def summarize_all_code(input_folder, output_file):
#     """
#     Reads code, summarizes functions/classes, and writes JSON output.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]

#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             block["summary"] = summary_text

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")

# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)

# import os
# import json
# from summarizer import summarizer, user
# from parser import read_all_code_files

# def generate_summary(prompt):
#     """
#     Generates a summary by initiating a chat with the summarizer agent.
#     Extracts the assistant's response from the chat history.
#     """
#     result = user.initiate_chat(summarizer, message=prompt)

#     if hasattr(result, "chat_history"):
#         for msg in reversed(result.chat_history):
#             if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
#                 return msg["content"].strip()

#     return "No summary generated"



# def summarize_all_code(input_folder, output_file):
#     """
#     Summarizes all function and class blocks from files in the input folder.
#     Saves the output to a structured JSON file.
#     """
#     all_code = read_all_code_files(input_folder)

#     for file in all_code:
#         for block in file["blocks"]:
#             block_name = block["name"]
#             block_code = block["code"]
#             print(f"\n🧠 Summarizing {block['type']} `{block_name}` in {file['filename']}...")

#             prompt = f"Summarize the following {block['type']} named {block_name}:\n\n{block_code}"
#             summary_text = generate_summary(prompt)

#             print("✅ Final Summary Captured:")
#             print(summary_text)

#             block["summary"] = summary_text  # Save it to summary.json

#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(all_code, f, indent=2)

#     print(f"\n✅ All code blocks summarized and saved to: {output_file}")


# if __name__ == "__main__":
#     input_folder = "input_code"
#     output_file = "output/summary.json"
#     summarize_all_code(input_folder, output_file)

