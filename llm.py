from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal

class LLM:
    MessageType = Literal["system", "human", "ai"]

    def __init__(self, model):
        self.ollama = OllamaLLM(model=model)

    def generate(self, prompt: list[tuple[MessageType, str]]):
        chat_template = ChatPromptTemplate.from_messages(prompt)
        chain = chat_template | self.ollama
        result = chain.invoke({})
        return result
    
    @staticmethod
    def create_message(type: MessageType, message: str):
        return (type, message)
