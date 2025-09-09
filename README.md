# Setup

Create virtual environment
```
python -m venv venv
.\venv\Scripts\Activate
```

To install the packages
```
pip install -r requirements.txt
```

To update the packages
```
pip freeze > requirements.txt
```
# Docker 

To build an image and run them.
```
docker build --pull -t ads:lab .
docker compose up
```

