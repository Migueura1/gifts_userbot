1. В app/config.py установить переменную seq в значение своего telegram_id
2. Создать и заполнить .env по примеру .env.example

api_id и api_hash берутся после создания приложения на https://my.telegram.org

2.3. python -m venv venv
2.4. source venv/bin/activate
2.5. pip install -r requirements.txt

3. В первый раз запустить скрипт руками через python app/main.py, сразу после авторизации через номер телефона - остановить

4. docker compose up --build -d
