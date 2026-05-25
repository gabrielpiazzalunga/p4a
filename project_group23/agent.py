import os
import json
import pandas as pd
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent

# Configure local LLM model
MODEL_NAME = "llama3.2"

# Define tools querying the output files or static data directly
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
def get_medical_insurance_benefits() -> str:
    """Returns the top industries offering medical insurance benefits and their posting counts.
    Useful for answering questions about which industries are most generous with medical insurance.
    """
    return (
        "Top industries by medical insurance benefits postings:\n"
        "1. Hospitals and Health Care: 235 postings\n"
        "2. Staffing and Recruiting: 130 postings\n"
        "3. Financial Services: 121 postings\n"
        "4. Construction: 116 postings\n"
        "5. IT Services and IT Consulting: 92 postings\n"
        "6. Manufacturing: 91 postings\n"
        "7. Insurance: 77 postings\n"
        "8. Defense and Space Manufacturing: 75 postings\n"
        "9. Business Consulting and Services: 71 postings\n"
        "10. Law Practice: 71 postings"
    )

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
tools = [get_industry_posting_count, get_top_industries, get_medical_insurance_benefits, get_top_countries]

def main():
    print(f"Connecting to local Ollama with model: {MODEL_NAME}")
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    
    # Initialize the Agent Graph
    agent_executor = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a helpful data assistant. Use your tools to answer questions about the LinkedIn job postings and companies dataset."
    )
    
    print("\n--- Data Agent CLI ---")
    print("Running your 3 project questions to generate execution traces...\n")
    
    project_questions = [
        "Based on our job postings dataset, what are the top industries by volume of listings, and which of these are the most generous in providing medical insurance?",
        "Why do you think Retail has so many job postings but almost no postings listing medical insurance compared to Hospitals and Health Care or Financial Services?",
        "Given this benefit gap in retail, how can we use this data to advise a job board or recruitment agency on how to target employer outreach or improve listing conversions?"
    ]
    
    for i, question in enumerate(project_questions, 1):
        print(f"\n=======================================================")
        print(f"PROJECT QUESTION {i}: {question}")
        print(f"=======================================================")
        print("Running agent...\n")
        
        try:
            inputs = {"messages": [{"role": "user", "content": question}]}
            response = agent_executor.invoke(inputs)
            
            print("--- Agent Execution Trace ---")
            for msg in response["messages"]:
                role = msg.__class__.__name__.replace("Message", "")
                print(f"\n[{role}]:")
                print(msg.content)
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"Tool Calls: {json.dumps(msg.tool_calls, indent=2)}")
            
            print("\nFinal Answer:\n", response["messages"][-1].content)
        except Exception as e:
            print(f"\nError running Question {i}: {str(e)}")
            print("Make sure your local Ollama server is running (ollama run llama3.2).")
            
    print("\n\n--- Interactive Mode ---")
    print("Ask any other questions. Press Ctrl+C or type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue
            
            print("Thinking...\n")
            inputs = {"messages": [{"role": "user", "content": user_input}]}
            response = agent_executor.invoke(inputs)
            
            print("\n--- Agent Execution Trace ---")
            for msg in response["messages"]:
                role = msg.__class__.__name__.replace("Message", "")
                print(f"\n[{role}]:")
                print(msg.content)
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"Tool Calls: {json.dumps(msg.tool_calls, indent=2)}")
            
            print("\nFinal Answer:\n", response["messages"][-1].content)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
