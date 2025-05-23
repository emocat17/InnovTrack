from datetime import datetime
import requests
import feedparser
import pandas as pd
import os
import re
from concurrent.futures import ThreadPoolExecutor

def clean_filename(title):
    illegal_chars_pattern = r'[\\/:*?"<>|\n]'
    safe_title = re.sub(illegal_chars_pattern, ' ', title)
    return safe_title

def download_pdf(pdf_url, title, year, quarter):
    quarter_dir = os.path.join(keyword, str(year), f"Q{quarter}")
    if not os.path.exists(quarter_dir):
        os.makedirs(quarter_dir)

    safe_title = clean_filename(title)
    pdf_path = os.path.join(quarter_dir, f"{safe_title}.pdf")

    if os.path.exists(pdf_path):
        print(f'数据库中已存在文件: {pdf_path}')
        return

    response = requests.get(pdf_url)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    print(f'正在下载文件: {pdf_path}')

def fetch_papers(query, start_date, keyword):
    base_url = 'http://export.arxiv.org/api/query?'
    start = 0
    max_results = 500  # 增加每次请求的最大结果数
    data = []

    with ThreadPoolExecutor(max_workers=10) as executor:  # 使用线程池来并行下载
        while True:
            params = {
                'search_query': query,
                'start': start,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'ascending'
            }
            response = requests.get(base_url, params=params)
            feed = feedparser.parse(response.content)

            if not feed.entries:
                break

            for entry in feed.entries:
                published_date = datetime.strptime(entry.published.split('T')[0], '%Y-%m-%d')
                if published_date < start_date:
                    continue
                if published_date > datetime.now():
                    break

                year = published_date.year
                quarter = (published_date.month - 1) // 3 + 1

                pdf_link = next((link.href for link in entry.links if 'title' in link and link.title.lower() == 'pdf'), None)

                if pdf_link:
                    executor.submit(download_pdf, pdf_link, entry.title, year, quarter)

                data.append({
                    '发布日期': entry.published,
                    '标题': entry.title,
                    '作者': ', '.join(author.name for author in entry.authors),
                    '摘要': entry.summary,
                    '链接': entry.link,
                    'PDF链接': pdf_link
                })

            start += len(feed.entries)
            print(f"Fetching next set of results from {start}...")
    return data

# 用户输入关键字
#keyword = input("请输入搜索关键字: ")
keyword = "zero trust"

# 创建以关键字命名的文件夹
if not os.path.exists(keyword):
    os.makedirs(keyword)

# search keywords and start date
query = f'all:"{keyword}"'
start_date = datetime(2020, 1, 1)

papers_data = fetch_papers(query, start_date, keyword)

# 保存到Excel表格
excel_filename = os.path.join(keyword, f"{keyword}_papers.xlsx")
df = pd.DataFrame(papers_data)
df.to_excel(excel_filename, index=False)

print(f"爬取完成，Excel表格已保存至 {excel_filename}")
