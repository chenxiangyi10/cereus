from typing import Union, Dict, List
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class RestrictedOutputPipeline:
    def __init__(self, model: Union[AutoGPTQForCausalLM, AutoModelForCausalLM], tokenizer : [AutoTokenizer], outputSet : Dict[str, List[int]]) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.outputSet = outputSet
        
    def __call__(self, prompt: str) -> str:
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')

        with torch.no_grad():
            outputs = self.model(input_ids.to(self.model.device))
            # for each class find out the max probability
            cls_wise_value = [max([torch.softmax(outputs.logits[:,-1,:], dim=-1)[0][i] for i in self.outputSet[cls]]) for cls in self.outputSet.keys()]
        del input_ids, outputs
        return list(self.outputSet.keys())[cls_wise_value.index(max(cls_wise_value))]