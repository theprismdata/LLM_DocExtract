# LLM_DocExtract

LLM FineTunning을 위해 각종 포맷의 문서에서 Text를 추출합니다.
문서는 MinIO에 존재한다고 가정합니다.

Environment
Python 3.10
torch 2.5.1
cuda version : cu124
Howto run
가상 환경 생성
```commandline
python -m venv .venv 
```
가상 환경에 라이브러리 설치(Windows)
```commandline
.venv\Scripts\activate.bat
pip install -r requirements.txt
```
가상 환경에 라이브러리 설치(Linux 계열)
```commandline
.venv\Scripts\activate
pip install -r requirements.txt
```


```commandline
그외 추가 라이브러리 설치
triton 다운로드
https://huggingface.co/Kefasu/triton/blob/main/triton-2.1.0-cp310-cp310-win_amd64.whl

pip install "triton-2.1.0-cp310-cp310-win_amd64.whl"
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install xformers --index-url https://download.pytorch.org/whl/cu124
pip install "unsloth[cu124-torch251] @ git+https://github.com/unslothai/unsloth.git"
```
```commandline
버킷이름 설정
DocumentExtract.py의 166Line 수정
bucket_name에 가져올 문서가 포함된 버킷 이름을 설정
```

```commandline
python DocumentExtract.py
```
```
결과물 result 폴더에 디렉토리가 생성되면서 text로 변환된 파일 생성됨.
```
```
지원되는 문서 포맷
doc, ppt, xls, pdf, txt
```