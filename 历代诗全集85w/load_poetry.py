# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 20:58
# @Author  : tk
# @FileName: load_poetry.py
import json

from fastdatasets.record import load_dataset, RECORD

record_file = ['./poetry_80w_part1.record ','./poetry_80w_part2.record ']
dataset = load_dataset.RandomDataset(record_file,
                                     options=RECORD.TFRecordOptions(compression_type='GZIP')).parse_from_numpy_writer()


def poetry_parser(x):
    x = str(x['node'].tolist(), encoding='utf-8')
    x = json.loads(x)
    return x


dataset = dataset.map(poetry_parser)

print('total', len(dataset))
for i in range(len(dataset)):
    d = dataset[i]
    print(d)
    if i > 3:
        break
