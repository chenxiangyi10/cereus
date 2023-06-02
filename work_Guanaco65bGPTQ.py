import time
from celery import Celery
from transformers import pipeline, logging
import os
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer
from prompts import PromptGuanaco

# Set the available cuda, 0 is the first gpu, 1 is the second
# os.environ["CUDA_VISIBLE_DEVICES"] = "1" # 2 GPUs are needed for 65b

# Specify the model name
model_dir = "F:\\guanaco-65B-GPTQ"
#model_basename = "Guanaco-65B-GPTQ-4bit.act-order.safetensors"

# load tokenizer and base model
tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)

# quantize_config = BaseQuantizeConfig(
#         bits=4,
#         group_size=128,
#         desc_act=False
#     )

model = AutoGPTQForCausalLM.from_quantized(model_dir, 
                                           #model_basename=model_basename, 
                                           use_triton=False, 
                                           use_safetensors=True, 
                                           quantize_config=None)

# Prevent printing spurious transformers error when using pipeline with AutoGPTQ
logging.set_verbosity(logging.CRITICAL)

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
def process_data_task(self, data: str, use_template: bool) -> str:
    # Set task state as "STARTED"
    self.update_state(state='STARTED')

    # wrap the query
    query_template = PromptGuanaco()
    query_template.use_template = use_template # if use template, the user-assistant like template will be used; otherwise, the prompt is as it is
    query = query_template.get_prompt(data)

    # Process data and return result
    output = pipe(query)[0]['generated_text']
    result = output[len(query):].lstrip()

    # Add a short delay before returning the result
    time.sleep(1)
    
    print(f"Task ID: {self.request.id} - Result: {result}")

    return result

# run in bash
# celery -A work_Guanaco65bGPTQ worker --loglevel=info --pool=solo