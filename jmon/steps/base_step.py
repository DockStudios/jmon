
from jmon.logger import logger
from jmon.step_logger import StepLogger
from jmon.step_state import StepState
from jmon.step_status import StepStatus


class BaseStep:

    # Key in steps YAML that the class is matched against
    CONFIG_KEY = None
    # Whether this step (on it's own) produces a
    # successful status, or whether child determine
    # the status
    # @TODO Come up with a better name (meta-step?/collection step?)
    CHILD_STEPS_FORM_STEP = False

    """Allow some step types to debug/info logging"""
    SHOULD_INFO_DEBUG_LOG = True

    def __init__(self, run, config, parent, run_logger=None):
        """Store member variables"""
        self._config = config
        self._run = run
        self._parent = parent
        self._child_steps = None
        self._status = StepStatus.NOT_RUN

        self._logger = (
            StepLogger(step=self, should_info_debug_log=self.SHOULD_INFO_DEBUG_LOG)
            if run_logger else
            logger
        )

        logger.debug(f"Creating step: {self.__class__.__name__}: {config}")

    @property
    def full_id(self):
        """Return full Id for step"""
        id = ""
        if self._parent is not None:
            id = self._parent.full_id + " -> "
        id += self.id
        return id

    @property
    def id(self):
        """ID string for step"""
        raise NotImplementedError

    @property
    def description(self):
        """Friendly description of step"""
        raise NotImplementedError

    @property
    def supported_clients(self):
        """Return list of supported clients"""
        raise NotImplementedError

    @property
    def status(self):
        """Return current status"""
        return self._status

    def as_dict(self):
        """Return information about step"""
        return {
            "name": self.id,
            "description": self.description,
            "log": "",
            "status": self.status.value,
            "children": [
                child.as_dict()
                for child in self.get_child_steps()
            ]
        }

    def get_child_steps(self):
        """Get child steps"""
        # Return cached child steps
        if self._child_steps is None:

            self._child_steps = []

            if not self._config or type(self._config) not in [list, dict]:
                return self._child_steps

            supported_child_steps = self.get_supported_child_steps()

            # Handle lists of steps
            if type(self._config) is list:
                for step_config in self._config:
                    for supported_step_name, supported_step_class in supported_child_steps.items():
                        if supported_step_name in step_config:
                            self._child_steps.append(
                                supported_step_class(
                                    run=self._run,
                                    config=step_config[supported_step_name],
                                    parent=self,
                                    run_logger=self._logger
                                )
                            )

            # Handle check dictionaries
            elif type(self._config) is dict:
                for step_name in self._config:
                    if step_name in supported_child_steps:
                        self._child_steps.append(
                            supported_child_steps[step_name](
                                run=self._run,
                                config=self._config[step_name],
                                parent=self,
                                run_logger=self._logger
                            )
                        )

        return self._child_steps

    def _check_valid_requests_response(self, element):
        """Check that the execution argument is a valid repsonse"""
        if element is None:
            self.set_status(StepStatus.FAILED)
            self._logger.error("This step requires a request to have been made")
            return True
        return False

    def _check_valid_dns_response(self, response):
        """Check that the execution argument is a valid DNS repsonse"""
        if response is None:
            self.set_status(StepStatus.FAILED)
            self._logger.error("This step requires a DNS step to have been performed")
            return True
        return False

    def get_supported_clients(self, supported_clients):
        """Return filtered list of supported clients"""
        supported_clients = [
            client
            for client in supported_clients
            if client in self.supported_clients
        ]
        for child_step in self.get_child_steps():
            supported_clients = child_step.get_supported_clients(supported_clients)
        return supported_clients

    @property
    def supported_child_steps(self):
        """Return list of child support step classes"""
        raise NotImplementedError

    def get_supported_child_steps(self):
        """Get dictionary of supported child steps"""
        return {
            child_step.CONFIG_KEY: child_step
            for child_step in self.supported_child_steps
            if child_step.CONFIG_KEY
        }

    def execute_selenium(self, state):
        """Execute step using selenium"""
        raise NotImplementedError

    def execute_requests(self, state):
        """Execute step using requests"""
        raise NotImplementedError

    def set_status(self, status):
        """Set status"""
        if status is StepStatus.FAILED:
            self._logger.error("Step failed")
        elif status is StepStatus.SUCCESS:
            self._logger.info(f"Step completed")
        elif status is StepStatus.TIMEOUT:
            self._logger.error("Step has failed due to run timeout reached")
        self._status = status

    def _validate_step(self):
        """Check step is valid"""
        raise NotImplementedError

    def validate_steps(self):
        """Validate step has a valid configuration"""
        self._validate_step()
        for child_step in self.get_child_steps():
            child_step.validate_steps()

    def has_timeout_been_reached(self):
        """Return whether timeout has been reached"""
        return self._run.get_remaining_time().total_seconds() <= 0

    def inject_variables_into_string(self, source):
        """Inject run variables into source string/list"""
        if type(source) is str:
            try:
                source = source.format(**self._run.variables)
            except KeyError:
                self._logger.warn(f"Could not inject variables on string: {source} due to missing variable")
        elif type(source) is list:
            source = [
                self.inject_variables_into_string(source_itx)
                for source_itx in source
            ]
        return source

    def execute(self, execution_method, state: StepState):
        """Execute the current step and then execute each of the child steps"""
        # Check for timeout in check
        if self.has_timeout_been_reached():
            self.set_status(StepStatus.TIMEOUT)
            return self.status

        self._status = StepStatus.RUNNING

        self._logger.info(f"Starting {self.id}")
        self._logger.info(self.description)

        getattr(self, execution_method)(state=state)

        # If status has been changed from running,
        # return
        if self.status is not StepStatus.RUNNING:
            return self.status

        # If child steps do not form part of this step,
        # mark status as success, if not already failed.
        if not self.CHILD_STEPS_FORM_STEP:
            self.set_status(StepStatus.SUCCESS)

        child_status = None

        for step in self.get_child_steps():
            child_state = state.clone_to_child()
            child_status = step.execute(
                execution_method=execution_method,
                state=child_state
            )

            state.integrate_from_child(child_state)

            # If child step has failed, return early
            if child_status is not StepStatus.SUCCESS:
                break

        if self.CHILD_STEPS_FORM_STEP:
            # Set current step to failed if child step has failed.
            self.set_status(child_status)

        # Return own status if child status is success or there it none,
        # otherwise, return child status as the outcome status
        return (self.status if (child_status is None or child_status is StepStatus.SUCCESS) else child_status)
