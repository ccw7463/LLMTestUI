from . import *

class ConversationHistory():
    def __init__(self, session_id):
        self.redis_client = redis.StrictRedis.from_url(URLConfig.REDIS_URL)
        self.session_id = session_id
            
    def add_chat(self, message_dict):
        '''
            Des:
                Save conversation based on the user session number
            Args:

        '''
        print("message_dict :",message_dict)
        key = f"session:{self.session_id}:chats"
        message_json = json.dumps(message_dict, ensure_ascii=False)
        list_length = self.redis_client.llen(key)
        if list_length < 3:
            self.redis_client.rpush(key, message_json)
        else:
            self.redis_client.lpop(key)  # Delete left first element in list 
            self.redis_client.rpush(key, message_json)  # Add new element to right
            
    def get_chats(self)->List[Dict]:
        '''
            Des:
                Retrieve the conversation of a specific session
                Used in task for extracting statistics
                Modify request based on previous conversations
            Returns:
                chat : A list of previously stored STATE (Dict type), including conversations, queries, etc.
        '''
        key = f"session:{self.session_id}:chats"
        chats = self.redis_client.lrange(key, 0, -1) 
        chats = [json.loads(chat.decode('utf-8')) for chat in chats]
        return chats

    def delete_chats(self):
        '''
            Des:
                Delete conversation based on the user session number
        '''        
        key = f"session:{self.session_id}:chats"
        self.redis_client.delete(key)
        
    def get_history_chats(self)->Optional[List[Dict[str,str]]]:
        '''
            Des: 
                Retrieve the conversation of a specific session and convert it to a multi-turn format (user, assistant)
        '''        
        previous_chats = self.get_chats()
        print("previous_chats :",previous_chats)
        if previous_chats:
            self.chats = []
            for chat in previous_chats:
                self.chats.extend([{"role":"user","content":chat['user']},
                                   {"role":"assistant","content":chat['assistant']}])
        else:
            self.chats = []
    
    def get_histotry_format_prompt(self):
        '''
            Des: 
                Convert multi-turn conversations of a specific session into langchain_core.messages (SystemMessage, HumanMessage, AIMessage)
            Returns:
                chat : list of langchain_core.messages format
        '''        
        self.history = [SystemMessage(content=system_prompt)]
        if self.chats:
            for chat in self.chats:
                if chat['role'] == "user":
                    self.history.append(HumanMessage(content=chat['content']))
                else:
                    self.history.append(AIMessage(content=chat['content']))
                    
                    