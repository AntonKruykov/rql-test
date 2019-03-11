# rql-test

### Запускать автотесты
 docker-compose up autotests

### Запускать проект
docker-compose up runserver

Все миграции вместе с фикстурами применяются при запуске

### Примеры вызовов API
[http://0.0.0.0:8000/](http://0.0.0.0:8000/)

[http://0.0.0.0:8000/users/](http://0.0.0.0:8000/users/)

[http://0.0.0.0:8000/users/?q=(first_name==%22Kruykov1%22),id=lt=30;last_name==Kruykov](http://0.0.0.0:8000/users/?q=(first_name==%22Kruykov1%22),id=lt=30;last_name==Kruykov)

### Пояснения
1. Написал парсер используя пакет pyparsing. 
2. В Django параметры url разбиваются по '&' и ';'. А в RQL ';' - логическое AND.
Поэтому пришлось сделать 
[манки-патчинг](https://github.com/AntonKruykov/rql-test/blob/master/rql_test/settings.py#L128).
В этот момент, у меня были сомнения, а "Правильный ли RQL" я пытаюсь сделать? 
Надеюсь, правильный =).
