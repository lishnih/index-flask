# index-flask

### Installation

```sh
$ python -m easy_install index_flask-0.2-py2.7.egg
```
- or
```sh
$ py -3 -m easy_install index_flask-0.2-py3.4.egg
```

### After installation

- First change SECRET_KEY in the config file: ***index_flask/config.py***

- Run to initialize first user:
```sh
$ index_flask-initialize_app.py
```

- Now you can run the package:
```sh
$ index_flask-standalone.py
```
- or (for debugging mode):
```sh
$ index_flask-standalone_debug.py
```

- And open in your preferred browser next link:
```sh
http://localhost:5000/
```

- It'a required to change root password as soon as possible (email: *root@localhost*, password: *1234*):
```sh
http://localhost:5000/change_password
```

License
----
MIT
LGPL v2+
