# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from .database import col


class DoubanmoviecrawlerPipeline:
    """
    数据保存到 MongoDB 中
    """

    @staticmethod
    def get_movie(item):
        return col.find_one({'douban_id': item['douban_id']})

    @staticmethod
    def save_movie(item):
        return col.insert_one(item)

    @staticmethod
    def update_movie(item):
        query = {'douban_id': item['douban_id']}
        return col.find_one_and_update(query, {'$set': item})

    def process_item(self, item, spider):
        exist = self.get_movie(item)
        if not exist:
            try:
                self.save_movie(dict(item))
            except Exception as e:
                print(item)
                print(e)
        else:
            self.update_movie(item)
