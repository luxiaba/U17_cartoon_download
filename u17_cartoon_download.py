#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import requests
import base64
import binascii
from bs4 import BeautifulSoup

'''
Download U17 cartoon
cartoon_url is Cartoon Page URL
Generated  directory:
    Cartoon/'Cartoon_name'/
        'Cartoon file':Download cartoon file
        info.log:Download chapters information
Attention:after delete info.log content finally leave a blank line

'''


def get_img_list(chapter_url):
    # Returns a list of all the pictures of each chapter.
    cartoon_html = requests.get(chapter_url).content
    img_url_list = re.findall(r'"src":"(.*?)"', cartoon_html)
    chapter_img_list = [base64.b64decode(each) for each in img_url_list]
    return chapter_img_list


def get_cartoon(url):
    soup = BeautifulSoup(requests.get(url,headers={ "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36" }).content)
    title = soup.find('title').string
    a = soup.find('ul', class_='cf', id='chapter')
    chapter_info = {}
    all_chapter = a.find_all('li')
    for x, each in enumerate(all_chapter):
        chapter_info['%s_cpt_title' % (x + 1)] = each.a.text
        chapter_url = each.a['href']
        chapter_info['%s_cpt_img_list' % (x + 1)] = (chapter_url)

    # Back data struct ->
    # title:title,chapter_info:chapter_info{'1_cpt_title':title,'1_cpt_img_list':img_list}
    return title, chapter_info


def download_chapter(title, chapter_info, start_chapter, end_chapter, new=None):
    if new is None:
        cpt_log = ''
        module = 'a'
        tips = 'Update done!'
    else:
        cpt_log = '    %s   Tables\n' % title
        module = 'w'
        tips = 'All done!'

    for n in range(start_chapter, end_chapter + 1):
        chapter_title = chapter_info['%s_cpt_title' % n]
        print('Download…… Chapter %s-----%s' %
              (n, chapter_title.encode('utf-8')))
        # log info
        cpt_log = cpt_log + 'Chapter %s-----' % n + chapter_title + '\n'
        # get each chapter picture list
        chapter_url = chapter_info['%s_cpt_img_list' % n]
        img_list = get_img_list(chapter_url)
        for i, each in enumerate(img_list):
            img = requests.get(each).content
            with open('Cartoon/%s/%s---%s.jpg' % (title, chapter_title, i + 1), 'wb') as f:
                        f.write(img)

    # log
    with open('Cartoon/%s/info.log' % title, '%s' % module) as f:
        f.write(cpt_log.encode('utf-8'))
    print('%s' % tips)


def main(cartoon_url, max_chapter=None):
    title, chapter_info = get_cartoon(cartoon_url)
    print('Start Check!')
    if os.path.exists('Cartoon/%s' % title):
    # chapter_num:Updated chapters local_chapter_num:Local chapters
        try:
            with open('Cartoon/%s/info.log' % title, 'r') as f:
                local_chapter_num = len(f.readlines()) - 1
        except:
            with open('Cartoon/%s/info.log' % title, 'w') as f:
                local_chapter_num = 0
        chapter_num = len(chapter_info) / 2
        # Judge whether need to update
        update = chapter_num - local_chapter_num
        if (update > 0):
            print('%s  have new chapter!' % title.encode('utf-8'))
            print('Start Update...')
            start_chapter = local_chapter_num + 1
            end_chapter = chapter_num
            download_chapter(title, chapter_info, start_chapter, end_chapter)
        else:
            print('No chapter to update!')
    else:
    # If the path does not exist, create.
        os.makedirs('Cartoon/%s' % title)
        print('Start Download %s...' % title.encode('utf-8'))
        start_chapter = 1
        end_chapter = len(chapter_info) / 2
        if max_chapter is not None:
            if end_chapter > max_chapter:
                end_chapter = max_chapter
        download_chapter(title, chapter_info, start_chapter, end_chapter, 1)


if __name__ == '__main__':
    cartoon_url = 'http://www.u17.com/comic/72983.html'
    main(cartoon_url)
