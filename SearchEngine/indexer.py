#!/usr/bin/python
# -*- coding:utf-8 -*-
import jieba
import pickle

from utils.database import col
from utils.validator import match_words


class Indexer:

    def __init__(self):
        pass

    @staticmethod
    def cut_document(document):
        """
        对 mongodb 中的每个文档的 summary 做分词
        同时在单词表中添加电影名、导演名、演员名等
        """

        # 对 summary 进行分词
        if 'summary' in document:
            words = jieba.lcut_for_search(document['summary'])
        else:
            words = []

        # 对标题进行分词
        extra_words = jieba.lcut_for_search(document['name'])

        # 对导演名进行分词
        for director in document['directors']:
            extra_words.extend(jieba.lcut_for_search(director))

        # 对演员名进行分词
        for actor in document['actors']:
            extra_words.extend(jieba.lcut_for_search(actor))

        words.extend(extra_words)

        words = filter(match_words, words)

        return words

    def count_words(self, document):
        """
        对完成分词后的文档进行词频统计
        """

        result_dict = {}

        words = self.cut_document(document)
        for word in words:
            word = word.strip()
            if word not in result_dict:
                result_dict[word] = 1
            else:
                result_dict[word] += 1

        with open('../data/result', 'a') as file_out:
            for k, v in result_dict.items():
                file_out.write(f'{k}\t{document["douban_id"]}\t{v}\n')

    def process_all_document(self):
        docs = col.find()
        for i, doc in enumerate(docs):
            print(f'***** {i}.Handling {doc["name"]} *****')
            self.count_words(doc)

    @staticmethod
    def make_dictionary():
        print('***** Create Posting Index *****')
        word_dictionary = {}

        file_in = open('../data/result', 'r')
        line = file_in.readline()
        while line:
            items = line[:-1].split('\t')
            if items[0] not in word_dictionary:
                posting = [items[1], items[2]]
                val = [posting]
                word_dictionary[items[0]] = val
            else:
                posting = [items[1], items[2]]
                val = word_dictionary[items[0]]
                val.append(posting)
                word_dictionary[items[0]] = val

            line = file_in.readline()

        file_in.close()
        with open('../data/postings', 'wb') as f:
            pickle.dump(word_dictionary, f)


if __name__ == '__main__':
    indexer = Indexer()

    indexer.process_all_document()
    indexer.make_dictionary()
