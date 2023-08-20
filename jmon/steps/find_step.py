
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from jmon.client_type import ClientType
from jmon.errors import StepValidationError
from jmon.step_state import SeleniumStepState
from jmon.step_status import StepStatus

from jmon.steps.action_step import ActionStep
from jmon.steps.base_step import BaseStep
from jmon.logger import logger
from jmon.steps.check_step import CheckStep
from jmon.utils import RetryStatus, retry


class FindStep(BaseStep):
    """
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
    """

    CONFIG_KEY = "find"
    _SUPPORTED_ATTRIBUTES = [
        "id",
        "class",
        "text",
        "placeholder",
        "tag"
    ]

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        return [
            ClientType.BROWSER_FIREFOX,
            ClientType.BROWSER_CHROME
        ]

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        return [
            FindStep,
            ActionStep,
            CheckStep
        ]

    @property
    def id(self):
        """ID string for step"""
        return f"Find"

    @property
    def description(self):
        """Friendly description of step"""
        _, description, _ = self._get_find_type()
        return f"Find element {description}"

    def _get_find_config(self):
        """Return dictionary of supported attributes"""
        config = {}
        for config_itx in self._config:
            for key_ in config_itx:
                if key_ in self._SUPPORTED_ATTRIBUTES:
                    config[key_] = config_itx[key_]
        return config

    def _validate_step(self):
        """Check step is valid"""
        invalid_type_error = """
Find must be a list of dictionaries. E.g.:
  - find:
     - id: my_div_id

Actual config: {config}
""".strip()

        if type(self._config) is not list:
            raise StepValidationError(invalid_type_error.format(config=self._config))

        found_types = []
        for item in self._config:
            if type(item) is not dict:
                raise StepValidationError(invalid_type_error.format(config=item))

            # Get a list of all valid attributes for find
            dict_contains_valid_key = False
            for key_ in item:
                if key_ in self._SUPPORTED_ATTRIBUTES:
                    dict_contains_valid_key = True
                    found_types.append(key_)

            # If the dictionary contains a supported attribute, ensure there
            # are no attributes that are not recognised.
            if dict_contains_valid_key:
                for key_ in item:
                    if key_ not in self._SUPPORTED_ATTRIBUTES:
                        raise StepValidationError(f"Find config contains invalid attribute: {key_}: {item}")
        
        # Allow 1 type or
        # text/placeholder with tag
        if not (len(found_types) == 1 or ('tag' in found_types and ('placeholder' in found_types or 'text' in found_types))):
            raise StepValidationError("Find only supports one of: id, class, tag. Or placeholder or text with optional tag")

    def _get_find_type(self):
        """Get find type based on config"""
        config = self._get_find_config()

        by_type = None
        description = None
        value = None

        if id := config.get('id'):
            by_type = By.ID
            value = id
            description = f"by ID: {value}"
        elif (text := config.get('text')) or (placeholder := config.get('placeholder')):
            if text:
                xpath_key = 'text'
                xpath_value = text
                xpath_template = f".//{{tag}}[contains(text(), '{xpath_value}')]"

            elif placeholder:
                xpath_key = 'placeholder'
                xpath_value = placeholder
                xpath_template = f".//{{tag}}[@placeholder='{xpath_value}']"

            tag = config.get('tag')
            description = f"by {xpath_key}: {xpath_value}"
            if not tag:
                tag = '*'
            else:
                description += f" and tag: {tag}"

            # Search by XPATH
            by_type = By.XPATH
            value = xpath_template.format(tag=tag)

        elif class_name := config.get('class'):
            by_type = By.CLASS_NAME
            value = class_name
            description = f"by class: {value}"

        elif tag := config.get('tag'):
            by_type = By.TAG_NAME
            value = tag
            description = f"by tag: {value}"

        return by_type, description, value

    @retry(count=5, interval=0.5)
    def _find_element(self, element, by_type, value):
        """Find element"""
        try:
            return element.find_element(by_type, value)
        except (selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.ElementNotInteractableException) as exc:
            self._logger.error("Could not find element")
            self._logger.debug(str(exc).split("\n")[0])
            return None

    def execute_selenium(self, state: SeleniumStepState):
        """Find element on page"""
        by_type, _, value, = self._get_find_type()
        element = self._find_element(state.element, by_type, value, only_if=lambda: not self.has_timeout_been_reached())
        if element is RetryStatus.ONLY_IF_CONDITION_FAILURE:
            self.set_status(StepStatus.TIMEOUT)

        if not element:
            self.set_status(StepStatus.FAILED)
        state.element = element
