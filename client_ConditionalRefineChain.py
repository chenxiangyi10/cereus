from paulapi import paulAPI
from refinechain import ConditionalRefinechain
from Documents import Docs
from prompts import prompt_instruct1, prompt_instrct_refine, prompt_instrct_refine_condition
from string import Template
import yaml

# load docs
docs = Docs(docs_dir='F:/test')
yaml_list = []
for item in docs.docs[55:]:

    # select the first doc
    doc = item['text_splitted']

    # prepare model
    pipe = paulAPI

    # define outputset
    outputSet = {'yes': [3582, 8241, 4874, 3869], 'no': [1217, 3782, 694, 1939]}

    # create conditional refine chain
    chain = ConditionalRefinechain(pipe, outputSet)

    # load docs to chain
    chain.load_docs(doc)

    # set prompts
    first_prompt = prompt_instruct1
    values = {'SystemMsg': 'You are given the following instruction and context which contains part of a scientific research paper. You should respond to the instruction according to the context.',
            'user_instruction': 'Describe the purpose of this research.',
            'Response': 'Response (start with "The purpose of this research is ..."):'}
    first_prompt = first_prompt.safe_substitute(values)

    continue_prompt = prompt_instrct_refine
    values = {'user_instruction': 'Both a description of a research purpose of a scientific research paper and only part of the context of the scientific research paper are provided. Review and refine the description based on the context provided.',
            'Response': 'Refined description (start with "The purpose of this research is ..."):'}
    continue_prompt = continue_prompt.safe_substitute(values)

    condition_prompt = prompt_instrct_refine_condition
    values = {'user_instruction': 'Both a description of a research purpose of a scientific research paper and only part of the context of the scientific research paper are provided. The objective is to improve this description using the provided context, if necessary. To begin, we must first decide if the current description is adequate and if the context lacks any vital information that should be included. The question we need to address is: "Is the present description sufficient, and does the context exclude any essential information that must be incorporated?"'}
    condition_prompt = condition_prompt.safe_substitute(values)

    chain.set_prompt(first_prompt, continue_prompt, condition_prompt)

    print("Check the following prompts:")
    print("-----------------------------")
    print("First prompt:")
    print(first_prompt)
    print("-----------------------------")
    print("Continue prompt:")
    print(continue_prompt)
    print("-----------------------------")
    print("Condition prompt:")
    print(condition_prompt)
    print("-----------------------------")

    print("Start chain...")
    # start chain
    response = chain.run()
    print(response)
    yaml_list.append({'file_dir':item['file_dir'], 'purpose': response})
    with open('F:/test/purpose.yaml', 'w', encoding="utf-8") as f:
        yaml.dump(yaml_list, f)