import re
import os
import sys

def split_chapters(text):
    """
    Splits the full text into chapters based on headers that match a pattern
    like "chapter1", "chapter2", etc. The regex is case-insensitive and uses
    a lookahead to capture text until the next chapter heading or the end of file.
    """
    # Regular expression:
    # (?=chapter\s?\d+|$) is a lookahead that stops the capture when the next chapter header starts
    # or we reach the end of the text.
    chapter_regex = re.compile(r"(chapter\s?\d+.*?)(?=chapter\s?\d+|$)", re.DOTALL | re.IGNORECASE)
    return chapter_regex.findall(text)

def main():
    if len(sys.argv) < 2:
        print("Usage: python split_chapters.py <input_text_file> [output_directory]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "chapters_output"

    # Create the output directory if it doesn't already exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Output directory '{output_dir}' created.")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    # Split the content into chapters
    chapters = split_chapters(content)
    if not chapters:
        print("No chapters found in the file. Please check the chapter heading format.")
        sys.exit(1)

    print(f"Found {len(chapters)} chapter(s).")

    for index, chapter in enumerate(chapters, start=1):
        # Grab the first line of the chapter to extract the chapter number.
        header_line = chapter.splitlines()[0]
        # Use a regex to extract the chapter number from a header like "chapter1"
        number_match = re.search(r"chapter\s?(\d+)", header_line, re.IGNORECASE)
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
