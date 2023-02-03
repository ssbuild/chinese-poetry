# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import json
import os
import numpy as np
from fastdatasets.record import RECORD, NumpyWriter
import pandas as pd

def process_nicheng(corpus_dir, outfile, file_suffix='.csv'):
    fs = os.listdir(corpus_dir)
    fs = [os.path.join(corpus_dir, name) for name in fs if name.endswith(file_suffix)]

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    count_map = {}
    for fname in fs:
        df = pd.read_csv(fname,encoding='utf-8',sep='\t')
        #df.to_csv(fname,sep='\t',line_terminator='\n',index=False)

        for name_,class_,title_  in zip(df['网名'],df['分类'],df['标签']):
            num += 1
            o = {}
            o['title'] = title_
            o['paragraphs'] = [name_]
            o['type'] = class_
            if class_ not in count_map:
                count_map[class_] = 0
            count_map[class_] += 1
            print(o)
            f_out.write(json.dumps(o, ensure_ascii=False) + '\n')

    print(num)
    print(count_map)
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

    corpus_dir = r'F:\nlpdata_2023\70万个网名'
    outfile = r'F:\nlpdata_2022\poetry_data\nickname.json'
    process_nicheng(corpus_dir, outfile, file_suffix='.txt')

    outfile2 = './nickname.record'
    convert2record([
        outfile,
    ], outfile2)
