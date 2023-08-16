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
# Startup
docker-compose up -d

# Modify any passwords in the .env file to secure the installation
vi .env

# Add check for W3Schools
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

## Creating Notifications

Create a new python module in `jmon/plugins/notifications` with a class inheriting from `NotificationPlugin`, implementing one or more of the following methods:
 * `on_complete`
 * `on_first_success`
 * `on_every_success`
 * `on_first_failure`
 * `on_every_failure`

For an example, see the `jmon/plugins/notifications/example_notification.py` plugin and the `jmon/plugins/notifications/slack_example.py` plugins

## Production Deployment

It is recommended to deploy Postgres, rabbitmq and redis is seperate high-availability clusters.

If using docker-compose to deploy this, update the .env with the details of the clusters and remove these services from the docker-compose.yml file.

## Upgrading

Before performing an upgrade, ensure to check the release for database changes.
If there are any database changes, it is safest to stop the jmon application (agents, scheduler and server).

To upgrade using docker-compose run:
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


## Local development

For most local development, using docker-compose appears to work well. The containers should load quickly on a change to the `jmon` code.

However, changing the `ui` code will result in a new npm build. The UI can be run locally, using:
```
cd ui
# This node env will instruct the UI to make API calls to https://localhost:5000
npm install
NODE_ENV=development npm start
```

