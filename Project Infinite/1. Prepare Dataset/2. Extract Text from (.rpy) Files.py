# Import Required Libraries
import os
import re

# Define the Directory for Input Files
input_dir = r".\Files (.rpy)"

# Define the Directory for Output Files
output_dir = r".\Files (.txt)"

# Define the Minimum Number of Lines for Saving Content
threshold = 10

# Initialize the Dictionary to Store Character Counts
character_counts = {}

# Initialize Variable to Keep Count of Lines Found and Lines Written
lines_found = 0
lines_written = 0

# Initialize Variable to Keep Temporary and Previous Character Name
temp_character_name = None
prev_character_name = None

# Define Function to Save Content of a Label Block
def save_contents():
    # Access Global Variables
    global label_block_contents, lines_found, lines_written

    # Check if Label was Found
    if label_name:
        # Construct the File Name for the Current Label
        filename = os.path.join(output_dir, label_name + '.txt')

        # Create Output Folder if Required
        os.makedirs(output_dir, exist_ok=True)

        # Increment the Count of Lines Found
        lines_found += len(label_block_contents)
                                
        # Check if the Content of Current Label Exceeds Threshold
        if len(label_block_contents) > threshold:
            # Increment the Count of Lines Written
            lines_written += len(label_block_contents)

            # Write the Content to the Output File
            with open(filename, 'w', encoding="utf-8") as f:
                f.write("\n".join(label_block_contents))

        # Reset the Label Block Contents
        label_block_contents = []  

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
        # If Current File has '.rpy' Extension
        if file.endswith('.rpy'):            
            # Construct the Full Path for the Current File
            file_path = os.path.join(root, file)

            # Initialize Variables for Processing the File
            label_block_found = False
            label_indentation = None
            label_name = None
            unwanted_block_found = False
            unwanted_block_indentation = None
            label_block_contents = []

            # Variables for multi-line quote management
            quote_open = False   # Variable to check if a quote is open
            temp_quote = ""      # Temporary storage for ongoing multi-line quote

            # Read the Contents of the Current File
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()

                # Split the Content into Lines
                lines = content.split("\n")

                # Loop Over All Lines
                for line in lines:
                    # Remove Leading and Trailing Whitespace from the Line
                    line_stripped = line.strip()

                    # Determine Current Indentation Level
                    current_indentation = len(line) - len(line_stripped)

                    # Skip Empty Line
                    if len(line_stripped) == 0:
                        continue

                    # Save Contents If Another Label is Found and Not Inside a Quote
                    if line_stripped.startswith("label") and label_block_found and not quote_open:
                        save_contents()

                    # If inside a multi-line quote and the line starts with "label", add it to the accumulated quote
                    if quote_open and line_stripped.startswith("label"):
                        temp_quote += "\n" + line_stripped
                        continue

                    # Detect Start of a Label Block
                    if line_stripped.startswith("label"):
                        # Extract Label Name by Removing 'label' Keyword and Trailing ':'
                        label_name = line_stripped.replace("label", "", 1).strip().rstrip(":")

                        # Mark Label Block as Found and Reset Indentation
                        label_block_found = True
                        label_indentation = None

                        # Move to Next Iteration
                        continue

                    # Handle Indentation within the Label Block
                    if label_block_found is True and label_indentation is None:
                        label_indentation = current_indentation

                    # Detect End of a Label Block and Not Inside a Quote
                    if label_block_found is True and label_indentation > current_indentation and not quote_open:
                        save_contents()
                        label_block_found = False
                        label_indentation = None
                        label_name = None

                    # If Inside an Open Quote (i.e., a Multi-line Quote)
                    if quote_open:                        
                        # Accumulate the Current Line's Content to the Ongoing Quote
                        temp_quote += " " + line_stripped  

                        # Check if the Current Line Ends with a Double-Quote, Signifying End of Multi-line Quote
                        if line_stripped.endswith('"'):
                            # Mark Quote as Closed
                            quote_open = False

                            # If Character Detected, Append Name and Quote
                            if temp_character_name:
                                label_block_contents.append(f"{temp_character_name} \"{temp_quote.strip()}")

                                # Update Quote Count for the Character
                                character_counts[temp_character_name] = character_counts.get(temp_character_name, 0) + 1

                                # Reset Temporary Character Name
                                temp_character_name = None

                            # Otherwise Append Quote
                            else:
                                label_block_contents.append(temp_quote)

                            # Reset the Accumulation
                            temp_quote = ""
                        else:
                            # Continue to the Next Line since We're Still Inside a Multi-line Quote
                            continue

                    # Process the Contents within the Label Block
                    if label_block_found is True and label_indentation <= current_indentation:
                        # Handle Indentation within Unwanted Blocks
                        if unwanted_block_found is True and unwanted_block_indentation is None:
                            unwanted_block_indentation = current_indentation
                        
                        # Detect End of Unwanted Block
                        if unwanted_block_found is True and unwanted_block_indentation > current_indentation:
                            unwanted_block_found = False
                            unwanted_block_indentation = None
                        
                        # Detect Start of Unwanted Block (`elif` or `else`)
                        if line_stripped.startswith("elif") or line_stripped.startswith("else"):
                            unwanted_block_found = True
                            continue

                        # Process the Actual Dialogues and Narrations
                        if unwanted_block_found is False:
                            # Remove `{}` and Everything Inside
                            line_uncurly = re.sub(r'\{.*?\}', '', line_stripped)

                            # Remove Trailing Space Inside the Double Quotes
                            line_untrailed = re.sub(r'^(\w+\s\".*?)(\s)\"$', r'\1"', line_uncurly)

                            # List of Keywords to Skip
                            skip_keywords = ["text"]

                            # Skip Lines Starting with Keywords
                            if any(line_untrailed.startswith(keyword) for keyword in skip_keywords):
                                continue
                            
                            # Attempt to Match the Current Line with the Character Quote Pattern
                            character_quote = re.match(r'(\w+)\s+.*?"(.*?)"', line_untrailed)
                            
                            # If Matched, Process Character's Quote
                            if character_quote:    
                                # Extract the Character Name and the Quote
                                character_name, quote = character_quote.groups()

                                # List of Character Names to Keep -> Add Functionality Later
                                correct_character_names = ["m", " mc", "y", "n", "s", "ny"]

                                # If List Contains Character Names, Save Only Them
                                if correct_character_names != []:
                                    # Skip Lines Starting with Wrong Character Names
                                    if not any(character_name == character for character in correct_character_names):
                                        continue

                                # Handle 'extend' Exception by Appending Previous Character Name and Quote
                                if character_name == "extend":
                                    label_block_contents.append(f"{prev_character_name} \"{quote}\"")

                                    # Update Quote Count for the Character
                                    character_counts[prev_character_name] = character_counts.get(prev_character_name, 0) + 1

                                # Append the Character's Name and Quote to Block Contents
                                else:                                    
                                    label_block_contents.append(f"{character_name} \"{quote}\"")

                                    # Update Quote Count for the Character
                                    character_counts[character_name] = character_counts.get(character_name, 0) + 1
                                
                                # Set Previous Character Name to Current in Order to Handle Possible 'extend' Exception in the Next Iteration
                                prev_character_name = character_name
                            else:
                                # If Not a Character Quote, Attempt to Match Narration Pattern
                                narration_quote = re.match(r'^"(.*?)"(\s*if .+:)?$', line_untrailed)

                                # If Matched, Process Narration Quote
                                if narration_quote:
                                    # Extract the Narration Quote
                                    quote_only = narration_quote.group(1)

                                    # Append Narration Quote to Block Contents
                                    label_block_contents.append(f"\"{quote_only}\"")

                                    # Update Narration Quote Count
                                    character_counts["narration"] = character_counts.get("narration", 0) + 1

                                # If Line Starts with a Quote and Isn't Inside an Open Multi-line Quote
                                elif line_untrailed.startswith('"') and not quote_open:
                                    # Begin a New Multi-line Quote Accumulation
                                    quote_open = True
                                    temp_quote = line_untrailed

                                # Check For Lines That Might Start a Multi-Line Quote For a Character
                                else:
                                    # Attempt to Match the Current Line With the Multi-Line Character Quote Pattern
                                    multiline_char_quote = re.match(r'(\w+)\s+"(.*?)(?!")$', line_untrailed)

                                    # If Matched, Extract The Character Name And The Beginning Of The Quote
                                    if multiline_char_quote:                                        
                                        temp_character_name = multiline_char_quote.group(1)
                                        temp_quote = multiline_char_quote.group(2)
                                        
                                        # Mark The Quote As Open Since It's a Multi-Line Quote
                                        quote_open = True


                # Save Remaining Contents After File Parsing   
                save_contents()

# Sort in Descending Order and Display Character Counts
sorted_counts = sorted(character_counts.items(), key=lambda x: x[1], reverse=True)
print('|------------------+--------------|')
print('| Character        | Count        |')
print('|------------------+--------------|')
for character, count in sorted_counts:
    print(f"| {character.ljust(16)} | {str(count).ljust(12)} |")
print('|------------------+--------------|')

# Display Total Lines Found and Written to Files
print(f"| {lines_found} line{' was' if lines_found == 1 else 's were'} found!".ljust(34) + '|')
print(f"| {lines_written} line{' was' if lines_written == 1 else 's were'} written!".ljust(34) + '|')
print('|---------------------------------|')