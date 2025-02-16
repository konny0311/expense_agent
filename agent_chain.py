import os
import tempfile
import uuid
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from streamlit.runtime.uploaded_file_manager import UploadedFile

import tools_defintion

SYSTEM_PROMPT = "あなたは経理専門家です。ユーザーからの作業依頼や問い合わせに快く回答してください。なお、あなたは関西出身で、優しい関西弁を話します。（例：〜やで、〜なんやな）"

prompt = ChatPromptTemplate.from_messages(
    [
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"), 
    ("human", "{inquiry}"),
    ]
)

model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0).bind_tools(tools_defintion.tools)

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow.add_node("model", call_model)
workflow.add_node("tools", tools_defintion.tool_node)

workflow.add_edge(START, "model")
workflow.add_conditional_edges("model", should_continue, ["tools", END])
workflow.add_edge("tools", "model")

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

def handle_uploaded_file(uploaded_file: UploadedFile) -> tuple[str, str]:
    """アップロードされたファイルを一時ファイルとして保存し、パスを返す"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        abs_path = os.path.abspath(tmp_file.name)
    return abs_path, f"\n 領収書画像の情報は以下の通りです。\n ファイル名: {uploaded_file.name}\n ファイルパス: {abs_path}"

def create_input_messages(user_message: str) -> list[dict]:
    """入力メッセージを作成する"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

def call_agent(user_message: str, thread_id: uuid.UUID, uploaded_file: Optional[UploadedFile] = None) -> tuple[uuid.UUID, str]:
    """エージェントを呼び出し、応答を返す"""
    print("thread id:", thread_id)
    print("uploaded_file:", uploaded_file)
    
    temp_file_path = None
    try:
        if uploaded_file:
            temp_file_path, file_info = handle_uploaded_file(uploaded_file)
            user_message += file_info

        input_messages = create_input_messages(user_message)
        config = {"configurable": {"thread_id": thread_id}}

        agent_response = app.invoke({"messages": input_messages}, config)
        print("agent_response:", agent_response)
        return thread_id, agent_response["messages"][-1].content

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return thread_id, f"エラーが発生しました: {str(e)}"

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"画像を削除しました。{temp_file_path}")

