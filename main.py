import os
import re
import time
import json
import requests
import lxml.html
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_urls(url: str) -> list[str]:
    r = requests.get(url)
    html = lxml.html.fromstring(r.text)
    script_tags = html.xpath("//script")
    formatting = re.sub(r'[\'",]', '', script_tags[3].text)
    formatted_list = re.findall("(?P<url>https?://[^\s]+.com[^\s]+)", formatting)
    return formatted_list


def download(download_url: str, file_dir: str, file_name: str):
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    response = requests.get(download_url)
    with open(f"{file_dir}/{file_name}", "wb") as f:
        f.write(response.content)
        print(f"{download_url} -> {file_name}")


def get_work_information(target_work_url: str) -> dict:
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=options)
    driver.get(target_work_url)

    time.sleep(5)

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

    return work_information


def save_works_information(file_dir: str, works_information: json) -> str:
    with open(file_dir, 'w') as f:
        json.dump(works_information, f, indent=4)

    if os.path.exists(file_dir):
        print(f"Metadata File -> {file_dir}")

    return file_dir


def save_img_urls(file_name: str, url_list: list[str]) -> str:
    with open(file_name, 'w') as f:
        for i in url_list:
            f.write(i + '\n')

    if os.path.exists(file_name):
        print(f"Image File List -> {file_name}")
    else:
        return "File Not Found"

    return file_name


def main(target_work_url, base_output_path):
    work_information = get_work_information(target_work_url)
    url_list = get_urls(target_work_url)

    if not os.path.exists(f"{base_output_path}/{work_information['title']}/{work_information['episode_title']}"):
        os.makedirs(f"{base_output_path}/{work_information['title']}/{work_information['episode_title']}")

    save_works_information(
        f"{base_output_path}/{work_information['title']}/{work_information['episode_title']}/metadata.json",
        work_information)

    save_img_urls(f"{base_output_path}/{work_information['title']}/{work_information['episode_title']}/img_url.txt",
                  url_list)

    for page_num, url in enumerate(url_list):
        download(
            url,
            f"{base_output_path}/{work_information['title']}/{work_information['episode_title']}/img",
            f"{page_num + 1}.webp")


if __name__ == '__main__':
    main(input("Enter the url: "), "./output")