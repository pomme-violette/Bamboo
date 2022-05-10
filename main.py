import os
import re
import requests
import json
import lxml.html

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common import by
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_urls(url):
    r = requests.get(url)
    html = lxml.html.fromstring(r.text)
    script_tags = html.xpath("//script")
    formatting = script_tags[3].text.replace("'", '').replace(',', '')
    formatted_list = re.findall("(?P<url>https?://[^\s]+)", formatting)
    return formatted_list


def save_urls(file_name, url_list):
    with open(file_name, 'w') as f:
        for i in url_list:
            f.write(i + '\n')
    return file_name


def download(download_url, file_dir, file_name):
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    response = requests.get(download_url)
    with open(f"{file_dir}/{file_name}", "wb") as f:
        f.write(response.content)
        # for CUI
        print(f"{download_url} -> {file_name}")


def get_work_information(target_work_url, file_dir):
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=options)
    driver.get(target_work_url)

    episode_title = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[1]/div[1]")
    episode_publish_date = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]")
    episode_next_publish_date = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[2]/div[1]/div[1]/p[2]")

    work_title = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[2]/div[1]/div[1]/h1")
    work_author = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[2]/div[1]/div[1]/div")
    work_description = driver.find_element(
        by=By.XPATH, value="/html/body/div[4]/div[2]/div[1]/div[1]/p[1]")

    work_id = target_work_url[28:32]
    episode_id = target_work_url[33:]

    work_information = {
        'title': work_title.text,
        'author': work_author.text,
        'description': work_description.text,
        'next_publish_date': episode_next_publish_date.text,
        'episode_title': episode_title.text,
        'publish_date': episode_publish_date.text,
        'work_id': work_id,
        'episode_id': episode_id,
        "work_url": target_work_url
    }

    driver.close()

    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    with open(f"{file_dir}/{work_title.text}_{episode_title.text}.json", 'w') as f:
        json.dump(work_information, f, indent=4)

    if os.path.exists(f"{file_dir}/{work_title.text}_{episode_title.text}.json"):
        print(f"{work_title.text}_{episode_title.text}.json is saved")

    return work_information


def main(target_work_url, base_output_path):
    if not os.path.exists(base_output_path):
        os.mkdir(base_output_path)

    work_information = get_work_information(
        target_work_url, f"{base_output_path}")

    url_list = get_urls(target_work_url)

    img_url_list_file_name = f"{work_information['title']}_{work_information['episode_title']}.txt"

    img_file_name = f"{work_information['title']}_{work_information['episode_title']}"

    img_url_list_path = save_urls(
        f"{base_output_path}/{img_url_list_file_name}", url_list)

    if os.path.exists(img_url_list_path):
        print(f"{img_url_list_path} is saved")

    for page_num, url in enumerate(url_list):
        download(
            url, f"{base_output_path}/{img_file_name}", f"{page_num+1}.webp")


if __name__ == '__main__':
    main(input("Enter the url: "), "./output")
