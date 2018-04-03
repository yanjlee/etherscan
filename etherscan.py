#!/usr/bin/env python2
# coding: utf-8

import re
import urllib2
import cookielib
import cfscrape
from webscraping import download, xpath, common, adt


SRC1 = 'https://etherscan.io/token/generic-tokentxns2?contractAddress=0xe25bcec5d3801ce3a794079bf94adf1b8ccd802d&mode=&p=%s'
SRC2 = 'https://etherscan.io/token/generic-tokenholders2?a=0xe25bcec5d3801ce3a794079bf94adf1b8ccd802d&p=%s'

def etherscan():
    found = adt.HashDict(int)
    f = open('transfers.csv', 'w')
    f.write('"TxHash","Age","From","To","Quantity"')
    hf = open('holder.csv', 'w')
    hf.write('"Rank","Address","Quantity","Percentage"')
    
    scraper = cfscrape.create_scraper()
    for i in range(10, 0, -1):
        url = SRC1 % str(i)
        html = scraper.get(url).content
        for k in parse(html):
            if k not in found:
                found[k]
                f.write(k + '\n')

        hurl = SRC2 % str(i)
        html2 = scraper.get(hurl).content
        for k in holders_parse(html2):
            if k not in found:
                found[k]
                hf.write(k + '\n')

def holders_parse(html):
    infos = []
    h = xpath.get(html, r'//table[@class="table"]', remove=None)
    for k in xpath.search(h, r'//tr', remove=None):
        if '</td><td>' in k:
            ms = [common.normalize(m) for m in xpath.search(k, r'//td')]
            infos.append('"'+'","'.join(ms)+'"')
    return infos

def parse(html):
    infos = []
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
    etherscan()
