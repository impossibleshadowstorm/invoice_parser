from django.test import SimpleTestCase
from common import logger

class TestCommon(SimpleTestCase):

    def test_common(self):
        logger.error("Test Sucess")
        self.assertTrue(True)
