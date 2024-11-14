
# Step Reference

Each of the following elements can be included in the step templates.

Compatibility between clients differ and compatibility across all used elements must contain a common client.



## GotoStep

Key: `goto`


Directive for loading a page.

This should generally always be used as a first directive of a step.

It can be used multiple times during a check.

This can be placed in the root of the check, e.g.
```
 - goto: https://example.com
 - find:
   - tag: input
   - url: https://example.com/?followed=redirect

 - goto: https://example.com/login
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- goto: https://example.com/?id={an_output_variable}
```

For non-browser based tests, additional arguments can be provided to the Goto step:
```
- goto:
    url: https://example.com/api/search
    headers:
      X-Api-Key: MyApiKey
    json: {'query': 'test'}
    method: POST
- goto:
    url: https://example.com/api/search
    headers:
      X-Api-Key: MyApiKey
    body: "Some body string"
    method: PUT
    # Ignore SSL certificate verification
    ignore-ssl: true
    # Set timeout (in seconds)
    timeout: 5
```
Variables can also be used inside the header values, URL and body


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`, `REQUESTS`

## FindStep

Key: `find`


Directive for finding an element of a page.

Each find can use on of the following attributes, some of which can be combined:
 * `id` - Search by ID of element on the page.
 * `class` - Search for element by class name.
 * `text` - Search for element by visible text. Can be combined with `tag`.
 * `placeholder` - Search for input element by placeholder value. Can be combined with `tag`.
 * `tag` - Search for element by tag (e.g. `a` for links). Can be combined with `placeholder` or `text`.

If an element cannot be found using the given parameters, the step will fail. No `check` action is required for validating this.

This can be placed in the root of the check, e.g.
```
 - goto: https://example.com
 - find:
   - tag: input
   - url: https://example.com/?followed=redirect
```

Find elements can be nested to find elements within other elements. E.g.:
```
 - goto: https://example.com
 - find:
   - id: content
   - find:
     - class: loginForm
     - find:
       - tag: input
       - placeholder: Username
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- find:
  - id: content-{an_output_variable}
  - find:
    - class: {another_output_variable}
    - find:
      - placeholder: Hello {output_name}
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

### ActionStep

Key: `actions`


Directive for performing an action task.

Each action directive may one or more actions.

This can be placed in the root of the check, e.g.
```
 - goto: https://example.com
 - actions:
   - click
```

It can also be placed within a find directive, e.g.:
```
 - goto: https://example.com
 - find:
   - tag: input
   - actions:
     - type: Pabalonium
     - press: enter
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### ClickAction

Key: `click`


Directive for clicking the current element, simulating a mouse left-click.

E.g.
```
- goto: https://example.com
- find:
  - id: login
  - actions:
    - click
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### TypeAction

Key: `type`


Directive for typing characters into the selected element.

Supported keys:
 * `enter`

E.g.
```
- goto: https://example.com
- find:
  - id: login
  - actions:
    - click
    - type: my-username
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- actions:
  - type: '{an_output_variable}'
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### PressAction

Key: `press`


Directive for pressing buttons, simulating a keyboard button press.

Supported keys:
 * `enter`

E.g.
```
- goto: https://example.com
- find:
  - id: login
  - actions:
    - press: enter
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### ScreenshotAction

Key: `screenshot`


Directive for capturing a screenshot of the current page.

A value must be provided, which will be the name given to the screenshot.

This action can be performed multiple times.

E.g.
```
- goto: https://example.com
- actions:
  - screenshot: example
- goto: https://example.com/login
- actions:
  - screenshot: example-login
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### WaitAction

Key: `wait`


Directive for waiting for page readiness.

Supported wait states:
 * `visible` - Wait for element to be visible on screen
 * `clickable` - Wait for element to be clickable

The default wait time is 60s.

E.g.
```
- goto: https://example.com
- find:
  - id: login
  - actions:
    - wait: visible
```

Specify custom timeout
```
- actions:
   - wait:
       type: visible
       # Timeout in seconds
       timeout: 30
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### ReportPerformanceAction

Key: `report-performance`


Directive for reporting performance

E.g.
```
- goto: https://example.com
- actions:
  - report-performance
```

This sets a "performance" run variable, which contains an instance of PerformanceData with the following attributes:
  * load
  * dom_content_loaded
  * interactive

This object can be used in plugins.


