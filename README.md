Как запустить сервер у себя
===========================

Раньше код работал на Python 2.7 с Django 1.4. Сейчас постепенно он переводится на Python 3.3 и Django 1.6.

Рекомендуем запускать проект через виртуальное окружение.

1. Поставьте пакетный менеджер

        sudo apt-get install python3-setuptools

2. Поставьте менеджер виртуальных окружений Питона

        sudo pip install virtualenv

3. Склонируйте репозиторий проекта, перейдите в него, создайте виртуальное окружение

        git clone https://github.com/vpavlenko/pythontutor-ru.git
        cd pythontutor-ru
        virtualenv-3.3 venv

4. Активируйте виртуальное окружение и установите зависимости проекта

        source venv/bin/activate

5. Создайте базу данных. При создании выберите `yes` и задайте логин и пароль администратора

        python3 manage.py syncdb
        python3 manage.py migrate tutorial

6. Запустите сервер разработчика

        python3 manage.py runserver


Лицензия
========

Курс построен на основе материалов Д. П. Кириенко, которые распространяются по лицензии [Creative Commons «Attribution-NonCommercial-ShareAlike»](http://creativecommons.org/licenses/by-nc-sa/3.0/deed.ru)
