# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import json
import os
import re

import numpy as np
from fastdatasets.record import RECORD, NumpyWriter


def process_shici(corpus_dir, outfile, file_suffix='.csv'):
    fs = os.listdir(corpus_dir)
    fs = [os.path.join(corpus_dir, name) for name in fs if name.endswith(file_suffix)]

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    for fname in fs:
        with open(fname, mode='r', encoding='utf-8', newline='\n') as f:
            text = f.read()

        text = text.replace('\r\n','\n')
        pos = text.find('------------------')
        note = ''
        if pos != -1:
            note = text[pos + len('------------------'):]
            text = text[:pos]


        text_list = text.split('\n')

        title = text_list[0]
        date =  text_list[1]
        index = -1
        for i in range(len(text_list)):
            if text_list[i].startswith('>'):
                index = i
                break
        backgroud = ''
        if index != -1:
            backgroud = text_list.pop(index)

        text = '\n'.join(text_list)

        pos = text.find('##')
        text = text[pos + 2:]
        paragraphs = re.split(re.compile('##'), text, re.MULTILINE)



        title = title.replace('#','').strip()
        date = date.strip()
        backgroud = backgroud.replace('>', '').strip()

        paragraphs_new = []
        for item in paragraphs:
            paragraphs_new.extend(item.split('\n'))

        paragraphs = [_.strip() for _ in paragraphs_new if _.strip()]
        paragraphs = [_.replace('\u3000','').replace('(./目录.md)','') for _ in paragraphs]


        num += 1
        o = {}
        o['title'] = title
        o['backgroud'] = backgroud
        o['paragraphs'] = paragraphs
        o['type'] = '毛泽东选集'
        o['note'] = note
        o['date'] = date

        print(paragraphs)
        f_out.write(json.dumps(o, ensure_ascii=False) + '\n')

    print(num)
    f_out.close()


def convert2record(src_list, dst):
    lines = []
    for src in src_list:
        with open(src, mode='r', encoding='utf-8') as f:
            lines += f.readlines()

    options = RECORD.TFRecordOptions(compression_type='GZIP')
    f = NumpyWriter(dst, options=options)
    i = 0
    for line in lines:

        jd = json.loads(line)
        if not jd:
            continue
        i += 1
        o = {
            'index': np.asarray(i, dtype=np.int32),
            'node': np.asarray(bytes(line, encoding='utf-8'))
        }
        f.write(o)
    f.close()


if __name__ == '__main__':
    # 唐诗宋词
    corpus_dir = r'F:\nlpdata_2023\MaoZeDongAnthology\src'
    outfile = r'F:\nlpdata_2022\poetry_data\毛泽东选集.json'
    process_shici(corpus_dir, outfile, file_suffix='.md')

    outfile2 = './毛泽东选集.record'
    convert2record([
        outfile,
    ], outfile2)
