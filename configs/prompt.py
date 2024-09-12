from . import *
from .config import SYSTEM_PROMPT

generate_prompt = """{MESSAGE}"""
generate_relevant_query = """# 요청문
{MESSAGE}

# 답변
{ANSWER}

주어진 요청문과 답변을 기반으로 추가적인 요청문 4개를 생성해주세요.

# 요청 형태
1. 유사한 질문 (1)
2. 유사한 질문 (2)
3. 질문 주제는 동일하지만 다른 유형의 질문 (3)
4. 질문 주제가 조금 다른 유형의 질문 (4)

요청 형태대로 요청문 4개를 생성합니다.

반드시 리스트 형태로 작성해주세요.

# 출력양식
[요청1, 요청2, 요청3, 요청4]
"""

def prompt_generate(STATE):    
    prompt = STATE['HISTORY']+[HumanMessage(content=generate_prompt.format_map(STATE['CURRENT']))]
    return prompt