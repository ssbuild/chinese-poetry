# -*- coding: utf-8 -*-
# @Time    : 2023/1/22 19:20
# @Author  : tk
# @FileName: make_dataset.py
import copy
import json
import os

import numpy as np
from fastdatasets.record import RECORD, NumpyWriter
from zhconv import convert


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
        'singer': 'author'
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
            muti_instance = None
            for k2 in keep_keys.keys() & jd.keys():
                try:
                    v = jd[k2]
                    if isinstance(v, list):
                        if len(v) == 0:
                            is_ignore = True
                            break
                        if isinstance(v[0], dict):
                            if 'paragraphs' in v[0]:
                                muti_instance_tmp = [paragraphs_objs['paragraphs'] for paragraphs_objs in v]
                                muti_instance = []
                                for paragraphs in muti_instance_tmp:
                                    muti_instance.append([convert(i, 'zh-cn') for i in paragraphs])
                                continue
                            else:
                                is_ignore = True
                                print(jd)
                                break

                    if isinstance(v, list):
                        v = [convert(i, 'zh-cn') for i in v]
                    else:
                        v = convert(v, 'zh-cn')
                    o[keep_keys[k2]] = v
                except Exception as e:
                    print(k2, f)
                    print(jd)
                    raise e
            if not is_ignore:
                if muti_instance is not None:
                    tmp_title = ['其一', '其二', '其三', '其四', '其五', '其六', '其七']
                    for sub_title, paragraphs in zip(tmp_title, muti_instance_tmp):
                        tmp_o = copy.deepcopy(o)
                        tmp_o['paragraphs'] = paragraphs
                        if 'title' in tmp_o:
                            tmp_o['title'] += sub_title
                        num += 1
                        f_out.write(json.dumps(tmp_o, ensure_ascii=False) + '\n')
                else:
                    num += 1
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
    corpus_dir = r'D:\nlpdata_2023\ChineseLyrics'
    outfile = r'D:\nlpdata_2022\poetry_data\歌词.json'
    process_common(corpus_dir, outfile, type='歌词', file_suffix='.json')

    outfile_record = './歌词.record'
    convert2record([outfile], outfile_record)
