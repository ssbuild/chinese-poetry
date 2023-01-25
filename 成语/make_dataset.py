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

    map_nums = {}
    for fname in fs:
        with open(fname, mode='r', encoding='utf-8', newline='\n') as f:
            lines = json.loads(f.read())
        basename = os.path.basename(fname)

        # 成语
        if basename.startswith('idiom'):
            dtype = '成语'
        # 汉字
        elif basename.startswith('word'):
            dtype = '汉字'
        # 词语
        elif basename.startswith('ci'):
            dtype = '词语'
        # 歇后语
        elif basename.startswith('xiehouyu'):
            dtype = '歇后语'
        else:
            raise ValueError('bad')

        for jd in lines:
            if not jd:
                continue
            if dtype == '成语':
                title = jd['word']
                paragraphs = [jd['explanation']]
            elif dtype == '汉字':
                title = jd['word']
                paragraphs = [jd['explanation']]
            elif dtype == '词语':
                title = jd['ci']
                paragraphs = [jd['explanation']]
            elif dtype == '歇后语':
                title = jd['riddle']
                paragraphs = [jd['answer']]
            else:
                raise ValueError('bad')
            if len(paragraphs[0]) == 0:
                continue
            num += 1
            if dtype not in map_nums:
                map_nums[dtype] = 0
            map_nums[dtype] += 1
            o = {}
            o['title'] = title
            o['paragraphs'] = paragraphs
            o['type'] = dtype
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
    corpus_dir = r'D:\nlpdata_2023\chinese-xinhua\data'
    outfile = r'D:\nlpdata_2022\poetry_data\成语.json'
    process_shici(corpus_dir, outfile, file_suffix='.json')

    outfile2 = './成语.record'
    convert2record([
        outfile,
    ], outfile2)
