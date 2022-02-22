## hazen-web-app

Repo dedicated to the hazen-web-app. This will be used in conjunction with the hazen repo, which will eventually 
be hazenlib, etc.

### Setup & Run

Setup:
- Setup venv, e.g. `(hazen-web-app)`
- Clone repo
- `cd hazen-web-app`
- `pip install -r requirements.txt`
  - Reminder for Tom: currently using `req_hazen-web-app.txt`
  - `requirements.txt` is old file associated with old hazen package built on Python 3.6 and other older packages

To run locally:
- `python hazen.py`
  - Entrypoint for running Flask app and database
- Open hazen-web-app at provided address, typically: `localhost:5000`

To deploy to Heroku:
- TBC