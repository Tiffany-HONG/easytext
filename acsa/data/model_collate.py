#!/usr/bin/env python 3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 PanXu, Inc. All Rights Reserved
#
"""
model collate 产生 模型输入

Authors: PanXu
Date:    2020/07/12 16:54:00
"""
from typing import Dict, List

import torch

from easytext.data import ModelCollate, Instance
from easytext.data.tokenizer import EnTokenizer
from easytext.data import Vocabulary, LabelVocabulary
from easytext.model import ModelInputs


class ACSAModelCollate(ModelCollate):
    """
    ACSA Model Collate
    """

    def __init__(self,
                 token_vocabulary: Vocabulary,
                 category_vocabulary: LabelVocabulary,
                 label_vocabulary: LabelVocabulary,
                 sentence_max_len=500):

        self._tokenizer = EnTokenizer(is_remove_invalidate_char=True)
        self._token_vocabulary = token_vocabulary
        self._category_vocabulary = category_vocabulary
        self._label_vocabulary = label_vocabulary

        self._sentence_max_len = sentence_max_len

    def __call__(self, instances: List[Instance]) -> ModelInputs:

        batch_size = len(instances)

        batch_max_len = 0

        for instance in instances:
            sentence = instance["sentence"]

            if "sentence_tokens" not in instance:
                sentence_tokens = self._tokenizer.tokenize(sentence)
                instance["sentence_tokens"] = sentence_tokens
            sentence_tokens = instance["sentence_tokens"]

            batch_max_len = len(sentence_tokens) if len(sentence_tokens) > batch_max_len else batch_max_len

        batch_max_len = batch_max_len if batch_max_len < self._sentence_max_len else self._sentence_max_len

        batch_sentence_indices = list()
        batch_category_index = list()
        batch_label_index = list()

        for instance in instances:
            sentence_tokens = [t.text for t in instance["sentence_tokens"]]
            sentence_indices = [self._token_vocabulary.padding_index] * batch_max_len

            for i, token in enumerate(sentence_tokens):
                sentence_indices[i] = self._token_vocabulary.index(token)

            batch_sentence_indices.append(sentence_indices)

            category = instance["category"]
            batch_category_index.append(self._category_vocabulary.index(category))

            if "label" in instance:  # 当进行预测的时候，是没有 label 的，所以这里要进行特殊处理下
                label = instance["label"]
                batch_label_index.append(self._label_vocabulary.index(label))

        sentence_tensor = torch.LongTensor(batch_sentence_indices)
        category_tensor = torch.LongTensor(batch_category_index)

        label_tensor = torch.LongTensor(batch_label_index)

        model_inputs = ModelInputs(batch_size=batch_size,
                                   model_inputs={
                                       "sentence": sentence_tensor,
                                       "category": category_tensor
                                   },
                                   labels=label_tensor)
        return model_inputs


















