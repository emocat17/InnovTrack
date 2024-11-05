# app/controllers/arxiv_data.py
import os
import pandas as pd
from fastapi import HTTPException

class ArxivData:
    @staticmethod
    async def read_arxiv_data(keyword: str):
        # 假设Data文件夹下的结构是 Data/{keyword}/{keyword}_papers.xlsx
        folder_path = os.path.join('Data', keyword)
        excel_filename = f"{keyword}_papers.xlsx"
        excel_path = os.path.join(folder_path, excel_filename)

        if not os.path.exists(excel_path):
            raise HTTPException(status_code=404, detail="文件未找到")

        # 使用 pandas 读取 Excel 文件
        try:
            df = pd.read_excel(excel_path)
            # 将 DataFrame 转换为字典列表返回
            return df.to_dict(orient='records')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取文件出错: {str(e)}")
        
arxiv_data = ArxivData()
