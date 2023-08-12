# Debugging issues

## Tasks are not being scheduled

1. Check celery dashboard for task history: http://localhost:5555/tasks (or the host running "flower")
2. Check the logs of the scheduler.
3. If there are no logs, or it shows a startup message with no further logs, enable debug mode in the run command:
```
celery <pre-existing args> --loglevel=DEBUG
```
4. If the final line of the log is:
```
beat: Acquiring lock...
```
5. Enter the redis container and delete the lock:
```
docker exec -ti jmon-redis-1 bash 
root@66d12edcb712:/data# redis-cli 
127.0.0.1:6379> auth <redis password>
127.0.0.1:6379> del redbeat::lock
(integer) 1
```
6. Restart the sheduler


