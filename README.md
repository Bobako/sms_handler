# sms_handler
Система создана для того, чтобы сообщения дошли до получателя, даже если первичный сервис рассылки по каким-то причинам не смог его доставить.
В этом случае система перенаправляет сообщение на вторичный сервис. Так же система включает сайт, предназначенный для мониторинга рассылки и сохранения информации
о получателях.

[ТЗ на проект](github.com/Bobako/sms_handler/task.md)

Инструменты, использованные в проекте:
    - Python (Flask, SQLAlchemy, а также менее значимые библиотеки)
    - HTML, CSS, JS (JQuery)

Потрогать демку проекта можно [тут](bobako.site/sms/). В демонстрационной версии отключена проверка полей при входе, запросы к реальному АПИ не совершаются, БД заполнена случайными данными. Демка развернута на Ubuntu 20.04 средствами NGINX, Gunicorn, Supervisord.

