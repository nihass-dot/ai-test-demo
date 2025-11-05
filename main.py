import os
import argparse
from generator import analyze_and_generate

def find_code_files(root_dir="."):
    """
    Finds all relevant code files in the project directory.
    You can add more extensions here if you use other languages!
    """
    code_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            # Ignore the virtual environment and the tests directory
            if "venv" in subdir or "tests" in subdir or ".git" in subdir:
                continue
            # Look for common code file extensions
            if file.endswith((".py", ".js", ".ts", ".java", ".go", ".rs")):
                code_files.append(os.path.join(subdir, file))
    return code_files

def main():
    parser = argparse.ArgumentParser(description="Generate tests for code.")
    # We add a new argument for the scan mode
    parser.add_argument("--scan", action="store_true", help="Scan the entire project for files to test.")
    parser.add_argument("--file", type=str, help="Analyze a single file.")
    args = parser.parse_args()

    files_to_process = []

    if args.scan:
        print(" Project Scan Mode: Finding all code files...")
        files_to_process = find_code_files()
        if not files_to_process:
            print("No code files found to scan.")
            return
        print(f"Found {len(files_to_process)} files to process.")
    elif args.file:
        files_to_process = [args.file]

    if not files_to_process:
        print(" Error: Please provide either --scan or --file.")
        return

    # Loop through all the files we need to process
    for source_file_to_analyze in files_to_process:
        print(f"\nMaster Chef Robot is starting...")
        print(f" Analyzing file: {source_file_to_analyze}")

        try:
            # THIS IS THE FIXED LINE
            with open(source_file_to_analyze, "r", encoding='utf-8') as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: Could not find the file '{source_file_to_analyze}'.")
            continue # Move to the next file
        except UnicodeDecodeError:
            print(f" Error: Could not read file '{source_file_to_analyze}' due to encoding issues. Skipping.")
            continue

        print("Asking the AI to analyze and generate a pln...")
        plan = analyze_and_generate(source_file_to_analyze, source_code)

        if plan and all(k in plan for k in ["test_file_path", "test_code"]):
            test_file_path = plan["test_file_path"]
            test_code = plan["test_code"]
            
            print(f" AI has a plan! It suggests writing a test to: {test_file_path}")
            
            os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
            
            with open(test_file_path, "a", encoding='utf-8') as f:
                f.write("\n\n# --- AI-Generated Test ---\n")
                f.write(test_code)
                f.write("\n# --- End AI-Generated Test ---\n")
            
            print(f" Success! The new test is in '{test_file_path}'")
        else:
            print(" The AI couldn't generate a valid plan for this file.")

if __name__ == "__main__":
    main()