# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import json
import os

import numpy as np
from fastdatasets.record import RECORD, NumpyWriter


def process_shici(corpus_dir, outfile, file_suffix='.csv'):
    fs = os.listdir(corpus_dir)
    fs = [os.path.join(corpus_dir, name) for name in fs if name.endswith(file_suffix)]

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    for fname in fs:
        with open(fname, mode='r', encoding='utf-8', newline='\n') as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.replace('\r\n', '').replace('\n', '')
            if not line:
                continue
            arr = line.split(',')
            if len(arr) == 0:
                continue
            if len(arr) != 2:
                arr = [arr[0], '男']
            num += 1
            o = {}
            o['title'] = '女' if arr[1] == '女' else '男'
            o['paragraphs'] = [arr[0]]
            o['type'] = '姓名'
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
    corpus_dir = r'D:\nlpdata_2023\Chinese-Names-Corpus\Chinese_Names_Corpus'
    outfile = r'D:\nlpdata_2022\poetry_data\xm.json'
    process_shici(corpus_dir, outfile, file_suffix='.txt')

    outfile2 = './xm.record'
    convert2record([
        outfile,
    ], outfile2)
