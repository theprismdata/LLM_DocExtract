#!/usr/bin/env python
# coding: utf-8
import torch
import time
import gc
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

def cleanup():
    if 'model' in globals():
        del globals()['model']
    if 'dataset' in globals():
        del globals()['dataset']
    gc.collect()
    torch.cuda.empty_cache()
cleanup()

ollama_llama3_emb_cpu = OllamaEmbeddings(model="llama3",num_gpu=0)

document = []
with open("After_clean/KDI_Report/2014-05-정책효과성 증대를 위한 집행과학에 관한 연구.pdf.txt", "r", encoding='UTF8') as f:
    document = f.readlines()

for doc_line in document:
    start = time.time()
    r2 = ollama_llama3_emb_cpu.embed_query(doc_line)
    meaure_time = time.time() - start
    print(meaure_time, doc_line)