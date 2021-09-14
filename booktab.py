from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from distutils.spawn import find_executable
from selenium.webdriver.common.by import By
from selenium import webdriver
import pathlib
import shutil
import base64
import time
import sys
import re


class text_changed(object):
    def __init__(self, locator, text):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        actual_text = EC._find_element(driver, self.locator).get_property("value")
        return actual_text != self.text


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        chromedriver = "chromedriver.exe"
    else:
        if find_executable("chromedriver"):
            chromedriver = "chromedriver"
        else:
            chromedriver = "./chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.set_page_load_timeout(120)
    driver.set_script_timeout(120)
    driver.get("http://web.booktab.it/BooktabWeb/")

    while True:
        input('Press [Enter] when you are on the first page of the ebook (must be on the first tab!)...')

        try:
            id = re.match(".*/BooktabWeb/#/([^/]*)/.*", driver.current_url)[1]
            shutil.rmtree(f"./dump/booktab/{id}", ignore_errors=True)
            pathlib.Path(f"./dump/booktab/{id}").mkdir(parents=True, exist_ok=True)
            print(f"\nStarted dumping Booktab book {id}...")

            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element_by_css_selector("#bookviewerWindow"))
            try:
                driver.find_element_by_css_selector(".darkGreySinglePageButton").click()
            except Exception:
                pass

            i = 0
            while True:
                canvas = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".deck-current canvas")))
                time.sleep(0.5)
                canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
                canvas_png = base64.b64decode(canvas_base64)
                with open(f"./dump/booktab/{id}/{i}.png", 'wb') as f:
                    f.write(canvas_png)
                    print(f"Dumped page {i}!")
                i += 1
                try:
                    page_number = driver.find_element_by_css_selector("#pageNumberValue").get_property("value")
                    WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".darkGreyNextArrow"))).click()
                    WebDriverWait(driver, 30).until(text_changed((By.CSS_SELECTOR, "#pageNumberValue"), page_number))
                    time.sleep(0.5)
                except TimeoutException:
                    print(f"\nFinished dumping Booktab book {id}!\n\n")
                    break
        except Exception:
            print("\n\nSomething went wrong!\n\n")
