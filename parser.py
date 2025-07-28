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





# import os
# import re

# def extract_code_blocks(file_content):
#     """
#     Extracts top-level functions and classes using regex.
#     This is designed to be language-neutral (works for Python, Java, JS, etc.)
#     by using general patterns and brace-level tracking for C-like languages.
#     Note: For highly accurate, language-specific parsing, a dedicated AST/CST
#     parser (like Tree-sitter) would be more robust, but this approach
#     aims for broad compatibility with regex.
#     """
#     code_blocks = []

#     # Pattern to match function or method definitions.
#     # Attempts to capture common patterns in C-like languages (Java, C++, JS, C#)
#     # and Python's 'def'.
#     # Group 1: 'def' or 'function' or None (for C-like where keyword is part of type/access modifier)
#     # Group 2: The actual name of the function/class.
#     # Group 3: The opening delimiter (':' for Python, '{' for C-like).
#     block_start_pattern = re.compile(
#         r"^\s*(?:(?:public|private|protected|static|async)\s+)?" # Optional access modifiers, static/async
#         r"(?:[a-zA-Z_][a-zA-Z0-9_<>\[\]\.]*\s+)?" # Optional return type (e.g., int, String, void)
#         r"(?:(def|class|function)\s+)?" # Optional keyword for Python/JS
#         r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(?" # The actual name, optional '('
#         r"(?:[^:\n]*)\s*([:{])", # Capture anything until ':' or '{' (the block start)
#         re.MULTILINE
#     )

#     lines = file_content.splitlines()
#     buffer = []
#     capture = False
#     current_type = None
#     current_name = ""
#     current_type_keyword = None # Store the keyword that started the block ('def', 'class', 'function')
#     start_line_indent = -1 # Indentation level of the line where the block started
#     brace_level = 0        # For C-like languages, tracks nested curly braces

#     for line_num, line in enumerate(lines):
#         stripped_line = line.strip()
#         leading_whitespace_len = len(line) - len(stripped_line)

#         # Check for a new block start
#         match = block_start_pattern.match(line) # Match against original line to get indentation
#         if match:
#             # If we were already capturing a block, save it before starting a new one
#             if capture and buffer:
#                 # Clean up trailing empty lines from the previous buffer
#                 while buffer and buffer[-1].strip() == "":
#                     buffer.pop()
#                 if buffer: # Only add if there's actual code content
#                     code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
            
#             # Reset for the new block
#             buffer = []
#             capture = True
            
#             # Determine the type and name based on the match
#             keyword_group = match.group(1) # 'def', 'class', 'function' or None if C-like
#             name_group = match.group(2)
#             block_opener = match.group(3)

#             current_name = name_group

#             if keyword_group == 'def' or keyword_group == 'function':
#                 current_type = 'function'
#             elif keyword_group == 'class':
#                 current_type = 'class'
#             else: # Fallback for C-like where keyword might be part of type/access modifier
#                 if 'class' in line.lower():
#                     current_type = 'class'
#                 elif '(' in line and ')' in line and '{' in line: # Heuristic for C-like function
#                     current_type = 'function'
#                 else:
#                     current_type = 'unknown' # Should ideally not happen with good patterns

#             current_type_keyword = keyword_group # Store the keyword for indentation logic

#             start_line_indent = leading_whitespace_len
#             buffer.append(line) # Add the definition line to the buffer

#             # Initialize brace level for C-like languages
#             if block_opener == '{':
#                 brace_level = line.count('{') - line.count('}')
#             else: # For Python's ':' or other non-brace languages
#                 brace_level = 0
#             continue # Move to the next line

#         # If currently capturing a block
#         if capture:
#             buffer.append(line) # Always append the original line to maintain indentation

#             # Update brace level for C-like languages
#             brace_level += line.count('{') - line.count('}')

#             # Determine if the current block has ended
#             block_ended = False

#             # Logic for C-like languages (based on brace level)
#             if brace_level == 0 and '{' in "".join(buffer[:2]): # Check if block started with a brace
#                 # Ensure it's not the very first line of the block (which would also have brace_level 0)
#                 if len(buffer) > 1 and stripped_line.endswith('}'):
#                     block_ended = True
            
