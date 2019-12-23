import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from datetime import datetime

import ptvsd

# ptvsd.enable_attach()
# ptvsd.wait_for_attach()

class TestGeneral:
    def setup_class(self):
        self.driver = webdriver.Chrome()

    def test_home(self):
        xpath = "/html/body/main/div/div[1]/section/div/div/form/div[6]/button"
        self.driver.get("django:8000")
        element = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        assert 1 == 1

    def test_admin_login(self):

        # go to main page
        xpath = "/html/body/main/div/div[1]/section/div/div/form/div[6]/button"
        self.driver.get("django:8000")
        element = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))

        # click on connexion
        xpath = "/html/body/header/nav/div[2]/div/small/a"
        logbutton = self.driver.find_elements(By.XPATH, xpath)[0]
        logbutton.click()

        # fill the id and connect
        xpath_connect = "/html/body/main/section/div[2]/div[2]/div/form/div[4]/button"
        connectbutton = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_connect)))

        xpath_email = "//*[@id='id_username']"
        email = self.driver.find_elements(By.XPATH, xpath_email)[0].send_keys("admin@example.com")

        xpath_pwd = "//*[@id='id_password']"
        pwd = self.driver.find_elements(By.XPATH, xpath_pwd)[0].send_keys("adminpass")

        connectbutton.click()

        # check that the login is successful
        xpath_meetings = "/html/body/main/div/div[2]/h4[2]/a"
        meetingsbutton = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_meetings)))

        assert meetingsbutton.tag_name == 'a'

    def test_create_organization(self):
        self.driver.get("django:8000/user/organization/create")
        # xpath for the validation button
        xpath_validation = "/html/body/main/div[2]/div/form/div[10]/input"
        # wait for the page to be loaded
        validation_button = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_validation)))

        # orga name
        xpath = "//*[@id='id_name']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("orga " + str(datetime.now()))

        xpath = "//*[@id='id_description_ifr']"
        # self.driver.find_elements(By.XPATH, xpath)[0].click()
        self.driver.execute_script("tinyMCE.activeEditor.setContent('%s')" % "dscription")

        xpath = "//*[@id='id_email']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("orga@orga.com")

        xpath = "//*[@id='id_phone_number']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("0666666666")

        xpath = "//*[@id='id_picture']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("/tests/images/img01.jpg")

        xpath = "//*[@id='id_min_fee']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("16")

        xpath = "//*[@id='id_advised_fee']"
        self.driver.find_elements(By.XPATH, xpath)[0].send_keys("18")

        validation_button.click()

        xpath_success = "/html/body/div[1]/div"
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath_success)))

        assert True

    def teardown_class(self):
        # delete the organization
        



        self.driver.close()
