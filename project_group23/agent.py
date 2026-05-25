import os
import json
import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# Configure local LLM model
MODEL_NAME = "qwen3.5:9b"

# Define tools querying the output files directly
@tool
def get_industry_posting_count(industry_name: str) -> str:
    """Queries the dataset and returns the number of full-time postings for the given industry name.
    Useful for answering questions about industry posting volume.
    """
    try:
        # Check if output directory exists, adjust path if needed
        filepath = "output/industry_posting_counts.csv"
        if not os.path.exists(filepath):
            filepath = "project_group23/output/industry_posting_counts.csv"
            
        df = pd.read_csv(filepath)
        match = df[df['industry_name'].str.lower() == industry_name.lower()]
        if not match.empty:
            count = match.iloc[0]['posting_count']
            return f"Industry '{industry_name}' has {count} full-time job postings."
        else:
            return f"Industry '{industry_name}' was not found in the dataset."
    except Exception as e:
        return f"Error querying dataset: {str(e)}"

@tool
def get_top_industries(n: int = 5) -> str:
    """Returns the top N industries by number of full-time postings.
    Useful for answering questions about which industries are the largest by volume.
    """
    try:
        filepath = "output/industry_posting_counts.csv"
        if not os.path.exists(filepath):
            filepath = "project_group23/output/industry_posting_counts.csv"

        df = pd.read_csv(filepath)
        top_n = df.head(n)
        result = "Top industries by posting count:\n"
        for i, row in top_n.iterrows():
            result += f"{i+1}. {row['industry_name']}: {row['posting_count']} postings\n"
        return result
    except Exception as e:
        return f"Error loading top industries: {str(e)}"

@tool
def get_top_countries(n: int = 5) -> str:
    """Returns the top N countries by number of companies in the dataset.
    Useful for answering questions about the geographic distribution of companies.
    """
    try:
        filepath = "output/top_countries.json"
        if not os.path.exists(filepath):
            filepath = "project_group23/output/top_countries.json"

        with open(filepath, "r") as f:
            data = json.load(f)
        top_countries = data.get("top_countries", [])[:n]
        result = "Top countries by number of companies:\n"
        for i, country in enumerate(top_countries):
            result += f"{i+1}. {country['country']}: {country['count']} companies\n"
        return result
    except Exception as e:
        return f"Error loading top countries: {str(e)}"

# List of tools
tools = [get_industry_posting_count, get_top_industries, get_top_countries]

# ReAct Agent Prompt Template
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

def main():
    print(f"Connecting to local Ollama with model: {MODEL_NAME}")
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    print("\n--- Data Agent CLI ---")
    print("Ask the agent questions about your LinkedIn Job Postings findings.")
    print("Press Ctrl+C or type 'exit' to quit.\n")
    
    default_question = "How many full-time postings does the Financial Services industry have, and which are the top 3 countries by company count in our dataset?"
    print(f"Demo question: {default_question}")
    print("Running demo...\n")
    
    try:
        agent_executor.invoke({"input": default_question})
    except Exception as e:
        print(f"\nError running demo: {str(e)}")
        print("Make sure your local Ollama server is running (ollama run qwen3.5:9b).")
        
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
            
            print("Thinking...\n")
            response = agent_executor.invoke({"input": user_input})
            print("\nFinal Answer:\n", response["output"])
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
