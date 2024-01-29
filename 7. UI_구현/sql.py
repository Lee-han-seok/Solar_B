import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine
import re
################# input your MariaDB information #################

host = '127.0.0.1'
user = 'root'
password = '1234'
database = 'goods'

def parking_to_original(df):
    english_mapping = {
        '금융회사': 'financial_company',
        '상품명': 'product_name',
        '적립방식': 'saving_method',
        '세전이자율': 'interest_rate_before_tax',
        '세후이자율': 'interest_rate_after_tax',
        '세후이자(예시)': 'example_interest_after_tax',
        '최고우대금리': 'highest_preferential_rate',
        '실질이자율': 'actual_interest_rate',
        '이자계산방식': 'interest_calculation_method',
        '기간': 'period',
        '이자지급': 'interest_payment',
        '비교 공시일': 'comparison_announcement_date',
        '담당부서 및 연락처': 'contact_department_and_number',
        '우대조건': 'preferential_conditions',
        '가입대상.1': 'eligible_customers',
        '가입방법': 'subscription_method',
        '만기후 이자율': 'post_maturity_interest_rate',
        '기타유의사항': 'additional_notes',
        '등급': 'rating',
        'cluster_num': 'cluster_number',
        '우대사항정리': 'preferential_conditions_summary',
        '급여이체': 'salary_transfer',
        '마케팅동의': 'marketing_consent',
        '자동이체': 'automatic_transfer',
        '카드실적': 'card_performance',
        '최초거래': 'first_transaction',
        '주택청약': 'housing_subscription',
        '비대면': 'non_face_to_face',
        '영업점': 'branch',
        '해당은행': 'specific_bank',
        '이체횟수': 'transfer_count',
        '만기': 'maturity',
        '변동금리': 'variable_interest_rate',
        '이벤트': 'event',
        '기타': 'others',
        '나이': 'age',
        '환경': 'environment',
        '신혼': 'newlywed',
        '반려인': 'pet_owner',
        '직장인': 'office_worker',
        '여행': 'travel'
    }
    original_mapping = {v: k for k, v in english_mapping.items()}
    df = df.rename(columns=original_mapping)
    return df

def medical_insurance_to_original(df):
    original_mapping = {
        'company_name': '회사명',
        'product_name': '상품명',
        'premium_male_30': '보험료_남_30',
        'premium_female_30': '보험료_여_30',
        'entry_age_start': '가입연령_시작',
        'entry_age_end': '가입연령_끝',
        'insurance_price_index': '보험가격지수',
        'deposit_protection': '예금자보호',
        'protection_insurance': '보장성보험',
        'withdrawal_period': '청약철회기간',
        'actual_loss_coverage_proportional_compensation': '실손형담보_비례보상',
        'premium_renewal': '보험료갱신형',
        'cancellation_refund_zero': '해약환급금_0원',
        'fixed_rate': '금리확정형',
        'product_description_summary': '상품설명서_요약'
    }
    df = df.rename(columns=original_mapping)
    return df

def deposit_insurance_to_original(df):
    english_mapping = {
        '회사명': 'company_name',
        '상품명': 'product_name',
        '상품형태': 'product_type',
        '공시이율': 'announced_interest_rate',
        '납입기간': 'payment_period',
        '1년_환급률': 'refund_rate_1yr',
        '3년_환급률': 'refund_rate_3yr',
        '5년_환급률': 'refund_rate_5yr',
        '7년_환급률': 'refund_rate_7yr',
        '10년_환급률': 'refund_rate_10yr',
        '20년_환급률': 'refund_rate_20yr',
        '예금자보호': 'deposit_protection',
        '저축성보험': 'savings_insurance',
        '청약철회기간': 'withdrawal_period',
        '금리확정형': 'fixed_rate',
        '금리연동형': 'linked_rate',
        '최저이율보장': 'guaranteed_minimum_interest',
        '실적배당형': 'performance_dividend',
        '변액보장': 'variable_coverage',
        '가입형태': 'subscription_type',
        '상품설명서_요약': 'product_description_summary'
    }
    original_mapping = {v: k for k, v in english_mapping.items()}
    df = df.rename(columns=original_mapping)
    return df

def house_deposit_to_original(df):
    english_mapping = {
        '은행사': 'bank_name',
        '상품명': 'product_name',
        '유형': 'type',
        '기본금리': 'basic_interest_rate',
        '최고우대금리': 'highest_preferential_rate',
        '기간': 'period',
        '금액제한': 'amount_limit',
        '우대사항 정리': 'preferential_conditions_summary'
    }    
    original_mapping = {v: k for k, v in english_mapping.items()}
    df = df.rename(columns=original_mapping)
    return df

