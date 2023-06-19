from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
import shutil
import os
from io import BytesIO
import requests
import base64
import time


def setup(path, delete_all=True):
    path_exists = os.path.exists(path)
    if not path_exists:
        os.mkdir(path)
    elif delete_all and path_exists:
        shutil.rmtree(path)
        os.mkdir(path)


def get_url(search):
    url_format = 'https://www.google.com/search?tbm=isch&q={}'
    search = search.replace(' ', ' ')
    url = url_format.format(search)
    return url


def save_images(srcs, category, keyword, data_dir):
    print('Done scraping, writing {} images to files'.format(category))
    srcs = [x for x in srcs if x]
    for i, src in enumerate(srcs):
        unique_image_name = '{}_{}.png'.format(keyword.replace(' ', '_').replace(':', '_').replace('/', '_'), i)
        file_path = os.path.join(data_dir, unique_image_name)

        if 'data:image' in src:
            readable_base64 = ''.join(src.split('base64,')[1:])
            content = base64.b64decode(readable_base64)
        else:
            r = requests.get(src)
            content = r.content

        img = Image.open(BytesIO(content)).convert('RGB')
        img.save(file_path)


def handle_scroll(driver):
    # scrolls to the bottom of the page
    # show more results button: mye4qd
    # you've reached the end: OuJzKb Yu2Dnd
    last_height = driver.execute_script("return window.pageYOffset")
    num_trials = 0
    max_trials = 3
    while True:
        try:
            show_more_results_btn = driver.find_element(By.CLASS_NAME, 'mye4qd')
            show_more_results_btn.click()
            continue
        except:
            pass

        driver.execute_script('window.scrollBy(0,100);')
        new_height = driver.execute_script("return window.pageYOffset")

        if new_height - last_height < 10:
            num_trials += 1
            if num_trials >= max_trials:
                break
            time.sleep(1)
        else:
            last_height = new_height
            num_trials = 0


def scrape_category(category_name, queries, data_dir):
    setup(os.path.join(data_dir, category_name))
    category_dir = os.path.join(data_dir, category_name)

    for query in queries:
        print('Scraping category: {} for query: {}'.format(category_name, query))
        driver.get(get_url(query))
        handle_scroll(driver)
        all_imgs = driver.find_elements(By.XPATH, '//*[@class="rg_i Q4LuWd"]')
        all_srcs = [x.get_attribute('src') for x in all_imgs]
        save_images(all_srcs, category_name, query, category_dir)


data_path = 'data'
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

setup(data_path)
categories = {
    'dog': ['dog', 'golden retriever', 'husky dog', 'bulldog', 'dalmatian', 'poodle'],
    'cat': ['cat', 'siamese cat', 'persian cat', 'ragdoll cat', 'shorthair cat']
}

for category in categories:
    category_queries = categories[category]
    scrape_category(category, category_queries, data_dir=data_path)
