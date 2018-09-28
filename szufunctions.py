import os
import bs4
import re
import requests
import szumysql


class szufunctions:
    # 给定一个URL，获取其HTML源码
    def gethtml(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
        s = requests.session()

        request = s.get(url, headers=headers)
        request.encoding = 'gbk'
        html = request.text
        return html

    # 下载附件
    def downloadattachments(self):
        # 构造请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'
        }
        html = self.gethtml(self.url)
        soup = bs4.BeautifulSoup(html, 'lxml')
        tds = soup.find_all('td', attrs={'style': "font-size: 9pt"})
        base_url = 'https://www1.szu.edu.cn/board/'
        for td in tds:
            if '附件' in str(td.contents):
                links = td.find_all('a')
                for a in links:
                    # 构造下载链接
                    download_url = base_url + a['href']
                    download_r = requests.get(download_url, headers=headers)
                    # 构造保存路径
                    download_path = '.\\attachments\\{}\\{}\\'.format(self.urlid, str(self.version))
                    file_name = a.string.strip('·')
                    # 如果路径不存在则创建
                    if not os.path.exists(download_path):
                        os.makedirs(download_path)
                    # 将内容写入文件
                    complete_path = download_path + file_name
                    if not os.path.exists(complete_path):
                        with open(complete_path, 'wb') as f:
                            f.write(download_r.content)
                        print('附件下载成功：URL id:{}, 文章版本:{}, 标题:{}, 文件名:{}'.format(self.urlid, self.version, self.title, file_name))
                    else:
                        print('文件名为 {} 的文件已存在，跳过'.format(file_name))

    # 获取URL id
    def geturlid(self, url):
        urlidcom = re.compile(r'id=([\d]+)')
        return urlidcom.findall(url)[0]

    # 获取标题
    def gettitle(self, html):
        soup = bs4.BeautifulSoup(html, 'lxml')
        html_title_list = soup.find_all('font', attrs={'size': '4'})
        titles = html_title_list[0].children
        for child in titles:
            if child.string != '　':
                return child.string.strip()

    # 获取发布时间
    def getreleasetime(self, html):
        soup = bs4.BeautifulSoup(html, 'lxml')
        html_releasetime_list = soup.find_all('font', attrs={'color': '#808080'})
        for releasetimes in html_releasetime_list:
            rtcom = re.compile(r'([\d]*-[\d]*-[\d]*\s.*)')
            try:
                return rtcom.findall(releasetimes.string.strip())[0]
                # 获取了第一个font元素就break，防止匹配多个
                break
            except Exception:
                print('获取发布时间出错！URL:', url)

    # 获取更新时间和点击数
    def getutandcl(self, html):
        soup = bs4.BeautifulSoup(html, 'lxml')
        utandcl = re.compile(r'([\d]+-[\d]+-[\d]+\s[\d]+:[\d]+:[\d]+).*:([\d]+)')
        m = utandcl.findall(
            soup.find('td', attrs={'align': 'right', 'valign': 'bottom', 'height': '40'}).string.strip())
        return m[0][0], m[0][1]

    # 获取正文内容（HTML源码）
    def getcontent(self, html):
        soup = bs4.BeautifulSoup(html, 'lxml')
        content_wrap = soup.find('td', attrs={'height': '90', 'valign': 'top'})
        # 去除外包的[]
        stripped_content = str(content_wrap.contents).strip('[]')
        # 去除内含的 , '\n',
        strcom = re.compile(r",\s'\\n',\s")
        fixed_content = re.sub(strcom, '', stripped_content)
        # 去除结尾的, 'EndFragment'
        strcom = re.compile(r",\s'EndFragment'")
        fixed_content = re.sub(strcom, '', fixed_content)
        return fixed_content

    def detailurlparser(self, cate, unit, url, has_attachment):
        # 分类
        self.cate = cate
        # 单位
        self.unit = unit
        # URL
        self.url = url
        # 发布时间
        self.releasetime = ''
        # 更新时间
        self.updatetime = ''
        # 点击数
        self.clickcount = ''
        # 标题
        self.title = ''
        # URL id
        self.urlid = ''
        # 版本号
        self.version = 1
        # 正文内容
        self.content = ''
        # 获取URL id
        self.urlid = self.geturlid(url)
        # 获取详情页HTML源代码
        self.html = self.gethtml(url)
        # 获取发布时间
        self.releasetime = self.getreleasetime(self.html)
        # 获取更新时间和点击数
        self.updatetime, self.clickcount = self.getutandcl(self.html)
        # 获取标题
        self.title = self.gettitle(self.html)
        # 获取正文内容
        self.content = self.getcontent(self.html)
        # 判断URL id对应记录是否存在
        if szumysql.isurlidexists(self.urlid):
            # 判断文章是否更新
            if szumysql.isupdated(self.urlid, self.updatetime):
                max_version = szumysql.getmaxversion(self.urlid)
                self.version = int(max_version) + 1
                # 有附件则下载
                if has_attachment == 1:
                    self.downloadattachments()
                szumysql.insert_detail(self.urlid, self.version, self.title, self.updatetime, self.content)
                print('更新文章成功：URL id:{}, 标题:{}, 最新版本号:{}'.format(self.urlid, self.title, self.version))
            # 无论文章是否更新，更新点击数
            max_version = szumysql.getmaxversion(self.urlid)
            self.version = max_version
            # 有附件则下载
            if has_attachment == 1:
                self.downloadattachments()
            szumysql.update_clickcount(self.urlid, self.clickcount)
            print('更新点击数成功：URL id:{}, 标题:{}, 当前点击数:{}'.format(self.urlid, self.title, self.clickcount))
        else:
            # 有附件则下载
            if has_attachment == 1:
                self.downloadattachments()
            szumysql.insert_base(self.urlid, self.url, self.cate, self.unit, self.releasetime, self.clickcount)
            szumysql.insert_detail(self.urlid, self.version, self.title, self.updatetime, self.content)
            print('插入文章成功：URL id:{}, 标题:{}'.format(self.urlid, self.title))
