from flask import Flask, render_template, request, url_for
import pandas as pd
from logic_ import *
from logic_final_cal import *
import numpy as np
from loding_str import *


app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# 고객 정보 입력

global client_col_list
global client_dict

client_col_list = ['이름','성별','나이','관심분야','수시입출금','저축목적','소득변동유무', '기간','금융권의범위','우대사항', '목돈마련','금액','선택상품','추천여부']
try: 
    df_client = pd.read_csv(r"C:\Users\NT551XCJ\Desktop\ASAC_yoonjae\final_pro\UI\client.csv", encoding = "cp949")
    df_client.drop(columns= "Unnamed: 0", inplace = True)
except:
    df_client = pd.DataFrame(columns = client_col_list)

# client_dict = {
#     '이름' :'신윤재',
#     '성별' :'여',
#     '나이' :34, '관심분야':'청년', '수시입출금' :"예", '저축목적' : '목돈마련','소득변동유무':'아니요',
#     '기간':'12개월', '금융권의범위':'일반은행', '금액' : 100, '선택상품':'파킹통장', 
#     '우대사항' :'급여이체', '목돈마련' : '목돈모으기'

# }
    
client_dict = {
'이름' :'신윤재',
'성별' :'여',
'나이' :34, '관심분야':'청년', '수시입출금' :"아니요", '저축목적' : '목돈마련','소득변동유무':'아니요',
'기간':'6개월', '금융권의범위':'일반은행', '금액' : 100, '선택상품':'예금 & 적금 상품', 
'우대사항' :'급여이체, 영업점,해당은행', '목돈마련' : '둘다','추천여부':'아니요'

}


@app.route("/")# request
def root():
    return render_template("main.html") #respose

@app.route("/client")
def client():
    return render_template("client.html")

@app.route("/client2")
def client2():
    return render_template("client2.html")

# 기본정보, 관심분야
@app.route("/form")
def form():
    global client_dict
    client_dict = dict()
    for c in client_col_list:
        client_dict[c] = np.nan
    return render_template("form.html")

# 저축목적
@app.route("/purpose")
def purpose():
    global client_dict
    client_dict['성별'] = request.args['gender']
    client_dict['나이'] = request.args['myage'] 
    client_dict['이름'] = request.args['myname']
    hobby = request.args.getlist('hobby')
    client_dict['관심분야'] = ",".join(hobby)
    
    
    return render_template("purpose.html")

#단기, 중장기 나누기
# 목적
@app.route("/Purpose_classification")
def Purpose_classification():
    global client_dict
    client_dict['저축목적']= request.args['purpose'] 
    if request.args['purpose'] == '단기적이벤트':
        # 수시 입출금 유무
        return render_template("frequent_.html")
    elif request.args['purpose'] == '목돈마련' :
        return render_template("form_long.html")
    
@app.route("/income_short")
def income_short():
    global client_dict
    client_dict['수시입출금'] = request.args['frequent']
    if request.args['frequent'] == "예":
        client_dict['선택상품'] = '파킹통장'
        return render_template("income_money.html")
    else:
        client_dict['선택상품'] = '단기 적금 상품'
        return render_template("period_income.html")

# 목돈 구체적 상황
@app.route("/long_event")
def long_event():
    global client_dict
    client_dict['목돈마련'] = request.args['m_purpose']
    if request.args['m_purpose'] == "목돈굴리기":
        client_dict['선택상품'] = '정기 예금 상품'
        return render_template("deposit.html")
    elif request.args['m_purpose'] =="목돈모으기":
        client_dict['선택상품'] = '정기 적금 상품'
        return render_template("saving.html")
    elif request.args['m_purpose'] =="둘다" :
        client_dict['선택상품'] = '예금 & 적금 상품'
        return render_template("de_save_two.html")
    elif request.args['m_purpose'] =="상관없음" :
        client_dict['선택상품'] = '예금 & 적금 상품'
        client_dict['기간'] = "12개월"
        client_dict['소득변동유무'] = "네"
        return render_template("range_prefer.html")

# 범위랑 우대사항 
@app.route("/range_prefer")
def range_prefer():
    global client_dict
    client_dict['소득변동유무'] = request.args['income']
    if client_dict['수시입출금'] == '예':
        client_dict['금액'] = request.args['amount']
    else :
        if request.args['period'] == "상관없음":
            client_dict['기간'] = "12개월"
            client_dict['추천여부'] ="예"
        else:
            client_dict['기간'] = request.args['period']
            client_dict['추천여부'] ="아니요"
    return render_template("range_prefer.html")

# 변경됨
@app.route("/formResult")
def formResult():
    global client_dict
    global client_col_list
    client_dict['금융권의범위'] = request.args['range']
    prefer = request.args.getlist('prefer')
    client_dict['우대사항'] = ",".join(prefer)

    
    idx = len(df_client)
    client_list = []
    for c in client_col_list:
        client_list.append(client_dict[c])

    df_client.loc[idx] = client_list
    # 저장
    df_client.to_csv("./client.csv", encoding = "cp949")

    return render_template("next.html")

