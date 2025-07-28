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