Client Support: `BROWSER_FIREFOX`

### CheckStep

Key: `check`


Directive for performing a check task.

Each check directive may one or more checks.

This can be placed in the root of the check, e.g.
```
 - goto: https://example.com
 - check:
     title: Example Page
     url: https://example.com/?followed=redirect
```

It can also be placed within a find directive, e.g.:
```
 - goto: https://example.com
 - find:
   - tag: input
   - check:
       text: Enter input
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`, `REQUESTS`

#### TitleCheck

Key: `title`


Directive for verifying HTML page title.

E.g.
```
- goto: https://example.com
- check:
    title: "Example - Homepage"
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    title: '{an_output_variable}'
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### UrlCheck

Key: `url`


Directive for verifying current page URL.

E.g.
```
- goto: https://example.com
- check:
    url: https://example.com/redirect-was-followed
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    url: https://example.com/{an_output_variable}
```


Client Support: `REQUESTS`, `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### ResponseCheck

Key: `response`


Directive for verifying HTTP response code

E.g.
```
- goto: https://example.com
- check:
    response: 200
```


Client Support: `REQUESTS`

#### JsonCheck

Key: `json`


Directive for verifying the content of a JSON repsonse.

One of two validation attributes must be used:
* equals - Checks the value matches the provided content
* contains - Checks that the provided value is within the content.

A "selector" attribute may be provided to verify the value of a single element of the JSON response.
The selector uses the syntax provided by [jsonpath](https://pypi.org/project/jsonpath-python).
If a selector is not provided, the entire JSON response will be checked.

```
- check:
    json:
      selector: '$.images[0]'
      contains: 1.jpg

- check:
    json:
      selector: '$.id'
      equals: 1
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    json:
      equals: '{an_output_variable}'
```


Client Support: `REQUESTS`

#### TextCheck

Key: `text`


Directive for verifying text content.

E.g.
```
- goto: https://example.com
- check:
    text: "It's good"
```

This directive can be used within a find element. E.g.:
```
- goto: https://example.com
- find:
  - id: login
  - check:
      text: Please Login
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    text: '{an_output_variable}'
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`

#### DnsRecordsCheck

Key: `records`


Directive for verifying the responses from DNS query.

One of the following validation attributes must be used:
* equals - Checks records match exactly
* contains - Checks that the provided records exist in the response
* count - Checks the number of records in the response
* min_count - Checks the minimum number of records in the response
* cname - Ensure a CNAME is present in the check

```
- dns: www.google.co.uk
- check:
    records:
      equals: 216.58.212.196

- check:
    records:
      contains: [212.58.237.1, 212.58.235.1]

# Ensure record points to CNAME
- check:
    records:
      cname: www.bbc.co.uk.pri.bbc.co.uk.

# Ensure that at 3 records exist
- check:
    records:
      count: 3

# Ensure that at least 3 records exist
- check:
    records:
      min_count: 3
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    records:
      equals: '{an_output_variable}'
```


Client Support: `REQUESTS`

#### BodyCheck

Key: `body`


Directive for verifying the content of the repsonse body.

One of two validation attributes must be used:
* equals - Checks the value matches the provided content
* contains - Checks that the provided value is within the content.

```
- check:
    body:
      contains: 'Some Text'

- check:
    body:
      equals: 'Some text'
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- check:
    body:
      equals: '{an_output_variable}'
```


Client Support: `REQUESTS`

## CallPluginStep

Key: `call_plugin`


Directive for executing a callable plugin.

This should generally always be used as a first directive of a step.

It can be used multiple times during a check.

This can be placed in the root of the check, e.g.
```
 - call_plugin:
     example-plugin:
       example_argument: 'example_value'
```


Client Support: `BROWSER_FIREFOX`, `BROWSER_CHROME`, `REQUESTS`

## DNSStep

Key: `dns`


Directive for checking a DNS response

This should generally always be used as a first directive of a step.

It can be used multiple times during a check.

This can be placed in the root of the check, e.g.
```
- dns: www.bbc.co.uk
```

Variables provided by callable plugins can be used in the type value, e.g.
```
- dns:
    domain: www.bbc.co.uk
    type: TXT
    name_servers:
     - 8.8.8.8
     - 1.1.1.1
    protocol: tcp
    lifetime: 2
    port: 53
    timeout: 5

```


Client Support: `REQUESTS`