#             # Logic for Python-like languages (based on indentation)
#             # This is a heuristic: if a line is less indented than the block start,
#             # or if it's an empty line at the block's indentation level.
#             # This needs to be careful not to prematurely end on comments or docstrings.
#             if current_type_keyword in ['def', 'class'] and not block_ended: # Only apply if not already ended by braces
#                 if stripped_line == "": # Empty line
#                     # Check if the next non-empty line (if any) is less indented
#                     next_non_empty_line_indent = -1
#                     for j in range(line_num + 1, len(lines)):
#                         next_stripped = lines[j].strip()
#                         if next_stripped:
#                             next_non_empty_line_indent = len(lines[j]) - len(next_stripped)
#                             break
                    
#                     if next_non_empty_line_indent != -1 and next_non_empty_line_indent <= start_line_indent:
#                         block_ended = True
#                 elif leading_whitespace_len < start_line_indent:
#                     # If indentation drops below the starting block's indentation, the block has ended.
#                     # This check needs to be AFTER checking for new block starts on the same line.
#                     if not block_start_pattern.match(line): # Ensure it's not a new block starting at lower indent
#                         block_ended = True
            
#             if block_ended:
#                 # Clean up trailing empty lines from the buffer before saving the block
#                 while buffer and buffer[-1].strip() == "":
#                     buffer.pop()
#                 if buffer: # Only add if there's actual code content
#                     code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
                
#                 # Reset state
#                 buffer = []
#                 capture = False
#                 current_type = None
#                 current_name = ""
#                 start_line_indent = -1
#                 brace_level = 0
#                 current_type_keyword = None # Reset keyword
#                 continue # Move to next line

#     # Add any leftover buffer at the end of the file (for the last block if not explicitly terminated)
#     if capture and buffer:
#         while buffer and buffer[-1].strip() == "": # Clean trailing empty lines
#             buffer.pop()
#         if buffer:
#             code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})

#     return code_blocks


# def read_all_code_files(folder_path: str) -> list[dict]:
#     """
#     Scans all relevant code files in the folder and extracts code blocks.
#     Returns a structured list of file data for LLM input.
#     """
#     all_files_data = []

#     # Define common code file extensions to process
#     code_extensions = (
#         ".py", ".java", ".js", ".ts", ".cpp", ".c", ".h", ".hpp", ".cs",
#         ".go", ".rb", ".php", ".html", ".css", ".sh", ".json", ".xml", ".md"
#     )
#     # Define directories to exclude from traversal
#     exclude_dirs = [
#         '.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build',
#         '.vscode', '.idea', 'target', 'bin', 'obj', 'out'
#     ]

#     print(f"Scanning directory: {folder_path}")
#     for root, dirs, files in os.walk(folder_path):
#         # Modify dirs in-place to skip excluded directories
#         dirs[:] = [d for d in dirs if d not in exclude_dirs]

#         for file in files:
#             file_extension = os.path.splitext(file)[1].lower()
            
#             # Use a single extraction function for all, relying on regex patterns
#             # to handle different language syntaxes. This is the "language-neutral" approach.
#             if file_extension in code_extensions:
#                 full_path = os.path.join(root, file)
#                 try:
#                     with open(full_path, "r", encoding="utf-8", errors='ignore') as f:
#                         code = f.read()
#                         blocks = extract_code_blocks(code) # Call the single extraction function
#                         all_files_data.append({
#                             "filename": file,
#                             "filepath": full_path,
#                             "blocks": blocks
#                         })
#                     print(f"  Parsed file: {full_path} (found {len(blocks)} blocks)")
#                 except Exception as e:
#                     print(f"  Error reading or parsing file {full_path}: {e}")
#             # else:
#             #     print(f"  Skipping non-code file or unsupported extension: {file}") # Optional: log skipped files
#     print(f"Finished scanning. Total files processed: {len(all_files_data)}")
#     return all_files_data





# import os
# import re

