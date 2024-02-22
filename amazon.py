#-*- codeing = utf-8 -*-

import urllib.request,urllib.error  # 指定URL

from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify,request

from multiprocessing.dummy import Pool

from flask_cors import CORS, cross_origin

import json

app = Flask(__name__)

CORS(app,methods=['GET', 'POST'],supports_credentials=True)


datas = []
statue_code = 200

@app.route('/amazon',methods=['POST'])
@cross_origin(origins="*",methods=['Post'],supports_credentials=True)
def index():
#    url = 'https://www.amazon.cn/dp/B00T5TONM8/ref=s9_acsd_ri_bw_c2_x_1_i?pf_rd_m=A1AJ19PSB66TGU&pf_rd_s=merchandised-search-6&pf_rd_r=ANKN492JMVFH783VRDNK&pf_rd_t=101&pf_rd_p=33bf5cd5-f5ec-4e60-9d40-6ea69af80339&pf_rd_i=42692071&th=1'

    urls = request.get_data()
    res = json.loads(urls)    # 将json格式转为字典
    # data = getData(url)
    # print(len(urls))
    # print(len(res))
    # print('res:' + request.)
    for key,value in res.items():
        print(key+":"+value)

    with Pool(3) as pool:
        datas = pool.map(getData, res.items())
    return jsonify({'data': datas})

def getData(item):
    feature = {}
    message = []
    msg = ""

    order = item[0][len(item[0])-1]
    url = item[1]
    order = order
    html = askURL(url)  # 爬取页面元素

    soup = BeautifulSoup(html,"html.parser")  # 解析

    print('html == '+ html)

    for style_or_script in soup(["script", "style"]):  # 移除script和style标签
        style_or_script.extract()
    # print(soup)
    try:
        title = soup.find(id='productTitle').text.strip()
    except AttributeError:
        title = None
        message.append("无法获取标题，页面结构可能发生了变化或者标题不存在。")


    try:
        tds1 = list(soup.select(".a-span3"))
        tds2 = list(soup.select(".a-span9"))
        if (len(tds1) > len(tds2)):
            tds1 = tds1[:10]
        if(len(tds1) < len(tds2)): # 出现商品无法配送至改地址字段
            tds2 = tds2[1:]
        for i in range(len(tds1)):  # 将feature放入字典
            feature[tds1[i].span.text.strip()] = tds2[i].span.text.strip()
    except Exception as e:
        message.append("无法获取产品参数，页面结构可能发生了变化或者产品参数不存在。")

    try:
        # items = soup.select(".a-spacing-mini")
        items = soup.find_all("li", class_="a-spacing-mini")
        des = []
        for i in range(len(items)):
            # print(items[i].span.text.strip())
            des.append(items[i].span.text.strip())
    except Exception as e:
        message.append("无法获取产品文案，页面结构可能发生了变化或者产品文案不存在。")

    if len(des) == 0 and len(feature) == 0:
        print('=======custume========')
        try:
            detail1 = list(soup.select(".a-fixed-left-grid.product-facts-detail"))
            for i in range(len(detail1)):
                fname = detail1[i].div.span.span.text.strip()
                fval = detail1[i].div.div.next_sibling.next_sibling.text.strip()
                feature[fname] = fval
        except Exception as e:
            message.append("无法获取产品参数，页面结构可能发生了变化或者产品参数不存在。")

        try:
            items = soup.find_all("span", class_="a-list-item a-size-base a-color-base")
            des = []
            for i in range(len(items)):
                # print(items[i].text.strip())
                des.append(items[i].text.strip())
        except Exception as e:
            message.append("无法获取产品文案，页面结构可能发生了变化或者产品文案不存在。")

    if len(message) == 0:
        msg = "success"
        message.append(msg)



    data = {
        'msg': message,
        'order': order,
        'title': title,
        'feature': feature,
        'description': des
    }

    # res.append(data)
    print(data)
    # datas.append(res)
    # print(res)

    return data

def askURL(url):
    # 用户代理
    # head = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    # }
    head = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Cookie': 'session-id=134-7314284-0699743; session-id-time=2082787201l; i18n-prefs=USD; ubid-main=131-6098044-8656223; lc-main=en_US; sp-cdn="L5Z9:SG"; session-token=1iKNEUokevoHwDgTq5Cy/rjCUwYeqIW/C+Q9Nb2P29D5WOWoy6G87lAXWtb8vBxFUL8+OKFEHS8BvfAcOtudsqVI1LurHCAHoCNQsdvV4hTW8+iRKL0cNRPO2DL8war8tftQsRZNW2bi2AfJOK3Sm4TXcKp45k0smpFRChYdNXGU6SMbAGM7BoufFQFKb+zXXMjVE8PlVj6tyv3H/0R+FeqivyIbI6/nlFVgGM9ybBtB9IJiHKgObFGL04dnsWYSvLHR8MxfwCAM15TjnRIuxkgxDJWahsMY3SXzYCZTCsZ9obC2AAD0t6+Dd6eCl5GEN6XrZfWpMwyS5liLTuy2eW2hyPMUq6tY',
        'Cache-Control': 'no-cache',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': "Windows",
        'Sec-Ch-Ua-Platform-Version': "10.0.0",
        'Sec-Ch-Viewport-Width': '835',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Viewport-Width': '835',
        'X-Amz-Acp-Params': 'tok=rYPaQwr5rMoAwklU5rV80DTLXyIbwstIsg6TZyCAcBI;ts=1705738260302;rid=BTDNCWKBGW2ZHX65ZCAP;d1=814;d2=0;tpm=CGHDB.content-id;ref=pd_ex_alt',
        'X-Requested-With': 'XMLHttpRequest'
    }
    request = urllib.request.Request(url,headers=head)
    # print(request.headers)
    html = ""
    try:
        response =urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print('code == ' + str(e.code))
            statue_code = e.code
        if hasattr(e,"code"):
            print(e.reason)
        print("html == " + html)
    return html

def set_cookie():
    return 0


if __name__ == '__main__':
    app.run(debug=True)
