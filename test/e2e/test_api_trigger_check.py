

from time import sleep

from selenium.webdriver.common.by import By

from test.e2e import EndToEndSeleniumTest
import jmon.models.check
import jmon.models.run


class TestApiTriggerCheck(EndToEndSeleniumTest):

    def find_check_details_table_row_by_label(self, label):
        """Find row of check details table by label td text"""
        # Get check details table
        check_details_table = self._selenium.find_element(By.XPATH, ".//table[@aria-label='Check details']")
        # Find tr, which contains a th with text and get td within the tr
        return check_details_table.find_element(By.XPATH, f".//tr[.//th[text()='{label}']]/td")

    def test_trigger_check(self):
        """Create check and trigger in UI"""
        check = jmon.models.check.Check.from_yaml(f"""
name: test-trigger-check
steps:
 - goto: http://server:5000
 - check:
     title: JMon

# Long interval to avoid two checks running
interval: 6000
"""
        )

        # Goto check page
        self._selenium.get(
            f"{self.BASE_URL}/checks/test-trigger-check/environments/default"
        )

        # Click on scheduler trigger
        action_buttons = self.find_check_details_table_row_by_label("Actions").find_elements(By.TAG_NAME, "button")
        check_trigger_button = [x for x in filter(lambda x: x.text == "Trigger Run", action_buttons)][0]
        check_trigger_button.click()

        # Find new row for trigger status
        manual_trigger_status = self.find_check_details_table_row_by_label("Manual Trigger Status")
        assert manual_trigger_status.text == "SCHEDULING"

        for _ in range(20):
            assert manual_trigger_status.text in ["SCHEDULING", "PENDING"]
            if manual_trigger_status.text == "PENDING":
                break
            sleep(0.25)
        else:
            raise Exception("Did not find PENDING state")
        
        for _ in range(60):
            if self._selenium.current_url != f"{self.BASE_URL}/checks/test-trigger-check/environments/default":
                break
            sleep(0.25)
        else:
            raise Exception("Did not redirect to results page")
        
        assert "/runs/" in self._selenium.current_url

        # Get run
        runs = jmon.models.run.Run.get_by_check(check=check, limit=1)
        assert len(runs) == 1
        run = runs[0]

        self._check_looks_like_a_valid_run_page(check_name="test-trigger-check", environment_name="default", run_timestamp=run.timestamp_id)
