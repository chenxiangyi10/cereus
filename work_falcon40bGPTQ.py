import time
from celery import Celery
from transformers import pipeline
import os
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer
import torch

# Set the available cuda, 0 is the first gpu, 1 is the second
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# Specify the model name
model_dir = "F:\\falcon-40b-instruct-GPTQ"

# load tokenizer and base model
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
model = AutoGPTQForCausalLM.from_quantized(model_dir, use_triton=False, use_safetensors=True, torch_dtype=torch.float32, trust_remote_code=True)

# create pipeline
temperature = 0.6
top_p = 0.95
pipe = pipeline(
    "text-generation",
    model=model, 
    tokenizer=tokenizer, 
    max_length=2048, #2048
    temperature=temperature,
    eos_token_id=tokenizer.eos_token_id,
    top_p=top_p,
    repetition_penalty=1.2,
)

celery_app = Celery("worker", broker="redis://paulchen.bio:6379/0", backend="redis://paulchen.bio:6379/1")

@celery_app.task(name='worker.process_data_task', bind=True)
def process_data_task(self, data: str) -> str:
    # Set task state as "STARTED"
    self.update_state(state='STARTED')

    # wrap the query
    query = '### Instruction: ' + data + '\n\n' + '### Response:'

    # Process data and return result
    output = pipe(query)[0]['generated_text']
    result = output[len(query):].lstrip()

    # Add a short delay before returning the result
    time.sleep(1)
    
    print(f"Task ID: {self.request.id} - Result: {result}")

    return result
