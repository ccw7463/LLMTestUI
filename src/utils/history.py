from . import *

class ConversationHistory():
    def __init__(self, SESSION_ID):
        self.REDIS_CLIENT = redis.StrictRedis.from_url(URLConfig.REDIS_URL)
        self.SESSION_ID = SESSION_ID
            
    def add_chat(self, message_dict):
        '''
            Des:
                Save conversation based on the user session number
            Args:

        '''
        print("message_dict :",message_dict)
        key = f"session:{self.SESSION_ID}:chats"
        message_json = json.dumps(message_dict, ensure_ascii=False)
        list_length = self.REDIS_CLIENT.llen(key)
        if list_length < 3:
            self.REDIS_CLIENT.rpush(key, message_json)
        else:
            self.REDIS_CLIENT.lpop(key)  # Delete left first element in list 
            self.REDIS_CLIENT.rpush(key, message_json)  # Add new element to right
            
    def get_chats(self)->List[Dict]:
        '''
            Des:
                Retrieve the conversation of a specific session
                Used in task for extracting statistics
                Modify request based on previous conversations
            Returns:
                chat : A list of previously stored STATE (Dict type), including conversations, queries, etc.
        '''
        key = f"session:{self.SESSION_ID}:chats"
        chats = self.REDIS_CLIENT.lrange(key, 0, -1) 
        chats = [json.loads(chat.decode('utf-8')) for chat in chats]
        return chats

    def delete_chats(self):
        '''
            Des:
                Delete conversation based on the user session number
        '''        
        key = f"session:{self.SESSION_ID}:chats"
        self.REDIS_CLIENT.delete(key)
        
    def get_history_chats(self)->Optional[List[Dict[str,str]]]:
        '''
            Des: 
                Retrieve the conversation of a specific session and convert it to a multi-turn format (user, assistant)
        '''        
        PREVIOUS_CHATS = self.get_chats()
        print("PREVIOUS_CHATS :",PREVIOUS_CHATS)
        if PREVIOUS_CHATS:
            self.CHATS = []
            for chat in PREVIOUS_CHATS:
                self.CHATS.extend([{"role":"user","content":chat['user']},
                                   {"role":"assistant","content":chat['assistant']}])
        else:
            self.CHATS = []
    
    def get_histotry_format_prompt(self):
        '''
            Des: 
                Convert multi-turn conversations of a specific session into langchain_core.messages (SystemMessage, HumanMessage, AIMessage)
            Returns:
                chat : list of langchain_core.messages format
        '''        
        self.HISTORY = [SystemMessage(content=SYSTEM_PROMPT)]
        if self.CHATS:
            for chat in self.CHATS:
                if chat['role'] == "user":
                    self.HISTORY.append(HumanMessage(content=chat['content']))
                else:
                    self.HISTORY.append(AIMessage(content=chat['content']))
                    
                    