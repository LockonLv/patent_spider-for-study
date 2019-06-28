import requests
import re
from bs4 import BeautifulSoup
import xlwt
import time
import random
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication,QFileDialog
from patent_download import Ui_patent_spider

user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
headers = {'User-Agent': user_agent}
url_header1="http://www.wanfangdata.com.cn/search/searchList.do?"
url_header2="http://www.wanfangdata.com.cn/search/searchList.do?beetlansyId=aysnsearch"
url_searchType="&searchType=patent"
url_pageSize="&pageSize=20"

url_showType="&showType=detail"

url_isHit="&isHit=&isHitUnit="

url_end="$patent_type&firstAuthor=false&navSearchType=patent&rangeParame="

global route

# route="D:\\"

order='correlation'
patent_type='发明专利'

class informationabout(QMainWindow,Ui_patent_spider):
    def __init__(self):
        super(informationabout, self).__init__()
        self.setupUi(self)
        self.path_road.clicked.connect(self.setPath)
        self.research.clicked.connect(self.get_allinformation)
        self.basicdata_save.clicked.connect(self.get_basicexcel)
        self.download.clicked.connect(self.download_pdf)

    def setPath(self):
        Save_path = QFileDialog.getExistingDirectory(self,'浏览','C:\\')
        self.route_show.setText(Save_path)
        route=Save_path


    # 获取在特定关键词下的专利数量
    def get_allinformation(self):
        searchWord=self.keyword.text()
        url_searchWord = "&searchWord= " + searchWord
        orders = self.order_choose.currentText()
        if orders == '相关度':
            order = 'correlation'
        elif orders == '下载量':
            order = 'download_num'
        elif orders == '申请时间':
            order = 'app_date02'
        elif orders == '公开时间':
            order = 'pub_date'
        else:
            order = 'correlation'
        url_order = "&order=" + order
        patent_type=self.type_choose.currentText()
        url_patent_type = "&isHitUnit=&facetField=$patent_type:" + patent_type
        url_facetName = "&facetName=" + patent_type
        url = url_header1 + url_searchType + url_pageSize + url_searchWord + url_showType + url_order + url_isHit + url_patent_type + url_facetName + url_end
        print(url)
        r = requests.get(url, headers=headers, verify=False)
        r.encoding = 'utf-8'
        sum = re.compile(r'找到 <span>.*?</span> 条结果', re.S)
        sumr = re.findall(sum, r.text)[0][9:14]  # 获取的所有数量
        self.label.setText(sumr+'篇')
        print(sumr)
        return sumr

    # 获取在特定关键词下的某一篇专利的链接，专利号，下载数量以及摘要
    def get_urlandabstrat(self,num,searchWord,order,patent_type):
        page=num//20+1
        url_page="&page="+str(page)
        url_searchWord = "&searchWord= " + searchWord
        url_order = "&order=" + order
        url_patent_type = "&isHitUnit=&facetField=$patent_type:" + patent_type
        url_facetName = "&facetName=" + patent_type
        urls = url_header2 + url_searchType + url_pageSize + url_page + url_searchWord + url_showType + url_order + url_isHit + url_patent_type + url_facetName + url_end
        r = requests.get(urls, headers=headers, verify=False)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        # a=soup.find_all(text={'showBox(.*?)'})
        class1 = soup.find_all(class_="title")
        urls0 = re.compile(r'&id=CN.*?" target', re.S)
        pagenum=num-(page-1)*20-1
        urlscode = re.findall(urls0, str(class1[pagenum]))[0][4:-8]
        print(urlscode)
        url="http://www.wanfangdata.com.cn/details/detail.do?_type=patent&id="+urlscode
        class2=soup.find_all(class_="summary")
        summary=""
        ch = str(class2[pagenum])
        for i in range(len(ch)):
            if '\u4e00' <= ch[i] <= '\u9fff' or ch[i]=='：':
                summary+=ch[i]
        # print(summary)
        dnum = re.compile(r'下载：<span>\d{1,4}</span>', re.S)
        download = re.findall(dnum, r.text)[pagenum]  # 下载数量
        download_num=re.findall('(\d{1,4})',download)

        # print(url)
        # r2 = requests.get(url, headers)
        # r2.encoding = 'utf-8'
        # soup2 = (BeautifulSoup(r2.text, 'lxml'))
        # class3 = soup2.find_all(class_="info_right author")
        # print(str(class3[11])[31:-6])


        return url,urlscode,download_num[0],summary


    def get_basicexcel(self):
        self.state.setText('简易资料整理中...')
        time.sleep(1)
        xls=xlwt.Workbook()
        sht1=xls.add_sheet('专利简要信息',cell_overwrite_ok=True)
        sht1.write(0, 0, '编号')
        sht1.write(0, 1, '专利名称')
        sht1.write(0, 2, '专利号')
        sht1.write(0, 3, '专利下载量')
        sht1.write(0, 4, '专利摘要')
        sht1.write(0, 5, '专利申请日期')
        sht1.write(0, 6, '专利公开日期')
        sht1.write(0, 7, '专利主权项')
        sht1.write(0, 8, '链接')

        requestnum = int(self.num_decide.text())
        searchWord = self.keyword.text()
        url_searchWord = "&searchWord= " + searchWord
        orders = self.order_choose.currentText()
        if orders == '相关度':
            order='correlation'
        elif orders == '下载量':
            order='download_num'
        elif orders == '申请时间':
            order='app_date02'
        elif orders == '公开时间':
            order='pub_date'
        else:
            order='correlation'
        url_order = "&order=" + order
        patent_type = self.type_choose.currentText()
        url_patent_type = "&isHitUnit=&facetField=$patent_type:" + patent_type
        # self.state.setText('简易资料整理中...')
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(requestnum + 1)
        for i in range(1, requestnum+1):
            self.progressBar.setValue(i)
            ran=random.random()
            time.sleep(ran)
            urli,urlscodei,download_numi,summaryi=self.get_urlandabstrat(i-1,searchWord,order,patent_type)
            r2 = requests.get(urli, headers)
            r2.encoding = 'utf-8'
            soup2 = (BeautifulSoup(r2.text, 'lxml'))
            class3 = soup2.find(class_="title")
            namei = ""
            ch = str(class3)
            for j in range(len(ch)):
                if '\u4e00' <= ch[j] <= '\u9fff':
                    namei += ch[j]

            datef = re.compile(r'''\d{4}-\d{2}-\d{2}''')
            datestart = re.findall(datef, r2.text)[0]
            dateend = re.findall(datef,r2.text)[1]

            soup3 = (BeautifulSoup(r2.text, 'lxml'))
            class4 = soup3.find_all(class_="info_right author")
            mainrights=str(class4[-1])[31:-6]
            print('i=',i)
            sht1.write(i, 0, str(i))
            sht1.write(i, 1, namei)
            sht1.write(i, 2, urlscodei)
            sht1.write(i, 3, download_numi)
            sht1.write(i, 4, summaryi)
            sht1.write(i, 5, datestart)
            sht1.write(i, 6, dateend)
            sht1.write(i, 7, mainrights)
            sht1.write(i, 8, urli)
        route=self.route_show.text()
        xls.save(route+'\\rightsdata.xls')
        self.progressBar.setValue(requestnum+1)
        print(route)
        print('finish')
        self.state.setText('资料整理完成')

    def getdownurl(self,url):
        text = requests.get(url, headers).text
        # print(text)
        # re0 = r'<a onclick="upload\((.*?)\)"'
        # firurl = re.findall(re0, text)
        firurl=["'6','CN201811172010.8','','WF','一种摆臂机械手','','patent'"]
        # print(firurl)
        if len(firurl) == 0:
            return
        strurl = str(firurl[0])
        # print(strurl)
        tpurl = re.split(',', strurl)
        endstp = []
        # print(tpurl)
        for ul in tpurl:
            elem = ul.strip('\'').strip('\'')
            endstp.append(elem)
        # print(endstp, type(endstp[0]))
        head = 'http://www.wanfangdata.com.cn/search/downLoad.do?page_cnt='
        # geturl = head + endstp[0] + "&language=" + endstp[2] + "&resourceType=" + endstp[6] + "&source=" + endstp[
        #     3] + "&resourceId=" + endstp[1] + "&resourceTitle=" + endstp[4] + "&isoa=" + endstp[5] + "&type=" + endstp[
        #              0]
        geturl = head + endstp[0] + "&language=" + endstp[2] + "&resourceType=" + endstp[6] + "&source=" + endstp[
            3] + "&resourceId=" + endstp[1] + "&resourceTitle=" + endstp[4] + "&isoa=" + endstp[5] + "&type=" + endstp[
                     0]
        # print(geturl)
        re1 = r'<iframe style="display:none" id="downloadIframe" src="(.*?)">'
        text = requests.get(geturl, headers).text
        sucurl = re.findall(re1, text)
        return sucurl[0]

    def get_pdf(self,url, title,code):
        text = requests.get(url, headers)
        route=self.route_show.text()
        path = route + '\\' + title + code + ".pdf"
        with open(path, 'wb') as f:
        	f.write(text.content)
        print("successf")


    def download_pdf(self):
        self.state.setText('pdf下载中...')
        requestnum=int(self.num_decide.text())
        searchWord = self.keyword.text()
        url_searchWord = "&searchWord= " + searchWord
        orders = self.order_choose.currentText()
        if orders == '相关度':
            order = 'correlation'
        elif orders == '下载量':
            order = 'download_num'
        elif orders == '申请时间':
            order = 'app_date02'
        elif orders == '公开时间':
            order = 'pub_date'
        else:
            order = 'correlation'
        url_order = "&order=" + order
        patent_type = self.type_choose.currentText()
        url_patent_type = "&isHitUnit=&facetField=$patent_type:" + patent_type
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(requestnum + 1)
        for i in range(1, requestnum+1):
            self.progressBar.setValue(i)
            ran=random.random()
            time.sleep(ran)
            urli,urlscodei,download_numi,summaryi=self.get_urlandabstrat(i-1,searchWord,order,patent_type)
            r2 = requests.get(urli, headers)
            r2.encoding = 'utf-8'
            soup2 = (BeautifulSoup(r2.text, 'lxml'))
            class3 = soup2.find(class_="title")
            namei = ""
            ch = str(class3)
            for j in range(len(ch)):
                if '\u4e00' <= ch[j] <= '\u9fff':
                    namei += ch[j]
            downurl=self.getdownurl(urli)
            print(i)
            print(namei)
            self.get_pdf(downurl,namei,urlscodei)

        print('all successful')
        self.progressBar.setValue(requestnum+1)
        self.state.setText('pdf下载完成')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = informationabout()
    ui.show()
    sys.exit(app.exec_())


# order:correlation 相关度；download_num 下载量；app_date02 申请时间；pub_date：公开时间





