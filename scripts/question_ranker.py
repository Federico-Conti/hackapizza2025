import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ibm.llms import WatsonxLLM
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

# Define the Question_type Enum
class Question_type(str, Enum):
    sbd = "Suggestion by distance"
    sbs = "Suggestion by ingredients"

# Define the Question_info Pydantic model
class Question_info(BaseModel):
    question: str = Field(..., title="Text", description="Text to evaluate")
    action: List[Question_type] = Field(..., title="Action Type", description="Action types to solve the question")

    class Config:
        arbitrary_types_allowed = True

# Function to load a CSV file and return a DataFrame
def load_csv(file_path):
    """Load CSV and return a DataFrame."""
    df = pd.read_csv(file_path)
    print("First 5 rows of the dataset:")
    print(df.head())
    return df

# Function to generate structured rankings using LangChain
def generate_rankings(questions, llm, template):
    """Generate structured rankings for questions using LangChain."""
    ranked_data = []
    for question in questions:
        # Create a prompt template with expected JSON output
        prompt = PromptTemplate(
            input_variables=["question"],
            template=template
        )
        print("question",question) 
        # Run the LLM chain
        llm_chain = prompt | llm
        result = llm_chain.run(question)

        # Parse the result into the structured Pydantic model
        try:
            parsed_result = Question_info.parse_raw(result)
            ranked_data.append(parsed_result.dict())
        except Exception as e:
            print(f"Failed to parse result for question: {question}. Error: {e}")
            continue
    return ranked_data

# Main function to orchestrate the workflow
def main(file_path, llm_api_key):
    # Load the dataset
    df = load_csv(file_path)
    if 'Question' not in df.columns:
        print("Error: The dataset must have a 'Question' column.")
        return

    # Initialize the WatsonxLLM model
    llm = WatsonxLLM(
        model_id="meta-llama/llama-3-3-70b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        apikey="AwfatdGk3za6K3e6Zn2KSE4WM4VBAjgMAxKSLM6IdilQ",
        project_id="e8e3fe0c-90f3-4897-858a-e7f659d21bb2",
    )

    # Define the prompt template
    template = (
        "You are an assistant that ranks questions based on their relevance to specific tasks. "
        "Given the following question, categorize and rank it in a structured JSON format. "
        "Output should strictly match the following JSON schema:\n\n"
        "{"
        "  'question': '<string>',"
        "  'action': ['<string>']"
        "}\n\n"
        "Question: {question}\n"
        "Output:"
    )

    # Generate rankings
    questions = df['Question'].tolist()
    ranked_data = generate_rankings(questions, llm, template)

    if not ranked_data:
        print("Failed to generate rankings.")
        return

    # Convert rankings to DataFrame
    ranked_df = pd.DataFrame(ranked_data)

    # Save the result
    output_path = 'ranked_questions.csv'
    ranked_df.to_csv(output_path, index=False)
    print(f"Ranked questions saved to {output_path}")

# Example usage (Replace with your API key)
if __name__ == "__main__":
    main('domande.csv', 'your_api_key_here')
