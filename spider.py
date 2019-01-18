from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
from urllib.parse import quote

import pymysql

db= pymysql.connect(host="localhost",user="root",password="clear",db="OnlineJudge",port=3306)
cursor = db.cursor()


import re
import requests
import pandas as pd#python的一个数据分析包
from retrying import retry
from concurrent.futures import ThreadPoolExecutor

from openpyxl import workbook  # 写入Excel表所用
from openpyxl import load_workbook  # 读取Excel表所用
from bs4 import BeautifulSoup as bs
import os
#os.chdir(r'C:\Users\Administrator\Desktop')  # 更改工作目录为桌面

KEYWORD = '香水'
MAX_PAGE = 1
#SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']

# browser = webdriver.Chrome()
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)#设置等待时间


def index_page(page):
    """
    抓取索引页
    :param page: 页码
    """
    print('正在爬取第', page, '页')
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
            input.clear()#清空搜索框
            input.send_keys(page)#传送入关键词
            submit.click()#点击提交
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
        get_products()
    except TimeoutException:
        index_page(page)


def get_products():
    """
    提取商品数据
    """
    html = browser.page_source#browser.page_source是获取网页的全部html
    doc = pq(html)#声明pq对象
    #print(doc)
    items = doc('#mainsrp-itemlist .items .item').items()
    title = []
    location = []
    price = []
    deal = []
    shop = []
    for item in items:
        #标题、区域、价格、销量、店铺名称
        title.append(item.find('.title').text().replace("\n", ""))#clear \n
        location.append(item.find('.location').text())
        price.append(item.find('.price').text().split('\n')[1])
        deal.append(item.find('.deal-cnt').text())
        shop.append(item.find('.shop').text())
        product = {
            'title': item.find('.title').text().replace("\n", ""),
            'location': item.find('.location').text(),
            'price': item.find('.price').text().split('\n')[1],
            'deal': item.find('.deal-cnt').text(),
            'shop': item.find('.shop').text()
        }
        print(product)
	#
        sql = "INSERT INTO UserProfile_shop(title,location,price,deal,shop) VALUES ('%s','%s','%s','%s','%s')" % (item.find('.title').text().replace("\n", ""),item.find('.location').text(),item.find('.price').text().split('\n')[1], item.find('.deal-cnt').text(),item.find('.shop').text())
        print(sql)
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except:
            # Rollback in case there is any error
       	    db.rollback()
    for i in range(48):  # 每页48条数据,写入工作表中
        ws.append([title[i], location[i], price[i], deal[i],shop[i]])



