# Import Required Libraries
import torch
import humanize
import transformers
import peft
import datasets
import matplotlib.pyplot

# Define Function to Find All 'Linear4bit' Layers
def find_target_modules(model):
    # Initialize a Set to Store Unique Layers
    unique_layers = set()
    
    # Iterate Over All Named Modules in the Model
    for name, module in model.named_modules():
        # Check if the Module Type Contains 'Linear4bit'
        if "Linear4bit" in str(type(module)):
            # Extract the Type of the Layer
            layer_type = name.split('.')[-1]
            
            # Add the Layer Type to the Set of Unique Layers
            unique_layers.add(layer_type)

    # Return the Set of Unique Layers Converted to List
    return list(unique_layers)

# Define Function to Print Information on Model's Parameters
def print_model_parameters_info(model):
    # Initialize Variables to Count Total and Trainable Parameters
    total_parameters = 0
    trainable_parameters = 0
    
    # Iterate Over All Named Parameters in the Model
    for _, parameter in model.named_parameters():
        # Increment the Total Parameters Count
        total_parameters += parameter.numel()

        # Fix Wrong Parameter Count
        if parameter.dtype == torch.uint8:
            total_parameters += parameter.numel()
        
        # Check if the Parameter Requires Gradients
        if parameter.requires_grad:
            # Increment the Trainable Parameters Count
            trainable_parameters += parameter.numel()

            # Fix Wrong Parameter Count
            if parameter.dtype == torch.uint8:
                trainable_parameters += parameter.numel()

    # Humanize the Counts for Printing
    total_parameters_humanized = humanize.intword(total_parameters, format="%.2f")
    original_parameters_humanized = humanize.intword(total_parameters - trainable_parameters, format="%.2f")
    trainable_parameters_humanized = humanize.intword(trainable_parameters, format="%.2f")

    # Print the Number of Total Parameters, Trainable Parameters and the Percentage of Trainable Parameters
    print('|--------------------------------------------|')
    print(f"| Total Parameters: {total_parameters_humanized}".ljust(45) + '|')
    print(f"| Original Parameters: {original_parameters_humanized}".ljust(45) + '|')
    print(f"| Trainable Parameters: {trainable_parameters_humanized}".ljust(45) + '|')
    print(f"| Trainable Percentage: {round(100 * trainable_parameters / total_parameters, 2)}%".ljust(45) + '|')
    print('|--------------------------------------------|')

# Quantization Settings
load_in_4bit = True
bnb_4bit_use_double_quant = True
bnb_4bit_quant_type = "nf4"
bnb_4bit_compute_dtype = torch.bfloat16

# Create Quantization Config
quantization_config = transformers.BitsAndBytesConfig(load_in_4bit=load_in_4bit, bnb_4bit_use_double_quant=bnb_4bit_use_double_quant, bnb_4bit_quant_type=bnb_4bit_quant_type, bnb_4bit_compute_dtype=bnb_4bit_compute_dtype)

# Create Device Map
device_map = {"":0}

# Load Config
config = transformers.AutoConfig.from_pretrained(r".\Model")

# Load Tokenizer
tokenizer = transformers.AutoTokenizer.from_pretrained(r".\Model")

# Load Model
model = transformers.AutoModelForCausalLM.from_pretrained(r".\Model", config=config, quantization_config=quantization_config, device_map=device_map)

# Prepare Model for Training
model = peft.prepare_model_for_kbit_training(model)

# QLoRA Config Settings
r = 8
lora_alpha = 16
target_modules = find_target_modules(model)
lora_dropout = 0.05
bias = "none" 
task_type = "CAUSAL_LM"

# Create QLoRA Config
peft_config = peft.LoraConfig(r=r, lora_alpha=lora_alpha, target_modules=target_modules, lora_dropout=lora_dropout, bias=bias, task_type=task_type)

# Convert Original Model to PEFT Model
model = peft.get_peft_model(model, peft_config)

# Print Parameter Infromation
print_model_parameters_info(model)

# Tokenization Settings
max_length = transformers.AutoConfig.from_pretrained(r".\Model").max_position_embeddings
padding = "max_length"
truncation = True
batched = True

# Load Dataset
dataset = datasets.load_dataset("json", data_files=r".\Dataset\Dataset.json")

# Fix Tokenizer Issue for Some Models
tokenizer.pad_token = tokenizer.eos_token

# Tokenize Dataset
dataset = dataset.map(lambda samples: tokenizer(samples["input"], max_length=max_length,padding=padding, truncation=truncation), batched=batched)

# Initialize Variable to Keep Count of Tokens in the Dataset
total_tokens_count = 0

# Calculate the Amount of Tokens in the Dataset
for index in range(dataset["train"].num_rows):
    # Calculate for 'input'
    input_tokens = tokenizer(dataset["train"]["input"][index])["input_ids"]

    # Calculate for 'output'
    output_tokens = tokenizer(dataset["train"]["output"][index])["input_ids"]

    # Add Both to the Total Counter
    total_tokens_count += len(input_tokens) + len(output_tokens)

# Trainer Settings
per_device_train_batch_size = 1
gradient_accumulation_steps = 1
warmup_steps = 0
max_steps = -1
num_train_epochs = 5
learning_rate = 2e-4
fp16 = True
logging_steps = 1
output_dir = r".\Adapter"
optim = "paged_adamw_32bit"

# Create Trainer
trainer = transformers.Trainer(
    model=model,
    train_dataset=dataset["train"],
    args=transformers.TrainingArguments(
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_steps=warmup_steps,
        max_steps=max_steps,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        fp16=fp16,
        logging_steps=logging_steps,
        output_dir=output_dir,
        optim=optim
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Train the Model
trainer.train()

# Save the Final Model
model.save_pretrained(output_dir)

# Create Lists for Step-Loss-Curve
steps = [log["step"] for log in trainer.state.log_history[:-1]]
losses = [log["loss"] for log in trainer.state.log_history[:-1]]

# Save Step-Loss-Curve
matplotlib.pyplot.plot(steps, losses)
matplotlib.pyplot.xlabel("Step")
matplotlib.pyplot.ylabel("Loss")
matplotlib.pyplot.savefig(f"{output_dir}/Step-Loss-Curve.png")