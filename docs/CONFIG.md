
### API_KEY


API key

Default unset, allowing unauthenticated access to APIs


Default: ``


### AWS_BUCKET_NAME

Name of s3 bucket for storing artifacts

Default: ``


### AWS_ENDPOINT

HTTPS url for AWS ENDPOINT for accessing S3. Set to minio API URL, if in use.

Default: ``


### BROKER_HOST

Broker hostname/ip

Default: ``


### BROKER_INSTANCE

Broker vhost

Default: ``


### BROKER_PASSWORD

Broker password

Default: ``


### BROKER_PORT

Broker port

Default: `0`


### BROKER_TYPE

Configure type of broker. Currently only supports 'amqp'

Default: `amqp`


### BROKER_USERNAME

Broker username

Default: ``


### CACHE_BROWSER


Whether to cache browser between runs.

This is experimental and might be unstable.

Use on non-production environment


Default: `False`


### CHECK_CRITICAL_THRESHOLD

Threshold for warning->critical check status in UI

Default: `99.0`


### CHECK_WARNING_THRESHOLD

Threshold for okay->warning check status in UI

Default: `99.9`


### CHROME_HEADLESS_MODE

Chrome headless mode. Options: None, New or Legacy

Default: `Legacy`


### DATABASE_HOST

Database hostname/IP

Default: ``


### DATABASE_NAME

Database DB name

Default: ``


### DATABASE_PASSWORD

Database password

Default: ``


### DATABASE_PORT

Database port

Default: ``


### DATABASE_TYPE

Database type - currently only 'postgresql' is supported

Default: ``


### DATABASE_USERNAME

Database username

Default: ``


### DEFAULT_CHECK_INTERVAL

Default check run interval, if not specified by check (seconds)

Default: `300`


### DEFAULT_CHECK_TIMEOUT

Default run timeout

Default: `60`


### FIREFOX_HEADLESS

Whether to run firefox in headless mode

Default: `True`


### MAX_CHECK_INTERVAL

Max check run interval

Default: `31536000`


### MAX_CHECK_QUEUE_TIME

Check queue timeout

Default: `120`


### MAX_CHECK_TIMEOUT

Max run timeout

Default: `300`


### MIN_CHECK_INTERVAL

Min check run interval

Default: `0`


### MIN_CHECK_TIMEOUT

Min run timeout

Default: `1`


### PREFER_CACHED_BROWSER


Whether the order of browser preference can be changed
to use a cached browser.

If a check supports Firefox and Chrome, firefox is used by default.

However, if an agent has a Chrome browser cached, enabling this option
will cause the run to switch to use Chrome, which will improve
run startup performance.

This may result in inconsistent browsers across runs, where a check is run
with one type of browser and a different on the next.


Default: `True`


### QUEUE_TASK_RESULT_RETENTION_MINS

Expiry time for celary task results from redis

Default: `1440`


### REDIS_HOST

Redis hostname/IP

Default: ``


### REDIS_INSTANCE

Redis instance ID

Default: ``


### REDIS_PASSWORD

Redis password

Default: ``


### REDIS_PORT

Redis port

Default: `0`


### REDIS_TYPE

Redis type - currently only supports 'redis'

Default: ``


### REDIS_USERNAME

Redis username

Default: ``


### RESULT_ARTIFACT_RETENTION_DAYS


Result artifact retention, containing logs and screenshots. This will replace any pre-existing S3 bucket policies.

Set to 0 if you are using a custom policy or do no want artifacts to be deleted.


Default: `365`


### RESULT_RETENTION_MINS


Expiry time of run results from database (in minutes).

Defaults to `RESULT_ARTIFACT_RETENTION_DAYS` (converted to minutes).

This should generally be configured to the same period of time as RESULT_ARTIFACT_RETENTION_DAYS.


Default: `525600`


### SCREENSHOT_ON_FAILURE_DEFAULT

Whether to always perform a screenshot after a run in browser tests

Default: `True`


### SENTRY_DSN

Sentry DSN to enable error reporting to sentry

Default: ``


### SENTRY_ENVIRONMENT

Sentry environment

Default: `prod`


### UI_RESULT_EXPIRE



Default: `604800`


### VICTORIAMETRICS_URL

Victoriametrics URL

Default: ``

