# jmon

Simple YAML config-based website/canary monitoring solution.

This project is currently in early development.

It can currently:
 * Register checks
 * Perform distributed checks across agents
 * Checks can:
   * Goto URL
   * Find elements by various properties
   * Check title/url/element text
   * Click on elements, send text and press enter
   * Find elements by ID/class/tag/placeholder/text
   * Verify response code and JSON content for API endpoints
   * Take screenshots
 * Custom plugins hooks for tasks for performing custom integrations

For a full list of check features, see [docs/step_reference.md](docs/step_reference.md)

For a list of upcoming features and issues being worked on, please see https://gitlab.dockstudios.co.uk/mjc/jmon/-/issues

## Additional sub-projects

 * Terraform provider to manage JMon checks and environments - https://gitlab.dockstudios.co.uk/pub/jmon/jmon-terraform-provider
 * Chrome browser plugin to capture user-journeys and automatically generate JMon step configuration - https://gitlab.dockstudios.co.uk/pub/jmon/jmon-chrome-plugin

## Getting started

```bash
# Clone the repository and cd into it
git clone https://github.com/DockStudios/JMon
cd JMon

# Modify JMon version and any passwords in the .env file to secure the installation
vi .env

# Review docs/CONFIG.md for any configuration values that you wish to change.
# Ensure the victoriametrics retention period matches you desired value in docker-compose.yml

# Startup
docker-compose up --pull -d

# Add check for W3Schools
# If an API key has been configured, use the header argument to curl:
# -H 'X-JMon-Api-Key: YOUR_API_KEY'
curl -XPOST localhost:5000/api/v1/checks -H 'Content-Type: application/yml' -d '

name: Check_W3Schools

steps:
  # Goto Homepage
  - goto: https://www.w3schools.com/default.asp
  - check:
      title: W3Schools Online Web Tutorials

  # Accept cookies
  - find:
    - id: accept-choices
    - actions:
      - click

  # Use search to find python
  - find:
    - placeholder: "Search our tutorials, e.g. HTML"
    - actions:
      - type: Python
      - press: enter
  - check:
      url: "https://www.w3schools.com/python/default.asp"
'

# Add check for Wikipedia
curl -XPOST localhost:5000/api/v1/checks -H 'Content-Type: application/yml' -d '
name: Check_Wikipedia

# Disable screenshots on error
screenshot_on_error: false


# Specify browser
# Options are:
#  * BROWSER_CHROME
#  * BROWSER_FIREFOX
#  * REQUESTS - for performing only json and response code checks
client: BROWSER_CHROME

# Check every 5 minutes
interval: 300

steps:
  # Check homepage
  - goto: https://en.wikipedia.org/wiki/Main_Page
  - check:
      title: Wikipedia, the free encyclopedia
  - actions:
    - screenshot: Homepage

  # Perform search
  - find:
    - id: searchform
    - find:
      - tag: input
      - actions:
        - type: Pabalonium
        - press: enter
  - check:
      url: "https://en.wikipedia.org/w/index.php?fulltext=Search&search=Pabalonium&title=Special%3ASearch&ns0=1"
  - find:
    - class: mw-search-nonefound
    - check:
        text: There were no results matching the query.
  - actions:
    - screenshot: SearchResults

  # Example call of plugin
  - call_plugin:
      example-plugin:
        example_argument: example_value

  # Use variable provided by example variable in call
  - goto: https://example.com/{variable_set_by_example_plugin}
'
```

After submitting new checks, new checks are scheduled every 30 seconds.

Goto http://localhost:5000 to view dashboard

Goto http://localhost:5555 to view the celary tasks.

Goto http://localhost:9001 to view minio for s3 bucket, logging in with AWS credentials from .env


## Step reference

For a full reference of steps, please see [docs/step_reference.md](docs/step_reference.md)

## Debugging issues

See [docs/debugging_issues.md](docs/debugging_issues.md) for known issue cases.

## Creating notifications plugins

Create a new python module in `jmon/plugins/notifications` with a class inheriting from `NotificationPlugin`, implementing one or more of the following methods:
 * `on_complete`
 * `on_first_success`
 * `on_every_success`
 * `on_first_failure`
 * `on_every_failure`

For an example, see the [jmon/plugins/notifications/example_notification.py](jmon/plugins/notifications/example_notification.py) plugin and the [jmon/plugins/notifications/slack_example.py](jmon/plugins/notifications/slack_example.py) plugins

## Creating Callable plugin

Create new python module in `jmon/plugins/callable`, with a class inherting from `CallablePlugin`, implementing the following:
 * `PLUGIN_NAME` - override property with the name of the plugin that will be called by the check step.
 * `handle_call` - implement method, with kwargs that are expected to be passed by the check step.

Plugins can set "run variables" during execution. These run variables can be injected into most check step.

