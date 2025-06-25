# LangGraph Summarizer Agent

This project uses **LangGraph**, **LangChain**, and **FastMCP** to build a multi-agent AI system that retrieves real-time information from the web and summarizes it based on user queries — for example:  
> "Summarize what happened in the latest F1 Grand Prix."

## 🧠 Architecture

The system is composed of 3 agent nodes:

1. **Planner Agent**  
   - Determines what information needs to be retrieved based on the user query  
   - Can call the `retrieve_information` tool up to 3 times

2. **Retriever Tool (MCP server)**  
   - Uses the [Tavily API](https://app.tavily.com) to perform live web searches  
   - Saves retrieved content to `retrieved_result.json`

3. **Summarizer Agent**  
   - Reads the JSON file and generates a concise, high-quality summary using LLM

## 🛠 Technologies Used

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [FastMCP](https://github.com/langchain-ai/mcp)
- [Tavily API](https://www.tavily.com/)
- [Groq API](https://console.groq.com/)
- Python 3.10+

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/your-username/langgraph-event-summarizer
cd langgraph-event-summarizer
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your .env file

```bash
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 4. Run the server

```bash
python retriever_server.py
```

### 5. Run the app

```bash
python client.py
```