def deposit_to_original(df):
    english_mapping = {
        '금융회사': 'financial_institution',
        '상품명': 'product_name',
        '적립방식': 'saving_method',
        '세전이자율': 'interest_rate_before_tax',
        '세후이자율': 'interest_rate_after_tax',
        '세후이자(예시)': 'interest_example_after_tax',
        '최고우대금리': 'highest_preferential_rate',
        '실질이자율': 'effective_interest_rate',
        '이자계산방식': 'interest_calculation_method',
        '기간': 'period',
        '비교 공시일': 'comparison_announcement_date',
        '담당부서 및 연락처': 'contact_department',
        '우대조건': 'preferential_conditions',
        '가입대상.1': 'target_customers',
        '가입방법': 'subscription_method',
        '만기후 이자율': 'post_maturity_interest_rate',
        '기타유의사항': 'other_notes',
        '등급': 'rating',
        'cluster_num': 'cluster_number',
        '우대사항정리': 'preferential_conditions_summary',
        '급여이체': 'salary_transfer',
        '마케팅동의': 'marketing_consent',
        '자동이체': 'automatic_transfer',
        '카드실적': 'card_performance',
        '최초거래': 'first_transaction',
        '주택청약': 'housing_subscription',
        '비대면': 'non_face_to_face',
        '영업점': 'branch',
        '해당은행': 'specific_bank',
        '이체횟수': 'transfer_count',
        '만기': 'maturity',
        '변동금리': 'variable_interest_rate',
        '이벤트': 'event',
        '기타': 'others',
        '나이': 'age',
        '환경': 'environment',
        '신혼': 'newlywed',
        '반려인': 'pet_owner',
        '직장인': 'office_worker',
        '여행': 'travel'
    }
    original_mapping = {v: k for k, v in english_mapping.items()}
    df = df.rename(columns=original_mapping)
    return df

def saving_to_original(df):
    english_mapping = {
        '금융회사': 'financial_company',
        '상품명': 'product_name',
        '적립방식': 'saving_method',
        '세전이자율': 'interest_rate_before_tax',
        '세후이자율': 'interest_rate_after_tax',
        '세후이자(예시)': 'example_interest_after_tax',
        '최고우대금리': 'highest_preferential_rate',
        '실질이자율': 'actual_interest_rate',
        '이자계산방식': 'interest_calculation_method',
        '기간': 'period',
        '비교 공시일': 'comparison_announcement_date',
        '담당부서 및 연락처': 'contact_department_and_number',
        '우대조건': 'preferential_conditions',
        '가입대상.1': 'eligible_customers',
        '가입방법': 'subscription_method',
        '만기후 이자율': 'post_maturity_interest_rate',
        '기타유의사항': 'additional_notes',
        '등급': 'rating',
        'cluster_num': 'cluster_number',
        '우대사항정리': 'preferential_conditions_summary',
        '급여이체': 'salary_transfer',
        '마케팅동의': 'marketing_consent',
        '자동이체': 'automatic_transfer',
        '카드실적': 'card_performance',
        '최초거래': 'first_transaction',
        '주택청약': 'housing_subscription',
        '비대면': 'non_face_to_face',
        '영업점': 'branch',
        '해당은행': 'specific_bank',
        '이체횟수': 'transfer_count',
        '만기': 'maturity',
        '변동금리': 'variable_interest_rate',
        '이벤트': 'event',
        '기타': 'others',
        '나이': 'age',
        '환경': 'environment',
        '신혼': 'newlywed',
        '반려인': 'pet_owner',
        '직장인': 'office_worker',
        '여행': 'travel'
    }
    original_mapping = {v: k for k, v in english_mapping.items()}
    df = df.rename(columns = original_mapping)
    return df



conn = pymysql.connect(host = host, user = user, password = password, db = database, charset = 'utf8')

def get_conn():
    '''
        데이터베이스 연결
        returns
            db 커넥션 객체
    '''
    return pymysql.connect(   host    = host,
                                    user    = user,
                                    password= password,
                                    database= database,
                                    # select의 결과 집합은 [ {}, {}, {}, ...] 형태로 나옴, 지정
                                    # cursorclass=pymysql.cursors.DictCursor
                                    )

def close_conn( conn ):
    '''
        데이터베이스 연결 종료
        parameters
            - conn : 커넥션 객체
    '''
    if conn:
        conn.close()
    pass


def get_sql( sql : str ):
    '''
        DQL  계열의 select 쿼리 수행
        parameters
            - sql : select 문
        returns
            - 결과 집합, DataFrame으로 리턴
    '''
    # 쿼리를 요청할대마다 => 접속 => 쿼리 => 닫기 반복
    conn = None
    results = pd.DataFrame() # 비어있는 데이터프레임 자료구조
    try:
        conn    = get_conn()
        results = pd.read_sql(sql, conn)
    except Exception as e:
        pass
    finally:
        close_conn( conn )
    return results


# df = get_sql('select * from final_saving')
# df = saving_to_original(df)
# print(df.replace("NA","0.0%"))