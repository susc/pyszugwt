import bs4
import re
from szufunctions import szufunctions


def main():
    # 实例化函数类
    sf = szufunctions()
    # 公文通列表页
    index_url = 'https://www1.szu.edu.cn/board/'
    try:
        # 获取文章URL列表
        html = sf.gethtml(index_url)
        soup = bs4.BeautifulSoup(html, 'lxml')
        detail_url_base = 'https://www1.szu.edu.cn/board/'
        detail_urls = soup.find_all(href=re.compile("^view.asp"))
        # 循环解析列表中的URL
        for url in detail_urls:
            # 获取文章分类
            cate = url.parent.previous_sibling.previous_sibling.previous_sibling.previous_sibling.string.strip()
            # 获取发文单位
            unit = url.parent.previous_sibling.previous_sibling.string.strip()
            # 检测是否含有附件
            attachment = url.parent.next_sibling.next_sibling.contents
            if len(attachment):
                has_attachment = 1
            else:
                has_attachment = 0
            url = detail_url_base + url['href']
            sf.detailurlparser(cate, unit, url, has_attachment)
        # 保持运行
        main()
    # 出错时重试
    except Exception:
        print('UNKNOWN ERROR, retrying...')
        main()


if __name__ == '__main__':
  main()
