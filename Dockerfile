FROM python:3.11-slim
LABEL authors="Dmitry Zhirov"

COPY requirements.txt /

RUN pip3 install --upgrade pip

RUN pip3 install -r /requirements.txt

COPY . /app

WORKDIR /app

EXPOSE 80

CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:80"]