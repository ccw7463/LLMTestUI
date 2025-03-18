from . import *

generate_prompt = """{message}"""

def prompt_generate(state):    
    prompt = state['history']+[HumanMessage(content=generate_prompt.format_map(state['current']))]
    return prompt

def prompt_generate_test(state):    
    prompt = [HumanMessage(content=generate_prompt.format_map(state['current']))]
    return prompt