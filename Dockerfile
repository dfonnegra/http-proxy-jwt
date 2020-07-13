FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ARG HTTP_PORT=8000
ENV HTTP_PORT ${HTTP_PORT}

EXPOSE ${HTTP_PORT}

COPY . .

WORKDIR ./src

CMD uvicorn run_server:app --host 0.0.0.0 --port ${HTTP_PORT}