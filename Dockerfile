FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY . .

CMD uvicorn run_server:app