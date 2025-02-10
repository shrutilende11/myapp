FROM mysql:8.0

# mysql root password will be set to root
ENV MYSQL_ROOT_PASSWORD=password

# mysql will create a new database named mydb
ENV MYSQL_DATABASE=image_app
# the file db_schema.sql will get executed immediately when 
# the container gets created
COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306
