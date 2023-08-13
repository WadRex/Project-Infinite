# Import Required Libraries
import transformers
import os
import json

# Define the Directory for Input Files
input_dir = r"..\1. Prepare Dataset\Files (.txt)"

# Define the Directory for Output Files
output_dir = r".\Dataset"

# Read Model's Sequence Length
max_length = transformers.AutoConfig.from_pretrained(r".\Model").max_position_embeddings
        
# Initialize Tokenizer 
tokenizer = transformers.AutoTokenizer.from_pretrained(r".\Model")

# Initialize List for Storing Dataset
dataset = []

# Initialize Variable to Keep Count of Tokens Written
total_tokens_count = 0

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
        # If Current File has '.txt' Extension
        if file.endswith('.txt'):            
            # Construct the Full Path for the Current File
            file_path = os.path.join(root, file)

            # Initialize Variable for Processing the File
            temp_input = ""

            # Read the Contents of the Current File
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()

                # Split the Content into Lines
                lines = content.split("\n")

                # Loop Over All Lines
                for index, line in enumerate(lines):
                    # Remove Leading and Trailing Whitespace from the Line
                    line_stripped = line.strip()

                    # Skip Empty Line
                    if len(line_stripped) == 0:
                        continue
                    
                    # Tokenize the Stripped Line
                    line_tokenized = tokenizer.encode(line_stripped)

                    # Check if the Current Line is Not the Last Line in the File
                    if index < len(lines) - 1:
                        # Tokenize the Temporary Input Variable
                        temp_input_tokens = tokenizer.encode(temp_input)

                        # Tokenize the Stripped Line with a Newline
                        current_line_tokens = tokenizer.encode(line_stripped + "\n")

                        # Tokenize the Next Stripped Line
                        next_line_tokens = tokenizer.encode(lines[index + 1].strip())

                        # Check If Total Tokens of Temporary Input, Current Line, and Next Line are Within Maximum Token Length
                        if len(temp_input_tokens) + len(current_line_tokens) + len(next_line_tokens) <= max_length:
                            temp_input += line_stripped + "\n"
                            
                            # Update Token Count
                            total_tokens_count += len(current_line_tokens)
                       
                        # Token Limit Exceeded
                        elif temp_input != "":
                            dataset.append({
                                "input": temp_input,
                                "output": line_stripped
                            })
                        
                            # Update Token Count
                            total_tokens_count += len(line_tokenized)

                            # Reset Temporary Input
                            temp_input = ""

                    # Handle Last Line in the File
                    elif temp_input != "":
                        dataset.append({
                            "input": temp_input,
                            "output": line_stripped
                        })

                        # Reset Temporary Input
                        temp_input = ""

    # Check if the Dataset Variable Contains Data
    if len(dataset) > 0:    
        # Create Dataset Directory if Required
        os.makedirs(output_dir, exist_ok=True)

        # Write the Content to the Output File as JSON
        with open(os.path.join(output_dir, "Dataset.json"), 'w', encoding="utf-8") as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

    # Display the Total Number of Pairs Created and the Total Number of Tokens Processed
    print('|----------------------------------|')
    print(f"| Sequence Length: {max_length}".ljust(35) + '|')
    print('|----------------------------------|')
    print(f"| {len(dataset)} pair{' was' if len(dataset) == 1 else 's were'} created!".ljust(35) + '|')
    print(f"| {total_tokens_count} token{' was' if total_tokens_count == 1 else 's were'} processed!".ljust(35) + '|')
    print("|----------------------------------|")