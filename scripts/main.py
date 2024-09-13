import sys
sys.path = [path for path in sys.path if not path.startswith('/workspace')]
sys.path.append("/workspace/changwoo/LLMTestUI")

from configs.prompt import *
from configs.config import *
from modules.chainlit import *
from chainlit.input_widget import Slider, Switch, Select
from utils.history import ConversationHistory
from transformers import AutoConfig, AutoTokenizer
from langchain.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.chat_models.huggingface import ChatHuggingFace
import uuid
from loguru import logger
from dotenv import load_dotenv
import os
load_dotenv()  # Load variables from .env file

class SessionSettings():
    '''
        Des:
            Variable management class 
            - Variables can be managed with cl.user_session, but object management is difficult
    ''' 
    def __init__(self):
        pass

@cl.on_chat_start
async def start_chat():
    '''
        Des:
            Initialization function
    '''    
    global CONV_OBJ
    logger.info(ModelConfig.MODEL_LST)
    SESSION_ID = uuid.uuid4().hex 
    CONV_OBJ = ConversationHistory(SESSION_ID) 
    SETTING_OBJ = SessionSettings()
    SETTING_OBJ.SETTINGS = await cl.ChatSettings(
        [
            Slider(id="temperature",label="temperature",initial=0.1,
                    min=0,max=1,step=0.1),
            Slider(id="top_k",label="top_k",initial=100,
                    min=0,max=200,step=10),
            Slider(id="top_p",label="top_p",initial=0.9,
                    min=0,max=1,step=0.1),
            Slider(id="max_new_tokens",label="Max Length",initial=4096,
                    min=0,max=8192,step=128),
            Slider(id="repetition_penalty",label="Repetiton Penalty",initial=1.03,
                    min=1,max=2,step=0.01),
            Select(id="use_model",
                   label="Select Model",
                   values=ModelConfig.MODEL_LST,
                   initial_index=0)
        ],
    ).send()
    
    # save variables
    cl.user_session.set("SETTING_OBJ",SETTING_OBJ)
    

@cl.on_message  
async def main(message: cl.Message):
    '''
        Des:
            Main Functions when you chat
        Args:
            chat message you did send
    '''
    global CONV_OBJ
    
    # load variables
    SETTING_OBJ = cl.user_session.get("SETTING_OBJ")
    
    # Set Message
    SETTING_OBJ.MESSAGE = message.content
    
    # load Tokenizer and set stop sequences
    tokenizer = AutoTokenizer.from_pretrained(SETTING_OBJ.SETTINGS['use_model'],use_auth_token=os.getenv('HUGGINGFACE_TOKEN'))
    stop_sequences = []
    if tokenizer.additional_special_tokens:
        for stop_seq in tokenizer.additional_special_tokens:
            if "end" in stop_seq:
                stop_sequences.append(stop_seq)
    stop_sequences.append(tokenizer.eos_token)
    final_stop_sequences = []
    for item in stop_sequences:
        if item not in final_stop_sequences:
            final_stop_sequences.append(item)
    
    # set model
    SETTING_OBJ.LLM = ChatHuggingFace(
        llm=HuggingFaceEndpoint(
            endpoint_url=ModelConfigFactory.get_config(SETTING_OBJ.SETTINGS['use_model']).ENDPOINT,
            huggingfacehub_api_token=os.getenv('HUGGINGFACE_TOKEN'),
            max_new_tokens=SETTING_OBJ.SETTINGS["max_new_tokens"],
            top_k=SETTING_OBJ.SETTINGS["top_k"],
            top_p=SETTING_OBJ.SETTINGS["top_p"],
            temperature=SETTING_OBJ.SETTINGS["temperature"],
            repetition_penalty=SETTING_OBJ.SETTINGS["repetition_penalty"],
            model_kwargs={},
            stop_sequences=final_stop_sequences
            ),
        model_id=SETTING_OBJ.SETTINGS["use_model"]
    )
    
    # save variables
    cl.user_session.set("SETTING_OBJ",SETTING_OBJ)
    
    # run
    await init()
    await general_answer()
    
async def init():
    
    global CONV_OBJ
    
    # load variables
    SETTING_OBJ = cl.user_session.get("SETTING_OBJ")
    
    # regenerate input message with history
    CONV_OBJ.get_history_chats()
    CONV_OBJ.get_histotry_format_prompt()
    SETTING_OBJ.STATE = {"CURRENT":{"MESSAGE":SETTING_OBJ.MESSAGE},
                         "HISTORY":CONV_OBJ.HISTORY}
    
    # save variables
    cl.user_session.set("SETTING_OBJ",SETTING_OBJ)
    
async def general_answer():
    '''
        Des:
            Generate Answer
    '''
    global CONV_OBJ
    
    # load variables
    SETTING_OBJ = cl.user_session.get("SETTING_OBJ")
        
    # generate answer
    msg = cl.Message(content='')
    Chain__generate = prompt_generate|SETTING_OBJ.LLM
    SETTING_OBJ.ANSWER = ""
    try:
        async for chunk in Chain__generate.astream(SETTING_OBJ.STATE):
            await msg.stream_token(chunk.content)
            SETTING_OBJ.ANSWER += chunk.content
    except Exception as e: 
        if str(e) == "System role not supported": # in case gemma
            SETTING_OBJ.STATE['HISTORY'] = SETTING_OBJ.STATE['HISTORY'][1:]
            async for chunk in Chain__generate.astream(SETTING_OBJ.STATE): # ignore system 
                await msg.stream_token(chunk.content)
                SETTING_OBJ.ANSWER += chunk.content
    CONV_OBJ.add_chat({"user":SETTING_OBJ.MESSAGE,
                       "assistant":SETTING_OBJ.ANSWER})
    
    # save variables
    cl.user_session.set("SETTING_OBJ",SETTING_OBJ)

@cl.on_chat_end
def end():
    global CONV_OBJ
    print("goodbye", cl.user_session.get("id"))
    CONV_OBJ.delete_chats()