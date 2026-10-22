# Deploy no PythonAnywhere

## 1. Envie o projeto

Clone o repositório em um diretório da sua conta, por exemplo:

```bash
cd ~
git clone <URL_DO_REPOSITORIO> motherclean
```

No painel **Web**, crie uma aplicação Django manual usando Python 3.10 ou superior.

## 2. Crie o ambiente virtual

Use a mesma versão de Python escolhida para a aplicação web:

```bash
cd ~/motherclean
mkvirtualenv --python=/usr/bin/python3.13 motherclean-venv
workon motherclean-venv
pip install -r requirements.txt
```

Se a versão configurada no painel for diferente, substitua `python3.13` pela versão disponível e selecione o caminho do ambiente virtual na aba **Web**.

## 3. Configure o arquivo WSGI

Na aba **Web**, abra o arquivo WSGI da aplicação e substitua seu conteúdo por este modelo. Troque `SEU_USUARIO` pelo nome da sua conta:

```python
import os
import sys

project_path = '/home/SEU_USUARIO/motherclean'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mc.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'SEU_USUARIO.pythonanywhere.com'
os.environ['DJANGO_SECRET_KEY'] = 'COLOQUE_UMA_CHAVE_FORTE_AQUI'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Gere uma chave localmente com:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Não publique essa chave no repositório.

## 4. Migre o banco e os arquivos estáticos

No console Bash:

```bash
cd ~/motherclean
workon motherclean-venv
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Por padrão, o projeto usa `db.sqlite3` dentro do diretório do projeto. Esse arquivo permanece na sua área de arquivos do PythonAnywhere. Faça backup antes de substituir ou atualizar o banco.

Se preferir o MySQL do PythonAnywhere, instale também `pip install -r requirements-mysql.txt` e configure estas variáveis no arquivo WSGI, usando os dados exibidos na aba **Databases**:

```python
os.environ['DB_ENGINE'] = 'mysql'
os.environ['DB_NAME'] = 'SEU_USUARIO$nome_do_banco'
os.environ['DB_USER'] = 'SEU_USUARIO'
os.environ['DB_PASSWORD'] = 'SENHA_DO_MYSQL'
os.environ['DB_HOST'] = 'SEU_USUARIO.mysql.pythonanywhere-services.com'
os.environ['DB_PORT'] = '3306'
```

Não envie a senha para o repositório. Sem `DB_ENGINE=mysql`, a aplicação usa SQLite.

## 5. Mapeie os arquivos estáticos

Na aba **Web**, em **Static files**, adicione:

- URL: `/static/`
- Directory: `/home/SEU_USUARIO/motherclean/staticfiles`

Salve e use o botão **Reload** na aplicação web.

## Verificação

No console Bash, rode `python manage.py check --deploy`. Configure qualquer aviso de segurança reportado antes de usar dados reais.