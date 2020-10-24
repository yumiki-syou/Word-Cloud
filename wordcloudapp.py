import urllib.request
from bs4 import BeautifulSoup
import re
import jieba
import pandas as pd
import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


def getHtml(url):
    """获取url页面"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    req = urllib.request.urlopen(req)
    content = req.read().decode('utf-8')

    return content


def getComment(url):
    """解析HTML页面"""
    html = getHtml(url)
    soupComment = BeautifulSoup(html, 'html.parser')

    comments = soupComment.findAll('span', 'short')
    onePageComments = []
    for comment in comments:
        # print(comment.getText()+'\n')
        onePageComments.append(comment.getText() + '\n')

    return onePageComments


if __name__ == '__main__':
    commentList = []
    f = open('movie.txt', 'w', encoding='utf-8')
    for page in range(4):  # 豆瓣爬取多页评论需要验证。
        url = 'https://movie.douban.com/subject/25798131/comments?start=' + str(
            20 * page) + '&limit=20&sort=new_score&status=P'
        print('第%s页的评论:' % (page + 1))
        print(url + '\n')

        for i in getComment(url):
            f.write(i)
            commentList.append(i)
            # print(i)
        # print('\n')
    # print(commentList)#短评的数组
    # 将数组转化为字符串
    comments = ''
    for k in range(len(commentList)):
        comments += commentList[k].strip()
    # print(comments)
    # 用正则表达式去除标点符号
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filiterdata = re.findall(pattern, comments)
    # print(filiterdata)#注意此时又变成数组了
    cleaned_comments = ''.join(filiterdata)
    # print(cleaned_comments)
    segment = jieba.lcut(cleaned_comments)
    # print(segment)
    word_df = pd.DataFrame({'segment': segment})
    # print(stopwords)
    # 去掉停用词
    stopwords = pd.read_csv('chineseStopWords.txt', index_col=False, quoting=3, \
                            sep='t', names=['stopwords'], encoding='utf-8')
    word_df = word_df[~word_df.segment.isin(stopwords.stopwords)]
    # print(word_df)
    # 统计词频并多到少排序
    words_stst = word_df.groupby('segment').agg(
        计数=pd.NamedAgg(column='segment', aggfunc='size')).reset_index().sort_values(
        by='计数', ascending=False)
    # print(words_stst)

    # 先把图片转换成多维数组
    mask = np.array(Image.open('img1.jpg'))

    # 配置词云参数
    word_cloud = WordCloud(font_path='simhei.ttf', mask=mask, background_color='white', \
                           max_font_size=80, random_state=30)
    # 把词频转换成字典
    # for x in words_stst.values:
    # print(x)
    word_fre = {x[0]: x[1] for x in words_stst.values}
    # 加载词云字典
    word_cloud = word_cloud.fit_words(word_fre)
    # 基于彩色图像生成相应彩色
    image_color = ImageColorGenerator(mask)
    # 绘制背景图片颜色
    word_cloud.recolor(color_func=image_color)
    word_cloud.to_file(r'result.png')
    # 形成图片
    image_result = word_cloud.to_image()
    # 展示图片
    image_result.show()
