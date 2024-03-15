# v4.18.1

In the release of 4.18.1, docker-compose volumes for postgres and redis have been implemented.

To avoid data-loss, the following script can be used to backup data from postgres/redis and restore to the new docker-comopose volumes.

For installations that are not using docker-compose, this can be ignored.

```
POSTGRES_VOLUME=/var/lib/postgresql/data
REDIS_VOLUME=/data


# Determine amount of database that requires backing up
docker-compose exec database du -hs $POSTGRES_VOLUME
docker-compose exec redis du -hs $REDIS_VOLUME

# Determine a location with enough space
BACKUP_LOCATION=/backup
echo "If running this as a script, verify that $BACKUP_LOCATION exists, as has enough space to contain the above space"
read

# Stop the stack
docker-compose stop

# Backup postgres database
mkdir $BACKUP_LOCATION/postgres
sudo docker-compose cp --archive database:$POSTGRES_VOLUME/. $BACKUP_LOCATION/postgres/

# Backup redis data
mkdir $BACKUP_LOCATION/redis
sudo docker-compose cp --archive redis:$REDIS_VOLUME/. $BACKUP_LOCATION/redis/

# Check out desired release, following README

# Bring up stack, without starting
docker-compose up --no-start

# Copy data back to volumes
sudo docker-compose cp --archive $BACKUP_LOCATION/postgres/. database:$POSTGRES_VOLUME/
sudo docker-compose cp --archive $BACKUP_LOCATION/redis/. redis:$REDIS_VOLUME/

# Bring up stack
docker-compose up -d

# Verify the data has been copied
docker-compose exec database du -hs $POSTGRES_VOLUME
docker-compose exec redis du -hs $REDIS_VOLUME
```
 
