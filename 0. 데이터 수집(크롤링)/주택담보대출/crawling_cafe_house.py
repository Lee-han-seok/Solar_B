from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import time
import json
import pandas as pd
from selenium.webdriver.common.alert import Alert

# 에러 발생 시 이전까지의 데이터를 저장하는 함수
def save_data_to_csv():
    data_list = list(zip(search_list_f, title_list, date_list, text_list, comment_list_all))

    file_path = 'output_data.csv'

    try:
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["검색어", "제목", "날짜", "본문", "댓글"])  # 헤더 추가

            for data in data_list:
                csv_writer.writerow(data)

        print(f"데이터를 {file_path}에 저장했습니다.")

    except Exception as e:
        print(f"데이터 저장 중 에러 발생: {e}")



# cafe url
c_url = "https://cafe.naver.com/10onepiece"
LOG_url = "https://nid.naver.com/nidlogin.login"

with open('crawling/login.json') as f: login_info = json.load(f)
ID, PW = login_info['id'], login_info['pw']

driver_options = webdriver.ChromeOptions()
driver_options.add_argument("headless")

driver = webdriver.Chrome()
#driver = webdriver.Chrome(options=driver_options)
driver.get(LOG_url)
driver1 = webdriver.Chrome()
#driver1 = webdriver.Chrome(options=driver_options)
driver1.get(LOG_url)



# 시간
driver.implicitly_wait(2)

# 로그인
driver.execute_script('document.getElementsByName("id")[0].value=\"' + ID + '\"')
driver.execute_script('document.getElementsByName("pw")[0].value=\"' + PW + '\"')
driver.find_element(By.XPATH, '//*[@id="log.login"]').click()
time.sleep(5)

driver1.execute_script('document.getElementsByName("id")[0].value=\"' + ID + '\"')
driver1.execute_script('document.getElementsByName("pw")[0].value=\"' + PW + '\"')
driver1.find_element(By.XPATH, '//*[@id="log.login"]').click()

# 게시글 불러오기
text_data = []
type_data = []

clubid = 19619212
menuid=357

# 주택담보대출 게시판 열기
driver.get(f'{c_url}?iframe_url=/ArticleList.nhn?search.clubid={clubid}%26search.menuid={menuid}%26')
time.sleep(2)
driver.switch_to.frame("cafe_main")

# 공지숨기기
driver.find_element(By.CSS_SELECTOR, '#main-area > div.list-style > div > div.check_box').click()


# 게시글검색
# search_list = list(df['상품명'].unique())
df = pd.read_csv('crawling\house_20.csv')
search_list = list((df['금융회사']+' '+df['상품명']).unique())


# 내용들 받을 빈 리스트 생성
title_list =[]
date_list =[]
text_list =[]
comment_list_all =[]
search_list_f = [] 


# 검색어별
for search in search_list[10:]:
    try:
        driver.execute_script(f'document.getElementsByName("query")[0].value=\"' + search + '\"')
        driver.find_element(By.CSS_SELECTOR, '#main-area > div.list-search > form > div.input_search_area > button').click()

        # 기간 3년으로 설정
        start_date = '20201101'
        # end_date : 자동설정됨

        driver.find_element(By.XPATH, '//*[@id="currentSearchDateTop"]').click() # 전체기간 클릭
        s_date = driver.find_element(By.XPATH, '//*[@id="input_1_top"]')
        s_date.clear()
        time.sleep(1)

        # start_date를 for문 통해 1글자씩 입력
        for c in start_date:
            s_date.send_keys(c)
            time.sleep(1)

        # 날짜 설정 버튼 & 검색버튼
        element = driver.find_element(By.XPATH, '//*[@id="btn_set_top"]')
        driver.execute_script("arguments[0].click();", element)

        # 검색버튼
        driver.find_element(By.CSS_SELECTOR, '#main-area > div.search_result > div:nth-child(1) > form > div.input_search_area > button').click()

        # 정확도순으로 바꾸기
        driver.find_element(By.XPATH, '//*[@id="searchOptionSortByDiv"]/a').click()
        driver.find_element(By.XPATH,'//*[@id="searchOptionSortByDiv"]/ul/li[2]/a').click()


        # 게시물 20개씩
        driver.find_element(By.XPATH, '//*//*[@id="listSizeSelectDiv"]/a').click()
        driver.find_element(By.XPATH,'//*[@id="listSizeSelectDiv"]/ul/li[4]/a').click()


        #게시글 가져오기
        post = '#main-area > div.article-board.result-board.m-tcol-c > table > tbody > tr:nth-child({}) > td.td_article > div.board-list > div > a'

        page_num = len(driver.find_elements(By.CSS_SELECTOR,"#main-area > div.article-board.result-board.m-tcol-c > table > tbody> tr"))


        for i in range(1, page_num+1):
            post_i = driver.find_element(By.CSS_SELECTOR, post.format(i))
            driver1.get(post_i.get_attribute('href'))
            time.sleep(2)
            driver1.switch_to.frame("cafe_main")

            # 제목
            soup = BeautifulSoup(driver1.page_source, 'html.parser')
            soup_title = soup.find(class_ = "title_text")
            title = soup_title.text

            # 날짜
            date = driver1.find_element(By.CSS_SELECTOR, '#app > div > div > div.ArticleContentBox > div.article_header > div.WriterInfo > div.profile_area > div.article_info > span')
            date = date.text

            # 본문
            soup_main = soup.find(class_ = "content CafeViewer")
            text= soup_main.text.strip()

            # 댓글 내용
            # 게시물이 사라졌으면 수행하지 않음
            soup_ct = soup.find_all(class_='comment_area')
            comment_list = []
            for comment in soup_ct:
                c_text = comment.find(class_ = "text_comment").text
                comment_list.append(c_text)

            # 리스트에 내용 추가    
            title_list.append(title)
            date_list.append(date)
            text_list.append(text)
            comment_list_all.append(comment_list)
            search_list_f.append(search)
            print(search)
            time.sleep(2)

    except Exception as e:
        print(f"에러 발생: {e}")
        # 에러가 발생하면 이전까지 수집한 데이터를 CSV 파일로 저장
        save_data_to_csv()


save_data_to_csv()

# driver.close()
# driver1.close()        

df = pd.DataFrame({'검색어':search_list_f,'제목':title_list, '날짜':date_list,'본문':text_list,'댓글':comment_list_all})
df
df.to_csv('cafe_house_review_4.csv',encoding='utf-8-sig', index = False)
