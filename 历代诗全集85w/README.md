
## 诗堂数据介绍 共计 853385 , 按照朝代
    数据切分成两部分：
    唐宋及其以前 poetry_85w_part1.record  359903
        {'先秦': 570, '南北朝': 4586, '唐': 49195, '唐末宋初': 1118, '宋': 287114, '宋末元初': 12058, '宋末金初': 234, '汉': 363, '秦': 2, '隋': 1170, '隋末唐初': 472, '魏晋': 3020, '魏晋末南北朝初': 1}
    元明清及以后 poetry_85w_part2.record  493482
    {'元': 37375, '元末明初': 15736, '当代': 28219, '明': 236957, '明末清初': 17700, '民国末当代初': 1948, '清': 90089, '清末民国初': 15367, '清末近现代初': 12464, '辽': 22, '近现代': 28419, '近现代末当代初': 3426, '金': 2741, '金末元初': 3019}
    


#### 参考数据集 https://github.com/Werneror/Poetry

## 使用demo
pip install -U fastdatasets
```python
import json
from fastdatasets.record import load_dataset, RECORD
record_file = ['./poetry_85w_part1.record ','./poetry_85w_part2.record ']
dataset = load_dataset.RandomDataset(record_file,options = RECORD.TFRecordOptions(compression_type='GZIP')).parse_from_numpy_writer()

def poetry_parser(x):
    x = str(x['node'].tolist(), encoding='utf-8')
    x = json.loads(x)
    return x
dataset = dataset.map(poetry_parser)

print('total',len(dataset))
for i in range(len(dataset)):
    d = dataset[i]
    print(d)
    if i > 3:
        break
```

![Image text](1.png)