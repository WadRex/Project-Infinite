# Import Required Libraries
import requests
import os
import tqdm

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

# Define the Target Repository Name
content = requests.get(f"https://huggingface.co/{repo_name}/tree/main/").text

# Initialize List for Storing Found File Names 
file_names = []

# Initialize Variable for Model Type and Tokenizer Method
model_type = None
tokenizer_method = None

# Loop Over All Lines
for line in content.split("\n"):
    # Identify Lines with File Links
    if f'/{repo_name}/resolve/main/' in line:
        # Determine Start and End of File Link
        start = line.find(f'/{repo_name}/resolve/main/')
        end = line.find('"', start)

        # Extract the File Name from Link
        file_name = line[start:end].rsplit('/', 1)[-1]

        # Append the File Name to List
        file_names.append(file_name)

        # Determine Tokenizer Method
        if file_name == "tokenizer.json":
            tokenizer_method = "regular"
        elif (file_name == "merges.txt" or file_name == "vocab.json") and tokenizer_method == None:
            tokenizer_method = "fallback"

        # Determine Model Type Based on File Extension
        if file_name.endswith(".safetensors"):
            model_type = "safetensors"
        elif file_name.endswith(".bin") and model_type == None:
            model_type = "bin"

# Process Each File Name Retrieved
for file_name in file_names:
    # Download Model's Config File
    if file_name == "config.json":
        download_file(file_name)

    # Download Model's Tokenizer Depending on Tokenizer Method
    if file_name == "tokenizer.json" and tokenizer_method == "regular":
        download_file(file_name)
    elif (file_name == "merges.txt" or file_name == "vocab.json") and tokenizer_method == "fallback":
        download_file(file_name)

    # Download Specific Model Files Depending on Model Type
    if (file_name.endswith("safetensors.index.json") or file_name.endswith(".safetensors")) and model_type == "safetensors":
        download_file(file_name)
    elif (file_name.endswith("bin.index.json") or file_name.endswith(".bin")) and model_type == "bin":
        download_file(file_name)