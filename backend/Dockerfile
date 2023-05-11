FROM python:3.7-alpine 

WORKDIR /app

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add libffi-dev

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]