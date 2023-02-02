# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import json
import os
import re

import numpy as np
from fastdatasets.record import RECORD, NumpyWriter



def B2Q(uchar):
    """单个字符 半角转全角"""
    inside_code = ord(uchar)
    if inside_code < 0x0020 or inside_code > 0x7e: # 不是半角字符就返回原来的字符
        return uchar
    if inside_code == 0x0020: # 除了空格其他的全角半角的公式为: 半角 = 全角 - 0xfee0
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return chr(inside_code)

def Q2B(uchar):
    """单个字符 全角转半角"""
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e: #转完之后不是半角字符返回原来的字符
        return uchar
    return chr(inside_code)


def stringQ2B(ustring):
    """把字符串全角转半角"""
    return "".join([Q2B(uchar) for uchar in ustring])

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是半角数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_Qnumber(uchar):
    """判断一个unicode是否是全角数字"""
    if uchar >= u'\uff10' and uchar <= u'\uff19':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是半角英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False


def is_Qalphabet(uchar):
    """判断一个unicode是否是全角英文字母"""
    if (uchar >= u'\uff21' and uchar <= u'\uff3a') or (uchar >= u'\uff41' and uchar <= u'\uff5a'):
        return True
    else:
        return False

def stringpartQ2B(ustring):
    """把字符串中数字和字母全角转半角"""
    return "".join([Q2B(uchar) if is_Qnumber(uchar) or is_Qalphabet(uchar) else uchar for uchar in ustring])


def remove_tags(line: str, prefix='<a', suffix='a>'):
    pos = line.find(prefix)
    if pos != -1:
        text = ''
        if pos > 0:
            text += line[:pos]
        pos2 = line.find(suffix, pos)
        if pos2 == -1:
            return None

        text += line[pos2 + len(suffix):]
        text = text.replace(suffix, '')
    else:
        text = line
    return text


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
            line = line.lstrip('<p>').rstrip('</p>')
            line = line.strip()
            num += 1
            o = {}

            line = re.split(re.compile('^(\d+)、'), line, maxsplit=2)[-1]
            line = remove_tags(line, '<a', '</a>')
            if line is None:
                continue

            line = remove_tags(line, '<u', '</u>')
            if line is None:
                continue

            line = stringpartQ2B(line)
            o['paragraphs'] = [line]
            o['type'] = '骂人'
            print(line)
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
    corpus_dir = r'F:\nlpdata_2023\maya\data\1juzi'
    outfile = r'F:\nlpdata_2022\poetry_data\骂人.json'
    process_shici(corpus_dir, outfile, file_suffix='.txt')

    outfile2 = './maya.record'
    convert2record([
        outfile,
    ], outfile2)
