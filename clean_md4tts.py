import re

def clean_markdown_for_tts_v1(text: str) -> str:
    """Translates markdown syntax into spoken context or SSML tags."""
    
    # 1. Translate Headers dynamically
    def parse_header(match):
        header_count = len(match.group(1))
        # Map the count to spoken words
        levels = {1: "Header one", 2: "Header two", 3: "Header three", 4: "Header four"}
        spoken_level = levels.get(header_count, f"Header {header_count}")
        
        # Example: "### Slit" -> "Header three: Slit."
        return f"{spoken_level}: {match.group(2)}."
        
    text = re.sub(r'^(#+)\s+(.*)$', parse_header, text, flags=re.MULTILINE)
    
    # 2. Translate Bold text (**word**)
    # We add commas around it to force the TTS engine to take a micro-pause.
    text = re.sub(r'\*\*(.*?)\*\*', r'emphasized, \1,', text)
    
    # 3. Strip out lists and remaining noise 
    text = re.sub(r'`+', '', text)
    text = re.sub(r'^\s*[-+]\s+', 'Point: ', text, flags=re.MULTILINE)
    
    return text.strip()



def clean_markdown_for_tts(text: str) -> str:
    """Translates markdown syntax into spoken context or SSML tags."""
    
    # 1. Translate Headers dynamically
    def parse_header(match):
        header_count = len(match.group(1))
        # Map the count to spoken words
        levels = {1: "Header one", 2: "Header two", 3: "Header three", 4: "Header four"}
        spoken_level = levels.get(header_count, f"Header {header_count}")
        
        # Example: "### Slit" -> "Header three: Slit."
        return f"{spoken_level}: {match.group(2)}."
        
    text = re.sub(r'^(#+)\s+(.*)$', parse_header, text, flags=re.MULTILINE)
    
    # 2. Translate Bold text (**word**)
    # We add commas around it to force the TTS engine to take a micro-pause.
    text = re.sub(r'\*\*(.*?)\*\*', r'emphasized, \1,', text)
    
    # 3. Strip out lists and remaining noise 
    text = re.sub(r'`+', '', text)
    text = re.sub(r'^\s*[-+]\s+', 'Point: ', text, flags=re.MULTILINE)
    
    return text.strip()
