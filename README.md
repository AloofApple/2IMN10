Create virtual environment
```
python -m venv venv
source venv/bin/activate
```


To build an image.
```
docker build -t my-python-app .
```

To update the packages
```
pip freeze > requirements.txt
```