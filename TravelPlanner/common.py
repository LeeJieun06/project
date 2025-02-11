import os
import openai
from dataclasses import dataclass
import pytz
from datetime import datetime, timedelta

mykey='본인의 OPENAI_API_KEY를 넣을 것.'

@dataclass(frozen=True)
class Model: 
    #현재는 basic 모델을 쓰는 걸로 되어 있으니 필요에 따라 수정. 가장 최신의 버전은 gpt-4o
    basic: str = "gpt-3.5-turbo-1106"
    advanced: str = "gpt-4-turbo"
    basic_old: str = "gpt-3.5-turbo" 
os.environ["OPENAI_API_KEY"]=mykey
model = Model();    
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=30, max_retries=1)
        
def makeup_response(message, finish_reason="ERROR"):
    return {
                "choices": [
                    {
                        "finish_reason": finish_reason,
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": message
                        }                   
                    }
                ],
                "usage": {"total_tokens": 0},
            }

def today():
    korea = pytz.timezone('Asia/Seoul')# 한국 시간대를 얻습니다.
    now = datetime.now(korea)# 현재 시각을 얻습니다.
    return(now.strftime("%Y%m%d"))# 시각을 원하는 형식의 문자열로 변환합니다.

def yesterday():    
    korea = pytz.timezone('Asia/Seoul')# 한국 시간대를 얻습니다.
    now = datetime.now(korea)# 현재 시각을 얻습니다.
    one_day = timedelta(days=1)    # 하루 (1일)를 나타내는 timedelta 객체를 생성합니다.
    yesterday = now - one_day # 현재 날짜에서 하루를 빼서 어제의 날짜를 구합니다.
    return yesterday.strftime('%Y%m%d') # 어제의 날짜를 yyyymmdd 형식으로 변환합니다.

def currTime():
    # 한국 시간대를 얻습니다.
    korea = pytz.timezone('Asia/Seoul')
    # 현재 시각을 얻습니다.
    now = datetime.now(korea)
    # 시각을 원하는 형식의 문자열로 변환합니다.
    formatted_now = now.strftime("%Y.%m.%d %H:%M:%S")
    return(formatted_now)                

