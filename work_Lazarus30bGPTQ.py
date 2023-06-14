import time
from celery import Celery
from transformers import pipeline, logging
import os
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer
from customPipeline import RestrictedOutputPipeline
from typing import Dict

# credit to TheBoke: https://huggingface.co/TheBloke/guanaco-65B-GPTQ/discussions/4

# Set the available cuda, 0 is the first gpu, 1 is the second
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# Specify the model name
model_dir = "F:\\30B-Lazarus-GPTQ4bit"

#model_basename = "Guanaco-65B-GPTQ-4bit.act-order.safetensors"

# load tokenizer and base model
print("Loading tokenizer")
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)
print("Loading model")
model = AutoGPTQForCausalLM.from_quantized(model_dir, 
                                           #model_basename=model_basename, 
                                           use_triton=False, 
                                           use_safetensors=True, 
                                           quantize_config=None)

# Prevent printing spurious transformers error when using pipeline with AutoGPTQ
logging.set_verbosity(logging.CRITICAL)

# create pipeline
temperature = 0.7
top_p = 0.95
pipe_normal = pipeline(
    "text-generation",
    model=model, 
    tokenizer=tokenizer, 
    max_length=2048, #2048
    temperature=temperature,
    eos_token_id=tokenizer.eos_token_id,
    top_p=top_p,
    repetition_penalty=1.2,
)

pipe_restricted = RestrictedOutputPipeline(
    model=model,
    tokenizer=tokenizer,
    outputSet={}
)

celery_app = Celery("worker", broker="redis://paulchen.bio:6379/0", backend="redis://paulchen.bio:6379/1")

@celery_app.task(name='worker.process_data_task', bind=True)
def process_data_task(self, data: str, outputSet: Dict) -> str:
    # Set task state as "STARTED"
    self.update_state(state='STARTED')

    # check whether the outputSet is empty
    if outputSet:
        pipe = pipe_restricted
        pipe.outputSet = outputSet
    else:
        pipe = pipe_normal

    # Process data and return result
    if outputSet:
        result = pipe(data)
    else:
        output = pipe(data)[0]['generated_text']
        result = output[len(data):].lstrip().rstrip()

    # Add a short delay before returning the result
    time.sleep(1)
    
    print(f"Task ID: {self.request.id} - Result: {result}")

    return result

# run in bash
# celery -A work_Lazarus30bGPTQ worker --loglevel=info --pool=solo
