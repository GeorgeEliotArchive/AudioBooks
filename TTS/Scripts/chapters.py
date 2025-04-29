import os
import sys
import re
import uuid
import shutil
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

# Configure your Azure Speech credentials here.
# AZURE_SPEECH_KEY = "Key"
# AZURE_SPEECH_REGION = "Region"

# Maximum number of characters per API call (adjust if needed)
MAX_CHARS = 20000

def split_chapters(text):
    """
    Splits the full text into chapters based on headers that match a pattern
    like "chapter I", "chapter II", etc. The regex is case-insensitive and uses
    a lookahead to capture text until the next chapter header or the end of the file.
    """
    # Match chapter headers like "chapter I" or "chapter ii"
    chapter_regex = re.compile(r"(chapter\s+[ivxlcdm]+.*?)(?=chapter\s+[ivxlcdm]+|$)", re.DOTALL | re.IGNORECASE)
    return chapter_regex.findall(text)

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_chapters.py <input_text_file> [output_directory]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "chapters_output"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    chapters = split_chapters(content)
    if not chapters:
        print("No chapters found in the file. Please check the chapter heading format.")
        sys.exit(1)
    
    print(f"Found {len(chapters)} chapter(s).")
    
    for index, chapter in enumerate(chapters, start=1):
        header_line = chapter.splitlines()[0]
        # Extract the Roman numeral
        number_match = re.search(r"chapter\s+([ivxlcdm]+)", header_line, re.IGNORECASE)
        chapter_number = number_match.group(1) if number_match else f"{index}"
        
        output_filename = os.path.join(output_dir, f"Chapter_{chapter_number}.txt")
        try:
            with open(output_filename, "w", encoding="utf-8") as out_f:
                out_f.write(chapter.strip())
            print(f"Wrote chapter {chapter_number} to '{output_filename}'")
        except Exception as e:
            print(f"Failed to write chapter {chapter_number}: {e}")

if __name__ == "__main__":
    main()