# def extract_code_blocks(file_content: str) -> list[dict]:
#     """
#     Extracts top-level functions and classes from file content using regex and
#     indentation/brace-level tracking. This aims for language-neutrality but
#     is still a heuristic approach.

#     Args:
#         file_content (str): The entire content of a code file.

#     Returns:
#         list[dict]: A list of dictionaries, each representing a code block
#                     with 'type' (class/function), 'name', and 'code'.
#     """
#     code_blocks = []

#     # Regex to capture Python functions/classes and C-like functions/classes.
#     # Group 1: The actual name of the function/class.
#     # Group 2: The opening delimiter (':' for Python, '{' for C-like).
#     # Group 3: The keyword used to define the block ('def', 'class', 'function').
#     block_start_pattern = re.compile(
#         r"^\s*(?:(?:public|private|protected|static|async)\s+)?" # Optional access/modifier for C-like
#         r"(?:[a-zA-Z_][a-zA-Z0-9_<>\[\]\.]*\s+)?" # Optional return type for C-like
#         r"(?:(def|class|function)\s+)?" # Optional keyword for Python/JS
#         r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(?" # The actual name, optional '('
#         r"(?:[^:\n]*)\s*([:{])", # Capture anything until ':' or '{' (the block start)
#         re.MULTILINE
#     )

#     lines = file_content.splitlines()
#     buffer = []
#     capture = False
#     current_type = None
#     current_name = ""
#     current_type_keyword = None # Store the keyword that started the block ('def', 'class', 'function')
#     start_line_indent = -1 # Indentation level of the line where the block started
#     brace_level = 0        # For C-like languages, tracks nested curly braces

#     for line_num, line in enumerate(lines):
#         stripped_line = line.strip()
#         leading_whitespace_len = len(line) - len(stripped_line)

#         # Check for a new block start
#         match = block_start_pattern.match(line) # Match against original line to get indentation
#         if match:
#             # If we were already capturing a block, save it before starting a new one
#             if capture and buffer:
#                 # Clean up trailing empty lines from the previous buffer
#                 while buffer and buffer[-1].strip() == "":
#                     buffer.pop()
#                 if buffer: # Only add if there's actual code content
#                     code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
            
#             # Reset for the new block
#             buffer = []
#             capture = True
            
#             # Determine the type and name based on the match
#             keyword_group = match.group(1) # 'def', 'class', 'function' or None if C-like
#             name_group = match.group(2)
#             block_opener = match.group(3)

#             current_name = name_group

#             if keyword_group == 'def' or keyword_group == 'function':
#                 current_type = 'function'
#             elif keyword_group == 'class':
#                 current_type = 'class'
#             else: # Fallback for C-like where keyword might be part of type/access modifier
#                 if 'class' in line.lower():
#                     current_type = 'class'
#                 elif '(' in line and ')' in line and '{' in line: # Heuristic for C-like function
#                     current_type = 'function'
#                 else:
#                     current_type = 'unknown' # Should ideally not happen with good patterns

#             current_type_keyword = keyword_group # Store the keyword for indentation logic

#             start_line_indent = leading_whitespace_len
#             buffer.append(line) # Add the definition line to the buffer

#             # Initialize brace level for C-like languages
#             if block_opener == '{':
#                 brace_level = line.count('{') - line.count('}')
#             else: # For Python's ':' or other non-brace languages
#                 brace_level = 0
#             continue # Move to the next line

#         # If currently capturing a block
#         if capture:
#             buffer.append(line) # Always append the original line to maintain indentation

#             # Update brace level for C-like languages
#             brace_level += line.count('{') - line.count('}')

#             # Determine if the current block has ended
#             block_ended = False

#             # Logic for C-like languages (based on brace level)
#             if brace_level == 0 and '{' in "".join(buffer[:2]): # Check if block started with a brace
#                 # Ensure it's not the very first line of the block (which would also have brace_level 0)
#                 if len(buffer) > 1 and stripped_line.endswith('}'):
#                     block_ended = True
            