#数据挖掘与分析
def data_solve(data):
    title = data.raw_title.values.tolist()
    #对每个标题进行分词： 使用lcut函数
    import jieba
    title_s = []
    for line in title:
        title_cut = jieba.lcut(line)
        title_s.append(title_cut)
    #对title_s中的每个list元素进行过滤 剔除不需要的词语，即把停用词表stopwords中有的词语都剔除掉

    #导入停用词表
    stopwords = pd.read_excel('stopwords.xlsx')
    #stopwords = stopwords.stopword.values.tolist()
    print(title_s)
    #剔除停用词
    title_clean = []
    for line in title_s:
        line_clean = []
        for word in line:
            if word not in stopwords:
                line_clean.append(word)
        title_clean.append(line_clean)
    #因为下面要统计每个词语的个数，所以为了准确性 这里对过滤后的数据tile_clean中的每个list的元素进行去重
    #即每个标题被分割后的词语唯一
    #进行去重
    title_clean_dist = []
    for line in title_clean:
        line_dist = []
        for word in line:
            if word not in line_dist:
                line_dist.append(word)
        title_clean_dist.append(line_dist)
    #将title_clean_dist转化为一个list:allwords_clean_dist
    allwords_clean_dist = []
    for line in title_clean_dist:
        for word in line:
            allwords_clean_dist.append(word)
    #把列表allwords_clean_dist转为数据框：
    df_allwords_clean_dist = pd.DataFrame({'allwords':allwords_clean_dist})
    #对过滤去重的词语 进行分类汇总：
    word_count = df_allwords_clean_dist.allwords.value_counts().reset_index()
    word_count.columns = ['word','count']

    #观察word_count表中的词语 发现jieba默认的词典无法满足需求：
    #有的词语（如 可拆洗、不可拆洗等）却被cut，这里根据需求对词典加入新词（也可以直接在词典dict.txt里面增删，然后载入修改过的dict.txt)
    #导入整理好的待添加词语：
    #add_words = pd.read_excel('add_words.xlsx')
    #添加词语：
    #for w in add_words.word:
    #    jieba.add_word(w, freq=1000)
    #======================================
    #注：再将上面的分词_过滤_去重_汇总 等代码执行一遍
    #得到新的word_count表
    #======================================

    # 词云可视化
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt#2D绘图库
    from scipy.misc import imread
    plt.figure(figsize=(10,6))
    pic = imread("background.jpg") #读取图片，自定义形状
    w_c = WordCloud(font_path = '/usr/share/fonts/SIMKAI.TTF',background_color="white",mask=pic,max_font_size=60,max_words=200,margin=1)
    wc = w_c.fit_words({x[0]:x[1] for x in word_count.head(100).values})
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('词云.png')  # 保存图片
    #plt.show()

    '''
    以上注释：
    background.jpg 是透明背景图
    "./data/simhei.ttf" 设置字体
    background_color 默认是黑色 这里设置成白色
    head(100) 取前100个词进行可视化
    max_font_size 字体最大字号
    interpolation = 'bilinear' 图优化
    "off" 去除边框
    分析结论：
    1. 组合、整装商品占比很高；
    2. 从沙发材质看：布艺沙发占比很高，比皮艺沙发多；
    3. 从沙发风格看：简约风格最多，北欧风次之，其他风格排名依次是美式、中式、日式、法式 等；
    4. 从户型看：小户型占比最高、大小户型次之，大户型最少。
    '''

    #不同关键词word对应的销量之和的统计分析
    #说明：例如词语'简约',则统计商品标题中含有'简约'一词的销量之和，即求出具有'简约'风格的商品销量之和
    import numpy as np#数学函数库

    w_s_sum = []
    for w  in word_count.word:
        i = 0;
        s_list = []
        for t in title_clean_dist:
            if w in t:
                s_list.append(data.sales[i])
            i += 1
        w_s_sum.append(sum(s_list))

    df_w_s_sum = pd.DataFrame({'w_s_sum':w_s_sum})

    #把word_count与对应的df_w_s_sum合并为一个表
    df_word_sum = pd.concat([word_count,df_w_s_sum],axis=1,ignore_index=True)
    df_word_sum.columns = ['word','count','w_s_sum']
    #对表df_word_sum中的word和w_s_sum两列数据进行可视化
    #取销量排名前30的词语进行绘图
    df_word_sum.sort_values('w_s_sum',inplace=True,ascending=True) #升序
    df_w_s = df_word_sum.tail(30) #取最大的30行数据

    import matplotlib
    from matplotlib import pyplot as plt
    font = {'family':'SimHei'} #设置字体
    matplotlib.rc('font', **font)

    index = np.arange(df_w_s.word.size)
    plt.figure(figsize=(6,12))
    plt.barh(index,df_w_s.w_s_sum,color='blue',align='center',alpha=0.8)
    plt.yticks(index,df_w_s.word,fontsize=11)#显示y轴的刻标以及对应的标签
    #添加数据标签
    for y,x in zip(index, df_w_s.w_s_sum):
        plt.text(x,y,'%.0f' %x, ha='left', va='center', fontsize=11)
    plt.savefig('不同关键词的销量之和.png')  # 保存图片
    #plt.show()
    #va参数有('top','bottom','center','baseline')
    #ha参数有('center','right','left')

    #商品价格分布情况分析
    #有些值太大，为了使可视化效果更加直观，我们选择价格小于20000的商品
    data_p = data[data['view_price'] < 20000]
    plt.figure(figsize=(7,5))
    plt.hist(data_p['view_price'],bins=15,color='blue')
    plt.xlabel('价格', fontsize=12)
    plt.ylabel('商品数量', fontsize=12)
    plt.title('不同价格对应的商品数量分布',fontsize=15)
    plt.savefig('不同价格对应的商品数量分布.png')  # 保存图片
    #plt.show()

    #商品的销量分布情况分析
    #为了是可视化效果更加直观，我们选择销量大于100的商品
    data_s = data[data['sales'] > 100]
    print('销量100以上的商品占比：%.3f'%(len(data_s)/len(data)))
    plt.figure(figsize=(7,5))
    plt.hist(data_s['sales'], bins=20,color='blue')#分20组
    plt.xlabel('销量',fontsize=12)
    plt.ylabel('商品数量',fontsize=12)
    plt.title('不同销量对应的商品数量分布',fontsize=15)
    plt.savefig('不同销量对应的商品数量分布.png')  # 保存图片
    #plt.show()

    #不同价格区间的商品的平均销量分布
    data['price'] = data.view_price.astype('int') #转为整型
    #用qcut将price列分为12组
    data['group'] = pd.qcut(data.price,12)
    df_group = data.group.value_counts().reset_index()
    #以group列进行分类求sales的均值
    df_s_g = data[['sales','group']].groupby('group').mean().reset_index()
    #绘柱形图
    index = np.arange(df_s_g.group.size)
    plt.figure(figsize=(8,4))
    plt.bar(index,df_s_g.sales,color='blue')
    plt.xticks(index,df_s_g.group,fontsize=11,rotation=30)
    plt.xlabel('Group')
    plt.ylabel('mean_sales')
    plt.title('不同价格区间的商品的平均销量')
    plt.savefig('不同价格区间的商品的平均销量.png')  # 保存图片
    #plt.show()

    #商品价格对销量的影响分析
    fig, ax = plt.subplots()
    ax.scatter(data_p['view_price'],data_p['sales'],color='blue')
    ax.set_xlabel('价格')
    ax.set_ylabel('销量')
    ax.set_title('商品价格对销量的影响')
    plt.savefig('商品价格对销量的影响.png')  # 保存图片
    #plt.show()

    #商品价格对销售额的影响分析
    data['GMV'] = data['price'] * data['sales']
    import seaborn as sns
    sns.regplot(x="price",y='GMV',data=data,color='blue')
    plt.savefig('商品价格对销售额的影响.png')  # 保存图片

    #不同省份的商品数量分布
    plt.figure(figsize=(8,4))
    data.province.value_counts().plot(kind='bar',color='blue')
    plt.xticks(rotation=0)
    plt.xlabel('省份')
    plt.ylabel('数量')
    plt.title('不同省份的商品数量分布')
    plt.savefig('不同省份的商品数量分布.png')  # 保存图片
   # plt.show()

    #不同省份的商品平均销量分布
    pro_sales = data.pivot_table(index='province',values='sales',aggfunc=np.mean)#分类求均值
    pro_sales.sort_values('sales',inplace=True,ascending=False) #排序
    pro_sales = pro_sales.reset_index() #重设索引
    index = np.arange(pro_sales.sales.size)
    plt.figure(figsize=(8,4))
    plt.bar(index,pro_sales.sales,color='blue')
    plt.xticks(index,pro_sales.province,fontsize=11,rotation=0)
    plt.xlabel('province')
    plt.ylabel('mean_sales')
    plt.title('不同省份的商品平均销量分布')
    plt.savefig('不同省份的商品平均销量分布.png')  # 保存图片
    #plt.show()

    #导出数据 并绘制热力型地图
    #pro_sales.to_excel('pro_sales.xlsx',index=False)






