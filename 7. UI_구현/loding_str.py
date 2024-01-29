
# 예적금 둘다
saving_deposit_ment = ["""💰 목돈 만들기와 굴리기를 희망하는 {client_name}님, 예금과 적금 동시 가입을 고려해 보세요! 
 현재 가지고 계신 목돈은 예금 상품에 예치하시고, 새로운 적금으로 또 다른 목돈을 만들어보세요.""",
'''🎉 분석이 완료되었어요. {client_name}님의 선호를 바탕으로 {client_name}님께 가장 유리한 
 정기예금 상품들과 정기적금 상품들을 추천해 드릴게요. ''']

# 예금
deposit_ment =[
    '''🏦 목돈 굴리기를 목표하면서, 희망 가입기간은  {period}인 {client_name}님에게는 정기 예금 상품이 적합해요. 
     ''',
     '''🎉 분석이 완료되었어요. {client_name}님의 선호를 바탕으로 {client_name}님께 가장 유리한 
정기예금 상품들을 추천해 드릴게요. ''']

# 적금(불규칙)
saving_income_irr_ment = ["""✨ 목돈 마련을 목표로 하며, 희망 가입기간은 {period}인 {client_name}님께는 
                     여유 자금이 생길 때마다 자유롭게 저축이 가능한 자유 적금이 적합해요. 
                     """, 
                     '''🎉 분석이 완료되었어요. {client_name}님의 선호를 바탕으로 {client_name}님께 가장 유리한 
                     정기적금 상품들을 추천해 드릴게요. ''']

# 적금(규칙)
saving_income_regular_ment = ['''✨ 목돈 마련을 목표로 하며, 희망 가입기간은 {period}인 {client_name}님께는 
                     매달 규칙적인 저축이 가능한 정액 적금 상품과, 여유 자금이 생길 때마다 자유롭게 저축이 가능한 자유 적금이 모두 적합해요.
                         ''', 
                        '''🎉 분석이 완료되었어요. {client_name}님의 선호를 바탕으로 {client_name}님께 가장 유리한 
                        정기적금 상품들을 추천해 드릴게요. ''']

# 적금(단기)
saving_short_ment = ['''✨ 단기간 빠르게 저축을 목표로 하는 {client_name}님께는 6개월 이하 단기 적금 상품이 적합해요. 
                빠르게 목돈을 마련해 목표하신 바를 이루실 수 있을거에요. 
                ''', 
                '''🎉 분석이 완료되었어요. {client_name}님의 선호를 바탕으로 {client_name}님께 가장 유리한 
                정기적금 상품들을 추천해 드릴게요. ''']

# 파킹
parking_ment = ['''✨ 수시 입출금이 필요한 {client_name}님에게는 파킹통장을 추천드려요! 
           파킹통장은 일반 예금에 비해 높은 금리를 보장하는 동시에 수시 입출금이 가능한 특징이 있어요. 
           다만, 장기적인 저축이 필요하시다면 예금과 적금 또한 고려해보세요! 
           ''',
           '''🎉분석이 완료되었어요. {client_name}님의 선호와 예상 예치 금액을 바탕으로 
           {client_name}님께 가장 유리한 상품들을 추천해 드릴게요. ''']


product_ment_dict = {
    '단기 적금 상품' : saving_short_ment,
    '파킹통장' : parking_ment,
    '정기 예금 상품' : deposit_ment,
    '예금 & 적금 상품' : saving_deposit_ment
}

def loding_page_conn(client_dict):
    ment_list = []
    selct_ment = None
    client_name = client_dict['이름']
    period = client_dict['기간']
    product = client_dict['선택상품']

    if product == '정기 적금 상품':
        if client_dict['소득변동유무'] == '아니요':
            selct_ment = saving_income_irr_ment
        else :
            selct_ment = saving_income_regular_ment
    else:
        selct_ment = product_ment_dict[product]
    
    if "period" in selct_ment[0]:
        ment_list.append(selct_ment[0].format(client_name = client_name, period=period))
        ment_list.append(selct_ment[1].format(client_name = client_name))
    else:
        ment_list.append(selct_ment[0].format(client_name = client_name))
        ment_list.append(selct_ment[1].format(client_name = client_name))

    return ment_list
