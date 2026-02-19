import json
from groq import Groq
from config import GROQ_API_KEY, MODEL
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS

class PelastusopistoAgent:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL
        self.conversation_history = []
        self.system_prompt = "Answer in Finnish"
    
    def chat(self, user_message, max_iterations=5):
        user_message = str(user_message).encode('ascii', 'ignore').decode('ascii')
        
        if not self.conversation_history:
            self.conversation_history.append({"role": "system", "content": self.system_prompt})
        
        self.conversation_history.append({"role": "user", "content": user_message})
        
        for i in range(max_iterations):
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=2000
            )
            
            msg = resp.choices[0].message
            
            if msg.tool_calls:
                tc_list = []
                for tc in msg.tool_calls:
                    tc_list.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": tc_list
                })
                
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    
                    if name in TOOL_FUNCTIONS:
                        res = TOOL_FUNCTIONS[name](**args)
                    else:
                        res = {"status": "error", "content": "Unknown"}
                    
                    res_str = json.dumps(res, ensure_ascii=True)
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": res_str
                    })
                continue
            
            answer = msg.content or "No response"
            self.conversation_history.append({"role": "assistant", "content": answer})
            return answer
        
        return "Too many iterations"
    
    def reset(self):
        self.conversation_history = []