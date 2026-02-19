"""Pelastusopisto-agentti"""

import json
from groq import Groq
from config import GROQ_API_KEY, MODEL
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS


class PelastusopistoAgent:
    """LLM-agentti joka osaa kayttaa fetch_page-tyokalua"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL
        self.conversation_history = []
        
        # System prompt - EI AAKKOSIA
        self.system_prompt = "Olet Pelastusopiston avustaja. Vastaat suomeksi kysymyksiin. Kayta fetch_page-tyokalua hakiessasi tietoa pelastusopisto.fi-sivustolta."
        
        print(f"Agentti alustettu (malli: {self.model})")
    
    def chat(self, user_message, max_iterations=5):
        """Laheta viesti agentille"""
        
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
            print(f"\n[Iteraatio {iteration + 1}/{max_iterations}]")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=2000
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                print(f"LLM haluaa kayttaa {len(message.tool_calls)} tyokalua")
                
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
                    
                    print(f"  Kutsutaan: {tool_name}({tool_args})")
                    
                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](**tool_args)
                        print(f"  Status: {result.get('status', 'unknown')}")
                    else:
                        result = {"status": "error", "content": f"Tuntematon tyokalu: {tool_name}"}
                    
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                continue
            
            else:
                print("LLM antoi lopullisen vastauksen")
                
                final_answer = message.content or ""
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_answer
                })
                
                return final_answer
        
        return "Virhe: Liian monta iteraatiota"
    
    def reset(self):
        """Tyhjenna keskusteluhistoria"""
        self.conversation_history = []
        print("Historia tyhjennetty")
```

---

## **Commit changes:**
```
Commit message: "Fix unicode encoding"
Commit changes
```

---

## **Streamlit automaattisesti redeploy:**
```
Odota 1-2 minuuttia
Streamlit huomaa muutoksen
Redeploy automaattisesti
Kokeile uudelleen!
