import json
import requests
from config import GROQ_API_KEY, MODEL
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS

class PelastusopistoAgent:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = MODEL
        self.conversation_history = []
        self.system_prompt = "Answer in Finnish"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def chat(self, user_message, max_iterations=5):
        user_message = str(user_message).encode('ascii', 'ignore').decode('ascii')
        
        if not self.conversation_history:
            self.conversation_history.append({"role": "system", "content": self.system_prompt})
        
        self.conversation_history.append({"role": "user", "content": user_message})
        
        for i in range(max_iterations):
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": self.conversation_history,
                "tools": TOOLS_SCHEMA,
                "tool_choice": "auto",
                "max_tokens": 2000
            }
            
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"API Error: {str(e)}"
            
            msg = data['choices'][0]['message']
            
            if 'tool_calls' in msg and msg['tool_calls']:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": msg.get('content', ''),
                    "tool_calls": msg['tool_calls']
                })
                
                for tc in msg['tool_calls']:
                    name = tc['function']['name']
                    args = json.loads(tc['function']['arguments'])
                    
                    if name in TOOL_FUNCTIONS:
                        res = TOOL_FUNCTIONS[name](**args)
                    else:
                        res = {"status": "error", "content": "Unknown"}
                    
                    res_str = json.dumps(res, ensure_ascii=True)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tc['id'],
                        "content": res_str
                    })
                continue
            
            answer = msg.get('content', 'No response')
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer
        
        return "Too many iterations"
    
    def reset(self):
        self.conversation_history = []