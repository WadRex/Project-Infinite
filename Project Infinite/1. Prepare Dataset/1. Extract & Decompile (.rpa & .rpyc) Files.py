# Import Required Libraries
import os
import subprocess

# Define the Directory for Input Files
input_dir = ".\Files (.rpa & .rpyc)"

# Define the Directory for Output Files
output_dir = ".\Files (.rpy)"

# Check if Input Directory Exists
if not os.path.exists(input_dir):
    print(f"Directory '{input_dir}' does not exist!")
    exit()

# Check if Input Directory is Empty
if not any([f for f in os.listdir(input_dir) if not f.startswith(".")]):
    print(f"Directory '{input_dir}' is empty!")
    exit()

# Walk Through All Files and Subdirectories in the Input Directory
for root, dirs, files in os.walk(input_dir):
    # Loop Over All Files in Current Directory
    for file in files:
        # Construct the Full Path for the Current File
        file_path = os.path.join(root, file)

        # If Current File has '.rpa' Extension
        if file.endswith('.rpa'):
            # Create Output Folder if Required
            os.makedirs(file_path.replace(input_dir, output_dir)[:-len(file)], exist_ok=True)

            # Execute 'unrpa' Command to Extract Contents of '.rpa' File to the Output Directory
            subprocess.run(['unrpa', '-mp', file_path.replace(input_dir, output_dir)[:-len(file)], file_path])
        
        # If Current File has '.rpyc' Extension
        elif file.endswith('.rpyc'):
            # Execute 'unrpyc' Command to Decompile '.rpyc' File
            subprocess.run(['python', '-m', 'unrpyc', file_path])

            # Create Output Folder if Required
            os.makedirs(file_path.replace(input_dir, output_dir)[:-len(file)], exist_ok=True)

            # Move '.rpy' in Output Folder
            os.rename(file_path[:-1], file_path.replace(input_dir, output_dir)[:-1])

# Walk Through All Files and Subdirectories in the Output Directory
for root, dirs, files in os.walk(output_dir):    
    # Loop Over All Files in Current Directory
    for file in files:       
        # If Current File has '.rpyc' Extension
        if file.endswith('.rpyc'):            
            # Construct the Full Path for the '.rpyc' File
            rpyc_path = os.path.join(root, file)
            
            # Execute 'unrpyc' Command to Decompile '.rpyc' File
            subprocess.run(['python', '-m', 'unrpyc', rpyc_path])
            
            # Delete the '.rpyc' File After Decompiling
            os.remove(rpyc_path)