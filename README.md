# LLM_DocExtract

### Stage 1. 문서에서 콘텍스트 추출하기
LLM FineTunning을 위해 각종 포맷의 문서에서 Text를 추출합니다.
문서는 MinIO에 존재한다고 가정합니다.

Run Environment (Window11에서 테스트 했습니다.)

##### Python 3.10
##### cu124
Howto run
가상 환경 생성
```
python -m venv .venv 
```
가상 환경에 라이브러리 설치(Windows)
```
.venv\Scripts\activate.bat
pip install -r requirements.txt
```
"triton-2.1.0-cp310-cp310-win_amd64.whl"를 설치하시기 바랍니다. 윈도우는 사전 빌드된 것으로 설치해야 합니다.
```
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124

pip install xformers --index-url https://download.pytorch.org/whl/cu124

pip install "unsloth[cu124-torch251] @ git+https://github.com/unslothai/unsloth.git"
```

가상 환경에 라이브러리 설치(Linux 계열)
```
.venv\Scripts\activate
pip install -r requirements.txt
```
버킷이름 설정
DocumentExtract.py의 256Line 수정

bucket_name에 가져올 문서가 포함된 버킷 이름을 설정

```
문서 추출
python DocumentExtract.py
```


```
결과물 result 폴더에 디렉토리가 생성되면서 text로 변환된 파일 생성됨.
```
```
지원되는 문서 포맷
doc, ppt, xls, pdf, txt
```
Extracted Text

![table_ex](https://github.com/user-attachments/assets/0c2466ef-c685-4888-90c9-9050d5b3fbe1)

### Stage 2.FineTunning을 위한 QA Set 생성
https://ollama.com 에서 ollama 다운로드 받으시고, 아래의 pull 명령으로 모델을 로컬에 받으시기 바랍니다. 
```
ollama pull llama3.1 
```

QASet 추출 자동화를 위해 LLM을 사용하는 경우가 있는데 여기서는 GPT를 사용하지 않고,로컬 시스템의 GPU를 사용하였습니다.

    
~~Extract-QA-Fair-Ollama-Hugging.ipynb에서는 위에서 추출한 텍스트 문서를 기반으로 QA Set을 생성합니다.~~
Extract-QA-Fair-llama3.1.py를 참조에서 수행하며 qa_pair_llama3.jsonl로 결과가 출력됩니다.

!주의 146라인에 repository_name에 Huggingface 저장소를 설정하시기 바랍니다.

추출한 텍스트 문서는 QA_input_docs에 있으며 KDI 연구 리포트를 사용하였습니다.

Ollama를 사용하여 Llama3.1에 텍스트 문서를 적용하여 QA Set을 생성하고, Huggingface에 등록합니다.

기반 코드(특히 프롬프트)는 Teddy님의 코드를 참조하였습니다.