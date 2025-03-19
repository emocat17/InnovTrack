# app/controllers/
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

def download_pdf(pdf_url, title, year, quarter, keyword):
    # 在 Data/keyword/papers/ 目录下创建文件夹结构
    papers_dir = os.path.join('Data', keyword, 'papers', str(year), f"Q{quarter}")
    if not os.path.exists(papers_dir):
        os.makedirs(papers_dir)
    
    safe_title = clean_filename(title)
    pdf_path = os.path.join(papers_dir, f"{safe_title}.pdf")

    if os.path.exists(pdf_path):
        return f'文件已存在: {pdf_path}'
    
    response = requests.get(pdf_url)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    print(f'正在下载文件: {pdf_path}')
    return f'正在下载文件: {pdf_path}'

def fetch_papers(query, start_date, keyword):
    base_url = 'http://export.arxiv.org/api/query?'
    start = 0
    max_results = 1000 #一次性爬取的最大数目
    data = []
    with ThreadPoolExecutor(max_workers=10) as executor: #并发线程
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
                # 提取并格式化发布日期，只保留日期部分
                published_date = datetime.strptime(entry.published.split('T')[0], '%Y-%m-%d')
                if published_date < start_date:
                    continue
                if published_date > datetime.now():
                    break

                year = published_date.year
                quarter = (published_date.month - 1) // 3 + 1

                pdf_link = next((link.href for link in entry.links if 'title' in link and link.title.lower() == 'pdf'), None)
                if pdf_link:
                    download_message = download_pdf(pdf_link, entry.title, year, quarter, keyword)

                data.append({
                    # 将日期格式化为仅包含年-月-日
                    '发布日期': published_date.strftime('%Y-%m-%d'),
                    '标题': entry.title,
                    '作者': ', '.join(author.name for author in entry.authors),
                    '摘要': entry.summary,
                    '链接': entry.link,
                    'PDF链接': pdf_link
                })

            start += len(feed.entries)

    # 按照发布日期从最新到最老排序数据
    data.sort(key=lambda x: x['发布日期'], reverse=True)
    
    return data

class ArxivSpider:
    @staticmethod
    async def fetch_arxiv_data(keyword):
        if not os.path.exists('Data'):
            os.makedirs('Data')
        
        # 在 Data/keyword 下创建 papers 文件夹
        keyword_dir = os.path.join('Data', keyword)
        os.makedirs(keyword_dir, exist_ok=True)  # 使用exist_ok简化目录创建

        papers_dir = os.path.join(keyword_dir, 'papers')
        if not os.path.exists(papers_dir):
            os.makedirs(papers_dir)

        query = f'all:"{keyword}"'
        start_date = datetime(2000, 1, 1)
        papers_data = fetch_papers(query, start_date, keyword)
        
        # 将数据转换为 DataFrame 并保存为 Excel 文件
        excel_filename = os.path.join(papers_dir, f"{keyword}_papers.xlsx")
        df = pd.DataFrame(papers_data)
        df.to_excel(excel_filename, index=False)
        print(f"爬取完成，Excel表格已保存至 {excel_filename}")
        return f"爬取完成，Excel表格已保存至 {excel_filename}"
    
arxiv_spider = ArxivSpider()
