'''
최종 로직 구현을 위한 함수
'''
import pandas as pd
import re
from sql import *
from logic_ import * 

# db연결 가능시 연결, 불가시 csv로 연결
Flag_db = True
try :
    get_conn()
except:
    Flag_db = False

# 파킹통장
def parking_cal(client_dict):
    if Flag_db :
        df = get_sql('select * from final_parking')
        df = parking_to_original(df)
    else:
        df = pd.read_csv("./data/final_parking.csv")

    # 금액구간에 알맞는 값 뽑아내기
    if int(client_dict['금액']) != 0 :
        df['기간적합'] = df['기간'].apply(lambda x : parking_m_cal(x,int(client_dict['금액'])))
        df = df[df['기간적합'] == 1]

    # 금융권범위선택
    df = bank_range(client_dict, df)
    # 우대사항값계산
    df = prefer(client_dict,df)
    # sort
    df = df.sort_values(by = '최종금리', ascending = False)[['금융회사','상품명', '최종금리','기간',]]
    #tolist
    df_list = result_tmpdf(df)
    return df_list

# 단기상품 적금
def short_event_cal(client_dict):
    if Flag_db:
        df = get_sql('select * from final_saving')
        df = saving_to_original(df)
    else:
        df = pd.read_csv("./data/final_saving.csv")

     # 기간 선택
    if client_dict['기간'] == "상관없음":
        df = df[df['기간'] == '6개월']
    elif client_dict[ '기간'] == "3개월이내" :
        df = df[df['기간'] == "3개월이하"]
    elif client_dict[ '기간'] == "3~6개월" :
        df = df[df['기간'] == "6개월미만"]
    elif client_dict[ '기간'] == "6개월" :
        df = df[df['기간'] == "6개월"]

    # 분류 
    df = classify_products(df)
    # 해당사항 추가
    df = interest_add(client_dict, df)

     # 금융권 범위선택
    df = bank_range(client_dict, df)
    # 소득변동유무(규칙적 - 정액, 불규칙적 - 자유)
    df = income_change(client_dict,df)
    # 우대사항 값계산
    df = prefer(client_dict,df)
    # sort
    df = df.sort_values(by = '최종금리', ascending = False)[['금융회사','상품명','적립방식','세전이자율','최종금리','우대사항정리']]
    # 이름 mapping과 홈페이지 넣기, 이미지 경로넣기
    df = rename_bank_name_link(df)
    # 선택한우대사항정리
    df['우대사항선택'] = df['우대사항정리'].apply(lambda x : prefer_choose_text(x, client_dict))
    #tolist
    df_list = result_tmpdf(df)
    return df_list

# 적금
def saving_cal(client_dict):

    df = get_sql('select * from final_saving')
    df = saving_to_original(df)
    if Flag_db:
        df = get_sql('select * from final_saving')
        df = saving_to_original(df)
    else:
        df = pd.read_csv("./data/final_saving.csv")
    
    # 기간 선택
    if client_dict['기간'] == "상관없음":
        df = df[df['기간'] == '12개월']
    else:
        df = df[df['기간'] == client_dict[ '기간']]

    # 분류 
    df = classify_products(df)
    # 해당사항 추가
    df = interest_add(client_dict, df)
    
    # 금융권 범위선택
    df = bank_range(client_dict,df)
    # 소득변동유무(규칙적 - 정액, 불규칙적 - 자유)
    df = income_change(client_dict,df)
    #비대면
    df = none_f_to_f(client_dict,df)
    
    # 우대사항 값계산
    df = prefer(client_dict,df)
    # sort
    df = df.sort_values(by = '최종금리', ascending = False)[['금융회사','상품명','적립방식','세전이자율','최종금리','우대사항정리']]
    # 이름 mapping과 홈페이지 넣기, 이미지 경로넣기
    df = rename_bank_name_link(df)

    # 추가 우대사항 정리
    # 선택한우대사항정리
    df['우대사항선택'] = df['우대사항정리'].apply(lambda x : prefer_choose_text(x, client_dict))

    #tolist
    df_list = result_tmpdf(df)
    return df_list

