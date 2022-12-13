<h1 align="center"> DRF_Fabrique (Django REST framework + redis + celery) </h1>
<p>Тестовое задание на позицию Python-разработчик(Django, DRF)</p>
<p>Тех. задание: https://www.craft.do/s/n6OVYFVUpq0o6L</p>
<hr/>
<h2>Начало</h2>
<p>Для того, чтобы протестировать проект - его нужно скачать!)</p>
<p>Создаём директорию под проект: </p>

    mkdir some_name    

<p>После, нужно перейти в новую директорию</p>

    cd some_name/    

<p>Скачиваем с github в нашу директорию:</p>

    git clone https://github.com/hulumulula/drf_fabrique.git 
    
<p>Переходим в директорию проекта</p>

    cd drf_fabrique/

<h2>Запуск</h2>
<h4>Через docker-compose</h4>
Чтобы запустить проект через докер - достаточно одной команды:

    docker-compose up --build
    
Докер сам соберёт проект и запустит его..
**Сервис** доступен по адресу

    127.0.0.1:8000/api/

Страница со **Swagger**

    127.0.0.1:8000/docs/swagger/
    
Также доступ к **Flower**

    127.0.0.1:5555/

<h4>Локально</h4>
Создаём виртуальное окружение и заходим в него

    python3 -m venv YourNameEnv
    source YourNameEnv/bin/activate
    
Устанавливаем все зависимости:

    pip install -r requierment.txt
    
Для пользователей Anaconda

    conda create YourNameEnv
    conda activate YourNameEnv
    conda install pip
    pip install -r requierment.txt

Нужно создать миграции и принять их

    python manage.py makemigrations
    python manage.py migrate

Чтобы запустить локально, нужно запустить каждую из служб отдельно
    
    python manage.py runserver
    redis-server
    python -m celery -A FabricaResheniy worker -l info -B
    python -m celery -A FabricaResheniy flower

<h2>Выполненные пункты:</h2>

- организовать тестирование написанного кода
- подготовить docker-compose для запуска всех сервисов проекта одной командой
- реализовать дополнительный сервис, который раз в сутки отправляет статистику по обработанным рассылкам на email  
> Все email будут отправляться каждый день в 12:00
- сделать так, чтобы по адресу /docs/ открывалась страница со Swagger UI и в нём отображалось описание разработанного API. Пример: https://petstore.swagger.io
- удаленный сервис может быть недоступен, долго отвечать на запросы или выдавать некорректные ответы. Необходимо организовать обработку ошибок и откладывание запросов
- обеспечить подробное логирование на всех этапах обработки запросов, чтобы при эксплуатации была возможность найти в логах всю информацию

<h4>Email</h4>

Вся почта будет идти на мой почтовый адрес. Поэтому вам нужно изменить настройки почты в **FabricaResheniy/settings.py** 
раздел **EMAIL** на ваши настройки. Все параметры настройки можно узнать у вашей почты.
Пример **mail.ru**: https://help.mail.ru/mail/mailer/popsmtp
