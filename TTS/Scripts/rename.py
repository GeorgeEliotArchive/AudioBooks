import os

# Folder where the MP3 files are located (use "." for current directory)
folder_path = "."

# Loop through all files in the directory for compressed mp3 files 
for filename in os.listdir(folder_path):
    if filename.endswith(".mp3") and "(compressed)" in filename:
      
        new_name = filename.replace(" (compressed)", "")
        # Get full paths
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)
        # Rename file
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} → {new_name}")