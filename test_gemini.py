
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_name = "gemini-3.5-flash-lite"

print("Testing model:", model_name)
print("Sending request to Gemini...")


llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    timeout=120,
    max_retries=0
)


try:
    response = llm.invoke("Reply with only: Gemini is working")
    print("Response:", response.content)
except Exception as e:
    print("Error:", repr(e))
