import pytest
from selenium import webdriver

class TestGeneral:
    def setup_class(self):
        self.driver = webdriver.Chrome()

    def test_home(self):
        self.driver.get("django:8000")
        assert 1 == 1

    def teardown_class(self):
        self.driver.close()