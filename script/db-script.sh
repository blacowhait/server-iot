command=$1
type=$2

if [ "$command" == "init" ]; then
    if [ "$type" == "docker" ]; then
        docker run --name postgre --rm -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e PGDATA=/var/lib/postgresql/data/pgdata -v /tmp:/var/lib/postgresql/data -p 54321:5432 -it postgres:14.1-alpine
    elif [ "$type" == "psql" ]; then
        sudo apt update
        sudo apt install postgresql postgresql-contrib
        sudo systemctl start postgresql.service
        sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
    else
        echo "Missing parameter, usage ./db-script.sh init [docker|psql]"
        exit 1
    fi
elif [ "$command" == "rollback" ]; then
    if [ "$type" == "docker" ]; then
        docker exec -it postgre psql -U postgres postgres -c "DROP TABLE IF EXISTS user_person, hardware, node, feed, channel, sensor CASCADE;"
    elif [ "$type" == "psql" ]; then
        PGPASSWORD=postgres psql -h $HOST -U postgres postgres -c "DROP TABLE IF EXISTS user_person, hardware, node, sensor, channel, feed CASCADE;"
    else
        echo "Missing parameter, usage ./db-script.sh rollback [docker|psql]"
        exit 1
    fi
elif [ "$command" == "admin" ]; then
    docker exec -it postgre psql -U postgres postgres -c "update user_person set is_admin='t',activated='t',token='Done' where id = '1';"
else
    echo "Missing parameter, usage ./db-script.sh [init|rollback] [docker|psql]"
    exit 1
fi