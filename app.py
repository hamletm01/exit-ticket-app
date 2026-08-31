def safe_gemini_call(prompt, system_instruction=None, response_json=False):
    clean_prompt = sanitize_text(prompt)
    if not clean_prompt:
        raise ValueError("Cannot process empty prompt payload.")

    # Using verified model endpoints for the google-genai SDK
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
    
    config_args = {"temperature": 0.2}
    
    if system_instruction:
        config_args["system_instruction"] = sanitize_text(system_instruction)
    if response_json:
        config_args["response_mime_type"] = "application/json"
        
    config = types.GenerateContentConfig(**config_args)
    
    last_err = None
    for model_name in models_to_try:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=clean_prompt,
                config=config
            )
            return res.text
        except Exception as e:
            last_err = e
            continue
            
    raise RuntimeError(f"API Request failed: {last_err}")
