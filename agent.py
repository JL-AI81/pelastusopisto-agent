"""Pelastusopisto-agentti"""

import json
from groq import Groq
from config import GROQ_API_KEY, MODEL
from tools import TOOLS_SCHEMA, TOOL_FUNCTIONS


class PelastusopistoAgent:
    """LLM-agentti joka osaa käyttää fetch_page-työkalua"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL
        self.conversation_history = []
        
        # System prompt
        self.system_prompt = """Olet Pelastusopiston avustaja. 
Vastaat suomeksi kysymyksiin jotka liittyvät Pelastusopistoon.
Käytä fetch_page-työkalua hakiessasi tietoa pelastusopisto.fi-sivustolta.
Tiivistä haettu tieto selkeästi käyttäjälle."""
        
        print(f"✓ Agentti alustettu (malli: {self.model})")
    
    def chat(self, user_message, max_iterations=5):
        """
        Lähetä viesti agentille.
        
        Args:
            user_message (str): Käyttäjän viesti
            max_iterations (int): Max tool calling -kierroksia
            
        Returns:
            str: Agentin vastaus
        """
        # Lisää käyttäjän viesti historiaan
        if not self.conversation_history:
            # Ensimmäinen viesti, lisää system prompt
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Tool calling -loop
        for iteration in range(max_iterations):
            print(f"\n[Iteraatio {iteration + 1}/{max_iterations}]")
            
            # Kutsu Groq API:a
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=2000
            )
            
            message = response.choices[0].message
            
            # Onko tool calls?
            if message.tool_calls:
                print(f"→ LLM haluaa käyttää {len(message.tool_calls)} työkalua")
                
                # Lisää LLM:n vastaus historiaan
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
                
                # Suorita työkalut
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"  → Kutsutaan: {tool_name}({tool_args})")
                    
                    # Suorita työkalu
                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](**tool_args)
                        print(f"  ← Status: {result.get('status', 'unknown')}")
                    else:
                        result = {"status": "error", "content": f"Tuntematon työkalu: {tool_name}"}
                    
                    # Lisää tulos historiaan
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                # Jatka looppia
                continue
            
            else:
                # Ei tool calls, lopullinen vastaus
                print("→ LLM antoi lopullisen vastauksen")
                
                final_answer = message.content or ""
                
                # Lisää historiaan
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_answer
                })
                
                return final_answer
        
        # Max iteraatiot ylitetty
        return "Virhe: Liian monta iteraatiota"
    
    def reset(self):
        """Tyhjennä keskusteluhistoria"""
        self.conversation_history = []
        print("✓ Historia tyhjennetty")