
from time import sleep
from selenium.webdriver.common.by import By
from pyvirtualdisplay import display

from jmon.client_type import ClientType
from jmon.runner import BrowserFactory
import jmon.models.check


class EndToEndBaseTest:
    """Base end-to-end tests"""

    BASE_URL = "http://server:5000"

    def setup_method(self, method):
        """Setup test"""
        pass

    def teardown_method(self, method):
        """Clean up test"""
        # Delete all checks
        for check in jmon.models.check.Check.get_all():
            check.delete()

    @classmethod
    def setup_class(cls):
        """Stub method for performing future setup class"""
        pass

    @classmethod
    def teardown_class(cls):
        """Stub method for performing future teardown"""
        pass


class EndToEndSeleniumTest(EndToEndBaseTest):
    """Base end-to-end tests using selenium"""

    def setup_method(self, method):
        """Setup test, start selenium"""
        self._browser_factory = BrowserFactory.get()
        self._browser = self._browser_factory.get_browser(ClientType.BROWSER_FIREFOX)
        self._selenium = self._browser.selenium_instance
        return super().setup_method(method)

    def teardown_method(self, method):
        """Teardown browser"""
        self._browser.teardown()
        return super().teardown_method(method)

    def setup_class(cls):
        """Create display"""
        EndToEndBaseTest.setup_class()
        cls._display = display.Display(visible=False)
        cls._display.start()

    def teardown_class(cls):
        """Teardown display"""
        cls._display.stop()
        cls._display = None
        EndToEndBaseTest.teardown_class()

    def _check_looks_like_a_valid_run_page(self, check_name, environment_name, run_timestamp):
        """Ensure page looks like a valid run page"""
        # Check page title
        title = self._selenium.find_element(By.ID, "run-title")
        assert title.text == f"{check_name} - {environment_name} - {run_timestamp}"

        # Attempt to find basic info in log
        for itx in reversed(range(5)):
            run_log = self._selenium.find_element(By.ID, "run-log").get_attribute("innerHTML")
            try:
                assert "Supported clients:" in run_log
                assert "Root -&gt; " in run_log
                assert "Step completed" in run_log
                break
            except AssertionError:
                if itx == 0:
                    print(run_log)
                    raise
                sleep(0.25)
