#working one this is 
import os
import re

def extract_code_blocks(file_content):
    """
    Extracts top-level functions and classes using regex.
    This is designed to be language-neutral (works for Python, Java, JS, etc.)
    by using general patterns and brace-level tracking for C-like languages.
    Note: For highly accurate, language-specific parsing, a dedicated AST/CST
    parser (like Tree-sitter) would be more robust, but this approach
    aims for broad compatibility with regex.
    """
    code_blocks = []

    # Pattern to match function or method definitions.
    # Attempts to capture common patterns in C-like languages (Java, C++, JS, C#)
    # and Python's 'def'.
    # This pattern is an improvement but still has limitations for complex cases.
    function_pattern = re.compile(
        r"^\s*(?:public|private|protected)?\s*(?:static|async)?\s*" # Access modifiers, static/async
        r"(?:[a-zA-Z_][a-zA-Z0-9_<>\[\]\.]*\s+)?" # Optional return type (e.g., int, String, void)
        r"(def|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)\s*(?:\{|:)", # 'def' or 'function', name, params, then '{' or ':'
        re.MULTILINE
    )
    # Pattern to match class definitions.
    # Attempts to capture common patterns in C-like languages and Python.
    class_pattern = re.compile(
        r"^\s*(?:public|private|protected)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::|\{|extends|implements)?", # 'class', name, then ':' or '{' or inheritance
        re.MULTILINE
    )

    lines = file_content.splitlines()
    buffer = []
    capture = False
    current_type = None
    current_name = ""
    brace_level = 0 # To track nested braces for C-like languages
    indentation_level = -1 # To track indentation for Python-like languages

    for line_num, line in enumerate(lines):
        stripped = line.strip()
        leading_whitespace_len = len(line) - len(stripped)

        # Check for class definition
        class_match = re.match(class_pattern, line) # Match against original line to get indentation
        if class_match:
            # If we were capturing a previous block, save it
            if capture and buffer:
                code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
            buffer = []
            current_type = "class"
            current_name = class_match.group(1) # Extract just the class name
            capture = True
            buffer.append(line) # Append original line to maintain indentation

            # Initialize brace level for C-like languages
            brace_level = line.count('{') - line.count('}')
            # Initialize indentation level for Python-like languages
            indentation_level = leading_whitespace_len
            continue # Move to next line after finding a new block start

        # Check for function definition
        function_match = re.match(function_pattern, line) # Match against original line
        if function_match:
            # If we were capturing a previous block, save it
            if capture and buffer:
                code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
            buffer = []
            current_type = "function"
            current_name = function_match.group(2) # Extract just the function name
            capture = True
            buffer.append(line) # Append original line to maintain indentation

            # Initialize brace level for C-like languages
            brace_level = line.count('{') - line.count('}')
            # Initialize indentation level for Python-like languages
            indentation_level = leading_whitespace_len
            continue # Move to next line after finding a new block start

        # If currently capturing a block
        if capture:
            buffer.append(line) # Always append the original line to maintain indentation

            # Update brace level for C-like languages
            brace_level += line.count('{') - line.count('}')

            # Logic for ending a block:
            # 1. For C-like languages: when brace_level returns to 0 after the initial open brace
            if brace_level == 0 and (stripped.endswith('}') or stripped == '}'):
                # Check if it's not the very first line of the block (which would have brace_level 0 too)
                if len(buffer) > 1:
                    code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
                    buffer = []
                    capture = False
                    current_type = None
                    current_name = ""
                    indentation_level = -1 # Reset
                    brace_level = 0 # Reset
                    continue

            # 2. For Python-like languages (or general indentation-based):
            # If the current line's stripped content is empty, or if its indentation
            # is less than the block's starting indentation (and it's not a new block start).
            # This is a heuristic and can be tricky for mixed indentation or comments.
            if stripped == "" or (leading_whitespace_len < indentation_level and stripped != ""):
                # If the buffer has content and we're not starting a new block,
                # it means the current block has ended.
                if buffer and not (re.match(class_pattern, line) or re.match(function_pattern, line)):
                    # Remove trailing empty lines from the buffer before saving the block
                    while buffer and buffer[-1].strip() == "":
                        buffer.pop()
                    if buffer: # Only add if there's actual code content
                        code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
                    buffer = []
                    capture = False
                    current_type = None
                    current_name = ""
                    indentation_level = -1 # Reset
                    brace_level = 0 # Reset
                    continue

    # Add any leftover buffer at the end of the file
    if buffer:
        while buffer and buffer[-1].strip() == "": # Clean trailing empty lines
            buffer.pop()
        if buffer:
            code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})

    return code_blocks


def read_all_code_files(folder_path):
    """
    Scans all relevant code files in the folder and extracts code blocks.
    Returns a language-agnostic structure for LLM input.
    """
    all_files_data = []

    # Define common code file extensions to process
    code_extensions = (
        ".py", ".java", ".js", ".ts", ".cpp", ".c", ".h", ".hpp", ".cs",
        ".go", ".rb", ".php", ".html", ".css", ".sh", ".json", ".xml", ".md"
    )
    # Define directories to exclude from traversal
    exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.vscode', '.idea']

    for root, dirs, files in os.walk(folder_path):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(code_extensions):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors='ignore') as f:
                        code = f.read()
                        blocks = extract_code_blocks(code)
                        all_files_data.append({
                            "filename": file,
                            "filepath": full_path,
                            "blocks": blocks
                        })
                except Exception as e:
                    print(f"Error reading or parsing file {full_path}: {e}")

    return all_files_data

