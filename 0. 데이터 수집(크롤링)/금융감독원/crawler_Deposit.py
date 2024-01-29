from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import json
import time
import pandas as pd

from urllib.request import urlopen
from html_table_parser import parser_functions as parser

Deposit_url = "https://finlife.fss.or.kr/finlife/svings/fdrmDpst/list.do?menuNo=700002"

driver_options = webdriver.ChromeOptions()
driver_options.add_argument("headless")

# driver = webdriver.Chrome(options=driver_options)
driver = webdriver.Chrome()
driver.get(Deposit_url)

period = "36개월"
csv_name = "./deposit_" +period[:-2] + ".csv" 

period_css = "#saving-date_label_{}"
period_dict = {"6개월" :'19',"12개월": '20',"24개월": '21',"36개월": '22'}
driver.find_element(By.CSS_SELECTOR, period_css.format(period_dict[period])).click()  
time.sleep(1)


# 가입대상
driver.find_element(By.CSS_SELECTOR, "#joinDeny43").click()  
time.sleep(0.5)
driver.find_element(By.CSS_SELECTOR, "#joinDeny44").click() 

# 금융상품 검색 클릭
search_css = "#content > div.sh2.w2 > div:nth-child(8) > div > button.search.ajaxFormSearch"
t = driver.find_element(By.CSS_SELECTOR, search_css)
t.click()
time.sleep(2)

# 총 몇개 상품?
total_len = int(driver.find_element(By.CSS_SELECTOR, "#content > div.result-txt > p > span > strong > em").text)
page_len = total_len//50 + 1

# 페이지 리스트 
driver.find_element(By.CSS_SELECTOR, "#pageUnit").send_keys("50")
driver.find_element(By.CSS_SELECTOR, "#content > div.page-check > button").click()

#현재 페이지 표에 있어서 정보들 다 가지고 오기

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
        # 개월수 넣어주기
        row_data.append(period)
        # 상세정보 열기 => 열면 r 하나 늘어남 
        detail_btn = body[-1].find_element(By.CSS_SELECTOR , "a")
        detail_btn.send_keys('\n')
        time.sleep(0.5)
        # print(index*2 + 1)
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

    return len(table_list)

print(page_len)
page = 3
for _ in range(page_len):
    if page == 3:
        table_crawler()
        page += 1
    else:
        # print(i + 3)
        try:
            page_num = driver.find_element(By.CSS_SELECTOR, f"#content > div.pagination-set > div > ul > li:nth-child({page}) > a")
        except :
            page = 5
            page_num = driver.find_element(By.CSS_SELECTOR, f"#content > div.pagination-set > div > ul > li:nth-child({page}) > a")
        page_num.click()
        time.sleep(1)
        table_crawler()
        page += 1
    print(page - 4)

col_name = ['금융회사','상품명','세전이자율','세후이자율','세후이자(예시)','최고우대금리','가입대상','이자계산방식','기간',
            '비교 공시일','담당부서 및 연락처', '우대조건','가입대상_상세','가입방법','만기후 이자율','기타유의사항']

df = pd.DataFrame(table_list, columns=col_name)

df.to_csv(csv_name, encoding='utf-8-sig', index = False)
driver.close()
# print(df.head())