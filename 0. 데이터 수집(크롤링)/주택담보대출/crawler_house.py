from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import json
import time
import pandas as pd

from urllib.request import urlopen
from html_table_parser import parser_functions as parser

house_url = "https://finlife.fss.or.kr/finlife/ldng/houseMrtg/list.do?menuNo=700007"

period = "10"
csv_name = "./house_" +period + ".csv" 
driver_options = webdriver.ChromeOptions()
driver_options.add_argument("headless")
driver = webdriver.Chrome(options=driver_options)
# driver = webdriver.Chrome()
driver.get(house_url)

# 대출기간 입력
preiod_css = "mortagageloan-input01"
preiod_ele = driver.find_element(By.ID, preiod_css)
preiod_ele.clear() # 삭제 후 입력해주기
preiod_ele.send_keys("20")

# 금융상품 검색 
search_css = "#content > div.sh2 > div:nth-child(6) > div > button.search.ajaxFormSearch"
t = driver.find_element(By.CSS_SELECTOR, search_css)
t.click()
time.sleep(2)

# 총 페이지 몇개? 
total_len = int(driver.find_element(By.CSS_SELECTOR, "#content > div.result-txt > p > span > strong > em").text)
page_len = total_len//50 + 1

# 첫째달, 마지막, 총 상환액  선택
css_check_box = "#content > div.check-set-all > div.label-set.check_area > label:nth-child({}) > span"
for i in range(7,10):
    driver.find_element(By.CSS_SELECTOR, css_check_box.format(i)).click()

# 페이지 리스트 
driver.find_element(By.CSS_SELECTOR, "#pageUnit").send_keys("50")
driver.find_element(By.CSS_SELECTOR, "#content > div.check-set-all > div.page-check > button").click()

table_list = []

def table_crawler():
    global table_list

    table = driver.find_element(By.CSS_SELECTOR,"#ajaxResult > table")
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for index, value in enumerate(rows[::2]):
        body = value.find_elements(By.TAG_NAME, "td")
        row_data = []
        # 기본 컬럼들 정보 넣어주기
        for i in body[1:-2]:
            row_data.append(i.text)
        #기간
        row_data.append(period)
        # 상세정보 열기 => 열면 r 하나 늘어남 
        detail_btn = body[-1].find_element(By.CSS_SELECTOR , "a")
        detail_btn.send_keys('\n')
        time.sleep(0.5)
        detail_data_all = rows[index*2 + 1].find_element(By.CLASS_NAME,"more-inner")
        # 공시일 추가
        row_data.append(detail_data_all.find_element(By.CSS_SELECTOR,"span").text)
        # 나머지 상세 정보들 추가 
        detail_data_list = detail_data_all.find_elements(By.CSS_SELECTOR,"dd")
        for d in detail_data_list:
            row_data.append(d.text)
        # 접어주기
        detail_btn.send_keys('\n')
        table_list.append(row_data)
        time.sleep(1)


for i in range(page_len):
    if i == 0:
        table_crawler()
    else:
        page_num = driver.find_element(By.CSS_SELECTOR, f"#content > div.pagination-set > div > ul > li:nth-child({i + 3}) > a")
        page_num.click()
        print(i)
        time.sleep(1)
        table_crawler()

col_name = ['금융회사','상품명','주택종류','금리방식','상환방식','당월 최저금리','당월최고금리','전월 평균금리','월평균 상환액','첫째달 상환액','마지막 상환액','총 대출비용','대출기간',
            '비교 공시일','담당부서 및 연락처','가입방법' , '대출 부대비용','중도상환수수료','연체이자율','대출한도']

df = pd.DataFrame(table_list, columns=col_name)
df.to_csv(csv_name, encoding='utf-8-sig', index = False)
driver.close()