
import os

import requests

from test.e2e import EndToEndBaseTest
import jmon.models.check


class TestApiCheck(EndToEndBaseTest):


    def test_register_check(self):
        """Register check with API"""
        create_res = requests.post(
            f"{self.BASE_URL}/api/v1/checks",
            headers={
                "Content-Type": "application/json"
            },
            data="""
name: Test-Check-Register

environment: default

steps:
 - goto: https://example.localhost

"""
        )
        assert create_res.status_code == 200
        assert create_res.json() == {'msg': 'Check created/updated', 'status': 'ok'}

        # Ensure check has been created
        check_res = requests.get(
            f"{self.BASE_URL}/api/v1/checks/Test-Check-Register/environments/default"
        )
        assert check_res.status_code == 200
        assert check_res.json() == {
            "name": "Test-Check-Register",
            'attributes': {},
            'calculated_interval': 300,
            'calculated_timeout': 60,
            'client': None,
            'enable': True,
            'interval': 0,
            'name': 'Test-Check-Register',
            'screenshot_on_error': None,
            'step_count': 1,
            'steps': [{'goto': 'https://example.localhost'}],
            'supported_clients': [
                'REQUESTS',
                'BROWSER_FIREFOX',
                'BROWSER_CHROME'
            ],
            'timeout': 0,
        }


