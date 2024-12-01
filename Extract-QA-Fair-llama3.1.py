#!/usr/bin/env python
# coding: utf-8
import gc
import torch
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from datasets import load_dataset    
from huggingface_hub import HfApi
from datasets import DatasetDict
import os
from tqdm import tqdm
import glob
import json
import yaml

gc.collect()
torch.cuda.empty_cache()
class ExtractQAFair:
    def __init__(self, model_id, output_jsonl, repository_name):
        with open('config/set-dev.yaml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            self.huggingface_token = config['Huggingface']['token']
        self.model_id = model_id
        self.output_jsonl = output_jsonl

        self.repo_name = repository_name
        self.input_info = []
        self.input_info.append({"FileName": "QA_input_docs/2014-05-정책효과성 증대를 위한 집행과학에 관한 연구.pdf.txt",
                           "Source": "KDI 연구보고서 2014-05 정책효과성 증대를 위한 집행과학에 관한 연구 김재훈"})

        self.prompt = PromptTemplate.from_template(
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
            "QUESTION": "PMDU(prime minister’s delivery unit)가 어떤 역할을 하는 조직인가요?",
            "ANSWER": "PMDU(Prime Minister’s Delivery Unit)는 일반적으로 국가 주요 우선 과제의 진행 상황을 감독하고 개선하기 위해 설립됩니다. "
        }},
        {{
            "QUESTION": "조직 형태로서의 네트워크는 계층제와 시장이라는 조직형태에서 어떠한 특성을 가지는가?",
            "ANSWER": "계층제적 지배구조는 수평적⋅수직적으로 분화되어 있고 지시⋅명령과 같은 행정적 수단에 의해 통제된다."    
        }},
        {{
            "QUESTION": "향후 발전을 위해 정부 역할은 어떻게 설정되어야 할까?",
            "ANSWER": "정부역할에 대한 새로운 관심과 개혁 노력이 뒤따를 필요가 있다."    
        }}
        ```
        """
        )
    def custom_json_parser(self, response):
        json_string = response.content.strip().removeprefix("```json\n").removesuffix("\n```").strip()
        json_string = f'[{json_string}]'
        json_fmt = json.loads(json_string)
        print(type(json_fmt))
        print(json_fmt)
        return json_fmt

    def gen_qa_set(self):
        model = ChatOllama(model=self.model_id, temperature=0, format='json')

        chain = (
            self.prompt
            | model
            | self.custom_json_parser
        )

        file_index = 0
        with open(self.input_info[file_index]["FileName"], "r", encoding="utf-8") as rf:
            element_text = rf.readlines()

        qa_pair = []
        element_text = element_text[:3]
        for idx, text_element in enumerate(tqdm(element_text)):
            try:
                if text_element.count('|') > 1:
                    print("Skeep Table Detect")
                    continue
                text_element = text_element.strip()
                llm_rtn = chain.invoke({"context": f"{text_element}", "domain": "report for policy study", "num_questions": "3"})
                qa_f = open("qa_debug.txt", "a", encoding='utf-8')
                if isinstance(llm_rtn, list):
                    for rtn_ele in llm_rtn:
                        output_string = f"{idx} : {text_element}\n"
                        qa_f.write(output_string)
                        output_string = f"{rtn_ele}\n"
                        qa_f.write(output_string)
                        qa_pair.append(rtn_ele)
                qa_f.close()
                print("---")
            except Exception as e:
                eqa_f = open("qa_error_debug.txt", "a", encoding='utf-8')
                eqa_f.write(text_element + '\n' + str(e)+'\n')
                eqa_f.close()

        qa_list = []
        for qa in qa_pair:
            key_list = list(qa.keys())
            qa_modified = {"question":'', "input":'', 'answer': '', "source": self.input_info[file_index]["Source"]}
            for key in key_list:
                if "q" in key.lower():
                    qa_modified['question']=qa[key]
                elif "a" in key.lower():
                    qa_modified['answer']=qa[key]
            qa_list.append(qa_modified)

        with open(self.output_jsonl, "w", encoding="UTF-8-sig") as jsonf:
            for qa in qa_list:
                print(qa)
                jsonf.write(json.dumps(qa, ensure_ascii=False) +"\n")
        self.dataset = load_dataset("json", data_files=self.output_jsonl)

    def push_to_hub(self):
        train_testvalid = self.dataset['train'].train_test_split(test_size=0.2)
        test_valid = train_testvalid['test'].train_test_split(test_size=0.5)
        ds = DatasetDict({
            'train': train_testvalid['train'],
            'test': test_valid['test'],
            'valid': test_valid['train']})

        #Hugginfface push
        # api = HfApi()
        ds.push_to_hub(self.repo_name, token=self.huggingface_token)

extract = ExtractQAFair(model_id='llama3.1', output_jsonl='qa_pair_llama3.jsonl', repository_name='prismdata/KDI-DATASET-2014')
extract.gen_qa_set()
print(extract.dataset)
extract.push_to_hub()