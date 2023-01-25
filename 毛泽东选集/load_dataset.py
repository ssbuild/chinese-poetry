import json

from fastdatasets.record import load_dataset, RECORD

record_file = './毛泽东选集.record'
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
