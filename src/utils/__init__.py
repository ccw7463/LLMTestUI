import redis
import json
from configs.config import system_prompt, URLConfig
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
