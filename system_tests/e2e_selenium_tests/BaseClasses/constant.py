import os
import sys
import time
from stormx_api_client.environments import SUPPORTED_ENVIRONMENTS
RUN_TESTS_HEADLESS = True
SINGLE_SIGN_ON_ENABLED = False

# NOTE: For running test without headless browser.
if sys.argv[2].lower() == 'false':
    RUN_TESTS_HEADLESS = False
FETCH_INSTANCE = sys.argv[1]  # Environment setup
# For running sso tests.
if 'sso' in sys.argv[3].lower():
    SINGLE_SIGN_ON_ENABLED = True
INVALID_URL_PARAMS = "/ABC/123"
BOOKING_PREVIOUS_DAY_INVENTORY_HOUR = 5
# STORMX_URL = os.getenv("URL", "http://192.168.56.101/")
STORMX_URL = SUPPORTED_ENVIRONMENTS[FETCH_INSTANCE]['php_host']
LOGOUT_URL = STORMX_URL + "/admin/index.php?logout=true"
IDP_URL = os.getenv("URL", "http://192.168.56.103/simplesaml/saml2/idp/SSOService.php?spentityid=stormx-sp")
MAX_EXPLICIT_WAIT = 10
SLEEP_SCALE_FACTOR = 1.0
SLEEP_ADDITIONAL_SECONDS = 0.0


def sleep(number_of_seconds):
    time.sleep(SLEEP_SCALE_FACTOR*number_of_seconds + SLEEP_ADDITIONAL_SECONDS)
