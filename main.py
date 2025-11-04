# main.py

# These are the tools our Project Manager needs to do its job.
import os          # To work with file paths and folders
import argparse    # To get instructions from the command line (like --file "...")
from generator import analyze_and_generate # To talk to our "AI Brain"

def main():
    """
    This is the main function where everything starts.
    """
    # 1. Get instructions from the user.
    # We expect the user to tell us which file to work on.
    parser = argparse.ArgumentParser(description="Generate tests for a given file.")
    parser.add_argument("--file", type=str, required=True, help="The source file to analyze.")
    args = parser.parse_args()

    source_file_to_analyze = args.file

    print(f"Robot is starting...")
    print(f"Analyzing file: {source_file_to_analyze}")

    # 2. Read the code from the file we were given.
    try:
        with open(source_file_to_analyze, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find the file '{source_file_to_analyze}'.")
        return

    # 3. Ask the "AI Brain" for a complete plan.
    print("Asking the AI to analyze and generate a plan...")
    plan = analyze_and_generate(source_file_to_analyze, source_code)

    # 4. If the AI gave us a good plan, follow it!
    if plan and all(k in plan for k in ["test_file_path", "test_code"]):
        test_file_path = plan["test_file_path"]
        test_code = plan["test_code"]
        
        print(f"AI has a plan! It suggests writing a test to: {test_file_path}")
        
        # Create the folder for the test if it doesn't exist yet.
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        
        # Open the test file and add the new test code to the end.
        with open(test_file_path, "a") as f:
            f.write("\n\n# --- AI-Generated Test ---\n")
            f.write(test_code)
            f.write("\n# --- End AI-Generated Test ---\n")
        
        print(f"🎉 Success! The new test is in '{test_file_path}'")
    else:
        # If the AI couldn't make a plan, tell us there was a problem.
        print("The AI couldn't generate a valid plan. Please check the logs.")

# This line makes sure the main() function runs when you execute the script.
if __name__ == "__main__":
    main()