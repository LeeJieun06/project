from flask import Flask, render_template, request 
import sys
from travel_chatbot import Chatbot

#travel_chatbot.py 실행한 후 생성된 어시스턴트의 id와 스레드 id 입력.

travel = Chatbot(
    assistant_id="asst_qXABMJ3MiHF8V879mxv6qed6",
    thread_id="thread_9n8TXZ5nXYfN6ddly1cBzGyQ"
)
import re
##임시 포맷팅 함수
def format_travel_plan_html(plan_text):
    """주어진 텍스트를 HTML로 변환하고, 특정 일차를 볼드 처리하며 이동 시간에 특정 스타일을 적용합니다."""
    # **로 둘러싸인 텍스트를 볼드 처리
    plan_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', plan_text)

    # 볼드 처리할 텍스트 지정
    bold_terms = {"1일차:", "2일차:", "3일차:"}
    for term in bold_terms:
        plan_text = plan_text.replace(term, f"<strong>{term}</strong>")
    
    # 이동 시간에 스타일 적용
    plan_text = plan_text.replace("이동 시간:", "<span class='travel-time'>이동 시간:</span>")
    
    # HTML로 변환
    html_content = plan_text.replace("###", "<h3>").replace("####", "<h4>").replace(" - ", "</h4><p>").replace("\n", "</p><p>") + "</p>"
    return f"<div>{html_content}</div>"

    

application = Flask(__name__)

@application.route("/chat-app")
def chat_app():
    return render_template("chat.html")

@application.route('/chat-api', methods=['POST'])
def chat_api():
    request_message = request.form.get("message")
    print("request_message:", request_message)
    try: 
        travel.add_user_message(request_message)
        run = travel.create_run()
        _, response_message = travel.get_response_content(run)
        response_html = format_travel_plan_html(response_message)  # 챗봇 응답을 HTML로 변환
        #response_python_code = travel.get_interpreted_code(run.id)
    except Exception as e:
        print("assistants ai error", e)
        response_html = "<p>[Assistants API 오류가 발생했습니다]</p>"
            
    print("response_html:", response_html)
    return {"response_message": response_html}#, "response_python_code": response_python_code}
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))#int(sys.argv[1]

