*************
index_flask
*************

**Installation**

::

  $ python -m easy_install <package.egg>
  $ py -3 -m easy_install <package.egg>

**After installation**

- First change SECRET_KEY in the config file: *index_flask/config.py*
- Run to initialize first user:

::

  $ index_flask-initialize_app.py

- Now you can run the package:

::

  $ index_flask-standalone.py

- or (for debugging mode):

::

  $ index_flask-standalone_debug.py

- And open in your preferred browser next link:
    http://localhost:5000/

- It'a required to change root password as soon as possible (email: *root@localhost*, password: *1234*):
    http://localhost:5000/change_password

License
--------
- MIT
- LGPL v2+
