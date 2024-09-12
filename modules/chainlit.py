from . import *

chat_profiles = GetProfile()
@cl.set_chat_profiles
async def chat_profile()->dict:
    '''
        Des:
            Retrieves information about the profile (chat type) to be used.
        Return:
            name
            markdown_description
            icon
    '''
    return [
        cl.ChatProfile(**profile) for profile in chat_profiles.get_cl_chat_profiles()
    ]
    
@cl.password_auth_callback
def auth_callback(username: str, password: str):
    '''
        Des:
            Function that receives account and password input
        Args:
            username : ID
            password : PW
        Return:
            cl.User or None
    '''
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", 
            metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None