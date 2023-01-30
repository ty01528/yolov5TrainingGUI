import os
import random
import yaml
import shutil


def getYaml(yamlPath):
    with open(yamlPath, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def setYaml(yamlPath, data):
    with open(yamlPath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True)


# 根据给出的picDir和annoDir以及分割比例，生成coco128格式的数据集,标注文件为yolo的txt格式
def generate_dataset(pic_dir, anno_dir, split_ratio, outputDir):
    train_pic_dir = os.path.join(outputDir, 'train')
    val_pic_dir = os.path.join(outputDir, 'val')

    if not os.path.exists(train_pic_dir):
        os.makedirs(train_pic_dir)
    if not os.path.exists(val_pic_dir):
        os.makedirs(val_pic_dir)

    pic_list = [f.split('.')[0] for f in os.listdir(pic_dir) if f.endswith('.jpg') or f.endswith('.png')]
    anno_list = [f.split('.')[0] for f in os.listdir(anno_dir) if f.endswith('.txt')]

    if set(pic_list) != set(anno_list):
        raise ValueError('图片文件和标注文件不一一对应')

    train_num = int(len(pic_list) * float(split_ratio))
    train_set = set(random.sample(pic_list, train_num))
    val_set = set(pic_list) - train_set

    for f in train_set:
        shutil.copyfile(os.path.join(pic_dir, f + '.jpg'), os.path.join(train_pic_dir, f + '.jpg'))
        shutil.copyfile(os.path.join(anno_dir, f + '.txt'), os.path.join(train_pic_dir, f + '.txt'))

    for f in val_set:
        shutil.copyfile(os.path.join(pic_dir, f + '.jpg'), os.path.join(val_pic_dir, f + '.jpg'))
        shutil.copyfile(os.path.join(anno_dir, f + '.txt'), os.path.join(val_pic_dir, f + '.txt'))

    return train_pic_dir, val_pic_dir
