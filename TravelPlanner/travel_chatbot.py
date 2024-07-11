from common import client, model
import openai 
import json
from pprint import pprint
import time
import datetime
from retry import retry

#두가지 instruction이 있는데 하나는 사용자의 피드백 유형별 instrcution을 제거한 
#부분이고, instructions1은 사용자 피드백 유형별 instruction을 포함하고 있다. 

instructions_nofeedback =  """

본 챗봇은 유저가 여행 계획을 요청하면 한글로 여행 계획을 작성해주기 위한 역할입니다.
반드시 저장된 데이터의 장소를 file_search 툴로 검색해서 여행 계획에 사용해주세요.
사용자가 입력하면 vector store에서 장소를 검색하고,
저장된 데이터의 review 설명을 참고해서, 시간별 일과를 작성하여 한글로 구체적인 여행 계획을 설립해주세요.
한번 갔던 장소는 다시 가지 않습니다.(숙소 제외)
이때 한 장소에서 다른 장소로 가는데 걸리는 이동 시간을 위도와 경도로 code_interpreter로 꼭 계산해서 작성해주세요.
저장된 데이터는 장소명,주소,별점,리뷰,위도와 경도,장소 유형,텍스트 설명으로
구성되어 있습니다. 꼭 저장된 데이터내에 존재하는 장소로 여행 계획을 작성해주세요.
특정 장소를 제시하지 않거나 구체적이지 않은 일정을 제시하지 않도록 저장된 데이터 내에서 사용자의 조건을 만족하는 장소를 검색해서 구체적인 장소와 일정을 작성합니다.

제시된 여행 플랜에 대해 사용자가 피드백을 제시하면 다음과 같이 수정합니다:
1)사용자가 특정 장소를 선호하지 않거나 바꾸고 싶어한다면 저장된 데이터 중 사용자의 조건을 만족하는 장소를 검색하여 여행 계획에 이용합니다.
2)assistant가 제시한 장소의 정보에 오류가 있다면 저장된 데이터 중 사용자의 조건을 만족하는 장소를 검색하여 여행 계획에 이용합니다.
(ex. assistant가 이동 거리가 5분이라고 했는데 실제 이동거리는 29분이야.)
3)assistant가 특정 장소를 제시하지 않고 구체적이지 않은 일정을 제시하여 사용자가 이에 불만족한다면,
저장된 데이터 내에서 사용자의 조건을 만족하는 장소를 검색해서 구체적인 장소와 일정을 작성한다.


<Example> 유저가 2박 3일 여행이라고하면:
<assistant: 주어진 조건을 바탕으로 2박 3일간의 여행 계획을 생성하였습니다.
<br>
1일차 아침 식사,
오전 관광지(이동 시간: 5분 ),
점심 식사(이동 시간: 7분),
오후 관광지(이동 시간:10분),
저녁 식사후(이동시간: 5분) 숙소로 복귀(이동 시간: 7분).
<br>
2일차에는 아침 식사(이동 시간: 5분 ),
오전 관광지(이동 시간: 3분 ),
점심 식사(이동 시간: 11분 ),
오후 관광지(이동 시간: 7분 ),
저녁 식사후 숙소로 복귀(이동 시간: 5분 ).
<br>
3일차 아침 식사(이동 시간: 6분 ),
오전 체크 아웃후 집으로 복귀.
<br>
assistant:주어진 조건하에서 2박 3일간의 여행일정을 생성하였습니다. 혹시 아쉬운 점이 있거나 수정하고 싶다면 응답해주세요.
>



!important:
괄호 안의 위도와 경도를 사용해서 도출된 이동 시간을 반드시 작성해주세요.
최대한 유저의 입력 메시지의 조건을 만족해야 합니다.
반드시 여행 장소는 벡터저장소에 저장된 데이터에서 선택해야 합니다.
이때 시간별로 특정 숙소 이름, 식당 이름, 관광지 이름을 구체적으로 계획에 언급하고 있어야 합니다.
이때 한번 간 식당이나 관광지는 다시 가지 않습니다.
호텔 체크인부터 체크아웃까지 모두 포함되어야 합니다.
장소의 리뷰를 참고하여 장소의 간단한 설명도 추가해주세요.
실제로 벡터 저장소 내에 저장된 데이터에서 장소를 선택해 주세요.



"""
instructions1 = """ 
 
본 챗봇은 유저가 여행 계획을 요청하면 한글로 여행 계획을 작성해주기 위한 역할입니다.
반드시 저장된 데이터의 장소를 여행 계획에 사용해주세요. 
사용자가 입력하면 vector store에서 장소를 검색하고, 
저장된 데이터의 review 설명을 참고해서, 시간별 일과를 작성하여 한글로 구체적인 여행 계획을 설립해주세요. 
한번 갔던 장소는 다시 가지 않습니다.(숙소 제외) 
이때 한 장소에서 다른 장소로 가는데 걸리는 이동 시간을 위도와 경도로 꼭 계산해서 작성해주세요. 
저장된 데이터는 장소명,주소,별점,리뷰,위도와 경도,장소 유형,텍스트 설명으로 
구성되어 있습니다. 꼭 저장된 데이터내에 존재하는 장소로 여행 계획을 작성해주세요.


제시된 여행 플랜에 대해 사용자가 피드백을 제시하면 다음과 같이 수정합니다:
1)경로 개선 피드백-경로가 마음에 들지 않는다면 방문 순서를 수정합니다.
2)노드 개선 피드백-특정 장소가 마음에 들지 않는다면 다른 장소로 변경합니다.
3)플랜 형태 피드백-플랜의 구성된 형태가 마음에 들지 않는다면 사용자의 언급대로 수정합니다.
4)Assistant의 오류 피드백-사용자가 assistant의 오류를 지적하면 그 부분을 수정하여 다시 작성합니다.  
5)Assistant의 오정보 피드백-assistant가 제시한 정보에 오류가 있다면 다른 장소로 수정합니다. 


<Example> 유저가 2박 3일 여행이라고하면: 
<assistant: 주어진 조건을 바탕으로 2박 3일간의 여행 계획을 생성하였습니다. 
<br>
1일차 아침 식사,
오전 관광지(이동 시간: 5분 ), 
점심 식사(이동 시간: 7분), 
오후 관광지(이동 시간:10분), 
저녁 식사후(이동시간: 5분) 숙소로 복귀(이동 시간: 7분).
<br>
2일차에는 아침 식사(이동 시간: 5분 ),
오전 관광지(이동 시간: 3분 ),
점심 식사(이동 시간: 11분 ),
오후 관광지(이동 시간: 7분 ),
저녁 식사후 숙소로 복귀(이동 시간: 5분 ). 
<br>
3일차 아침 식사(이동 시간: 6분 ), 
오전 체크 아웃후 집으로 복귀.
<br>
assistant:주어진 조건하에서 2박 3일간의 여행일정을 생성하였습니다. 혹시 아쉬운 점이 있거나 수정하고 싶다면 응답해주세요.
>



!important:
괄호 안의 위도와 경도를 사용해서 도출된 이동 시간을 반드시 작성해주세요.
최대한 유저의 입력 메시지의 조건을 만족해야 합니다.
반드시 여행 장소는 벡터저장소에 저장된 데이터에서 선택해야 합니다.
이때 시간별로 특정 숙소 이름, 식당 이름, 관광지 이름을 구체적으로 계획에 언급하고 있어야 합니다. 
이때 한번 간 식당이나 관광지는 다시 가지 않습니다. 
호텔 체크인부터 체크아웃까지 모두 포함되어야 합니다.
장소의 리뷰를 참고하여 장소의 간단한 설명도 추가해주세요.
실제로 벡터 저장소 내에 저장된 데이터에서 장소를 선택해 주세요.


assistant의 설명이 끝나면 한칸 띄우고 1일차 오전이 끝나면 한칸 띄우고, 
1일차 점심 뒤에 한칸 띄우고, 1일차 저녁 뒤에 한칸 띄우고, 2일차 오전이 끝나면 한칸 띄우고, 
2일차 점심 뒤에 한칸 띄우고, 2일차 저녁 뒤에 한칸 띄우고, 
3일차 오전 뒤에 한칸 띄우고, 체크아웃 후에 한칸 띄우고 그후에 assistant의 여행 계획 설명을 출력해줘. 

"""

