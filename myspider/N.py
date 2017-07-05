# -*- coding: utf-8 -*-

# 定义映射
na_map = {
    'id': 'NEWSID',  # 新闻的ID
    't': 'NEWSTITLE',  # 标题
    'kw': 'KEYWORD',  # 关键字
    'd': 'DESCRIPTION',  # 摘要
    'm': 'MEDIA',  # 发表媒体
    'sm': 'SOURCEMEDIA',  # 转载媒体
    'pd': 'PUBDATE',  # 发表日期
    'c': 'CONTENT',  # 新闻内容
    'url': 'URL',  # 网页链接
    'fp': 'FILEPATH',  # 完整网页存储在本地的路径
    'site': 'WEBSITENAME',  # 保存网站名，方便分类检索
    'type': 'TYPE' # 分类
    # 'save': 'SAVEFLAG', # 设置时候将新闻的内容部分提取出来存在文件系统中
}

na_reverse_map = {
    'NEWSID': 'id',
    'NEWSTITLE': 't',
    'KEYWORD': 'kw',
    'DESCRIPTION': 'd',
    'MEDIA': 'm',
    'SOURCEMEDIA': 'sm',
    'PUBDATE': 'pd',
    'CONTENT': 'c',
    'URL': 'url',
    'FILEPATH': 'fp',
    'WEBSITENAME': 'site',
    # 'SAVEFLAG': 'save',
}

# 定义默认值
na_default = {
    'id': None,
    't': 'Not Found',
    'kw': 'Not Found',
    'un': 'Not Found',
    'm': 'Not Found',
    'sm': 'Not Found',
    'pd': '1900-01-01',
    'c': 'Not Found',
    'url': 'Not Found',
    'fp': None,
    # 'save': False,
}


# 将新闻内容存在本地的item净化后其他部分存储在数据库中
def cleanItem(item):
    del item[na_map['c']]
    return item


# 将抓取的新闻属性配置在config里面构造相应的Item并返回
def na(Item, config={}, options = {}):
    try:
        item = Item()
        fields = item.fields
        itemAttrChecker(fields, config)
        for fie in fields:
            key = na_reverse_map[fie]
            item[fie] = key in config and config[key] or na_default[key]
        return item
    except Exception, e:
        print Exception, e


def itemAttrChecker(fields, attrObj):
    for attr in attrObj:
        if not (attr in na_map and na_map[attr] in fields):
            err('please check the key: [' + attr + '], may be not exist.')


# 错误提示函数
def err(msg=''):
    raise Exception(msg)
