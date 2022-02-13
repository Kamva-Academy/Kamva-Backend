## Instalation

- `git clone https://github.com/Rastaiha/workshop_backend.git`
- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python3 manage.py migrate`
- `python3 manage.py createsuperuser`
- `python3 manage.py runserver`

## APIs

To see apis check http://127.0.0.1:8000/api after running projec on local
 
## Deployment

after being logged in to server and workshop_backend folder, run:
- `git pull`
- `docker-compose up -d --build`
- `docker-compose restart nginx`

## Contribution

1. Select an issue from [here](https://github.com/Rastaiha/workshop_backend/issues) that you want to work on.
2. Create a new branch from `main` and fix selected issue on new branch.
3. After fixing selected issue, create a pull request (PR) to `main` and waits until reviewr review your code.
4. If reviewer noticed you for a mistake in PR, be responsible to fix that.
5. At the end, reviewer merges your PR and your contribution complete!
