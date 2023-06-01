import time
from celery import Celery
from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline
import os

# Set the available cuda, 0 is the first gpu, 1 is the second
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

# load tokenizer and base model
tokenizer = LlamaTokenizer.from_pretrained("TheBloke/wizard-vicuna-13B-HF")
base_model = LlamaForCausalLM.from_pretrained(
    "TheBloke/wizard-vicuna-13B-HF",
    load_in_8bit=True,
    device_map='auto'
)

# create pipeline
temperature = 0.6
top_p = 0.95
pipe = pipeline(
    "text-generation",
    model=base_model, 
    tokenizer=tokenizer, 
    max_length=2048, #2048
    temperature=temperature,
    top_p=top_p,
    repetition_penalty=1.2,
)

celery_app = Celery("worker", broker="redis://paulchen.bio:6379/0", backend="redis://paulchen.bio:6379/1")

@celery_app.task(name='worker.process_data_task', bind=True)
def process_data_task(self, data: str):
    # Set task state as "STARTED"
    self.update_state(state='STARTED')

    # wrap the query
    query = 'User: ' + data + '\n\n' + 'Assistant:' # for wizard-vicuna-13B template

    # Process data and return result
    output = pipe(query)[0]['generated_text']
    result = output[len(query):].lstrip()

    # Add a short delay before returning the result
    time.sleep(1)
    
    print(f"Task ID: {self.request.id} - Result: {result}")

    return result
