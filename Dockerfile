# Use an official Python runtime as a parent image
FROM python:3.6.6-alpine3.8

WORKDIR /app

COPY . /app

RUN apk --update add --no-cache g++

RUN pip install -r requirements.txt

EXPOSE 70

ENV NAME Pred2

CMD ["python", "find_missing_values.py"]