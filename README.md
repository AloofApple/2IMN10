# Docker 

To build an image, run them and choose the amount of clients.
```
docker-compose down -v --remove-orphans
docker-compose up --build --scale client=50
```

Note that you can rebuild the image by running again the same command. There is no need to delete images and/or containers.
