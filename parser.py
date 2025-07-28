import os
import re

# ==============================================================================
#  LANGUAGE-SPECIFIC PARSERS
# ==============================================================================

def _extract_python_blocks(file_content):
    """
    Extracts only top-level functions and classes from Python code,
    preventing methods inside classes from being duplicated.
    """
    blocks = []
    lines = file_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # We only care about blocks defined at the top level (indentation 0)
        if (stripped.startswith("def ") or stripped.startswith("class ")) and (len(line) - len(line.lstrip(' ')) == 0):
            block_type = "function" if "def" in stripped else "class"
            
            match = re.search(r'(?:class|def)\s+([_a-zA-Z0-9]+)', stripped)
            block_name = match.group(1) if match else "Unnamed"

            block_code_lines = [line]
            
            # Find the end of this top-level block to know how many lines to skip
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # A new top-level block means the current one has ended
                if next_line.strip() != "" and (len(next_line) - len(next_line.lstrip(' ')) == 0):
                    break
                
                block_code_lines.append(next_line)
                j += 1
            
            blocks.append({
                "type": block_type,
                "name": block_name,
                "code": "\n".join(block_code_lines).rstrip()
            })
            
            # Crucially, move the outer loop's cursor past this entire block
            i = j - 1
        
        i += 1
            
    return blocks


def _extract_c_like_blocks(file_content):
    """
    Extracts functions and classes from C-like languages (Java, C++, JS)
    using brace counting for accurate block detection.
    """
    blocks = []
    lines = file_content.split('\n')
    
    # This pattern looks for common keywords at the start of a block
    # It's flexible enough for class definitions, constructors, and functions
    block_start_pattern = re.compile(
        r'^\s*(?:public\s+|private\s+|protected\s+)?'
        r'(?:static\s+|final\s+)?'
        r'(class|void|int|double|string|bool|constructor|function|BankAccount)\s+'
        r'([_a-zA-Z0-9]+)\s*\(?.*\s*\{'
    )

    i = 0
    while i < len(lines):
        line = lines[i]
        match = block_start_pattern.search(line)
        
        if match:
            keyword = match.group(1)
            block_type = "class" if keyword == "class" else "function"
            block_name = match.group(2)
            
            block_code_lines = [line]
            brace_level = line.count('{') - line.count('}')
            
            # If the opening line also closes the brace, handle it
            if brace_level == 0 and '{' in line:
                 blocks.append({
                    "type": block_type,
                    "name": block_name,
                    "code": "\n".join(block_code_lines)
                })
                 i += 1
                 continue

            if brace_level > 0:
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    block_code_lines.append(next_line)
                    brace_level += next_line.count('{')
                    brace_level -= next_line.count('}')
                    if brace_level == 0:
                        i = j # Move outer loop cursor
                        break
            
            blocks.append({
                "type": block_type,
                "name": block_name,
                "code": "\n".join(block_code_lines)
            })

        i += 1
        
    return blocks

# ==============================================================================
#  MAIN DISPATCHER
# ==============================================================================

def read_all_code_files(folder_path):
    """
    Reads all supported files from a directory, determines the language,
    and dispatches to the correct parser.
    """
    all_files_data = []
    print(f"Scanning directory: {folder_path}")

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            file_extension = filename.split('.')[-1]
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Could not read file {filename}: {e}")
                continue

            blocks = []
            if file_extension == 'py':
                blocks = _extract_python_blocks(content)
            elif file_extension in ['java', 'cpp', 'js']:
                blocks = _extract_c_like_blocks(content)
            else:
                continue
            
            print(f"  Parsed file: {filepath} (found {len(blocks)} blocks)")
            all_files_data.append({
                "filename": filename,
                "filepath": filepath,
                "blocks": blocks
            })

    print(f"Finished scanning. Total files processed: {len(all_files_data)}")
    return all_files_data


