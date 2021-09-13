from seleniumwire import webdriver
import aiofiles
import pathlib
import asyncio
import aiohttp
import shutil
import re


async def main():
    global done
    options = {'ignore_http_methods': ['HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE']}
    driver = webdriver.Chrome("chromedriver", seleniumwire_options=options)
    driver.set_page_load_timeout(120)
    driver.set_script_timeout(120)
    driver.get('https://www.pearson.it/')
    while True:
        input('Press [Enter] when you are on a page of the ebook (must be on the first tab!)...')
        type = input("What type of ebook is this?\n"
                     "1) eText ISE\n"
                     "2) Reader+\n"
                     ">>> ")
        try:
            if type == "1":
                del driver.requests
                try:
                    element = driver.find_element_by_css_selector('.pageNavigation .pageNavigationContainer .nextPage .navigationBtn')
                except Exception:
                    element = driver.find_element_by_css_selector('.pageNavigation .pageNavigationContainer .previousPage .navigationBtn')
                element.click()
                driver.wait_for_request('/pages/*', timeout=30)
                for request in driver.requests:
                    if "/eplayer/pdfassets/" in str(request.url) and "/pages/" in str(request.url):
                        template = request
                        break

                async with aiohttp.ClientSession(headers=dict(template.headers),
                                                connector=aiohttp.TCPConnector(limit=0)) as cs:
                    done = False
                    baseurl = template.url[:template.url.rfind("/")] + "/page"

                    async def fetch_page(number):
                        global done
                        if done:
                            return
                        retries = 0
                        while True:
                            try:
                                async with cs.get(f"{baseurl}{number}") as req:
                                    if not req.ok:
                                        done = True
                                        return
                                    async with aiofiles.open(f"./dump/pearson/etext-ise/{id}/{number}.png", 'wb') as f:
                                        await f.write(await req.read())
                                        print(f"Fetched page {number}!")
                            except Exception:
                                if retries > max_retries:
                                    raise
                                retries += 1
                                continue

                    async def worker():
                        while not tasks.empty():
                            await tasks.get_nowait()

                    id = re.match(".*/eplayer/pdfassets/.*/.*/(.*)/pages/.*", template.url)[1]
                    shutil.rmtree(f"./dump/pearson/etext-ise/{id}", ignore_errors=True)
                    pathlib.Path(f"./dump/pearson/etext-ise/{id}").mkdir(parents=True, exist_ok=True)
                    print(f"\nStarted dumping eText ISE book {id}...")

                    i = 0
                    amount = 25
                    max_retries = 3
                    while not done:
                        tasks = asyncio.Queue()
                        for x in range(i, i + amount):
                            tasks.put_nowait(fetch_page(x))

                        await asyncio.gather(*[worker() for _ in range(amount)])

                        i += amount

                    print(f"\nFinished dumping eText ISE book {id}!\n\n")

            if type == "2":
                del driver.requests
                try:
                    element = driver.find_element_by_css_selector('.pageNavigation .pageNavigationContainer .nextPage .navigationBtn')
                except Exception:
                    element = driver.find_element_by_css_selector('.pageNavigation .pageNavigationContainer .previousPage .navigationBtn')
                element.click()
                driver.wait_for_request('/pages/*', timeout=30)
                for request in driver.requests:
                    if "/products/epubs/generated/" in str(request.url) and "/pages/" in str(request.url):
                        template = request
                        break

                async with aiohttp.ClientSession(headers=dict(template.headers),
                                                connector=aiohttp.TCPConnector(limit=0)) as cs:
                    done = False
                    baseurl = template.url[:template.url.rfind("/")] + "/page"

                    async def fetch_page(number):
                        global done
                        if done:
                            return
                        retries = 0
                        while True:
                            try:
                                async with cs.get(f"{baseurl}{number}") as req:
                                    if not req.ok:
                                        done = True
                                        return
                                    async with aiofiles.open(f"./dump/pearson/reader-plus/{id}/{number}.png", 'wb') as f:
                                        await f.write(await req.read())
                                        print(f"Fetched page {number}!")
                            except Exception:
                                if retries > max_retries:
                                    raise
                                retries += 1
                                continue

                    async def worker():
                        while not tasks.empty():
                            await tasks.get_nowait()

                    id = re.match(".*/products/epubs/generated/(.*)/.*/pages/.*", template.url)[1]
                    shutil.rmtree(f"./dump/pearson/reader-plus/{id}", ignore_errors=True)
                    pathlib.Path(f"./dump/pearson/reader-plus/{id}").mkdir(parents=True, exist_ok=True)
                    print(f"\nStarted dumping Reader+ book {id}...")

                    i = 0
                    amount = 25
                    max_retries = 3
                    while not done:
                        tasks = asyncio.Queue()
                        for x in range(i, i + amount):
                            tasks.put_nowait(fetch_page(x))

                        await asyncio.gather(*[worker() for _ in range(amount)])

                        i += amount

                    print(f"\nFinished dumping Reader+ book {id}!\n\n")
        except Exception:
            print("\n\nSomething went wrong!\n\n")


if __name__ == "__main__":
    asyncio.run(main())
