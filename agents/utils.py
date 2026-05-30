def extract_json(text: str) -> list:
    import json, re
    # strip markdown fences
    text = re.sub(r'```json\s*', '', text)  
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    try:
        result = json.loads(text)
        return result if isinstance(result, list) else [result]
    except json.JSONDecodeError:
        # try to extract first [ ... ] or { ... } block
        match = re.search(r'(\[.*?\]|\{.*?\})', text, re.DOTALL)
        if match:
            try:
                # Basic cleanup for common issues like trailing commas before closing brackets
                # Note: A more robust parser would be better, but this regex handles many cases
                clean_json = re.sub(r',\s*([\]}])', r'\1', match.group())
                result = json.loads(clean_json)
                return result if isinstance(result, list) else [result]
            except:
                pass
    return []
