docker rm -f redis

docker-compose up --build -d --scale client=50

Start-Sleep -Seconds 5

docker stop server2 server3

Start-Sleep -Seconds 20

docker start server2 server3