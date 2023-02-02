# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import copy
import json
import os

import numpy as np
import unicodedata
from fastdatasets.record import RECORD, NumpyWriter
from zhconv import convert

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

def process_common(corpus_dir, outfile, type, file_prefix=None, file_suffix=None, file_extra=None):
    fs = os.listdir(corpus_dir)
    if file_prefix is not None and file_suffix is not None:
        fs = [os.path.join(corpus_dir, name) for name in fs if
              name.startswith(file_prefix) and name.endswith(file_suffix)]
    elif file_prefix is not None:
        fs = [os.path.join(corpus_dir, name) for name in fs if name.startswith(file_prefix)]
    elif file_suffix is not None:
        fs = [os.path.join(corpus_dir, name) for name in fs if name.endswith(file_suffix)]
    else:
        raise ValueError('file_prefix and file_suffix must set one at least')
    if file_extra is not None:
        fs.append(os.path.join(corpus_dir, file_extra))
    fs = sorted(fs)

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    keep_keys_ = {
        'title': 'title',
        'author': 'author',
        'content': 'paragraphs',
        'rhythmic': 'title',
        'chapter': 'title',
        'paragraphs': 'paragraphs',
        'name': 'title',
        'singer': 'author',
        'lyric': 'paragraphs'
    }
    for f in fs:
        f_in = open(f, mode='r', encoding='utf-8', newline='\n')
        jds = json.loads(f_in.read())
        f_in.close()

        content_flag = False
        if isinstance(jds, dict):
            if 'paragraphs' in jds:
                jds = [jds]
            elif 'content' in jds:
                jds = jds['content']
                content_flag = True

        if content_flag:
            if isinstance(jds[0], dict) and 'content' in jds[0]:
                jds = [jd for contents in jds for jd in contents['content']]

        keep_keys = copy.deepcopy(keep_keys_)
        for jd in jds:
            o = {'type': type}
            if 'title' in jd:
                keep_keys.pop('rhythmic', None)
                keep_keys.pop('chapter', None)

            is_ignore = False
            for k2 in keep_keys.keys() & jd.keys():
                try:
                    v = jd[k2]
                    if isinstance(v, list):
                        v = [i.strip() for i in v if len(i.strip()) > 0]
                        v = [convert(i, 'zh-cn') for i in v]
                    else:
                        v = convert(v, 'zh-cn')
                    o[keep_keys[k2]] = v
                except Exception as e:
                    print(k2, f)
                    print(jd)
                    raise e
            if o['title'] == '万万没想到':
                is_ignore = True

            if not is_ignore:
                paragraphs = o['paragraphs']
                x = ','.join(paragraphs)
                x = x.replace(',,', '。')
                x = stringpartQ2B(x)
                x = unicodedata.normalize('NFKC', x)
                x = x.replace('\ufeff,','')
                o['paragraphs'] = x.split('。')

                x = o['title']
                x = stringpartQ2B(x)
                x = unicodedata.normalize('NFKC', x)
                x = x.replace('\ufeff,', '')
                o['title'] = x

                num += 1
                print(o)
                f_out.write(json.dumps(o, ensure_ascii=False) + '\n')

    print(type, num)
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
    # 对联
    corpus_dir = r'F:\nlpdata_2023\ChineseLyrics'
    outfile = r'F:\nlpdata_2022\poetry_data\歌词.json'
    process_common(corpus_dir, outfile, type='歌词', file_suffix='.json')

    outfile_record = './歌词.record'
    convert2record([outfile], outfile_record)
