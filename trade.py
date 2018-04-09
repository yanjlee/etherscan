#!/usr/bin/env python2
# coding: utf-8

import re
import urllib2
import cookielib
import cfscrape
from webscraping import download, xpath, common, adt

MAN = '0xe25bcec5d3801ce3a794079bf94adf1b8ccd802d'
QASH = '0x618e75ac90b12c6049ba3b27f5d5f8651b0037f6'

def scrape_holder_transfer(holders, coin):
    typ = MAN if coin == 'MAN' else QASH
    scraper = cfscrape.create_scraper()
    def parse_html2(html):
        infos = []
        for i in html.split("<td></td></tr>"):
            ms = xpath.search(i, r"//span[@class='address-tag']")
            txhash = common.normalize(ms[0]) if len(ms) > 0 else ''
            fm = common.normalize(ms[1]) if len(ms) > 1 else ''
            too = common.normalize(ms[2]) if len(ms) > 2 else ''

            age = xpath.get(i, r"//span[@rel='tooltip']/@title")
            quantity = common.regex_get(i, r'>([\d\.\,]+)</td>$')
            direction = common.normalize(xpath.get(i, r'//span[@class="label\slabel.+"]'))

            if txhash:
                info = '"' + '","'.join([txhash, age, fm, direction, too, quantity]) + '"' 
                infos.append(info)
        return infos

    num = 0 
    for holder in holders:
        f = open('./holders/%s.csv' % holder, 'w')
        f.write('"TxHash", "Age", "From", "Direction", "To", "Quantity"\n')
        url = 'https://etherscan.io/token/generic-tokentxns2?contractAddress=%s&mode=&a=%s&p=%s' % (typ, holder, num)
        html = scraper.get(url).content

        lst = parse_html2(html)
        page_num = common.regex_get(html, r'/b>\sof\s<b>(\d+)<')
        if page_num and page_num >= 5:
            page_num = 5 
        for k in range(2, page_num+1):
            html = scraper.get(url).content
            lst += parse_html2(html)
        for k in lst:
            f.write(k+'\n')

if __name__ == '__main__':
    scrape_holder_transfer(['0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208'], 'MAN')
