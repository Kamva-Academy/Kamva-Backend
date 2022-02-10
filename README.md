## Instalation
- `git clone https://github.com/Rastaiha/workshop_backend.git`
- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser`
- `python3 manage.py runserver`

## APIs
To see api check http://127.0.0.1:8000/api after running projec on local
 
## Deployment
after being logged to server and workshop_backend folder, run:
- `git pull`
- `docker-compose up -d --build`
- `docker-compose restart nginx`
