# energyusage
Provide analysis and charting of energy usage

To run the website:
```
python run.py
```

Or in headless mode:
```
setsid gunicorn --bind 0.0.0.0:8000 wsgi:app -t 600
```

To initialise the database on first use:
```
python
from energy import db
db.create_all()
```