#             # Logic for Python-like languages (based on indentation)
#             # This is a heuristic: if a line is less indented than the block start,
#             # or if it's an empty line at the block's indentation level.
#             # This needs to be careful not to prematurely end on comments or docstrings.
#             if current_type_keyword in ['def', 'class'] and not block_ended: # Only apply if not already ended by braces
#                 if stripped_line == "": # Empty line
#                     # Check if the next non-empty line (if any) is less indented
#                     next_non_empty_line_indent = -1
#                     for j in range(line_num + 1, len(lines)):
#                         next_stripped = lines[j].strip()
#                         if next_stripped:
#                             next_non_empty_line_indent = len(lines[j]) - len(next_stripped)
#                             break
                    
#                     if next_non_empty_line_indent != -1 and next_non_empty_line_indent <= start_line_indent:
#                         block_ended = True
#                 elif leading_whitespace_len < start_line_indent:
#                     # If indentation drops below the starting block's indentation, the block has ended.
#                     # This check needs to be AFTER checking for new block starts on the same line.
#                     if not block_start_pattern.match(line): # Ensure it's not a new block starting at lower indent
#                         block_ended = True
            
#             if block_ended:
#                 # Clean up trailing empty lines from the buffer before saving the block
#                 while buffer and buffer[-1].strip() == "":
#                     buffer.pop()
#                 if buffer: # Only add if there's actual code content
#                     code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
                
#                 # Reset state
#                 buffer = []
#                 capture = False
#                 current_type = None
#                 current_name = ""
#                 start_line_indent = -1
#                 brace_level = 0
#                 current_type_keyword = None # Reset keyword
#                 continue # Move to next line

#     # Add any leftover buffer at the end of the file (for the last block if not explicitly terminated)
#     if capture and buffer:
#         while buffer and buffer[-1].strip() == "": # Clean trailing empty lines
#             buffer.pop()
#         if buffer:
#             code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})

#     return code_blocks


# def read_all_code_files(folder_path: str) -> list[dict]:
#     """
#     Scans all relevant code files in the folder and extracts code blocks.
#     Returns a structured list of file data for LLM input.

#     Args:
#         folder_path (str): The path to the root directory of the codebase.

#     Returns:
#         list[dict]: A list of dictionaries, each representing a file,
#                     containing 'filename', 'filepath', and a list of 'blocks'.
#     """
#     all_files_data = []

#     # Define common code file extensions to process
#     code_extensions = (
#         ".py", ".java", ".js", ".ts", ".cpp", ".c", ".h", ".hpp", ".cs",
#         ".go", ".rb", ".php", ".html", ".css", ".sh", ".json", ".xml", ".md"
#     )
#     # Define directories to exclude from traversal
#     exclude_dirs = [
#         '.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build',
#         '.vscode', '.idea', 'target', 'bin', 'obj', 'out'
#     ]

#     print(f"Scanning directory: {folder_path}")
#     for root, dirs, files in os.walk(folder_path):
#         # Modify dirs in-place to skip excluded directories
#         dirs[:] = [d for d in dirs if d not in exclude_dirs]

#         for file in files:
#             if file.endswith(code_extensions):
#                 full_path = os.path.join(root, file)
#                 try:
#                     with open(full_path, "r", encoding="utf-8", errors='ignore') as f:
#                         code = f.read()
#                         blocks = extract_code_blocks(code)
#                         all_files_data.append({
#                             "filename": file,
#                             "filepath": full_path,
#                             "blocks": blocks
#                         })
#                     print(f"  Parsed file: {full_path} (found {len(blocks)} blocks)")
#                 except Exception as e:
#                     print(f"  Error reading or parsing file {full_path}: {e}")
#     print(f"Finished scanning. Total files processed: {len(all_files_data)}")
#     return all_files_data






#working one this is 
# # import os
# import re

# def extract_code_blocks(file_content):
#     """
#     Extracts top-level functions and classes using regex.
#     This is designed to be language-neutral (works for Python, Java, JS, etc.)
#     by using general patterns and brace-level tracking for C-like languages.
#     Note: For highly accurate, language-specific parsing, a dedicated AST/CST
#     parser (like Tree-sitter) would be more robust, but this approach
#     aims for broad compatibility with regex.
#     """
#     code_blocks = []