@app.route("/loding_page")
def loding_page():

    global client_dict
    global client_col_list
    client_dict['금융권의범위'] = request.args['range']
    prefer = request.args.getlist('prefer')
    client_dict['우대사항'] = ",".join(prefer)

    idx = len(df_client)
    client_list = []
    for c in client_col_list:
        client_list.append(client_dict[c])

    df_client.loc[idx] = client_list
    # 저장
    df_client.to_csv("./client.csv", encoding = "cp949")

    client_name = client_dict['이름']
    product = client_dict['선택상품']
    ment_list = loding_page_conn(client_dict)

    return render_template("loding_page.html", client_name = client_name, 
                           ment_list = ment_list,
                           product = product, recommend= client_dict['추천여부'])

@app.route("/logic_result")
def logic_result():
    global df_list
    global client_dict
    # 쿼리
    if client_dict[ '저축목적'] == "단기적이벤트"  and client_dict[ '수시입출금'] == "아니요": 
        df_list_s = short_event_cal(client_dict)
        income_client = client_dict['소득변동유무']
        return render_template("formResult_saving.html", df_s = df_list_s, income_client= income_client)

    elif client_dict[ '저축목적'] == "단기적이벤트"  and client_dict[ '수시입출금'] == "예": 
        df_list = parking_cal(client_dict)
        return render_template("formResult_parking.html", df = df_list)

    # 목돈마련 => 목돈모으기(적금)
    elif  client_dict[ '저축목적'] == "목돈마련" and client_dict[ '목돈마련'] == "목돈모으기" :
        df_list_s = saving_cal(client_dict)
        income_client = client_dict['소득변동유무']
        return render_template("formResult_saving.html", df_s = df_list_s, income_client= income_client)
    
    # 목돈마련 => 목돈 굴리기 (예금)
    elif client_dict['저축목적'] =="목돈마련" and client_dict['목돈마련'] == '목돈굴리기':
        df_list_d = deposit_cal(client_dict)
        return render_template("formResult_deposit.html", df_d = df_list_d)

    # 목돈마련 => 둘다 & 상관없음 ( 예금, 적금)
    elif client_dict['목돈마련'] == '둘다' or client_dict['목돈마련'] == '상관없음' :
        df_list_d = deposit_cal(client_dict)
        df_list_s = saving_cal(client_dict)
        income_client = client_dict['소득변동유무']

        return render_template("formResult_two.html", df_d = df_list_d, df_s = df_list_s, income_client= income_client)

@app.route("/formResult_Housing")
def formResult_Housing():
    return render_template("formResult_Housing.html")

@app.route("/formResult_mz")
def  formResult_mz():
    # df_client = pd.read_csv("./client.csv", encoding="cp949")

    df = mz_cal(client_dict)

    df_list_rate = mz_list(df[['은행', '기본 금리(3년 고정)','최종금리','최고우대금리','이미지경로']])
    print(df['이미지경로'])
    df_pre_ch = mz_list(df[['우대사항선택']])
    df_all_pre = mz_list(df[['마케팅동의', '자동이체','카드실적','최초거래','주택청약','급여이체','기타','소득 우대금리']])

    myname = client_dict['이름']

    return render_template("formResult_mz.html" ,myname = myname ,df_list_rate = df_list_rate, 
                           df_pre_ch = df_pre_ch, df_all_pre = df_all_pre)

@app.route("/insurance")
def  insurance():
    try:
        df_client_sex = client_dict["성별"]
    except:
        df_client_sex = "남"
    df = insurance_cal(df_client_sex)
    name_insur = list(df.iloc[:,0])
    prcie_index = list(df.iloc[:,1])
    price = list(df.iloc[:,2])
    summary_insur = list(df.iloc[:,3])

    return render_template("formResult_insurance.html", summary = summary_insur, 
                           name_insur = name_insur,
                           price = price, 
                           prcie_index = prcie_index , sex = df_client_sex)

@app.route("/mz_detail")
def mx_detail():
    image_url = url_for('static', filename='image/청년도약계좌_상세페이지.jpg')
    return render_template("mz_detail.html", image_url=image_url)

@app.route("/deposit_insurance")
def  deposit_insurance():
    image_url = url_for('static', filename='image/저축성보험_상세페이지.jpg')
    return render_template("form_result_deposit_insurance.html", image_url=image_url)


@app.route("/auto_recommend")
def  auto_recommend():
    image_url = url_for('static', filename='image/자동추천.jpg')
    return render_template("form_result_auto_recommend.html", image_url=image_url)



if __name__ == "__main__" :
    app.run(host = '0.0.0.0', port = 3600, debug = True)