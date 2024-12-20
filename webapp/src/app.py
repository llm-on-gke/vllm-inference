import gradio as gr
import requests
import os
from langchain_community.llms import VLLMOpenAI
llm_url = os.environ.get('LLM_URL')
llm_name= os.environ.get('LLM_NAME')
llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base=f"{llm_url}/v1",
    model_name=f"{llm_name}",
    model_kwargs={"stop": ["."]},
)


def predict(question):
    data = {"prompt": question}	
    print("Testing....")
    #res=requests.post(f"{llm_url}/v1/models/model:predict", json=data)
    
    return llm(question)

examples = [
    ["Who is Lionel Messi?"],
    ["Explain quantum physics."],
    ["What is the capital of France and Germany."],
]
logo_html = '<div style="text-align: center;"><img src="file/falcon.jpeg" alt="Logo" style="height: 100px;"></div>'

demo = gr.Interface(
    predict, 
    [ gr.Textbox(label="Enter prompt:", value="Who is Lionel Messi?"),
      
    ],
    "text",
    examples=examples,
    title= llm_name+" Knowledge Bot" +logo_html
    )

demo.launch(server_name="0.0.0.0", server_port=7860)