#     # Pattern to match function or method definitions.
#     # Attempts to capture common patterns in C-like languages (Java, C++, JS, C#)
#     # and Python's 'def'.
#     # This pattern is an improvement but still has limitations for complex cases.
#     function_pattern = re.compile(
#         r"^\s*(?:public|private|protected)?\s*(?:static|async)?\s*" # Access modifiers, static/async
#         r"(?:[a-zA-Z_][a-zA-Z0-9_<>\[\]\.]*\s+)?" # Optional return type (e.g., int, String, void)
#         r"(def|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)\s*(?:\{|:)", # 'def' or 'function', name, params, then '{' or ':'
#         re.MULTILINE
#     )
#     # Pattern to match class definitions.
#     # Attempts to capture common patterns in C-like languages and Python.
#     class_pattern = re.compile(
#         r"^\s*(?:public|private|protected)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::|\{|extends|implements)?", # 'class', name, then ':' or '{' or inheritance
#         re.MULTILINE
#     )

#     lines = file_content.splitlines()
#     buffer = []
#     capture = False
#     current_type = None
#     current_name = ""
#     brace_level = 0 # To track nested braces for C-like languages
#     indentation_level = -1 # To track indentation for Python-like languages

#     for line_num, line in enumerate(lines):
#         stripped = line.strip()
#         leading_whitespace_len = len(line) - len(stripped)

#         # Check for class definition
#         class_match = re.match(class_pattern, line) # Match against original line to get indentation
#         if class_match:
#             # If we were capturing a previous block, save it
#             if capture and buffer:
#                 code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#             buffer = []
#             current_type = "class"
#             current_name = class_match.group(1) # Extract just the class name
#             capture = True
#             buffer.append(line) # Append original line to maintain indentation

#             # Initialize brace level for C-like languages
#             brace_level = line.count('{') - line.count('}')
#             # Initialize indentation level for Python-like languages
#             indentation_level = leading_whitespace_len
#             continue # Move to next line after finding a new block start

#         # Check for function definition
#         function_match = re.match(function_pattern, line) # Match against original line
#         if function_match:
#             # If we were capturing a previous block, save it
#             if capture and buffer:
#                 code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#             buffer = []
#             current_type = "function"
#             current_name = function_match.group(2) # Extract just the function name
#             capture = True
#             buffer.append(line) # Append original line to maintain indentation

#             # Initialize brace level for C-like languages
#             brace_level = line.count('{') - line.count('}')
#             # Initialize indentation level for Python-like languages
#             indentation_level = leading_whitespace_len
#             continue # Move to next line after finding a new block start

#         # If currently capturing a block
#         if capture:
#             buffer.append(line) # Always append the original line to maintain indentation

#             # Update brace level for C-like languages
#             brace_level += line.count('{') - line.count('}')

#             # Logic for ending a block:
#             # 1. For C-like languages: when brace_level returns to 0 after the initial open brace
#             if brace_level == 0 and (stripped.endswith('}') or stripped == '}'):
#                 # Check if it's not the very first line of the block (which would have brace_level 0 too)
#                 if len(buffer) > 1:
#                     code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#                     buffer = []
#                     capture = False
#                     current_type = None
#                     current_name = ""
#                     indentation_level = -1 # Reset
#                     brace_level = 0 # Reset
#                     continue

#             # 2. For Python-like languages (or general indentation-based):
#             # If the current line's stripped content is empty, or if its indentation
#             # is less than the block's starting indentation (and it's not a new block start).
#             # This is a heuristic and can be tricky for mixed indentation or comments.
#             if stripped == "" or (leading_whitespace_len < indentation_level and stripped != ""):
#                 # If the buffer has content and we're not starting a new block,
#                 # it means the current block has ended.
#                 if buffer and not (re.match(class_pattern, line) or re.match(function_pattern, line)):
#                     # Remove trailing empty lines from the buffer before saving the block
#                     while buffer and buffer[-1].strip() == "":
#                         buffer.pop()
#                     if buffer: # Only add if there's actual code content
#                         code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#                     buffer = []
#                     capture = False
#                     current_type = None
#                     current_name = ""
#                     indentation_level = -1 # Reset
#                     brace_level = 0 # Reset
#                     continue

