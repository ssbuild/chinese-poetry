# -*- coding: utf-8 -*-
# @Time    : 2023/1/24 15:16
# @Author  : tk
# @FileName: update_bert_vocab.py
import json
from collections import OrderedDict

from fastdatasets.record import load_dataset, RECORD
from tqdm import tqdm
from zhconv import convert


def is_chinese_char(cp):
    if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
            (cp >= 0x3400 and cp <= 0x4DBF) or  #
            (cp >= 0x20000 and cp <= 0x2A6DF) or  #
            (cp >= 0x2A700 and cp <= 0x2B73F) or  #
            (cp >= 0x2B740 and cp <= 0x2B81F) or  #
            (cp >= 0x2B820 and cp <= 0x2CEAF) or
            (cp >= 0xF900 and cp <= 0xFAFF) or  #
            (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
        return True
    return False


record_file = './poetry_tangsong.record'
dataset = load_dataset.RandomDataset(record_file,
                                     options=RECORD.TFRecordOptions(compression_type='GZIP')).parse_from_numpy_writer()


def poetry_parser(x):
    x = str(x['node'].tolist(), encoding='utf-8')
    x = json.loads(x)
    return x


dataset = dataset.map(poetry_parser)

print('total', len(dataset))

vocab = {}
for i in tqdm(range(len(dataset)), total=len(dataset)):
    d = dataset[i]
    if i < 3:
        print(d)
    string = d.get('title', '') + ''.join(d['paragraphs'])
    string = convert(string, 'zh-cn')
    for char in string:
        if not is_chinese_char(ord(char)):
            continue
        if char not in vocab:
            vocab[char] = 0
        vocab[char] += 1
vocab = dict(sorted(vocab.items(), key=lambda x: x[1], reverse=True))

new_vocab = {k: v for k, v in vocab.items() if v > 10}
print(vocab)
print(len(vocab))

bert_vocab_file = r'E:\algo_project\deep_training-examples\task_pretrain\lm_pretrain\config_gpt2\vocab.txt'
bert_vocab = OrderedDict()
with open(bert_vocab_file, mode='r', encoding='utf-8', newline='\n') as f:
    lines = f.readlines()
    for line in lines:
        line = line.replace('\r\n', '').replace('\n', '')
        if not line:
            continue
        bert_vocab[line] = len(bert_vocab)

for k, v in new_vocab.items():
    if k not in bert_vocab:
        bert_vocab[k] = len(bert_vocab)

print(bert_vocab)

bert_vocab_file = r'E:\algo_project\deep_training-examples\task_pretrain\poetry_gpt2_pretrain\config_gpt2\vocab.txt'
with open(bert_vocab_file, mode='w', encoding='utf-8', newline='\n') as f:
    for k in bert_vocab:
        f.write(k + '\n')
