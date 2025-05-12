import gradio as gr
import requests
import os
from langchain_community.llms import VLLMOpenAI
import json
from openai import OpenAI

llm_url = os.environ.get('LLM_URL')
llm_name= os.environ.get('LLM_NAME')
APIGEE_HOST=os.environ.get('APIGEE_HOST')
APIKEY=os.environ.get('APIKEY')
llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base=f"{llm_url}/v1",
    model_name=f"{llm_name}",
    model_kwargs={"stop": ["."]},
)
#llm=OpenAI(
#    api_key="EMPTY",
#    base_url=f"{llm_url}/v1",
#    model=f"{llm_name}",
#)

def predict(question):
    url = f"https://{APIGEE_HOST}/v1/products?count=100"
    headers = {'x-apikey': APIKEY, 'Content-type': 'application/json'}

    resp = requests.get(url, headers = headers)
    products = resp.json()  # Parse JSON response
    
    # Create a more structured prompt for better results
    system_prompt = """You are a helpful assistant that analyzes product information.
    When describing products, focus on key details like:
    - name
    - categories
    - priceUsd
    - description
    Provide a concise and natural summary."""
    
    user_prompt = f"""I want information about {question}.
    Here are the product details in JSON format:
    {json.dumps(products, indent=2)}
    
    Please provide a natural summary focusing on products related to {question}. 
    If no relevant products are found, please indicate that."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    #chat_response = llm.chat.completions.create(
    #model=f"{llm_name}",
    #messages=[
    #    {"role": "system", "content": "You are a helpful assistant."},
    #    {"role": "user", "content": "Tell me a joke."},
    #]
    #)
    #print("Chat response:", chat_response)

    response = requests.post(
        f"{llm_url}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": llm_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 600  # Adjust based on your needs
        }
    )
    # Debug the response
    response_data = response.json()
    print("API Response:", response_data)  # For debugging
        
    if response.status_code != 200:
        return f"Error: API returned status code {response.status_code}"
            
    # Check if response has the expected structure
    if "choices" not in response_data:
        return f"Error: Unexpected API response format: {response_data}"
            
    if not response_data["choices"]:
            return "Error: No completion choices returned"
            
    return response_data["choices"][0]["message"]["content"].strip()
         

examples = [
    ["Sunglass"],
    ["Shoes"],
    ["Clothes"],
]
logo_html = '<div style="text-align: center;"><img src="file/falcon.jpeg" alt="Logo" style="height: 100px;"></div>'

demo = gr.Interface(
    predict, 
    [ gr.Textbox(label="Enter prompt:", value="Sunglass"),
      
    ],
    "text",
    examples=examples,
    title= llm_name+" Knowledge Bot" +logo_html
    )

demo.launch(server_name="0.0.0.0", server_port=7860)