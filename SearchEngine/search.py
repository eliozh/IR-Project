# -*- coding: utf-8 -*-

import pickle
import math
import jieba
import os

from utils.database import col
from utils.validator import match_words
from SearchEngine.indexer import Indexer


class IndexSearch:

    def __init__(self, cwd):
        self.posting = open(os.path.join(cwd, 'data', 'postings'), 'rb')
        self.word_dictionary = pickle.load(self.posting)

    def calculate_tfidf(self, word):
        score_dictionary = {}

        if word not in self.word_dictionary:
            return 0

        for posting in self.word_dictionary[word]:
            douban_id = posting[0]
            freq = posting[1]

            idf = math.log(float(100) / len(self.word_dictionary[word]))
            tf = 1 + math.log(int(freq)) if freq > 0 else 0
            tfidf_score = tf * idf
            score_dictionary[douban_id] = tfidf_score

        score = sorted(score_dictionary.items(), key=lambda d: d[1], reverse=True)
        return score

    @staticmethod
    def get_word_count_in_document(word, document):
        words = Indexer.cut_document(document)
        cnt = 0
        for one in words:
            if one == word:
                cnt += 1
        return cnt

    def id2doc(self, douban_id):
        doc = col.find_one({'douban_id': douban_id})
        return doc

    def calculate_bm25(self, query_words):
        score_dictionary = {}
        b = 0.5  # 参数调节因子
        k = 10  # 调节因子
        avdl = 800  # 文档平均长度

        id_of_query_words = set()

        split_query_word = jieba.lcut_for_search(query_words)
        split_query_word = list(filter(match_words, split_query_word))

        for word in split_query_word:
            if word not in self.word_dictionary:
                continue

            for posting in self.word_dictionary[word]:
                douban_id = posting[0]
                id_of_query_words.add(douban_id)

        for idx in id_of_query_words:
            bm25_score = 0
            for word in split_query_word:
                doc = col.find_one({'douban_id': idx})
                freq = self.get_word_count_in_document(word, doc)

                doc_len = len(self.word_dictionary[word])
                idf = math.log(float(100) / doc_len)
                normalizer = 1 - b + b * (doc_len / avdl)

                bm25_score += float((k + 1) * freq) / (freq + k * normalizer) * idf
            score_dictionary[idx] = bm25_score

        score = sorted(score_dictionary.items(), key=lambda d: d[1], reverse=True)

        return score


if __name__ == '__main__':
    pass
