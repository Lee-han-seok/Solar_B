'''
로직을 구현하기 위해 만든 함수 집합 파일
'''

import pandas as pd
import re
from sql import *


# 은행명 변경을 위한 코드 및 로고 이미지 경로 저장
# 주식회사 카카오뱅크 -> 카카오뱅크 or 농협은행 -> NH농협은행
def rename_bank_name_link(df):
    bank_grade = pd.read_csv("data/bank_grade_for_ui.csv" ,encoding = "cp949")
    bank_name_dict = dict(zip(bank_grade['구분'], bank_grade['은행명_전처리']))
    df['금융회사'] = df['금융회사'].apply(lambda x : bank_name_dict[x])
    
    bank_page_dict = dict(zip(bank_grade['은행명_전처리'], bank_grade['은행_대표홈페이지']))
    df['홈페이지'] = df['금융회사'].apply(lambda x : bank_page_dict[x])
    df['이미지경로'] = df['금융회사'].apply(lambda x : f"/static/logo_bank/{x}.png")
    return df

# 청년도약계좌에서 이미지 경로 만들기 
def rename_bank_name_link_mz(df):
    df['이미지경로'] = df['은행'].apply(lambda x : f"/static/logo_bank/{x}.png")
    return df

# 파킹통장 금액 구간 처리
# "100만원 이상 ~ 200만원 미만" 으로 되어 있는 텍스트들 처리 
# 사용자가 입력 시, 알맞은 상품 추출 
def parking_m_cal(m_range , money):
    # m_range : 구간 텍스트 ("100만원 미만" 등)
    # money : 입력된 돈
    p = re.compile("[0-9]+")

    if "~" in m_range:
        if "초과" in m_range and "이하" in m_range:
            m_range_list = p.findall(m_range)
            if int(m_range_list[0] )< money and money <= int(m_range_list[1]):
                return 1

        if "초과" in m_range and "미만" in m_range:
            m_range_list = p.findall(m_range)
            if int(m_range_list[0] )< money and money < int(m_range_list[1]):
                return 1

        if "이상" in m_range and "미만" in m_range:
            m_range_list = p.findall(m_range)
            if (int(m_range_list[0] )<= money) and  (money < int(m_range_list[1])):
                    return 1
    else: 
        if "이하" in m_range:
            if  int(p.findall(m_range)[0]) >= money :
                return 1
        if "미만" in m_range:
            if  int(p.findall(m_range)[0]) > money :
                return 1
        if "이상" in m_range:
            if  int(p.findall(m_range)[0]) <= money :
                return 1
        if "초과" in m_range:
            if  int(p.findall(m_range)[0]) < money :
                return 1

    return 0 

# 상품 유형구분
# 관심 상품을 선택을 위한 함수 (상품들을 각각 분류해줌)
def classify_products(df):
    def classify_product(row):
        product_name = row['상품명']
        
        if any(keyword in product_name for keyword in ['직장인', '중기근로자']):
            return '직장인'
        if any(keyword in product_name for keyword in ['펫', '반려']):
            return '반려인'
        if any(keyword in product_name for keyword in ['청년', '청소년', 'MZ', '영플러스']):
            return '청년'
        if any(keyword in product_name for keyword in ['Solo', '결혼', '신혼']):
            return '신혼'
        if any(keyword in product_name for keyword in ['여행', '트래블']):
            return '여행'
        if any(keyword in product_name for keyword in ['저탄소', 'ESG', '해양플라스틱', '초록', '탄소제로', '친환경', '그린']):
            return '환경보호'
        if any(keyword in product_name for keyword in ['아이사랑', '기업 정기적금', '기업정기적금', '착한누리', '수산물좋아', '엑스포', '더드리고', '미즈월', '파킹','아이','꿈나무']):
            return '삭제'
        return '전체'

    df['분류'] = df.apply(classify_product, axis=1)
    df = df[df['분류'] != '삭제']
    return df

# 특수 케이스 추가 
# 관심 상품 선택 시, 돌아가는 함수
def interest_add(client_dict, df):
    interest_list = client_dict[ '관심분야'].split(",")

    tmp_df = df[df['분류']=="전체"]

    if "해당사항없음" in  client_dict[ '관심분야']:
        return tmp_df
    
    for interest in interest_list:
        tmp_df = pd.concat([tmp_df,df[df['분류'] == interest]])
        tmp_df.reset_index(drop= True, inplace = True)
    
    return tmp_df

