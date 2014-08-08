# -*- coding: utf-8 -*-
__author__ = 'CrazyHedgehog'

import cookielib
import urllib
import urllib2
import time
import random
import string
from bs4 import BeautifulSoup
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import re


class PDFtoTXT:
    @staticmethod
    def __countPages(in_Pdf_File_Path):
        rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)
        data = file(in_Pdf_File_Path, 'rb').read()
        return len(rxcountpages.findall(data))

    @staticmethod
    def __IsText(FileObject,in_Pdf_File_Path):
        FileObject.seek(0,2) # move the cursor to the end of the file
        SizeOnePage = FileObject.tell()/ PDFtoTXT.__countPages(in_Pdf_File_Path)
        Text = True
        if SizeOnePage > 200000:
           Text = False
        return Text
    @staticmethod
    def __getStrFromPdf(in_Pdf_File_Path):
        fp = file(in_Pdf_File_Path, 'rb')
        if  PDFtoTXT.__IsText(fp,in_Pdf_File_Path):
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos=set()

            pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)

            for page in pages:
                interpreter.process_page(page)
            fp.close()
            device.close()
            str = retstr.getvalue()
            retstr.close()
        return str

    @staticmethod
    def ConvertPdfToText(in_Pdf_File_Path, out_Txt_File_Path):
        fo= open(out_Txt_File_Path, "w")
        fo.write(PDFtoTXT.__getStrFromPdf(in_Pdf_File_Path))
        fo.close()


class Article:
    def __init__(self, id_elibrary, author, journal, year, pages, title, university,
                 type_art, language, num_journal, volume_journal):
        self.id_elibrary = id_elibrary.replace(';', ' ')
        self.author = author.replace(';', ' ')
        self.journal = journal.replace(';', ' ')
        self.year = year.replace(';', ' ')
        self.pages = pages.replace(';', ' ')
        self.title = title.replace(';', ' ')
        self.university = university.replace(';', ' ')
        self.type_art = type_art.replace(';', ' ')
        self.language = language.replace(';', ' ')
        self.num_journal = num_journal.replace(';', ' ')
        self.volume_journal = volume_journal.replace(';', ' ')

    def get_for_csv(self):
        res_string = ''
        res_string += self.id_elibrary + ';' + self.title + ';' + self.author + ';'
        res_string += self.university + ';' + self.type_art + ';' + self.language + ';'
        res_string += self.journal + ';' + self.volume_journal + ';' + self.num_journal + ';'
        res_string += self.pages
        return res_string


def parse_html_article(html):
    soup = BeautifulSoup(html)

    res_str = soup.get_text()
    for tmp in res_str.splitlines():

        if tmp.find(u'Язык') != -1:
            print tmp


def check_green(id_article):
    url = 'http://elibrary.ru/item.asp?id=' + str(id_article)
    response = urllib2.urlopen(url)
    html = response.read()
    if '<div id="blockedip"' in html:
        print 'BLOCKED!!'
        return -1
    if 'javascript:load_article()' in html:
        download_html(html, id_article)
        if download_pdf(id_article) == -1:
            return -2
        return 1
    else:
        return 0



def download_html(html, id_article):
    name = str(id_article) + '.html'
    file_html = open('/home/crazyhedgehog/Desktop/htmls/' + name, 'w')
    file_html.write(html)
    file_html.close()
    print 'HTML file has been saved'



def download_pdf(id_article):
    start = 'window.location.href="'
    finish = '.pdf"'
    response = urllib2.urlopen('http://elibrary.ru/full_text.asp?id=' + str(id_article))
    html = response.read()
    start_index = html.find(start) + len(start)
    finish_index = html.find(finish) + len(finish) - 1
    result_name = html[start_index:finish_index]
    if finish_index <= start_index or result_name.find('http') != 0 or finish_index == -1 or start_index == -1:
        print 'ERROR in download pdf'
        return -1
    else:
        file_pdf = open('/home/crazyhedgehog/Desktop/pdfs/' + str(id_article) + '.pdf', 'wb')
        response = urllib2.urlopen(result_name)
        buffer = response.read()
        file_pdf.write(buffer)
        file_pdf.close()
        print 'PDF file has been saved'
        return 0

def register_new_user():
    new_name = ''.join(random.choice(string.ascii_lowercase) for x in range(8))
    payload = {
    'surname': new_name,
    'name': new_name,
    'lastname': new_name,
    'pol': 1,
    'bday': 1,
    'bmonth': 1,
    'byear': 1987,
    'orgname': u'Lietuvos zemes ukio konsultavimo tarnyba',
    'orgdepname': u'LIETUVOS ZEMES UKIO KONSULTAVIMO TARNYBA',
    'town': u'Kedainiu',
    'post': 'Student',
    'ulogin': new_name,
    'upassword': 'hedgehogpass',
    'email': new_name +'@gmail.com'
}

    register_url = 'http://elibrary.ru/author_info.asp'
    auth_url = 'http://elibrary.ru/'
    cj = cookielib.CookieJar()
    proxy = urllib2.ProxyHandler({'http': '183.230.127.60:8085'})
    opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj))

    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib2.install_opener(opener)
    data = urllib.urlencode(payload)
    req = urllib2.Request(register_url, data)
    resp = urllib2.urlopen(req)
    user = {'login': new_name, 'password': 'hedgehogpass'}
    data = urllib.urlencode(user)
    req = urllib2.Request(auth_url, data)
    resp = urllib2.urlopen(req)

    print 'New user has been register successfully'
    return user

f = open('/home/crazyhedgehog/Desktop/htmls/17971111.html', 'r')
parse_html_article(f.read())



'''

user = register_new_user()
auth_url = 'http://elibrary.ru/'
cj = cookielib.CookieJar()
proxy = urllib2.ProxyHandler({'http': '176.73.142.89:1080'})
opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)
data = urllib.urlencode(user)
req = urllib2.Request(auth_url, data)
resp = urllib2.urlopen(req)




count = 0


start_time = time.time()
start_index = 17972100
for i in range(start_index, 17980000): #18893966   1. 17949544
    count += 1
    if(count % 10 == 0):
        print "time from start: %f " % (time.time() - start_time)

    result = check_green(i)
    if result == 1:
        #f.write(url + '\n')
        print str(count) + ' articles were produced, Done! id = ' + str(i)
    elif result == -1:
        break
    elif result == -2:
        user = register_new_user()
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        data = urllib.urlencode(user)
        req = urllib2.Request(auth_url, data)
        resp = urllib2.urlopen(req)
        i -= 1
    else:
        print(str(count) + ' articles were produced')


#req = urllib2.Request(auth_url)
#resp = urllib2.urlopen(req)

#buffer = resp.read()
#print(buffer)


'''


#TODO 1. check green
#TODO 2. get pdf from id
#TODO 3. get greens file
#TODO 4. parsing html

#classes
#Html parser (get information from html code)
#elibrary wrapper (download pdf from id,
#article
