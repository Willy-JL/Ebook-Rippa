from selenium.common.exceptions import TimeoutException
from seleniumwire import webdriver
import os

options = {'ignore_http_methods': ['HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']}
driver = webdriver.Chrome(seleniumwire_options=options)
driver.set_page_load_timeout(120)
driver.set_script_timeout(120)
driver.get('https://www.pearson.it/')
input('Press [Enter] when you are on the first page of the ebook...')
i = int(input('From what number do you want to begin? (If you have ripped a part of this ebook already put the number of the last .png file +1, otherwise just put 0)\n'))
while True:
    del driver.requests
    el = driver.find_element_by_id('ebookScreen')
    action = webdriver.common.action_chains.ActionChains(driver)
    action.move_to_element_with_offset(el, 90, 90)
    action.click()
    action.perform()
    try:
        driver.wait_for_request('/ebookassets/*', timeout=30)
    except TimeoutException:
        break
    swf = driver.last_request.response.body
    with open(f'dump/{i}.swf', 'wb') as f:
        f.write(swf)
    os.system(f'swfrender.exe dump/{i}.swf -o dump/{i}.png -Y 1896')
    i += 1
