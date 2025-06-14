import pandas as pd
import json
from groq import Groq
import tempfile

def extract_text_from_excel(file_path: str) -> str:
    try:
        df = pd.read_excel(file_path)
        return df.to_string()
    except Exception as e:
        return f"Error reading Excel file: {str(e)}"

def modify_excel_with_ai(file_path: str, instructions: str, groq_client: Groq) -> str:
    df = pd.read_excel(file_path)
    
    data_sample = df.head(10).to_dict('records')
    columns = df.columns.tolist()
    
    prompt = f"""
    You are an Excel data modification assistant. Given the following data structure and instructions, provide Python pandas code to modify the data.
    
    Columns: {columns}
    Sample Data: {json.dumps(data_sample, indent=2)}
    
    Instructions: {instructions}
    
    Provide only the pandas code that modifies the dataframe 'df'. Do not include imports or explanations.
    Example format:
    df['new_column'] = df['existing_column'] * 2
    df = df.dropna()
    """
    
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=1024
    )
    
    code = response.choices[0].message.content.strip()
    
    try:
        exec(code, {"df": df, "pd": pd})
        
        output_path = tempfile.mktemp(suffix='.xlsx')
        df.to_excel(output_path, index=False)
        
        return output_path
    except Exception as e:
        raise ValueError(f"Error executing AI-generated code: {str(e)}")