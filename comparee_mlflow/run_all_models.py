import subprocess

# List of models to evaluate
models = [
    "sshleifer/distilbart-cnn-12-6",
    "facebook/bart-large-cnn",
    
]

# Run the compare.py script for each model
for model in models:
    print(f"Running evaluation for model: {model}")
    subprocess.run(["mlflow", "run", ".", "-e", "main", "-P", f"model={model}"])
    print(f"Completed evaluation for model: {model}")
