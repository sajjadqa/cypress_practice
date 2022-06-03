import requests

from stormx_verification_framework import StormxSystemVerification


class TestApiHotelSearchInternal(StormxSystemVerification):
    """
    Verify hotel search behavior for the internal hotel search endpoint (`/api/v1/tvl/airline/{airline_id}/hotels`).
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestApiHotelSearchInternal, cls).setUpClass()

    def test_tvl_internal_get_hotels(self):
        """
        test GET tvl/airline/{airline_id}/hotels
        """
        airline_id = '294'
        no_inv_airline_id = '265'
        stormx_headers = self._generate_tvl_stormx_headers()

        no_inv_resp = requests.get(
            url=self._api_host + '/api/v1/tvl/airline/' + no_inv_airline_id + '/hotels?port=YYZ&room_count=1&provider=tvl',
            headers=stormx_headers)
        self.assertEqual(no_inv_resp.status_code, 200)
        no_inv_resp_json = no_inv_resp.json()
        self.assertEqual(len(no_inv_resp_json['data']), 0)

        inv_resp = requests.get(
            url=self._api_host + '/api/v1/tvl/airline/' + airline_id + '/hotels?port=LAX&room_count=1&provider=tvl',
            headers=stormx_headers)
        self.assertEqual(inv_resp.status_code, 200)
        inv_resp_json = inv_resp.json()
        self.assertGreater(len(inv_resp_json['data']), 0)