# 对数据进行清洗处理
def clean_solve():
    datatmsp = pd.read_excel('test2.xlsx')
    import missingno as msno#missingno绘制缺失数据分布图
    msno.bar(datatmsp.sample(len(datatmsp)), figsize=(10,4))#缺失值可视化处理
    #删除缺失值过半的列
    half_count = len(datatmsp)/2
    datatmsp = datatmsp.dropna(thresh = half_count, axis = 1)
    #删除重复行
    datatmsp = datatmsp.drop_duplicates()

    #取出这4列数据
    data = datatmsp[['item_loc','raw_title','view_price','view_sales']]
    #对区域列的省份和城市进行拆分：
    #生成province列：
    data['province'] = data.item_loc.apply(lambda x: x.split(' ')[0])
    #注：因直辖市的省份和城市相同 这里根据字符长度进行判断
    data['city'] = data.item_loc.apply(lambda x: x.split()[0] if len(x) < 5 else x.split()[1])
    #提取销量列中的数字，得到sales列：
    data['sales'] = data.view_sales.apply(lambda  x: x.split('人')[0])

    #将数据类型进行转换
    data['sales'] = data.sales.astype('int')
    list_col = ['province', 'city']
    for i in list_col:
        data[i] = data[i].astype('category')
    #删除不用的列
    data = data.drop(['item_loc', 'view_sales'], axis = 1)#使用0值表示沿着每一列或行标签\索引值向下执行方法 使用1值表示沿着每一行或者列标签模向执行对应的方法
    return data


def main():
    """
    遍历每一页
    """
    for i in range(1, MAX_PAGE + 1):
        index_page(i)
    browser.close()


if __name__ == '__main__':

    #  创建Excel表并写入数据
    wb = workbook.Workbook()  # 创建Excel对象
    ws = wb.active  # 获取当前正在操作的表对象
    # 往表中写入标题行,以列表形式写入！
    ws.append(['raw_title', 'item_loc', 'view_price', 'view_sales', 'shop'])
    main()#爬数据 存数据库 存excel表
    wb.save('test2.xlsx')  # 存入所有信息后，保存为test2.xlsx

    data = clean_solve()
    data_solve(data)#数据分析
    # 关闭数据库连接
    db.close()
