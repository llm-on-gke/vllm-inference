import gradio as gr
import requests
import os
from langchain_community.llms import VLLMOpenAI
import requests
import json

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


def predict(question):
    data = {"prompt": question}	
    print("Testing....")

    url = 'https://'+APIGEE_HOST+'/v1/products?count=100'
    headers = {'x-apikey': APIKEY, 'Content-type': 'application/json'}

    resp = requests.get(url, headers = headers)
    #res=requests.post(f"{llm_url}/v1/models/model:predict", json=data)
    
    return llm("Summarize the product of "+question + " in the following text: "+ resp.text)

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