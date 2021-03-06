# coding: utf-8

import os
import random
from pathlib import Path

import sentencepiece as spm

def preproc(config):
    random.seed(config['random_seed'])

    prefix = Path(config['corpus_prefix'])
    src_train_orig = prefix / config['train_source']
    trg_train_orig = prefix / config['train_target']
    src_dev_orig = prefix / config['dev_source']
    trg_dev_orig = prefix / config['dev_target']
    src_test_orig = prefix / config['test_source']
    trg_test_orig = prefix / config['test_target']

    # make subword dir
    subword_dir = prefix / 'subword'
    if not os.path.exists(subword_dir):
        os.makedirs(subword_dir, exist_ok=True)

    corpus = []
    for filepath in [src_train_orig, trg_train_orig]:
        with open(filepath, 'r', encoding='utf-8') as f:
            corpus.extend(f.readlines())
    train_data_path = subword_dir / 'train.data'
    with open(train_data_path, 'w', encoding='utf-8') as ofs:
        random_idx = list(range(len(corpus)))
        random.shuffle(random_idx)
        for idx in random_idx:
            ofs.write(corpus[idx])

    model_prefix = subword_dir / 'spm'
    spm.SentencePieceTrainer.Train('--input=%s --vocab_size=%s --model_prefix=%s' %
                                   (train_data_path, config['vocabulary_size'], model_prefix))

    sp = spm.SentencePieceProcessor()
    sp.Load(str(model_prefix.with_suffix('.model')))

    src_files = [config['train_source'], config['dev_source'], config['test_source']]
    for filename in src_files:
        orig_file = prefix / filename
        subword_file = subword_dir / Path(filename).name
        with open(orig_file) as ifs, open(subword_file, 'w', encoding='utf-8') as ofs:
            for line in ifs:
                print(' '.join(map(str, sp.EncodeAsPieces(line.strip()))), file=ofs)

    sp.SetEncodeExtraOptions('bos:eos')
    trg_files = [config['train_target'], config['dev_target'], config['test_target']]
    for filename in trg_files:
        orig_file = prefix / filename
        subword_file = subword_dir / Path(filename).name
        with open(orig_file) as ifs, open(subword_file, 'w', encoding='utf-8') as ofs:
            for line in ifs:
                print(' '.join(map(str, sp.EncodeAsPieces(line.strip()))), file=ofs)
