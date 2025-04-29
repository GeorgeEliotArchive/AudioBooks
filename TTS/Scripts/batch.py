import os
import sys
import uuid
import shutil
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment

# Configure your Azure Speech credentials here.
#AZURE_SPEECH_KEY = "key"
#AZURE_SPEECH_REGION = "region"

# Maximum number of characters per synthesis call.
MAX_CHARS = 20000

def chunk_text(text, max_chars):
    """
    Splits the given text into chunks of up to max_chars characters.
    (A simple splitter that can be extended to preserve sentence boundaries.)
    """
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def synthesize_text_to_mp3(text, output_filename, speech_config):
    """
    Uses the Azure Speech SDK to convert text to speech and writes
    the audio to output_filename.
    Logs the file size after synthesis.
    Returns True on success, False on error.
    """
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_filename)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = synthesizer.speak_text_async(text).get()
    
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"Generated file size for {output_filename}: {file_size} bytes")
        return True
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.error_details:
            print(f"Error details: {cancellation_details.error_details}")
        return False
    else:
        print(f"Unexpected synthesis result: {result.reason}")
        return False

def combine_mp3_files(file_list, output_filename):
    """
    Combines all MP3 files in file_list into one MP3 file.
    """
    combined = AudioSegment.empty()
    for f in file_list:
        try:
            segment = AudioSegment.from_mp3(f)
            combined += segment
        except Exception as e:
            print(f"Error processing file {f}: {e}")
    combined.export(output_filename, format="mp3")
    print(f"Combined audio saved to {output_filename}")

def process_text_file(input_filepath, output_filepath, speech_config):
    """
    Processes a single text file:
      - Reads the file,
      - Splits it into chunks,
      - Synthesizes each chunk (leaving temporary chunks on disk),
      - Combines them into a final output MP3.
    """
    try:
        with open(input_filepath, "r", encoding="utf-8") as f:
            full_text = f.read()
    except Exception as e:
        print(f"Could not open or read the file {input_filepath}: {e}")
        return

    # Create a unique temporary folder for the chunk files
    temp_dir = f"temp_audio_{os.path.splitext(os.path.basename(input_filepath))[0]}_{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Temporary folder created for '{input_filepath}': {temp_dir}")

    # Chunk the text.
    text_chunks = chunk_text(full_text, MAX_CHARS)
    print(f"Text split into {len(text_chunks)} chunks.")

    generated_files = []
    for idx, chunk in enumerate(text_chunks, start=1):
        chunk_filename = os.path.join(temp_dir, f"chunk_{idx}.mp3")
        print(f"Synthesizing chunk {idx} to {chunk_filename}...")
        success = synthesize_text_to_mp3(chunk, chunk_filename, speech_config)
        if not success:
            print(f"Failed to synthesize audio for chunk {idx} in '{input_filepath}'. Skipping file.")
            return
        generated_files.append(chunk_filename)

    # Combine the chunks into one MP3 file.
    combine_mp3_files(generated_files, output_filepath)

    # Note: the temporary folder is NOT deleted so you can review the chunks.
    print(f"Processing complete for '{input_filepath}'. Temporary files are kept at: {temp_dir}\n")

def process_all_text_files(input_folder, output_folder, speech_config):
    """
    Loops through all .txt files in input_folder, processes each,
    and outputs MP3 files to output_folder, keeping the base file names.
    """
    if not os.path.isdir(input_folder):
        print(f"Input folder '{input_folder}' does not exist or is not a directory.")
        sys.exit(1)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)
        print(f"Output folder '{output_folder}' created.")

    # Process every .txt file in the folder.
    txt_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.txt')]
    if not txt_files:
        print("No text files found in the input folder.")
        return

    for filename in txt_files:
        input_filepath = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]
        output_filepath = os.path.join(output_folder, f"{base_name}_output.mp3")
        print(f"---\nProcessing file: {input_filepath}\nOutput file will be: {output_filepath}")
        process_text_file(input_filepath, output_filepath, speech_config)

def main():
    if len(sys.argv) != 3:
        print("Usage: python batch.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Create the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    # Set the voice to en-GB Libby for UK English
    speech_config.speech_synthesis_voice_name = "en-GB-LibbyNeural"

    process_all_text_files(input_folder, output_folder, speech_config)

if __name__ == "__main__":
    main()
