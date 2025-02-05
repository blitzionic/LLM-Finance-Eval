import os
import openai
import json
from dotenv import load_dotenv
from abc import ABC, abstractmethod

load_dotenv()

class Agent(ABC):
    def __init__(self, model="gpt-4o", pyd_model=None):
        self.model = model
        self.pyd_model = pyd_model
        self.api_key = os.getenv("OPENAI_API_KEY") 
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPEN_AI_KEY environment variable.")
        openai.api_key = self.api_key
        # Initialize function_schema to None; subclasses can set it as needed.
        self.function_schema = None

    @abstractmethod
    def system_prompt(self):
        # This method must be implemented in each subclass.
        pass

    def generate_response(self, prompt, temperature=0, max_tokens=1000, stop=None):
      try:
        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        if self.function_schema:
          response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            functions=[self.function_schema],
            function_call={"name": self.function_schema.get("name")},
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
          )
          
        message = response.choices[0].message
        # Extract the JSON arguments returned by the function call.
        arguments = message.get("function_call", {}).get("arguments", "{}")
        return json.loads(arguments)
        
        return response.choices[0].message["content"].strip()
      except Exception as e:
          print(f"Error generating response for Base Agent: {}")
          return {}
