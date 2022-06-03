import requests

from stormx_verification_framework import StormxSystemVerification


class TestQrCodes(StormxSystemVerification):
    """
    Verify QR code functionality is functioning properly.
    """
    selected_environment_name = None

    @classmethod
    def setUpClass(cls):
        super(TestQrCodes, cls).setUpClass()

    def test_bad_meal_qr_code(self):
        url = self._api_host + '/offer/meal/qr/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaaaaaaa/meal.png'
        headers = self._generate_passenger_headers()
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Meal not found.', response.text)