# 예금
def deposit_cal(client_dict):
    if Flag_db:
        df = get_sql('select * from final_deposit')
        df = deposit_to_original(df)
    else:
        df = pd.read_csv("./data/final_deposit.csv")

    # 기간 선택
    if client_dict[ '기간'] == "상관없음":
        df = df[df['기간'] == '12개월']
    else:
        df = df[df['기간'] == client_dict[ '기간']]
    
    # 분류 
    df = classify_products(df)
    # 해당사항 추가
    df = interest_add(client_dict, df)

    # 금융권 범위선택
    df = bank_range(client_dict,df)
    #비대면
    df = none_f_to_f(client_dict,df)
    # 우대사항 값계산
    df = prefer(client_dict,df)
    # sort
    df = df.sort_values(by = '최종금리', ascending = False)[['금융회사','상품명','최종금리','세전이자율', '이자계산방식','우대사항정리']]
    # 이름 mapping과 홈페이지 넣기
    df = rename_bank_name_link(df)

    # 선택한우대사항정리
    df['우대사항선택'] = df['우대사항정리'].apply(lambda x : prefer_choose_text(x, client_dict))
    #tolist
    df_list = result_tmpdf(df)

    return df_list

# 청년 도약계좌
def mz_cal(client_dict):
    df = pd.read_csv("./data/청년도약계좌df.csv", encoding='cp949') 
    
    list_prefer = []
    for prefer in client_dict['우대사항'].split(","):
        list_prefer.append(prefer.strip())

    if "해당사항없음" in list_prefer:
        list_prefer.remove("해당사항없음")

    def rate_cal(x):
        total_ = float(x['기본 금리(3년 고정)'])

        for c in list_prefer:
            if c not in df.columns:
                continue
            if x[c] == "-":
                continue
            else:
                total_+= float(x[c].replace("%",""))

        return round(total_,2)
    
    def Highest(x):
        highest_rate = float(x['기본 금리(3년 고정)'])
        highest_rate += float(x['소득 우대금리'])
        highest_rate += float(x['최대'].replace("%",""))
        return round(highest_rate,2)
    
    df['최고우대금리'] = df.apply(lambda x : Highest(x) , axis = 1)
    df['최종금리'] = df.apply(lambda x : rate_cal(x), axis = 1)

    # 선택한것의 우대사항만 보여주기
    def prefer_mz(x, list_prefer):
        # 새롭게 뽑은 우대사항 list
        final_list = []

        # 해당상품의 우대사항 list
        p = re.compile(r'\*(.*?):')
        prefer_all_list = p.findall(x)
        for i in range(len(prefer_all_list)):
            prefer_all_list[i] = prefer_all_list[i].strip()

        prefer_all_list = set(prefer_all_list)
        list_prefer = set(list_prefer)

        #교집합 찾기
        intersection_set  = list(list_prefer & prefer_all_list)

        # 교집합에서 list 뽑아오기
        prefer_all_list = x.split("*")[1:]
        for s in prefer_all_list:
            cat = s.split(":")
            cat = cat[0].strip()
            if cat in intersection_set:
                final_list += [s]

        if not final_list:
            final_list = ["-"]
        return "\n".join(final_list)
    
    # 선택한우대사항정리
    df['우대사항선택'] = df['우대사항 정리'].apply(lambda x : prefer_mz(x, list_prefer))      
    # sort
    df = df.sort_values(by = '최종금리', ascending = False)
    # 이름 mapping과 홈페이지 넣기
    df['이미지경로'] = df['은행'].apply(lambda x : f"/static/logo_bank/{x}.png")

    # 3개
    df = df.head(3)

    return df

# 보험
def insurance_cal(df_client_sex):

    if Flag_db:
        df = get_sql('select * from final_medical_insurance')
        df = medical_insurance_to_original(df)
    else:
        df = pd.read_csv("./data/final_medical_insurance.csv")
    df = df.head(3)
    
    # 성별에 따라 변경
    if df_client_sex == "여":
        df = df[['상품명','보험가격지수','보험료_여_30','상품설명서_요약']]
    else:
        df = df[['상품명','보험가격지수','보험료_남_30','상품설명서_요약']]
    df = df.sort_values(by = "보험가격지수", ascending = True)
    df = df.head(3)
    return df