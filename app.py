import os
import uuid
from typing import Annotated, List, TypedDict
import operator
from dotenv import load_dotenv
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver

load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="AI Startup Incubator", page_icon="🚀", layout="wide")

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str

# --- LLM ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# --- Worker Nodes ---
def researcher_agent(state: AgentState):
    original_idea = state["messages"][0].content
    response = llm.invoke([
        HumanMessage(content=f"Market Researcher Role: Provide a brief market analysis for this startup idea: {original_idea}. Focus on target audience and competition.")
    ])
    response.content = f"MARKET_REPORT: {response.content}"
    return {"messages": [response]}

def designer_agent(state: AgentState):
    original_idea = state["messages"][0].content
    response = llm.invoke([
        HumanMessage(content=f"Product Designer Role: Create a 3-point feature list for: {original_idea}.")
    ])
    response.content = f"DESIGN_SPECS: {response.content}"
    return {"messages": [response]}

# --- Supervisor ---
def ceo_supervisor(state: AgentState):
    history = [m.content for m in state["messages"]]
    full_history_text = "\n".join(history)

    if "MARKET_REPORT:" not in full_history_text:
        return {"next_agent": "researcher"}
    if "DESIGN_SPECS:" not in full_history_text:
        return {"next_agent": "designer"}
    return {"next_agent": "end"}

# --- Build Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_agent)
workflow.add_node("designer", designer_agent)
workflow.add_node("ceo", ceo_supervisor)
workflow.set_entry_point("ceo")
workflow.add_conditional_edges(
    "ceo",
    lambda x: x["next_agent"],
    {"researcher": "researcher", "designer": "designer", "end": END},
)
workflow.add_edge("researcher", "ceo")
workflow.add_edge("designer", "ceo")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "multi_agent_orchestration")

# --- Streamlit UI ---
st.title("🚀 AI Startup Incubator")
st.markdown("Enter your startup idea and let the AI team — **CEO**, **Market Researcher**, and **Product Designer** — evaluate it for you.")

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "result" not in st.session_state:
    st.session_state.result = None

# Sidebar: past session info
with st.sidebar:
    st.header("Session Info")
    st.caption(f"Thread ID: `{st.session_state.thread_id}`")
    if st.button("🔄 New Session"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.result = None
        st.rerun()

# Input form
with st.form("idea_form"):
    user_idea = st.text_area("What is your startup idea?", height=100, placeholder="e.g. AI-powered food delivery platform...")
    submitted = st.form_submit_button("🚀 Evaluate My Idea")

if submitted and user_idea.strip():
    initial_input = {"messages": [HumanMessage(content=user_idea.strip())]}
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with MongoDBSaver.from_conn_string(MONGODB_URI, DB_NAME) as checkpointer:
        app = workflow.compile(checkpointer=checkpointer)

        status_container = st.empty()
        progress_bar = st.progress(0)

        steps = ["CEO reviewing project...", "Researcher analyzing market...", "Designer drafting specs...", "CEO finalizing..."]
        step_idx = 0

        for output in app.stream(initial_input, config):
            node_name = list(output.keys())[0]
            label = {
                "ceo": "🤵 CEO is reviewing the project status...",
                "researcher": "🔬 Researcher is analyzing market trends...",
                "designer": "🎨 Designer is drafting product specifications...",
            }.get(node_name, f"Running {node_name}...")
            status_container.info(label)
            step_idx += 1
            progress_bar.progress(min(step_idx / 4, 1.0))

        progress_bar.progress(1.0)
        status_container.success("✅ Evaluation complete!")

        final_state = app.get_state(config)
        st.session_state.result = final_state.values["messages"]

# Display results
if st.session_state.result:
    st.markdown("---")
    st.header("📋 CEO's Final Startup Prospectus")

    for msg in st.session_state.result:
        if isinstance(msg, AIMessage):
            content = msg.content
            if content.startswith("MARKET_REPORT:"):
                st.subheader("🔬 Market Research Report")
                st.markdown(content.replace("MARKET_REPORT: ", "", 1))
            elif content.startswith("DESIGN_SPECS:"):
                st.subheader("🎨 Product Design Specifications")
                st.markdown(content.replace("DESIGN_SPECS: ", "", 1))
            else:
                st.markdown(content)
elif submitted:
    st.warning("Please enter a startup idea before submitting.")
