"""Pelastusopisto-agentti"""

import json
from groq import Groq
from config import GROQ_API_KEY, MODEL
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS


class PelastusopistoAgent:
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL
        self.conversation_history = []
        self.system_prompt = "Olet Pelastusopiston avustaja. Vastaat suomeksi."
        print("Agentti alustettu")
    
    def chat(self, user_message, max_iterations=5):
        
        if not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        for iteration in range(max_iterations):
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=2000
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](**tool_args)
                    else:
                        result = {"status": "error", "content": "Tuntematon tyokalu"}
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                continue
            
            else:
                final_answer = message.content or ""
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_answer
                })
                
                return final_answer
        
        return "Liian monta iteraatiota"
    
    def reset(self):
        self.conversation_history = []