Objects for accessing run information, check methods and logging methods are available within the plugin class instance.

For an example, see the [jmon/plugins/callable/example_callable_plugin.py](jmon/plugins/callable/example_callable_plugin.py) example plugin.

## Production Deployment

It is recommended to deploy Postgres, rabbitmq and redis is seperate high-availability clusters.

If using docker-compose to deploy this, update the .env with the details of the clusters and remove these services from the docker-compose.yml file.

Create unique API key (see `.env`). Alternatively, disable API key access by removing or setting to an empty string.

## Upgrading

Before performing an upgrade, ensure to check the release for database changes.
If there are any database changes, it is safest to stop the jmon application (agents, scheduler and server).

### Re-built images

To upgrade using re-built images using docker-compose run:
```
# Stop docker-compose stack
docker-compose stop

# Adjust JMon version in .env
vi .env

# Bring up application, rebuilding the containers
## Initially perform DB migration
docker-compose up --pull database dbmigrate

## Bring up remaining application
docker-compose up --pull
```

### Custom images

To upgrade using custom built images, run:
```
# Stop docker-compose stack
docker-compose stop

# Manually back up any local modifications (.env file and any plugins), and optionally git stash them
git stash

# Pull latest changes
git fetch --all

# To check out a particular release tag
git checkout v<new version>

# Restore modifications - this may require manual conflict resolution
git stash pop

# Bring up application, rebuilding the containers
## Initially perform DB migration
docker-compose up -d --build database dbmigrate

## Bring up remaining application
docker-compose up -d --build
```

### s3 artifact storage

The artifacts can be stored in s3.

Create an s3 bucket and provide the jmon containers with access to the bucket with the following permissions:

 * PutObject
 * GetObject
 * ListObjects
 * PutLifecycleConfiguration (unless `RESULT_ARTIFACT_RETENTION_DAYS` has been disabled)

The IAM role providing permission can be attached to the EC2 instance running the containers, or to the containers directly if deploying to ECS.

Update the .env (or environment variables for the containers, if the containers have been deployed in a different manor) with the S3 bucket name.

## Browser caching and headless mode

**Note the browser caching functionality is experimental and may lead to instability**

Browser caching can be enabled, which will share browser instances between runs.
Headless is enabled by default, but can be enabled/disabled in the config (and different headless modes can be configured for chrome)

Performance:

| Browser | Headless Mode | Browser Caching | Check speed (run in a small development environment - values for comparison only) |
|---------|---------------|-----------------|-----------------------------------------------------------------------------------|
| Firefox | Disabled      | Disabled        | 9500ms                                                                            |
| Firefox | Disabled      | Enabled         | 320ms (30x performance improvement)                                               |
| Firefox | Enabled       | Disabled        | 4654ms                                                                            |
| Firefox | Enabled       | Enabled         | 733ms                                                                             |
| Chrome  | None          | Disabled        | 1730ms                                                                            |
| Chrome  | None          | Enabled         | 530ms (~3-4x performance improvement)                                             |
| Chrome  | New           | Disabled        | 2110ms                                                                            |
| Chrome  | New           | Enabled         | 1274ms                                                                            |
| Chrome  | Legacy        | Disabled        | 1514ms                                                                            |
| Chrome  | Legacy        | Enabled         | 580ms                                                                             |

This can be enabled by setting the `CACHE_BROWSER` environment variable to `True` on the agents

## Terminology

* Environment - an arbritrary object for grouping checks. Can be used to group checks by application environment (e.g. dev, prod) or tenants (customer-a, customter-b) or anything else
* Check - A check is defined and created via the API (or via Terraform provider). A single check is tied to a single environment.
* Run - Runs are created at intervals, which are an execution of a check. When a run is executed, it creates an instance of the Check's steps and executes them and results in a pass/fail status.
* Step - A section of executable part of the check, e.g. Find, Goto etc. These are defined in the check steps definition. Instances of 'Steps' are accessible to plugins, which contain information about the active instance of the step.

## Local development

For most local development, using docker-compose appears to work well. The containers should load quickly on a change to the `jmon` code.

However, changing the `ui` code will result in a new npm build. The UI can be run locally, using:
```
cd ui
# This node env will instruct the UI to make API calls to https://localhost:5000
npm install
NODE_ENV=development npm start
```

## Architecture

 * API/UI - written in python and javascript/angular, which handles API requests for interacting with configuration and results
 * Postgres - Storing check information and results
 * S3 - Stores run artifacts (log and screenshots), using minio by default
 * Redis - Stores check/result metrics and configuration for celery
 * RabbitMQ - Handles queuing of tasks for distribution to agents
 * Agents - Uses celery to run checks and built-in maintenance tasks
 * Flower - Provides a dashboard for monitoring the celery tasks
