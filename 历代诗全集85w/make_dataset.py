# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import json
import os
import pandas as pd
import numpy as np
from fastdatasets.record import RECORD, NumpyWriter


def process_shici(corpus_dir, outfile, file_suffix='.csv'):
    fs = os.listdir(corpus_dir)
    fs = [os.path.join(corpus_dir, name) for name in fs if name.endswith(file_suffix)]

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    map_nums = {}
    for fname in fs:
        df = pd.read_csv(fname,sep=',')
        for title,dynasty,author,content in zip(df['题目'],df['朝代'],df['作者'],df['内容']):

            num += 1
            content: str


            o = {}
            o['title'] = title
            o['author'] = author
            o['paragraphs'] = [_ + '。' for _ in content.split('。') if _]
            o['type'] = dynasty

            if dynasty not in map_nums:
                map_nums[dynasty] = 0
            map_nums[dynasty] += 1

            f_out.write(json.dumps(o, ensure_ascii=False) + '\n')

    print(map_nums)
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
    corpus_dir = r'D:\nlpdata_2023\Poetry\唐宋'
    outfile = r'D:\nlpdata_2022\poetry_data\poetry_85w_part1.json'
    process_shici(corpus_dir, outfile)

    outfile2 = './poetry_85w_part1.record'
    convert2record([
        outfile,
    ], outfile2)

    # 元明清近现代
    corpus_dir = r'D:\nlpdata_2023\Poetry\元明清近现代'
    outfile = r'D:\nlpdata_2022\poetry_data\poetry_85w_part2.json'
    process_shici(corpus_dir, outfile)

    outfile2 = './poetry_85w_part2.record'
    convert2record([
        outfile,
    ], outfile2)
