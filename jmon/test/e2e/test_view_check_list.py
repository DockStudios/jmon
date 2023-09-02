
from selenium.webdriver.common.by import By

from jmon.models.run import RunTriggerType
from jmon.test.e2e import EndToEndSeleniumTest
import jmon.models.check
import jmon.tasks.perform_check


class TestApiTriggerCheck(EndToEndSeleniumTest):

    def _create_and_trigger_run(self, name, working):
        """Create run and trigger check"""
        check = jmon.models.check.Check.from_yaml(
            f"""
name: {name}
steps:
 - goto: http://server:{5000 if working else 5923}
 - check:
     title: JMon

# Long interval to avoid two checks running
interval: 6000
"""
        )
        jmon.tasks.perform_check.perform_check.apply_async(
            args=(check.name, check.environment.name),
            kwargs={"trigger_type": RunTriggerType.SCHEDULED.value},
            options=check.task_options
        ).get()

    def test_view_check_list(self):
        """Check check list in homepage"""
        # Create working check
        self._create_and_trigger_run("working_check", working=True)
        self._create_and_trigger_run("semi_working_check", working=True)
        self._create_and_trigger_run("semi_working_check", working=True)
        self._create_and_trigger_run("semi_working_check", working=False)

        # Go to homepage
        self._selenium.get(self.BASE_URL)

        # Find table on page
        check_table = self._selenium.find_element(By.CLASS_NAME, "MuiDataGrid-main")

        # Check table header
        header_row = check_table.find_element(By.CLASS_NAME, "MuiDataGrid-columnHeaders")
        assert [
            header.text
            for header in header_row.find_elements(By.CLASS_NAME, "MuiDataGrid-columnHeader")
        ] == ["Environment", "Name", "Average Success", "Latest Status", "Enabled"]

        # Check rows
        expected_rows = [
            # Check failed test with 2dp. of accuracy
            ['default', 'semi_working_check', '66.67%', 'Failed', 'Enabled', ''],
            # Check successful with rounded percentage
            ["default", "working_check", "100%", "Success", "Enabled", ""]
        ]
        for row in check_table.find_element(By.CLASS_NAME, "MuiDataGrid-virtualScrollerContent").find_elements(By.CLASS_NAME, "MuiDataGrid-row"):
            assert expected_rows.pop(0) == [td.text for td in row.find_elements(By.CLASS_NAME, "MuiDataGrid-cell")]
        assert len(expected_rows) == 0
