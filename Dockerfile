FROM python:3.9
ENV PYTHONBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD gunicorn core.wsgi --chdir src --bind 0.0.0.0 --preload --log-file -

