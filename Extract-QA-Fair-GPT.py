#!/usr/bin/env python
# coding: utf-8

from langchain_core.prompts import PromptTemplate
import yaml
import json
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from datasets import load_dataset

with open('config/set.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

OPENAI_API_KEY = config['openai']['apikey']
OPENAI_CHAT_MODEL = config['openai']['chat_model']
HUGGINGFACE_API_KEY = config['Huggingface']['token']

def custom_json_parser(response):
    json_string = response.content.strip().removeprefix("```json\n").removesuffix("\n```").strip()
    json_string = f'[{json_string}]'
    return json.loads(json_string)

prompt = PromptTemplate.from_template(
    """Context information is below. You are only aware of this context and nothing else.
---------------------

{context}

---------------------
Given this context, generate only questions based on the below query.
You are an Teacher/Professor in {domain}. 
Your task is to provide exactly **{num_questions}** question(s) for an upcoming quiz/examination. 
You are not to provide more or less than this number of questions. 
The question(s) should be diverse in nature across the document. 
The purpose of question(s) is to test the understanding of the students on the context information provided.
You must also provide the answer to each question. The answer should be based on the context information provided only.

Restrict the question(s) to the context information provided only.
QUESTION and ANSWER should be written in Korean. response in JSON format which contains the `question` and `answer`.
DO NOT USE List in JSON format.
ANSWER should be a complete sentence.

#Format:
```json
{{
    "QUESTION": "바이든 대통령이 서명한 '안전하고 신뢰할 수 있는 AI 개발과 사용에 관한 행정명령'의 주요 목적 중 하나는 무엇일까요?",
    "ANSWER": "바이든 대통령이 서명한 행정명령의 주요 목적은 AI의 안전 마련과 보안 기준 마련을 위함이에요."
}},
{{
    "QUESTION": "메타의 라마2가 오픈소스 모델 중에서 어떤 유형의 작업에서 가장 우수한 성능을 발휘했나요까?",
    "ANSWER": "메타의 라마2는 RAG 없는 질문과 답변 및 긴 형식의 텍스트 생성에서 오픈소스 모델 중 가장 우수한 성능을 발휘했어요."    
}},
{{
    "QUESTION": "IDC 예측에 따르면 2027년까지 생성 AI 플랫폼과 애플리케이션 시장의 매출은 얼마로 전망되나요?",
    "ANSWER": "IDC 예측에 따르면 2027년까지 생성 AI 플랫폼과 애플리케이션 시장의 매출은 283억 달러로 전망됩니다."    
}}
```
"""
)


llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        temperature=0,
        model_name=OPENAI_CHAT_MODEL,
        streaming=False,
        callbacks=[StreamingStdOutCallbackHandler()],
    )
chain = (
    prompt
    | llm
    | custom_json_parser
)


lines = []
with open("QA_input_docs/2014-05-정책효과성 증대를 위한 집행과학에 관한 연구.pdf.txt", "r", encoding='UTF8') as rf:
    lines = rf.readlines()

lines_sample = lines[:100]

qa_pair = []
for text_element in lines_sample:
    try:
        llm_rtn = chain.invoke({"context": text_element, "domain": "policy", "num_questions": "3"})
    except Exception as e:
        pass
    qa_pair.extend(llm_rtn)
print(qa_pair[:10]) 


#backup
with open("qa_pair_gpt.json", "w") as f:
    json.dumps(qa_pair)

#생성된 QA에 데이터 출처 추가하여 저장하고
with open("qa_pair_gpt.jsonl", "w", encoding="utf-8") as f:
    for qa in qa_pair:
        if 'question' in qa.keys():
            qa_modified = {
                "instruction": qa["question"],
                "input": "",
                "output": qa["answer"],
                "source":"KDI-연구보고서-정책효과성 증대를 위한 집행과학에 관한 연구-2014.12.31"
            }
        else:
            qa_modified = {
                "instruction": qa["QUESTION"],
                "input": "",
                "output": qa["ANSWER"],
                "source":"KDI-연구보고서-정책효과성 증대를 위한 집행과학에 관한 연구-2014.12.31"
            }
        f.write(json.dumps(qa_modified, ensure_ascii=False) + "\n")

#Hugginface에 등록하기위해 로딩...
jsonl_file = "qa_pair_gpt.jsonl"
dataset = load_dataset("json", data_files=jsonl_file)

# 데이터셋을 허브에 등록함.
repo_name = "prismdata/KDI-2014-DATASET-TEST"
dataset.push_to_hub(repo_name, token=HUGGINGFACE_API_KEY)