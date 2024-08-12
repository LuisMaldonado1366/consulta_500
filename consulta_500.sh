#!/bin/sh
#declaramos variables de directorios
docker_image='consulta_500'
#eliminamos imagenes no  necesarias
#Esta linea debe de descomentarse cada que se haga un pull en directorio1
#docker image rm $(docker images -a -q)
#git pull origin main
docker build -t $docker_image .
docker compose up -d