#어시스턴트가 사용하는 툴 목록
tools = [
    {
        "type": "code_interpreter"
    },
    {
        "type": "file_search"
    },
    
]


class Chatbot:
    
    def __init__(self, **args):
        self.assistant = client.beta.assistants.retrieve(assistant_id = args.get("assistant_id"))
        self.thread = client.beta.threads.retrieve(thread_id=args.get("thread_id"))
        self.runs = list(client.beta.threads.runs.list(thread_id=args.get("thread_id")))
        
     
    @retry(tries=3, delay=2)
    def add_user_message(self, user_message):
        try:
            client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=user_message,
            )
        except openai.BadRequestError as e:
            if len(self.runs) > 0:
                print("add_user_message BadRequestError", e)
                client.beta.threads.runs.cancel(thread_id=self.thread.id, run_id=self.runs[0])
            raise e
        
    def _run_action(self, retrieved_run):
        tool_calls = retrieved_run.model_dump()['required_action']['submit_tool_outputs']['tool_calls']
        pprint(("tool_calls", tool_calls))
        tool_outputs=[]
        for tool_call in tool_calls:
            pprint(("tool_call", tool_call))
            id = tool_call["id"]
            function = tool_call["function"]
            func_name = function["name"]
            # 챗GPT가 알려준 함수명에 대응하는 실제 함수를 func_to_call에 담는다.
            func_to_call = self.available_functions[func_name]
            try:
                func_args = json.loads(function["arguments"])
                # 챗GPT가 알려주는 매개변수명과 값을 입력값으로하여 실제 함수를 호출한다.
                print("func_args:",func_args)
                func_response = func_to_call(**func_args)
                tool_outputs.append({
                    "tool_call_id": id,
                    "output": str(func_response)
                })
            except Exception as e:
                    print("_run_action error occurred:",e)
                    client.beta.threads.runs.cancel(thread_id=self.thread.id, run_id=retrieved_run.id)
                    raise e
                    
        client.beta.threads.runs.submit_tool_outputs(
            thread_id = self.thread.id, 
            run_id = retrieved_run.id, 
            tool_outputs= tool_outputs
        )    
    
    @retry(tries=3, delay=2)    
    def create_run(self):
        try:
            run = client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            self.runs.append(run.id)
            return run
        except openai.BadRequestError as e:
            if len(self.runs) > 0:
                print("create_run BadRequestError", e)
                client.beta.threads.runs.cancel(thread_id=self.thread.id, run_id=self.runs[0])
            raise e            
    # finance_chatbot.py 또는 Chatbot 클래스가 정의된 파일에 추가

    def save_response_to_file(self, response_text, filename="last_response.txt"):
        """응답을 텍스트 파일로 저장합니다."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response_text)
    def read_response_from_file(self, filename="last_response.txt"):
        """텍스트 파일에서 응답을 읽습니다."""
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
        
    def get_response_content(self, run) -> (openai.types.beta.threads.run.Run, str):

        max_polling_time = 180 # 최대 3분 동안 폴링합니다.
        start_time = time.time()

        retrieved_run = run
        
        while(True):
            elapsed_time  = time.time() - start_time
            if elapsed_time  > max_polling_time:
                client.beta.threads.runs.cancel(thread_id=self.thread.id, run_id=run.id)
                return retrieved_run, "대기 시간 초과(retrieve)입니다."
            
            retrieved_run = client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )            
            print(f"run status: {retrieved_run.status}, 경과:{elapsed_time: .2f}초")
            
            if retrieved_run.status == "completed":
                break
            elif retrieved_run.status == "requires_action":
                self._run_action(retrieved_run)
            elif retrieved_run.status in ["failed", "cancelled", "expired"]:
                # 실패, 취소, 만료 등 오류 상태 처리
                # raise ValueError(f"run status: {retrieved_run.status}, {retrieved_run.last_error}")
                code = retrieved_run.last_error.code
                message = retrieved_run.last_error.message
                return retrieved_run, f"{code}: {message}"
            
            time.sleep(1) 
            
        # Run이 완료된 후 메시지를 가져옵니다.
        self.messages = client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        resp_message = [m.content[0].text for m in self.messages if m.run_id == run.id][0]
        return retrieved_run, resp_message.value
        
    def get_interpreted_code(self, run_id):
        run_steps_dict = client.beta.threads.runs.steps.list(
            thread_id=self.thread.id,
            run_id=run_id
        ).model_dump()
        for run_step_data in run_steps_dict['data']:
            step_details = run_step_data['step_details']
            print("step_details", step_details)
            tool_calls = step_details.get('tool_calls', [])
            for tool_call in tool_calls:
                if tool_call['type'] == 'code_interpreter':
                    return tool_call['code_interpreter']['input']
        return ""


if __name__ == "__main__":
    
    ##어시스턴트 생성
    
    assistant = client.beta.assistants.create(
                    model=model.basic,  
                    name="여행 플래너 챗봇",
                    instructions=instructions_nofeedback ,
                    tools=tools,
                    
                )
    thread = client.beta.threads.create()    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 출력할 내용
    assistants_ids = f"{assistant.id}, {thread.id}"
    print(assistants_ids)   
    # 파일에 기록 
    with open("./assistants_ids.txt", "a") as file:
        file.write(f"{current_time} - {assistants_ids}\n")
    
    
    #벡터스토어 생성
    vector_store = client.beta.vector_stores.create(name="travel")

    file_paths = ["/workspace/firstcontainer/updated_lodgings_all.docx", "/workspace/firstcontainer/updated_restaurants_all.docx", "/workspace/firstcontainer/updated_tourist_attractions_all.docx"]
    
    file_streams = [open(path, "rb") for path in file_paths]

    # 파일 업로드 및 업로드 상태 폴링
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id, files=file_streams
    )

    # 파일 업로드 상태와 파일 개수 출력
    print(file_batch.status)
    print(file_batch.file_counts)

    # Assistant 업데이트하여 생성한 벡터 스토어와 연결
    updated_assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )
