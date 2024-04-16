#라이브러리 import
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib.request
import time
import os
import io
import base64
from PIL import Image
from tqdm import tqdm

from utils import load_csv

from selenium import webdriver                                               ## Import Driver for working on a Web
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

data = load_csv(r'Menurecipe_20240401.csv')

for menu in data:

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])                                 # keep automation
    chrome_options.add_experimental_option('useAutomationExtension', False)                                # bot hidden on web
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument("--incognito")                                                     # To keep THE browser active
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs", prefs)

    #검색어 입력받기
    #searchKey = input('Search key:')
    searchKey = menu[3]



    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

    #chrome 브라우저 실행 및 google 이미지 검색 페이지 접속
    driver.get("https://www.google.co.kr/imghp?hl=ko&tab=wi&authuser=0&ogbl")

    #검색어 입력 및 검색 버튼 클릭
    elem = driver.find_element("name", "q")
    elem.send_keys(searchKey)
    elem.send_keys(Keys.RETURN)

    #이미지 스크롤링
    SCROLL_PAUSE_TIME = 3
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            try:
                driver.find_element(By.CSS_SELECTOR, "").click()
            except:
                break
        last_height = new_height
    images = []
    print("scroll done")
    #이미지 다운로드
    print(len(driver.find_elements(By.XPATH, '//h3[@class="ob5Hkd"]')))
    for img in tqdm(driver.find_elements(By.XPATH, '//h3[@class="ob5Hkd"]')[:250]):
        try:
            actions = ActionChains(driver)
            actions.move_to_element(img).perform()
            image = img.find_element(By.XPATH, './/a').get_attribute('href')
            images.append(image)
        except:
            print('failed at fetching element')
    count = 1

    os.makedirs(f'.\imgs\{searchKey}',exist_ok=True)

    menu_ID = int(menu[2])

    invalid_websites = ["costco","tripadvisor"]

    for image_url in images:
        skip = False
        try:

            driver.get(image_url)
            time.sleep(0.5)
            data_url = driver.find_element(By.XPATH, '//img[@class="sFlh5c pT0Scc iPVvYb"]').get_attribute('src')

            for website in invalid_websites:
                if website in data_url:
                    skip = True

            if skip:
                continue

            if data_url.startswith('data:image'):
                print(data_url)
                # Convert base64 image to binary
                image = Image.open(io.BytesIO(base64.b64decode(data_url.split(',')[1])))
            else:
                # Download image from URL using urllib
                req = urllib.request.Request(data_url, headers=headers)
                with urllib.request.urlopen(req) as url:
                        print(url)
                        image_data = url.read()
                image = Image.open(io.BytesIO(image_data))

            filename = './imgs/{}/{:d}_01_00001_{:05d}.jpg'.format(searchKey, menu_ID, count)

            count+=1

            with open(filename, 'wb') as f:
                image.save(f) 
        
            if count > 200:
                break

        except Exception as e:
            print('e : ', e)
            pass

    driver.close()
