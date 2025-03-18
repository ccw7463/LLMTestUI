
import os
import uuid
from dotenv import load_dotenv
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from src.configs.prompt import prompt_generate
from src.configs.config import ModelConfig, ModelConfigFactory
from src.modules.chainlit import *
from chainlit.input_widget import Slider, Select
from src.utils.history import ConversationHistory
from src.utils.logger import setup_logger
from pathlib import Path

load_dotenv()  # Load variables from .env file

logger = setup_logger(script_name=Path(__file__).stem)

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
    global conv_obj
    session_id = uuid.uuid4().hex 
    conv_obj = ConversationHistory(session_id) 
    setting_obj = SessionSettings()
    setting_obj.settings = await cl.ChatSettings(
        [
            Slider(id="temperature",label="temperature",initial=0.5,
                    min=0,max=1,step=0.1),
            Slider(id="top_k",label="top_k",initial=100,
                    min=0,max=200,step=10),
            Slider(id="top_p",label="top_p",initial=0.7,
                    min=0,max=1,step=0.1),
            Slider(id="max_new_tokens",label="Max Length",initial=2048,
                    min=0,max=8192,step=128),
            Slider(id="repetition_penalty",label="Repetiton Penalty",initial=1.03,
                    min=1,max=2,step=0.01),
            Select(id="use_model",
                   label="Select Model",
                   values=ModelConfig.model_lst,
                   initial_index=0)
        ],
    ).send()
    logger.info(f"setting_obj.settings : {setting_obj.settings}")
    # save variables
    cl.user_session.set("setting_obj",setting_obj)
    

@cl.on_message  
async def main(message: cl.Message):
    '''
        Des:
            Main Functions when you chat
        Args:
            chat message you did send
    '''
    global conv_obj
    
    # load variables
    setting_obj = cl.user_session.get("setting_obj")
    
    # Set Message
    setting_obj.message = message.content
    
    # load Tokenizer and set stop sequences
    tokenizer = AutoTokenizer.from_pretrained(setting_obj.settings['use_model'],use_auth_token=os.getenv('HUGGINGFACE_TOKEN'))
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
    setting_obj.llm = ChatHuggingFace(
        llm=HuggingFaceEndpoint(
            endpoint_url=ModelConfigFactory.get_config(setting_obj.settings['use_model']).ENDPOINT,
            huggingfacehub_api_token=os.getenv('HUGGINGFACE_TOKEN'),
            max_new_tokens=setting_obj.settings["max_new_tokens"],
            top_k=setting_obj.settings["top_k"],
            top_p=setting_obj.settings["top_p"],
            temperature=setting_obj.settings["temperature"],
            repetition_penalty=setting_obj.settings["repetition_penalty"],
            model_kwargs={},
            stop_sequences=final_stop_sequences
            ),
        model_id=setting_obj.settings["use_model"],
        stream_mode=True
    ).bind(max_tokens=setting_obj.settings["max_new_tokens"])
    
    # save variables
    cl.user_session.set("setting_obj",setting_obj)
    
    # run
    await init()
    await general_answer()
    
async def init():
    global conv_obj
    
    # load variables
    setting_obj = cl.user_session.get("setting_obj")
    
    # regenerate input message with history
    conv_obj.get_history_chats()
    conv_obj.get_histotry_format_prompt()
    setting_obj.state = {"current":{"message":setting_obj.message},
                         "history":conv_obj.history}
    
    # save variables
    cl.user_session.set("setting_obj",setting_obj)
    
async def general_answer():
    '''
        Des:
            Generate Answer
    '''
    global conv_obj
    
    # load variables
    setting_obj = cl.user_session.get("setting_obj")
        
    # set chain
    Chain__generate = prompt_generate|setting_obj.llm
    
    # generate answer
    msg = cl.Message(content='')
    setting_obj.answer = ""
    try:
        async for chunk in Chain__generate.astream(setting_obj.state):
            logger.info(f"chunk.content : {chunk.content}")
            await msg.stream_token(chunk.content)
            setting_obj.answer += chunk.content
    except Exception as e: 
        if str(e) == "System role not supported": # in case gemma
            setting_obj.state['history'] = setting_obj.state['history'][1:]
            async for chunk in Chain__generate.astream(setting_obj.state):
                await msg.stream_token(chunk.content)
                setting_obj.answer += chunk.content
    conv_obj.add_chat({"user":setting_obj.message,
                       "assistant":setting_obj.answer})
    
    # save variables
    cl.user_session.set("setting_obj",setting_obj)

@cl.on_chat_end
def end():
    global conv_obj
    print("goodbye", cl.user_session.get("id"))
    conv_obj.delete_chats()