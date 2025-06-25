from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import asyncio
import os
import json

# preparing api keys
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


# setting up graph components
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def summarizer_agent(state: AgentState) -> AgentState:
    ("Summarizing\n")
    try:
        with open("retrieved_result.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        return {"messages": state["messages"] + [SystemMessage(content=f"Error reading file: {e}")]}
    
    retrieved_info = "\n\n".join(item["content"] for item in data)
    
    query = state["messages"][0].content

    message = HumanMessage(content=f"""
    Based on my query:
    {query}

    And the retrieved information below:

    {retrieved_info}

    Write a concise, informative summary. 
    """)

    system_prompt = SystemMessage(content=f"""
    You are a summarizer agent, that gets some real time retrieved info, and
    summarizes it to the user based on their query.
    """)

    model = ChatGroq(model="qwen-qwq-32b")
    response = model.invoke([system_prompt] + [message])

    return {"messages": [response]}


def planner_router(state: AgentState) -> str:
        last_message = state['messages'][-1]

        if isinstance(last_message, AIMessage) and not last_message.tool_calls:
            return 'summarize'
        else:
            return 'tool'



async def main():
    if os.path.exists("retrieved_result.json"):
        os.remove("retrieved_result.json")

    ## Client setup

    client = MultiServerMCPClient(
        {
            "retrieve": {
                "command":"python",
                "args":["retrieve_server.py"],
                "transport":"stdio"
            }
        }
    )
    tools = await client.get_tools()


    ## Planner agent set up
    model = ChatGroq(model="qwen-qwq-32b").bind_tools(tools)

    def planner_agent(state: AgentState) -> AgentState:
        print("Entered planning tool\n")
        if os.path.exists("retrieved_result.json"):
            try:
                with open("retrieved_result.json", "r") as f:
                    data = json.load(f)
            except Exception as e:
                return {"messages": state["messages"] + [SystemMessage(content=f"Error reading file: {e}")]}
        else:
            data = []

        system_prompt = SystemMessage(content= f"""
        You are a planner agent.

        The user has asked for a summary of a recent event. Your job is to plan what information needs to be retrieved from the web using the `retrieve_information` tool, so the summarizer can write a high-quality, accurate summary.

        You may call the tool **up to 3 times**, but only when the current data does not already provide enough information.

        ### Tool input format:
        You must use the tool with valid JSON input in the following format:
        ```json
        {{ "query": "your search phrase here" }}

        Example:                              
        If the user asks: "summarize what happened in the latest F1 Grand Prix", 
        you should first search to find what the latest F1 race was, then search for results or news about that race.

        current retrieved data: {data}          
        
        """)
        
        query = [system_prompt] + state["messages"]

        response = model.invoke(query)

        return {'messages': [response]}

    
    ## Building the graph
    
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_agent)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("summarizer", summarizer_agent)

    graph.add_edge(START, "planner")
    graph.add_conditional_edges(
        "planner",
        planner_router,
        {
            'summarize': 'summarizer',
            'tool': 'tools'
        }
    )
    graph.add_edge('tools', 'planner')
    graph.add_edge('summarizer', END)

    app = graph.compile()


    ## Running the app
    query = input("What would you like me to summarize? ")
    result = await app.ainvoke({'messages': HumanMessage(content=query)})
    summary = result['messages'][-1].content
    print("\n Summary: \n")
    print(summary)



if __name__ == "__main__":
    asyncio.run(main())

