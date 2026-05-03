import os
from langchain_google_genai import ChatGoogleGenerativeAI
from supabase import create_client, Client
from dotenv import load_dotenv
from models import AgentState

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", temperature=1.0
).with_structured_output(AgentState)
