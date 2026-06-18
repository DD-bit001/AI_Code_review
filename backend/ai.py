from openai import AsyncOpenAI
import json

async def perform_code_review(provider_config: dict, files: list, review_mode: str) -> dict:
    client = AsyncOpenAI(
        base_url=provider_config["base_url"],
        api_key=provider_config.get("api_key") or "dummy",
    )
    
    system_prompt = f"""You are an expert AI Code Reviewer. 
You are performing a '{review_mode}' review.
Analyze the provided code and return a JSON object with the following structure:
{{
  "summary": "High-level overview of findings",
  "issues": [
    {{"severity": "Critical|High|Medium|Low", "description": "Issue description", "file_path": "path", "line_number": 0}}
  ],
  "recommendations": [
    "string"
  ]
}}
Only return the valid JSON, no markdown formatting.
"""

    code_context = ""
    for f in files:
        code_context += f"\\n--- {f.file_path} ---\\n{f.content}\\n"
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please review the following code:\\n{code_context}"}
    ]
    
    try:
        response = await client.chat.completions.create(
            model=provider_config["model_name"],
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"} if "openai" in provider_config["base_url"] else None,
        )
        content = response.choices[0].message.content
        
        # Simple cleanup if the model outputs markdown anyway
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
            
        return json.loads(content)
    except Exception as e:
        return {
            "summary": f"Failed to perform review: {str(e)}",
            "issues": [],
            "recommendations": []
        }

async def generate_architecture_analysis(provider_config: dict, files: list) -> str:
    client = AsyncOpenAI(
        base_url=provider_config["base_url"],
        api_key=provider_config.get("api_key") or "dummy",
    )
    
    system_prompt = "You are a Software Architect. Analyze the provided codebase and generate a comprehensive architecture summary in Markdown format."
    
    file_list = "\\n".join([f.file_path for f in files])
    code_context = ""
    # To avoid context limits, we might just pass the tree and a few core files, but for this assignment, we pass all text files.
    for f in files:
        code_context += f"\\n--- {f.file_path} ---\\n{f.content}\\n"
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the project file structure and code:\\n{code_context}\\n\\nPlease generate an Architecture Analysis."}
    ]
    
    try:
        response = await client.chat.completions.create(
            model=provider_config["model_name"],
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate analysis: {str(e)}"

async def generate_documentation(provider_config: dict, files: list) -> str:
    client = AsyncOpenAI(
        base_url=provider_config["base_url"],
        api_key=provider_config.get("api_key") or "dummy",
    )
    
    system_prompt = "You are a Technical Writer. Analyze the provided codebase and generate a comprehensive README.md including Setup Instructions, Features, Environment Variables, and Architecture Overview."
    
    code_context = ""
    for f in files:
        code_context += f"\\n--- {f.file_path} ---\\n{f.content}\\n"
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the code:\\n{code_context}\\n\\nPlease generate the Documentation."}
    ]
    
    try:
        response = await client.chat.completions.create(
            model=provider_config["model_name"],
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate documentation: {str(e)}"

async def chat_with_code(provider_config: dict, files: list, history: list, new_message: str) -> str:
    client = AsyncOpenAI(
        base_url=provider_config["base_url"],
        api_key=provider_config.get("api_key") or "dummy",
    )
    
    code_context = ""
    for f in files:
        code_context += f"\\n--- {f.file_path} ---\\n{f.content}\\n"
        
    system_prompt = f"You are an AI assistant helping a developer understand their code. Use the provided codebase as context to answer their questions.\\n\\nCode Context:\\n{code_context}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": new_message})
    
    try:
        response = await client.chat.completions.create(
            model=provider_config["model_name"],
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"
