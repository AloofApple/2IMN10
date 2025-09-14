# Docker 

To build an image,  run them and choose the amount of clients.
```
docker-compose up --build --scale client=2
```

# Virtual Environment 

To create virtual environment run the following commands, else install the dependencies locally.
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
