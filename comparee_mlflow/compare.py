from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from datasets import load_metric
import mlflow
#import argparse
import time
import gc

model_name = "Varosa/mbart-many-to-many"

# Initialize ROUGE metric
rouge_metric = load_metric("rouge")

# Summarize a single text
def summarize(text, model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    input_ids = tokenizer.encode(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(input_ids, max_length=100, num_beams=4, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Evaluate one model
def evaluate_model(model_name, sample_texts, references):
    if mlflow.active_run():
        mlflow.end_run()

    mlflow.start_run(run_name=model_name)
    summaries = []
    start_time = time.time()

    for text in sample_texts:
        summary = summarize(text, model_name)
        summaries.append(summary)

    end_time = time.time()
    inference_time = end_time - start_time

    # Debugging: Print predictions and references
    print("Predictions (summaries):", summaries)
    print("References:", references)

    # Log metrics
    mlflow.log_metric("inference_time", inference_time)
    try:
        results = rouge_metric.compute(predictions=summaries, references=references)
        print("ROUGE Results:", results)  # Debugging: Print raw ROUGE results

        # Flatten ROUGE metrics before logging
        rouge_results = {
            "rouge1_f": results['rouge1'].mid.fmeasure,
            "rouge1_p": results['rouge1'].mid.precision,
            "rouge1_r": results['rouge1'].mid.recall,
            "rouge2_f": results['rouge2'].mid.fmeasure,
            "rouge2_p": results['rouge2'].mid.precision,
            "rouge2_r": results['rouge2'].mid.recall,
            "rougeL_f": results['rougeL'].mid.fmeasure,
            "rougeL_p": results['rougeL'].mid.precision,
            "rougeL_r": results['rougeL'].mid.recall,
        }

        for key, value in rouge_results.items():
            mlflow.log_metric(key, value)
    except Exception as e:
        print("Error computing or logging ROUGE metrics:", e)

    mlflow.end_run()
    gc.collect()

def main():
    model_name = ""

    #parser = argparse.ArgumentParser()
    #parser.add_argument("--model", type=str, required=True, help="Model name to evaluate")
    #args = parser.parse_args()

    # Define the sample texts and references
    sample_texts = [
        "Videos that say approved vaccines are dangerous and cause autism, cancer or infertility are among those that will be taken down, the company said.",
        "Tech giants have been criticised for not doing more to counter false health information on their sites.",
    ]
    references = [
        "Some vaccine-related videos will be taken down.",
        "Tech giants are criticized for spreading false information.",
    ]

    # Set MLflow tracking URI
    #mlflow.set_tracking_uri("file:///app/mlruns") #file:///home/vboxuser/coursework-Chisomikec/comparee_mlflow/mlruns
    experiment_name = "model_compare"
    
    mlflow.set_experiment(experiment_name)

    # Ensure the experiment is created
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print("Experiment 'model_compare' does not exist. Creating it...")
        mlflow.create_experiment(experiment_name)
    else: 
        print(f"Using experiment '{experiment_name}' (ID: {experiment.experiment_id})")
    # Run evaluation
    evaluate_model(model_name, sample_texts, references)

if __name__ == "__main__":
    main()