#     # Add any leftover buffer at the end of the file
#     if buffer:
#         while buffer and buffer[-1].strip() == "": # Clean trailing empty lines
#             buffer.pop()
#         if buffer:
#             code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})

#     return code_blocks


# def read_all_code_files(folder_path):
#     """
#     Scans all relevant code files in the folder and extracts code blocks.
#     Returns a language-agnostic structure for LLM input.
#     """
#     all_files_data = []

#     # Define common code file extensions to process
#     code_extensions = (
#         ".py", ".java", ".js", ".ts", ".cpp", ".c", ".h", ".hpp", ".cs",
#         ".go", ".rb", ".php", ".html", ".css", ".sh", ".json", ".xml", ".md"
#     )
#     # Define directories to exclude from traversal
#     exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.vscode', '.idea']

#     for root, dirs, files in os.walk(folder_path):
#         # Modify dirs in-place to skip excluded directories
#         dirs[:] = [d for d in dirs if d not in exclude_dirs]

#         for file in files:
#             if file.endswith(code_extensions):
#                 full_path = os.path.join(root, file)
#                 try:
#                     with open(full_path, "r", encoding="utf-8", errors='ignore') as f:
#                         code = f.read()
#                         blocks = extract_code_blocks(code)
#                         all_files_data.append({
#                             "filename": file,
#                             "filepath": full_path,
#                             "blocks": blocks
#                         })
#                 except Exception as e:
#                     print(f"Error reading or parsing file {full_path}: {e}")

#     return all_files_data





# #parser.py
# import os
# import re

# def extract_code_blocks(file_content):
#     """
#     Extracts top-level functions and classes using regex.
#     This is language-neutral (works for Python, Java, JS, etc.).
#     """
#     code_blocks = []

#     # Pattern to match function or method definitions (basic cross-language pattern)
#     function_pattern = re.compile(r"^\s*(public|private|protected)?\s*(static\s+)?[a-zA-Z0-9<>\[\]]+\s+\w+\s*\(.*?\)\s*\{", re.MULTILINE)
#     class_pattern = re.compile(r"^\s*(public|private|protected)?\s*class\s+\w+", re.MULTILINE)



#     lines = file_content.splitlines()
#     buffer = []
#     capture = False
#     current_type = None
#     current_name = ""

#     for line in lines:
#         stripped = line.strip()

#         # Check for class definition
#         if re.match(class_pattern, stripped):
#             if buffer:
#                 code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#                 buffer = []
#             current_type = "class"
#             current_name = stripped
#             capture = True
#             buffer.append(stripped)

#         # Check for function definition
#         elif re.match(function_pattern, stripped):
#             if buffer:
#                 code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#                 buffer = []
#             current_type = "function"
#             current_name = stripped
#             capture = True
#             buffer.append(stripped)

#         elif capture:
#             # Keep adding lines until a blank line or indentation reset
#             if stripped == "":
#                 capture = False
#                 code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})
#                 buffer = []
#             else:
#                 buffer.append(stripped)

#     # Add any leftover buffer
#     if buffer:
#         code_blocks.append({"type": current_type, "name": current_name, "code": "\n".join(buffer)})

#     return code_blocks


# def read_all_code_files(folder_path):
#     """
#     Scans all .py or .java files in the folder and extracts code blocks.
#     Returns a language-agnostic structure for LLM input.
#     """
#     all_blocks = []

#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.endswith((".py", ".java", ".js", ".cpp", ".c", ".ts")):
#                 full_path = os.path.join(root, file)
#                 with open(full_path, "r", encoding="utf-8") as f:
#                     code = f.read()
#                     blocks = extract_code_blocks(code)
#                     all_blocks.append({
#                         "filename": file,
#                         "blocks": blocks
#                     })

#     return all_blocks
