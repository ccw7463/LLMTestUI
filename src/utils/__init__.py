import redis
import json
from configs.config import SYSTEM_PROMPT, URLConfig
from typing import List, Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
