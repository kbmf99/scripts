# coding: UTF-8
import unittest
import time
import logging
import os
import sys
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Variables
timestamp = time.strftime("%Y%m%d-%H%M%S")
# user = "FFFF8660@AD.FRANCETELECOM.FR"
# password = "Orange**1"
resolution = "1920,1080"
start = time.time()

# Performance data
mainpage_load = 0
logout_time = 0

contactspage_load = 0

# Let the fun begin

class PHLOX(unittest.TestCase):
    
    def setUp(self):
        # Webdriver config
        p = webdriver.FirefoxProfile()
        sitelist = "phlox.itn.intraorange"
        p.set_preference("browser.tabs.remote.force-enable", 1)
        p.set_preference("network.negotiate-auth.trusted-uris", sitelist)
        p.set_preference("network.negotiate-auth.delegation-uris", sitelist)
        p.set_preference("network.automatic-ntlm-auth.trusted-uris", sitelist)
        p.update_preferences()

        self.driver = webdriver.Firefox(p)

    def test_all(self):

        self.start()
        self.checkIntegrity()
        self.openZimbra()
	self.checkPHLOXContact()
        self.logout()


    def start(self):
        try:
            global mainpage_load
            print("[TEST START --- PHLOX] --- Starting test, session %s" % self.driver.session_id)
            mainpage_load_start = time.time()
            self.driver.get("https://phlox.itn.intraorange")
            mainpage_load_end = time.time()
            mainpage_load = mainpage_load_end - mainpage_load_start
            self.assertIn("Welcome - Orange", self.driver.title)

        except:
            self.driver.save_screenshot("/usr/share/centreon/www/screenshots/phlox.png")
            print("[TEST FAIL] --- Could not open the main page")
            raise
        
        else:
            print("[TEST OK] --- Main page opened successfully")


    def checkIntegrity(self):
        try:
	    time.sleep(10)
            self.assertIn("Formationt Zimbra", self.driver.page_source)

        except:
 	    self.driver.save_screenshot("/usr/share/centreon/www/screenshots/phlox.png")
            print("[TEST FAIL] --- Could not find 'Formationt Zimbra' on the page")
            raise

        else:
            self.driver.save_screenshot("/usr/share/centreon/www/screenshots/phlox.png")
            print("[TEST OK] --- Found 'Formationt Zimbra'")


    def openZimbra(self):
        try:
            self.driver.get("https://zimbra.itn.intraorange")
            #element = self.driver.find_element_by_id("username")
	    #element.send_keys("formationt.zimbra@orange.com")
	    #element = self.driver.find_element_by_id("password")
	    #element.send_keys("Orange**1")
	    #element = self.driver.find_element_by_xpath("//input[@type='submit']")
            global contactspage_load
            contactspage_start = time.time()
            self.assertIn("TRN ZIMBRA ForamtionT",self.driver.page_source)
            contactspage_end = time.time()
            contactspage_load = contactspage_end - contactspage_start

        except:
            self.driver.save_screenshot("/usr/share/centreon/www/screenshots/phlox.png")
            print("[TEST FAIL] --- Could not open Zimbra correctly")
            raise

        else:
            self.driver.save_screenshot("/usr/share/centreon/www/screenshots/phlox.png")
            print("[TEST OK] --- Open Zimbra OK")

    def checkPHLOXContact(self):
        try:
            element = self.driver.find_element_by_xpath("//a[@id='TAB_ADDRESSBOOK']")
            element.click()
            self.assertIn("PHLOX, SSPO", self.driver.page_source)
       	 
        except:
            print("[TEST FAIL] --- Could not find the SSPO PHLOX contact")
            raise

        else:
            print("[TEST OK] --- Found the SSPO PHLOX contact")

    def logout(self):
        try:
	    global logout_time
            element = self.driver.find_element_by_xpath("//a[@href='/?loginOp=logout']")
	    logout_time_start=time.time()
	    element.click()
            logout_time_end=time.time()
	    logout_time=logout_time_end - logout_time_start
            self.assertIn("Zimbra Web Client Sign In", self.driver.title)

	except:
	    print("[TEST FAIL] --- Could not log out")
	    raise

	else:
            print("[TEST OK] --- Logged out successfully")




    def tearDown(self):

        self.driver.close()
        end = time.time()
        elapsed = end - start
        logging.info("[TEST END] --- Test finished in %s seconds | mainpage_load=%.2fs, logout_time=%.2fs" % (round(elapsed, 2), mainpage_load, logout_time))
        print("[TEST END] --- Test finished in %s seconds | mainpage_load=%.2fs, logout_time=%.2fs" % (round(elapsed, 2), mainpage_load, logout_time))
        
    
if __name__ == "__main__":
    display = Display(visible=0, size=(1366, 768))
    display.start()
    unittest.main()
    display.quit()
