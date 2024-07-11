개발환경: Groom IDE, Python, Flask, Chromedriver, Selenium...
사용한 패키지 버전은 논문에 언급되어 있다.
Groom IDE에서 Flask 컨테이너 생성후 프로젝트 생성하기.

-가장 먼저 웹 어플리케이션 실행 전에 OPENAI키와 CREDIT이 필요하다.
OPENAI 서비스 이용을 위해서는 OPENAI에서 로그인 후, 
새로운 개인키를 발급받아야 한다.
(https://platform.openai.com/api-keys)

OPENAI API 사이트에서 credit balance를 결제해두고 
어시스턴트 생성이나 데이터 저장, 답변 생성등에 이용할 수 있다.
(https://platform.openai.com/settings/organization/billing/overview)

각 GPT모델마다 비용이 다르니 참고할 것.
(https://openai.com/api/pricing/)



-웹 어플리케이션을 통해 챗봇 실행
1. common.py 실행
common.py의 mykey에는 openai 본인 키를 넣을 것. 
class model에서 사용하고자 하는 gpt모델의 종류를 작성할 수 있다. 
그 후 실행한다.
(+ FLASK 서버 구동)

2. travel_chatbot.py 실행
travel_chatbot.py 실행후 생성된 어시스턴트의 아이디와 쓰레드 아이디를
application.py의 챗봇 인스턴트 생성에 입력할 것. 
그 후 저장한다.

3. application.py 실행

4. 웹 애플리케이션 실행한다.
https://firstcontainer-mxmwz.run.goorm.site/chat-app 
에서 웹 애플리케이션 사용가능하다.



-OPENAI Playground에서 어시스턴트 실행
새로운 어시스턴트를 Playground 환경에서 간단하게 생성하고 실행할 수 있음.
(https://platform.openai.com/playground/assistants)

1. 벡터 저장소를 생성하여 데이터를 업로드 해두고 어시스턴트 생성 때 연결해야 한다.
(https://platform.openai.com/storage/vector_stores)

2. Assistant의 Name, Instructions, Model, Tools 옵션을 통해 기존과 동일하게 설정 가능.

3. 생성후 스레드 칸에 입력하면 이에 대한 어시스턴트의 답변을 받을 수 있다. 