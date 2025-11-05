import google.generativeai as genai
import os
import json
import dotenv
dotenv.load_dotenv()    
import ast


# --- Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_and_generate(source_file_path, source_code):
    """
    Asks the AI to analyze the code and return a complete plan in JSON format.
    """
    
    # This is the prompt for the AI. It starts with f"""...
    prompt = f"""
You are an expert software engineer specializing in automated testing for all programming languages.

Analyze the provided source code and generate a comprehensive, context-aware unit test.

Return ONLY a single valid JSON object.

JSON Format:
{{
"language": "<identified_language>",
"framework": "<identified_framework>",
"test_file_path": "<conventional_test_file_path>",
"test_code": "<the_full_generated_test_code_as_a_string>"
}}

Example:
{{
"language": "python",
"framework": "pytest",
"test_file_path": "tests/test_dataprocessor.py",
"test_code": "def test_calculate_average_with_empty_list():\\n    with pytest.raises(ZeroDivisionError):\\n        calculate_average([])"
}}

Source File Path: `{source_file_path}`
Source Code:
```{source_file_path.split('.')[-1]}
{source_code}
"""
     # The 'try' block is now OUTSIDE the string and properly indented inside the function.
        # The 'try' block is now OUTSIDE the string and properly indented inside the function.
    # It has 4 spaces at the beginning, just like the 'prompt' line above it.
    try:
        # These lines are inside the 'try' block, so they have 8 spaces.
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # If AI wraps response in ```json ... ```
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()

        analysis_result = json.loads(response_text)
        test_code = analysis_result.get("test_code", "")
        if test_code:
            try:
                ast.parse(test_code)
                print("✅ AI-generated code is syntactically valid.")
            except SyntaxError as e:
                print(f"❌ AI generated invalid Python code: {e}")
                print("Discarding this test to prevent errors.")
                return None 
        return analysis_result

    # These 'except' blocks are also inside the function, so they have 4 spaces.
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from AI response.")
        print("Raw response:", response.text)
        return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None