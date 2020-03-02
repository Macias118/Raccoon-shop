from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import unittest

class PageTest(unittest.TestCase):

    def setUp(self):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')

        self.driver = webdriver.Chrome('C:\\Users\\maciejrx\\Documents\\python_exercise\\test-training\\tests\\chromedriver.exe')

    def test_result_count(self):
        self.driver.get('localhost:5000/login')

        user_field = self.driver.find_element_by_name('username')
        psswrd_field = self.driver.find_element_by_name('psswrd')
        user_field.clear()
        psswrd_field.clear()

        self.assertEqual(1,1)

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)