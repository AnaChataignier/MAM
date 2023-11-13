# OS

```
python3 -m venv .venv
```

```
source .venv/bin/activate
```

```
pip install requirements
```


Nao use os comandos abaixo muitas vezes.

"Popula com 10 Usuarios(2 staff, 8 tecnicos)"
```
python manage.py runscript scripts.users_script -v3
```

Popula com 100 clientes com endereço e uma os pra cada cliente
```
python manage.py runscript scripts.end_cli_os_script -v3
```

"Testa a model do app de autenticação"
```
python manage.py test authentication.tests.test_model.CustomUserTestCase
```
Teste1
