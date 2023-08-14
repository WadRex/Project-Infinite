# Import Required Libraries
import os
import requests
import tqdm
import huggingface_hub

# Define Function to Download a Specific File
def download_file(file_name):
    # Create Model Directory if Required
    os.makedirs(r".\Model", exist_ok=True)

    # Send Request to Fetch File from Huggingface Repository
    response = requests.get(f"https://huggingface.co/{repo_name}/resolve/main/{file_name}", stream=True)

    # Check for Errors in the Response
    response.raise_for_status()
    
    # Extract Total File Size from Headers
    total_size = int(response.headers.get('content-length', 0))
    
    # Display a Progress Bar for the Download Process
    with tqdm.tqdm(desc=file_name, total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
        # Create or Overwrite the File in Write Mode to Save the Retrieved Data
        with open(os.path.join("./Model", file_name), 'wb') as f:
            # Loop Through the Downloaded Data in Chunks and Write to the File
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

                # Adjust the Progress Bar based on the Size of the Saved Chunk
                bar.update(len(chunk))

# Define the Target Repository Name
repo_name = "huggyllama/llama-7b"

# Initialize Variable for Model Type and Tokenizer Method
model_type = None
tokenizer_method = None

# Initialize Variable for Storing Repo File Names 
file_names = huggingface_hub.list_repo_files(repo_name)

# Loop Over All File Names
for file_name in file_names:
    # Determine Tokenizer Method
    if file_name == "tokenizer.json":
        tokenizer_method = "regular"
    elif file_name == "tokenizer.model" and tokenizer_method != "regular":
        tokenizer_method = "model"
    elif (file_name == "merges.txt" or file_name == "vocab.json") and (tokenizer_method != "regular" and tokenizer_method != "model"):
        tokenizer_method = "fallback"

    # Determine Model Type Based on File Extension
    if file_name.endswith(".safetensors"):
        model_type = "safetensors"
    elif file_name.endswith(".bin") and model_type != "safetensors":
        model_type = "bin"

# Loop Over All File Names
for file_name in file_names:
    # Download Model's Config File
    if file_name == "config.json":
        download_file(file_name)

    # Download Model's Tokenizer Depending on Tokenizer Method
    if file_name == "tokenizer.json" and tokenizer_method == "regular":
        download_file(file_name)
    if file_name == "tokenizer.model" and tokenizer_method == "model":
        download_file(file_name)
    elif (file_name == "merges.txt" or file_name == "vocab.json") and tokenizer_method == "fallback":
        download_file(file_name)

    # Download Specific Model Files Depending on Model Type
    if (file_name.endswith("safetensors.index.json") or file_name.endswith(".safetensors")) and model_type == "safetensors":
        download_file(file_name)
    elif (file_name.endswith("bin.index.json") or file_name.endswith(".bin")) and model_type == "bin":
        download_file(file_name)