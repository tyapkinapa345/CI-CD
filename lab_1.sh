#!/bin/bash
docker pull mariadb:latest
docker run --name my-db -e MYSQL_ROOT_PASSWORD=root123 -p 3306:3306 -d mariadb:latest
sleep 45
docker exec -i my-db mariadb -u root -proot123 <<EOF
CREATE USER 'analyst'@'%' IDENTIFIED BY 'analyst123';
GRANT ALL PRIVILEGES ON *.* TO 'analyst'@'%';
FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User='analyst';
EOF
