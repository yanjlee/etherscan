#!/usr/bin/env python2
# coding: utf-8

import re
import urllib2
import cookielib
import cfscrape
from webscraping import download, xpath, common, adt

MAN = '0xe25bcec5d3801ce3a794079bf94adf1b8ccd802d'
QASH = '0x618e75ac90b12c6049ba3b27f5d5f8651b0037f6'
BAG = {'MAN':[], 'QASH':[]}

def scrape_title(num, typ):
    f = open('title_%s.txt' % typ, 'w')
    D = download.Download(read_cache=False)

    key = MAN if typ == 'MAN' else QASH
    url = 'https://etherscan.io/token/%s' % key

    html = D.get(url)
    ts = common.regex_get(html, r'Total\sSupply\:[^<]*</td>[^<]*<td>([^<]+)<')
    vt = common.regex_get(html, r'Value\sper\sToken\:[^<]*</td>[^<]*<td>([^<]+)<')
    th = common.regex_get(html, r'Token\sHolders\:[^<]*</td>[^<]*<td>([^<]+)<')
    f.write('Total Supply: %s\n' % ts)
    f.write('Value per Token: %s\n' % vt)
    f.write('Token Holders: %s\n' % th)
    f.write('No.Of.Transfers: %s\n' % num)

def etherscan(typ):
    found = adt.HashDict(int)
    f = open('transfers_%s.csv' % typ, 'w')
    f.write('"TxHash","Age","From","To","Quantity"\n')
    hf = open('holder_%s.csv' % typ, 'w')
    hf.write('"Rank","Address","Quantity","Percentage"\n')
    
    key = MAN if typ == 'MAN' else QASH
    SRC1 = 'https://etherscan.io/token/generic-tokentxns2?contractAddress=%s&mode=&p=' % key
    if typ == 'MAN' :
        SRC2 = 'https://etherscan.io/token/generic-tokenholders2?a=%s&s=2.5E%%2b26&p=' % key
    else:
        SRC2 = 'https://etherscan.io/token/generic-tokenholders2?a=%s&s=1E%%2b15&p=' % key

    scraper = cfscrape.create_scraper()
    for i in range(10, 0, -1):
        url = SRC1 + str(i)
        print 'Downloading %s' % url
        html = scraper.get(url).content
        for k in parse(html):
            if k not in found:
                found[k]
                f.write(k + '\n')

        hurl = SRC2 + str(i)
        print 'Downloading %s' % hurl
        html2 = scraper.get(hurl).content
        for k in holders_parse(html2, i):
            if k not in found:
                found[k]
                
    num = common.regex_get(html, r'A\sTotal\sof\s(\d+)\sevents\sfound')
    scrape_title(num, typ)

def holders_parse(html, i):
    infos = []
    h = xpath.get(html, r'//table[@class="table"]', remove=None)
    for k in xpath.search(h, r'//tr', remove=None):
        if '</td><td>' in k:
            ms = [common.normalize(m) for m in xpath.search(k, r'//td')]
            infos.append('"'+'","'.join(ms)+'"')
    return infos

def parse(html, page):
    for i in html.split("<td></td></tr>"):
        ms = xpath.search(i, r"//a[@target='_parent']")
        txhash = ms[0] if len(ms) > 0 else ''
        fm = ms[1] if len(ms) > 1 else ''
        too = ms[2] if len(ms) > 2 else ''

        age = xpath.get(i, r"//span[@rel='tooltip']/@title")
        quantity = common.regex_get(i, r'>([\d\.\,]+)</td>$')

        info = '"' + '","'.join([txhash, age, fm, too, quantity]) + '"'
        infos.append(info)
    return infos

if __name__ == '__main__':
    for typ in ['MAN', 'QASH']:
        print 'scrape %s...' % typ
        etherscan(typ)
