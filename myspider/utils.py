# -*- coding:utf-8 -*-

import pymongo, logging
from myspider.config import DUPLICATE_FILTER_DB as DF
from myspider.config import MY_SPIDER_DB as SDB

df_collection = pymongo.MongoClient(DF['server'], DF['port'])[DF['db']][DF['collection']]


# 实现增量爬取， 如果该链接已经爬取则返回False
def duplicateFilter(options={}):
    url = options['url']
    site = options['site']
    count = df_collection.find({'url': url, 'site': site}).count()
    if count:
        logging.info(url + ' has been download, skip it.')
        return False
    else:
        df_collection.insert_one({'url': url, 'site': site})#插入数据库
        return True


def clearDB(sites=[], del_df=False):
    df_coll = pymongo.MongoClient(DF['server'], DF['port'])[DF['db']][DF['collection']]
    myspider_db = pymongo.MongoClient(SDB['server'], SDB['port'])[SDB['db']]

    # 清空duplicate数据库
    def delDF():
        df_coll.delete_many({})

    # 删除所有网站数据库
    def delAllSites():
        collections = myspider_db.collection_names()
        for coll in collections:
            myspider_db[coll].delete_many({})

    # 删除部分网站数据库
    def delManySites(list=[]):
        collections = myspider_db.collection_names()
        for l in list:
            if l in collections:
                coll = myspider_db[l]
                coll.delete_many({})

    if del_df:
        delDF()
    if 'all' in sites:
        delAllSites()
    else:
        delManySites(sites)


clearDB(['all'], True)
