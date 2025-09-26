from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel

from fastapi import FastAPI
from agents.support.agent import agent
from langchain_core.messages import HumanMessage
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}



class Message(BaseModel):
    message: str

@app.post("/chat/{chat_id}")
async def chat(chat_id: str, item: Message):
    human_message = HumanMessage(content=item.message)
    response = agent.invoke({"messages": [human_message]})
    last_message = response["messages"][-1]
    return last_message.text


@app.post("/chat/{chat_id}/stream")
async def stream_chat(chat_id: str, message: Message):
    human_message = HumanMessage(content=message.message)
    async def generate_response():
        for message_chunk, metadata in agent.stream({"messages": [human_message]}, stream_mode="messages"):
            if message_chunk.content:
                yield f"data: {message_chunk.content}\n\n"

        print(message_chunk.content, end="|", flush=True)

    return StreamingResponse(generate_response(), media_type="text/event-stream")