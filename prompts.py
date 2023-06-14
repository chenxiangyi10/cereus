from string import Template
prompt_template_chat = "$User_name: $message\n\n$AI_name:"
prompt_template_chat_Guanaco = "### Human: $message\n### Assistant:"
prompt_template_chat_WizardVicuna = "User: $message\n\nAssistant:"

prompt_instruct1 = Template('$SystemMsg\n\nInstruction: $user_instruction\n\nContext: $context\n\n$Response')
"""Example of prompt_instruct1:

You are given the following instruction and context which contains part of a scientific research paper. You should respond to the instruction according to the context.

Instruction: Describe the purpose of this research.

Context: We developed a super computer that can perform 1000 times faster than the current fastest super computer...

Response (start with "The purpose of this research is ..."):
"""

prompt_instruct2 = Template('$SystemMsg\n\nInstruction: $user_instruction\n\nContext: $context\n\n$Response: $response_prefix')
"""Example of prompt_instruct2:

You are given the following instruction and context which contains part of a scientific research paper. You should respond to the instruction according to the context.

Instruction: Describe the purpose of this research.

Context: We developed a super computer that can perform 1000 times faster than the current fastest super computer...

Response (start with "The purpose of this research is ..."): The purpose of this research is to
"""

prompt_instrct_refine_condition = Template('$user_instruction\n\nDescription: $description\n\nContext: $context\n\nResponse ("yes" or "no"):')
"""Example of prompt_instrct_refine:

Both a description of a research purpose and only part of the context of the scientific research paper are provided. The objective is to improve this description using the provided context, if necessary. To begin, we must first decide if the current description is adequate and if the context lacks any vital information that should be included. The question we need to address is: "Is the present description sufficient, and does the context exclude any essential information that must be incorporated?""

Description: The purpose of this research is to...

Context: We developed a super computer that can perform 1000 times faster than the current fastest super computer...

Response ("yes" or "no"):
"""

prompt_instrct_refine = Template('$user_instruction\n\nDescription: $description\n\nContext: $context\n\n$Response')
"""Example of prompt_instrct_refine:

Both a description of a research purpose and only part of the context of the scientific research paper are provided. Review and refine the description based on the context provided.

Description: The purpose of this research is to...

Context: We developed a super computer that can perform 1000 times faster than the current fastest super computer...

Refined description (start with "The purpose of this research is ..."):
"""