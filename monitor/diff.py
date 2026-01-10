import difflib

def get_new_content(old_text: str, new_text: str) -> str:
    """
    Compares old and new text and returns the *added* content.
    Using a set-based approach for lines/paragraphs to avoid noise.
    """
    if not old_text:
        return new_text
    
    old_lines = set(old_text.splitlines())
    new_lines = set(new_text.splitlines())
    
    # Calculate added lines
    added_lines = new_lines - old_lines
    
    # Sort them by their appearance in the new_text to maintain some flow
    # (Checking index in new_text list)
    new_text_lines = new_text.splitlines()
    ordered_added = []
    
    for line in new_text_lines:
        if line in added_lines and len(line) > 20: # Filter out short noise
            ordered_added.append(line)
            
    return "\n".join(ordered_added)
