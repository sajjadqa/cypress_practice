import json
import requests

from stormx_verification_framework import (
    StormxSystemVerification,
    display_response,
)


class TestRateCap(StormxSystemVerification):
    def setup(self):
        super(TestRateCap, self).setUp()

    def test_add_rate_cacp(self):

        currency = self.get_available_currencies_for_rate_cap()
        warning = 100
        currency_to_add = ''
        if len(currency) > 0:
            currency_to_add = currency[0]['id']
            # add rate cap
            response = self.add_edit_rate_cap(rate_cap_currency=currency_to_add, rate_cap_warning=warning)
            self.assertGreater(int(response), 0)

            rate_caps = self.get_rate_caps()

            # validate rate caps are getting added
            self.assertGreater(len(rate_caps), 0)
        else:
            print ("No Currency available to add rate cap")


    def test_edit_rate_cap(self):

        currency = self.get_available_currencies_for_rate_cap()
        warning = 50
        currency_to_add = ''
        if len(currency) > 0:
            currency_to_add = currency[0]['id']
            # add rate cap
            rate_cap_id = self.add_edit_rate_cap(rate_cap_currency=currency_to_add, rate_cap_warning=warning)
            self.assertGreater(int(rate_cap_id), 0)

            response = self.add_edit_rate_cap(currency_to_add, 120, rate_cap_id)

            self.assertEqual(response, True)
        else:
            print ("No Currency available to add/edit rate cap")


    def test_validate_edit_rate_cap_(self):

        currency = self.get_available_currencies_for_rate_cap()
        warning = 100
        currency_to_add = ''
        if len(currency) > 0:
            currency_to_add = currency[0]['id']
            # add rate cap
            rate_cap_id = self.add_edit_rate_cap(rate_cap_currency=currency_to_add, rate_cap_warning=warning)
            self.assertGreater(int(rate_cap_id), 0)

            response = self.add_edit_rate_cap(currency_to_add, 99999999, rate_cap_id)

            self.assertEqual(response, False)
        else:
            print ("No Currency available to validate rate cap")



    def test_remove_rate_cap(self):

        currency = self.get_available_currencies_for_rate_cap()
        warning = 150
        currency_to_add = ''
        if len(currency) > 0:
            currency_to_add = currency[0]['id']
            # add rate cap
            rate_cap_id = self.add_edit_rate_cap(rate_cap_currency=currency_to_add, rate_cap_warning=warning)
            self.assertGreater(int(rate_cap_id), 0)

            # remove rate cap
            response = self.remove_rate_cap(rate_cap_id)

            self.assertEqual(response, True)
        else:
            print ("Nothing to remove")
