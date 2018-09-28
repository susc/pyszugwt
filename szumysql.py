import pymysql
import datetime


# 判断URL id对应的记录是否存在
def isurlidexists(urlid):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    sql = r"SELECT * FROM `base` WHERE `urlid` = {}".format(str(urlid))
    cursor.execute(sql)
    result = cursor.fetchone()
    db.close()
    return result is not None


# 判断文章是否更新
def isupdated(urlid, updatetime):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    sql = r"SELECT `updatetime`, `version` FROM `detail` WHERE `urlid` = {} ORDER BY `version` ASC".format(str(urlid))
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        max_version = 1
        for result in results:
            if result[1] > max_version:
                max_version = result[1]
            dbupdatetime = result[0]
        updatetime = datetime.datetime.strptime(updatetime, "%Y-%m-%d %H:%M:%S")
        diff = updatetime - dbupdatetime
        return diff.seconds != 0
    except Exception:
        print('ERROR in isupdated, SQL:', sql)
    db.close()


# 获取URL id对应内容最大版本号
def getmaxversion(urlid):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    sql = r"SELECT `version` FROM `detail` WHERE `urlid` = {} ORDER BY `version` DESC".format(str(urlid))
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        max_version = result[0]
        return max_version
    except Exception:
        print('ERROR in getmaxversion, SQL:', sql)
    db.close()


# 向base表中插入记录
def insert_base(urlid, url, cate, unit, releasetime, clickcount):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    url = pymysql.escape_string(url)
    sql = r"INSERT INTO `base` (`sysid`, `urlid`, `url`, `cate`, `unit`, `releasetime`, `clickcount`) VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}')".format(urlid, url, cate, unit, releasetime, clickcount)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception:
        print('ERROR in insert_base, SQL:', sql)
        db.rollback()
    db.close()


# 向detail表中插入记录
def insert_detail(urlid, version, title, updatetime, content):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    content = pymysql.escape_string(str(content))
    sql = r"INSERT INTO `detail` (`sysid`, `urlid`, `version`, `title`, `updatetime`, `content`) VALUES (NULL, '{}', '{}', '{}', '{}', '{}')".format(urlid, version, title, updatetime, content)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception:
        print('ERROR in insert_detail, SQL:', sql)
        db.rollback()
    db.close()


# 更新点击数
def update_clickcount(urlid, clickcount):
    db = pymysql.connect('127.0.0.1', 'alpha', 'alpha520', 'szugwt')
    cursor = db.cursor()
    sql = r"UPDATE `base` SET `clickcount` = '{}' WHERE `base`.`urlid` = {}".format(clickcount, urlid)
    try:
        cursor.execute(sql)
        db.commit()
    except Exception:
        print('ERROR in update_clickcount, SQL:', sql)
        db.rollback()
    db.close()
