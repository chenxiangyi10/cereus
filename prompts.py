from typing import Optional
class Prompt:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.prompt_elements = {
            "User_name": '',
            "AI_name": '',
            "separator": '',
        }
        self.use_template = True
    def set_prompt_elements(self, user: str = '', ai: str = '', separator: str = '') -> None:
        self.prompt_elements["User_name"] = user
        self.prompt_elements["AI_name"] = ai
        self.prompt_elements["separator"] = separator
    def get_prompt(self, user_message: str, response_prefix: Optional[str] = None) -> str:
        if not self.use_template:
            return user_message
        if response_prefix is None:
            prompt = f"{self.prompt_elements['User_name']}: {user_message}{self.prompt_elements['separator']}{self.prompt_elements['AI_name']}:"
        else:
            prompt = f"{self.prompt_elements['User_name']}: {user_message}{self.prompt_elements['separator']}{self.prompt_elements['AI_name']}: {response_prefix}"
        return prompt

    
class PromptGuanaco(Prompt):
    def __init__(self) -> None:
        super().__init__('Guanaco')
        self.set_prompt_elements('### Human', '### Assistant', '\n')
    
class PromptWizard_vicuna(Prompt):
    def __init__(self) -> None:
        super().__init__('wizard_vicuna')
        self.set_prompt_elements('User', 'Assistant', '\n\n')