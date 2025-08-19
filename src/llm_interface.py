"""
LLM interface for GigaCAD - supports both Groq API and local LMStudio
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import requests
from groq import Groq
from .config import config

class LLMInterface(ABC):
    """Abstract base class for LLM interfaces"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_message: str = "", 
                      temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], 
                                system_message: str = "") -> Dict[str, Any]:
        """Generate response with tool calling capabilities"""
        pass

class GroqInterface(LLMInterface):
    """Interface for Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
    
    async def generate(self, prompt: str, system_message: str = "", 
                      temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text using Groq API"""
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], 
                                system_message: str = "") -> Dict[str, Any]:
        """Generate response with tool calling using Groq"""
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            result = {
                "content": response.choices[0].message.content,
                "tool_calls": []
            }
            
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            return result
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

class LMStudioInterface(LLMInterface):
    """Interface for local LMStudio endpoint"""
    
    def __init__(self):
        self.base_url = config.LMSTUDIO_BASE_URL
        self.model = config.LMSTUDIO_MODEL
    
    async def generate(self, prompt: str, system_message: str = "", 
                      temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text using local LMStudio"""
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"LMStudio error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"LMStudio error: {str(e)}")
    
    async def generate_with_tools(self, prompt: str, tools: List[Dict[str, Any]], 
                                system_message: str = "") -> Dict[str, Any]:
        """Generate response with tool calling using LMStudio"""
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto"
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"LMStudio error: {response.status_code} - {response.text}")
            
            result = response.json()
            response_data = {
                "content": result["choices"][0]["message"]["content"],
                "tool_calls": []
            }
            
            if "tool_calls" in result["choices"][0]["message"]:
                for tool_call in result["choices"][0]["message"]["tool_calls"]:
                    response_data["tool_calls"].append({
                        "id": tool_call["id"],
                        "function": {
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"]
                        }
                    })
            
            return response_data
        except Exception as e:
            raise Exception(f"LMStudio error: {str(e)}")

class LLMFactory:
    """Factory for creating LLM interfaces"""
    
    @staticmethod
    def create_interface(llm_type: str = "groq") -> LLMInterface:
        """Create LLM interface based on type"""
        if llm_type.lower() == "groq":
            return GroqInterface()
        elif llm_type.lower() == "lmstudio":
            return LMStudioInterface()
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}") 