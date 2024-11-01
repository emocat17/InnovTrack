import requests
from bs4 import BeautifulSoup

class DocumentController:
    @staticmethod
    async def fetch_data():
        res = requests.get("https://www.tiobe.com/tiobe-index/")
        if res.status_code == 200:
            sp = BeautifulSoup(res.text, 'html.parser')
            best = sp.select('tbody tr td:nth-child(5)')
            if len(best) != 0:
                result = "TIOBE目前排名前10的编程语言是：\n" + "\n".join(
                    [f"Top {i+1}: {best[i].getText()}" for i in range(10)]
                )
                return result
        return result(content="获取数据失败")

document_controller = DocumentController()
