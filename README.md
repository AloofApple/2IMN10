# TODO

TODO: Restructure the folders such that the client, server and load balancer have a own folder Each folder needs its own docker file.    


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
docker-compose up --build
```


