# LLM_DocExtract

### Stage 1. 문서에서 콘텍스트 추출하기
sLLM을 구축하기 위한 FineTunning용 테이터 셋을 생성하기휘 각종 포맷의 문서에서 Text를 추출합니다.
문서는 MinIO에 존재한다고 가정합니다.

Run Environment (Window11에서 테스트 하였습니다.)

##### Python 3.10
가상 환경 생성
```
python -m venv .venv 
```
가상 환경에 라이브러리 설치(Windows)
```
.venv\Scripts\activate.bat
pip install -r requirements.txt
```
버킷이름 설정
document_extract.py의 256Line 수정

bucket_name에 가져올 문서가 포함된 버킷 이름을 설정
```
문서 추출
python document_extract.py
```

```
결과물 result 폴더에 디렉토리가 생성되면서 text로 변환된 파일 생성됨.
```
```
지원되는 문서 포맷
doc, ppt, xls, pdf, txt
```
추출된 데이터 예제(Markdown 형식)

![table_ex](https://github.com/user-attachments/assets/0c2466ef-c685-4888-90c9-9050d5b3fbe1)

### Stage 2.FineTunning을 위한 QA Set 생성
GPT를 사용하는 경우와 llama3.1이 가능하며, 그외에 다른 로컬 모델도 가능합니다.

#### 1. GPT를 사용할 경우
 Jupyter를 이용할 경우 Extract-QA-Fair-GPT.ipynb를 실행합니다.

 Command line prompt를 사용할 경우 다음의 명령으로 실행합니다.
 ```
 python Extract-QA-Fair-GPT.py
 ```
 
 QA Set을 생성하기 위한 파일은 QA_input_docs폴더에 있다고 가정 합니다.

 파일은 Stage1의 결과물을 이용하거나 일반 txt파일을 사용하여도 무방 합니다.

 repo_name에 설정된 Huggingface 저장소에 데이터셋이 등록됩니다. 

#### 2. llama3를 이용할 경우
https://ollama.com 에서 ollama 다운로드 받으시고, 아래의 pull 명령으로 모델을 로컬에 받으시기 바랍니다.

```
ollama pull llama3.1 
```
GPU를 사용할 경우 6기가 정도의 메모리가 소요됩니다. 실험 환경에서는 GeForce GTX 1060 6G를 사용하였습니다.

다음의 명령으로 텍스트 파일에서 QA Set을 추출합니다. 
```commandline
python Extract-QA-Fair-llama3.1.py
```
추출된 별과물은 qa_pair_llama3.jsonl에 저장되고, 바로 huggingface에 등록됩니다.

초기에는 결과물 확인을 위하여 extract.generate_qa_set(numofsample)의 numofsample를 작게 설정하는 것이 좋습니다.
```
extract.generate_qa_set(numofsample=10)
```
파일 전체를 이용할 경우 numofsample을 None으로 설정합니다.
```
extract.generate_qa_set(numofsample=None)
```
만약 내용을 직접 수정하거나, 추가할 경우 qa_pair_llama3.jsonl파일의 내용을 question, answer 형식에 맞추어 수정 후
아래의 코드 이후만 수정하여 배포합니다.
```commandline
extract.load_ds()
```

추출한 원본 문서는 QA_input_docs에 있으며 KDI 2014 연구 리포트를 사용하였습니다.

--------------------------------------------------------
기반 코드(특히 프롬프트)는 Teddy님의 코드를 참조하였습니다.