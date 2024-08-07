FROM python:3.11.7-slim-bullseye

WORKDIR /E-commerce

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /E-commerce/entrypoint.sh
RUN chmod +x /E-commerce/entrypoint.sh

COPY . .

ENTRYPOINT ["/E-commerce/entrypoint.sh"]