# 선택 우대사항만 추출
def prefer_choose_text(x, client_dict):
    # 새롭게 뽑은 우대사항 list
    list_prefer = ['만기']
    for prefer in client_dict['우대사항'].split(","):
        list_prefer.append(prefer.strip())

    if "해당사항없음" in list_prefer:
        list_prefer.remove("해당사항없음")

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
    x = x.replace('"', "")
    prefer_all_list = x.split("*")[1:]
    
    for s in prefer_all_list:
        cat = s.split(":")
        cat = cat[0].strip()
        if cat in intersection_set:
            final_list += [s]
    # print(final_list)
    if not final_list:
        final_list = ["-"]
    return "\n".join(final_list)

# 금융권의 범위 선택
# 일반은행 선택시 => 일반은행만 , 전체 선택시 => 안정성 평가 3등급 이상만
def bank_range(client_dict, df):
    # client_dict : 고객정보 입력 => 여기서는 금융권의범위만 추출하게 됨
    # df : 상품 df 
    
    df['금융회사종류'] = df['금융회사'].apply(lambda x : "저축" if "저축" in x else "일반")
    if client_dict[ '금융권의범위'] == "일반은행" :
        df = df[df['금융회사종류'] == "일반"]
    elif client_dict[ '금융권의범위'] == "일반은행+저축은행":
        df['등급'] = df['등급'].astype(int)
        df = df[df['등급'] <= 3]
    return df

# 소득 변동 유무  (불규칙적인 소득이라면 자유 적금만 추천)
def income_change(client_dict, df):
    if client_dict['소득변동유무'] == "아니요" :
        df = df[df['적립방식'] == '자유적립식']
    return df

# 선택된 우대사항만 포함시켜서 최종 보장 금리 계산
def prefer(client_dict, df):
    col_list_all = ['금융회사', '상품명', '적립방식', '세전이자율', '세후이자율', '세후이자(예시)', '최고우대금리','실질이자율',
        '이자계산방식', '기간','비교 공시일', '담당부서 및 연락처', '우대조건', '가입대상.1', '가입방법', '만기후 이자율', '기타유의사항','등급', 'cluster_num','우대사항정리']

    # 선택한 우대사항 리스트만 선택해서 가지고오기 => 만기는 항상 포함됨
    list_prefer = ["만기"]

    for prefer in client_dict['우대사항'].split(","):
        list_prefer.append(prefer.strip())

    if "해당사항없음" in list_prefer:
        list_prefer.remove("해당사항없음")

    client_list = col_list_all + list_prefer

    df = df[client_list]
    df = df.replace("NA","0.0%") # NA값으로 되어있는 아이들은 다 0%로 변경 
    # 우대사항 값계산
    def rate_cal(x):
        if client_dict[ '수시입출금'] == "예" and client_dict['저축목적'] =='단기적이벤트':
            total_ = float(x['세전이자율'] * 100) # 파킹통장은 달라서
        else:
            try:
                total_ = float(x['세전이자율'][:-1])
            except:
                total_ = float(x['최고우대금리'][:-1])

        for c in list_prefer:
            try:
                total_+= float(x[c].replace("%",""))
            except:
                pass

        return round(total_,2)
   
    df['최종금리'] = df.apply(lambda x : rate_cal(x), axis = 1)
    return df

# 우대사항에서 비대면 선택시 가입방법 온라인 상품만 선택됨
def none_f_to_f(client_dict, df):
    if  "비대면" in client_dict[ '우대사항']:
        # 가입방법 선택
         df = df[df['가입방법'] == "온라인"]
    return df

# 완성된 df를 list로 변경 (html로 넘기기 위해)
# 같은 은행이 뽑히지 않도록 같은 은행 제품은 하나만 남도록 처리 
def result_tmpdf(tmp_df):
    tmp_df.drop_duplicates(inplace= True,subset='금융회사')
    tmp_df = tmp_df.head(3)
    df_list = []
    for i in range(len(tmp_df)):
        df_list.append(tmp_df.iloc[i,:].to_list())
    return df_list 

# 청년도약계좌 리스트로 변경
def mz_list(df):
    df_list = []
    for i in range(len(df)):
        df_list.append(df.iloc[i,:].to_list())
    return df_list

