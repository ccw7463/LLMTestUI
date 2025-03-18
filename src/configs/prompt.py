from . import *

generate_prompt = """{MESSAGE}"""

def prompt_generate(STATE):    
    prompt = STATE['HISTORY']+[HumanMessage(content=generate_prompt.format_map(STATE['CURRENT']))]
    return prompt