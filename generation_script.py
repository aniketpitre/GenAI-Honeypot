import os
import sys
import json
import argparse
from pathlib import Path
import google.generativeai as genai


def main():
    parser = argparse.ArgumentParser(description="Generative AI Honeypot File Creator")
    parser.add_argument('--persona', required=True, help='Path to persona_config.json')
    parser.add_argument('--output', required=True, help='Root directory to write generated files')
    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    genai.configure(api_key=api_key)

    with open(args.persona, 'r') as f:
        config = json.load(f)

    files = config.get('files', [])
    if not files:
        print("No files specified in persona config.")
        sys.exit(1)

    model = genai.GenerativeModel('models/gemini-2.0-flash')

    for file_obj in files:
        rel_path = file_obj['path']
        prompt = file_obj['prompt']
        # Write to /generated_files instead of system locations
        out_path = Path(args.output) / rel_path.lstrip('/')
        gen_root = Path(args.output)
        if str(gen_root) == '/':
            gen_root = Path('/generated_files')
            out_path = gen_root / rel_path.lstrip('/')
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"[GEN] Generating {rel_path} -> {out_path}")
            print(f"[GEN] Prompt: {prompt}")
            response = model.generate_content(prompt)
            print(f"[GEN] API Response: {response}")
            content = response.text if hasattr(response, 'text') else str(response)
            with open(out_path, 'w') as outf:
                outf.write(content)
            print(f"[GEN] Written: {out_path}")
            if out_path.exists():
                print(f"[GEN] File exists: {out_path}")
            else:
                print(f"[ERROR] File {out_path} was NOT created!")
        except Exception as e:
            print(f"[ERROR] Exception generating {rel_path}: {e}")

if __name__ == "__main__":
    main()
