# Мини читабельность
Тестовое задание.

## Возможные улучшения

- Можно написать тесты
- Можно, чтобы обработчик текста работал отдельно от основного приложения - в базу записывать номер задания (так же будет работать , как 'кеш'). 
- Можно сохранять все в файл , и выдавать по отдельному url ечрез nginx
- Добавить сваггер. 

## Работа приложения
8000 порт
/ - начальная страница
/api/process_url/ - апи POST body : ```{"url": "https...."}```

## Installation Питон

```sh
python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt
python src/manage.py runserver
```


## Docker

```sh
docker-compose up --build -d
```
