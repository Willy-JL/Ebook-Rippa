from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from distutils.spawn import find_executable
from selenium.webdriver.common.by import By
from selenium import webdriver
import cairosvg
import pathlib
import shutil
import base64
import time
import sys
import re


def fetch_blob(driver, uri):
    result = driver.execute_async_script("""
        var uri = arguments[0];
        var callback = arguments[1];
        var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'arraybuffer';
        xhr.onload = function(){ callback(toBase64(xhr.response)) };
        xhr.onerror = function(){ callback(xhr.status) };
        xhr.open('GET', uri);
        xhr.send();
        """, uri)
    if isinstance(result, int):
        raise Exception(f"Request failed with status {result}")
    return base64.b64decode(result)


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
    driver.get("https://my.zanichelli.it/dashboard/home")

    while True:
        input('Press [Enter] when you are on the first page of the ebook (must be on the first tab!)...')
        type = input("What type of ebook is this?\n"
                     "1) Booktab\n"
                     "2) Kitaboo Webreader\n"
                     ">>> ")

        try:
            if type == "1":
                id = input("With what name should this book be saved?\n"
                           "(Leave empty to autodetect the id)\n"
                           ">>> ") or re.match(".*/BooktabWeb/#/([^/]*)/.*", driver.current_url)[1]
                pathlib.Path(f"./dump/zanichelli/booktab/{id}").mkdir(parents=True, exist_ok=True)
                while True:
                    try:
                        i = int(input("From what number do you want to begin?\n"
                                      "(If you have ripped a part of this ebook already put the number of the last .png file +1, otherwise just put 0)\n"
                                      ">>> "))
                        assert i >= 0
                        break
                    except Exception:
                        print("Please choose a valid number!")
                print(f"\nStarted dumping Booktab book {id}...")

                driver.switch_to.default_content()
                driver.switch_to.frame(driver.find_element_by_css_selector("#bookviewerWindow"))
                try:
                    driver.find_element_by_css_selector(".darkGreySinglePageButton").click()
                except Exception:
                    pass

                while True:
                    canvas = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".deck-current canvas")))
                    time.sleep(0.5)
                    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
                    canvas_png = base64.b64decode(canvas_base64)
                    with open(f"./dump/zanichelli/booktab/{id}/{i}.png", 'wb') as f:
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

            if type == "2":
                id = input("With what name should this book be saved?\n"
                           "(Leave empty to autodetect the id)\n"
                           ">>> ") or "".join([ char.lower() for char in driver.title if char.isalnum() ])
                pathlib.Path(f"./dump/zanichelli/kitaboo/{id}").mkdir(parents=True, exist_ok=True)
                while True:
                    try:
                        i = int(input("From what number do you want to begin?\n"
                                      "(If you have ripped a part of this ebook already put the number of the last .png file +1, otherwise just put 0)\n"
                                      ">>> "))
                        assert i >= 0
                        break
                    except Exception:
                        print("Please choose a valid number!")
                print(f"\nStarted dumping Kitaboo book {id}...")

                try:
                    driver.find_element_by_css_selector(".single-column-view-icon").find_element_by_xpath("./..").click()
                except Exception:
                    pass

                while True:
                    driver.switch_to.default_content()
                    driver.switch_to.frame(driver.find_element_by_css_selector(".epub_container_active"))
                    svg = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "figure#bodyimage img[src]")))
                    svg_bytes = fetch_blob(driver, svg.get_attribute("src"))
                    cairosvg.svg2png(svg_bytes, scale=2, write_to=f"./dump/zanichelli/kitaboo/{id}/{i}.png")
                    print(f"Dumped page {i}!")
                    i += 1
                    try:
                        driver.switch_to.default_content()
                        assert driver.find_element_by_css_selector("rightnavigation-view").get_attribute("aria-hidden") == "false"
                        driver.find_element_by_css_selector("button.rightNavigation").click()
                        time.sleep(0.5)
                    except AssertionError:
                        print(f"\nFinished dumping Kitaboo book {id}!\n\n")
                        break
        except Exception:
            print("\n\nSomething went wrong!\n\n")
