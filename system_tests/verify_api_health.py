
import requests

from stormx_verification_framework import StormxSystemVerification


class TestApiHealth(StormxSystemVerification):
    """
    Verify `/health-check-api` endpoint behavior.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHealth, cls).setUpClass()

    def test_health_check__happy(self):
        url = self._api_host + '/health-check-api?from=system-test'
        headers = {'User-Agent': 'stormx_system_test'}
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_health_check__without_from_parameter(self):
        url = self._api_host + '/health-check-api'  # note: no `from` parameter
        headers = {'User-Agent': 'stormx_system_test'}
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)
