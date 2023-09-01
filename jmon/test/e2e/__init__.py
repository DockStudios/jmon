

import jmon.models.check


class EndToEndBaseTest:

    BASE_URL = "http://server:5000"

    def teardown_method(self, method):
        """Clean up test"""
        # Delete all checks
        for check in jmon.models.check.Check.get_all():
            check.delete()
