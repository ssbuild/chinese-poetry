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


def process_quantangshi(corpus_dir1, corpus_dir2, outfile):
    fs1 = os.listdir(corpus_dir1)
    fs2 = os.listdir(corpus_dir2)

    fs1 = [os.path.join(corpus_dir1, name) for name in fs1 if name.startswith('poet')]
    fs2 = [os.path.join(corpus_dir2, name) for name in fs2 if name.startswith('poet')]

    fs1 = sorted(fs1)
    fs2 = sorted(fs2)
    assert len(fs1) == len(fs2)

    f_out = open(outfile, mode='w', encoding='utf-8', newline='\n')
    num = 0

    keep_keys = ['title', 'author', 'paragraphs']
    for f1, f2 in zip(fs1, fs2):
        n1 = f1.split('.')[-2]
        n2 = f2.split('.')[-2]
        assert n1 == n2
        type = os.path.basename(f1)
        if type.find('song') != 0:
            type = '宋诗'
        else:
            type = '唐诗'
        f_in1 = open(f1, mode='r', encoding='utf-8', newline='\n')
        f_in2 = open(f2, mode='r', encoding='utf-8', newline='\n')
        jd1s = json.loads(f_in1.read())
        jd2s = json.loads(f_in2.read())
        f_in1.close()
        f_in2.close()

        dict_1 = {d['id']: d for d in jd1s}
        dict_2 = {d['id']: d for d in jd2s}
        for k in dict_1.keys() & dict_2.keys():
            jd1 = dict_1[k]
            jd2 = dict_2[k]
            try:
                assert jd1['id'] == jd2['id'], ValueError(f1, jd1, f2, jd2)
            except Exception as e:
                print(e)
                continue
            num += 1

            o = {}
            for k2 in keep_keys & jd1.keys():
                v = jd1[k2]
                if isinstance(v, list):
                    v = [convert(i, 'zh-cn') for i in v]
                else:
                    v = convert(v, 'zh-cn')
                o[k2] = v
            o['tones'] = jd2['strains']
            o['type'] = type
            f_out.write(json.dumps(o, ensure_ascii=False) + '\n')

    print(num)
    f_out.close()


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
        'paragraphs': 'paragraphs'
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
    # 唐诗宋词
    corpus_dir1 = r'D:\nlpdata_2022\诗句\chinese-poetry\json'
    corpus_dir2 = r'D:\nlpdata_2022\诗句\chinese-poetry\strains\json'
    outfile_0 = r'D:\nlpdata_2022\poetry_data\poetry.tangsong.json'
    process_quantangshi(corpus_dir1, corpus_dir2, outfile_0)

    # 全宋词
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\ci'
    outfile_1 = r'D:\nlpdata_2022\poetry_data\ci.song.json'
    process_common(corpus_dir, outfile_1, type='宋词', file_prefix='ci.song', file_extra='宋词三百首.json')

    # 楚辞
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\chuci'
    outfile_2 = r'D:\nlpdata_2022\poetry_data\chuci.json'
    process_common(corpus_dir, outfile_2, type='楚辞', file_suffix='.json')

    # 曹操诗
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\caocaoshiji'
    outfile_3 = r'D:\nlpdata_2022\poetry_data\caocaoshiji.json'
    process_common(corpus_dir, outfile_3, type='曹操诗', file_suffix='.json')

    # 论语
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\lunyu'
    outfile_4 = r'D:\nlpdata_2022\poetry_data\lunyu.json'
    process_common(corpus_dir, outfile_4, type='论语', file_suffix='.json')

    # 孟学
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\mengxue'
    outfile_5 = r'D:\nlpdata_2022\poetry_data\mengxue.json'
    process_common(corpus_dir, outfile_5, type='孟学', file_suffix='.json')

    # 诗经
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\shijing'
    outfile_6 = r'D:\nlpdata_2022\poetry_data\shijing.json'
    process_common(corpus_dir, outfile_6, type='诗经', file_suffix='.json')

    # 四书五经
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\sishuwujing'
    outfile_7 = r'D:\nlpdata_2022\poetry_data\sishuwujing.json'
    process_common(corpus_dir, outfile_7, type='四书五经', file_suffix='.json')

    # 五代 花间集
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\wudai\huajianji'
    outfile_8 = r'D:\nlpdata_2022\poetry_data\huajianji.json'
    process_common(corpus_dir, outfile_8, type='花间集', file_suffix='.json')

    # 五代 南唐二主词
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\wudai\nantang'
    outfile_9 = r'D:\nlpdata_2022\poetry_data\nantang.json'
    process_common(corpus_dir, outfile_9, type='南唐词', file_suffix='poetrys.json')

    # 幽梦影
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\youmengying'
    outfile_10 = r'D:\nlpdata_2022\poetry_data\youmengying.json'
    process_common(corpus_dir, outfile_10, type='幽梦影', file_suffix='.json')

    # 元曲
    corpus_dir = r'D:\nlpdata_2022\诗句\chinese-poetry\yuanqu'
    outfile_11 = r'D:\nlpdata_2022\poetry_data\yuanqu.json'
    process_common(corpus_dir, outfile_11, type='元曲', file_suffix='.json')

    outfile2 = './poetry_tangsong.record'
    convert2record([
        outfile_0, outfile_1, outfile_2, outfile_3, outfile_4,
        outfile_5, outfile_6, outfile_7, outfile_8, outfile_9,
        outfile_10, outfile_11,
    ], outfile2)
