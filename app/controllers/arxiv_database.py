# app/controllers/paper_database.py
import os
import pandas as pd
import logging

class ArxivDatabase:
    @staticmethod
    async def read_paper_data(keyword):
        # 获取文件夹路径
        data_folder = os.path.join('Data', keyword, 'papers')  # 修改此行
        logging.info(f"尝试访问文件夹路径: {data_folder}")
        
        # 确保文件夹存在
        if not os.path.exists(data_folder):
            logging.error(f"文件夹未找到: {data_folder}")
            raise FileNotFoundError(f"没有找到对应的文件夹: {data_folder}")

        # 精确匹配文件名
        expected_file_name = f"{keyword}_papers.xlsx"
        excel_file_path = os.path.join(data_folder, expected_file_name)
        logging.info(f"尝试读取文件: {excel_file_path}")

        if not os.path.exists(excel_file_path):
            logging.error(f"文件未找到: {excel_file_path}")
            raise FileNotFoundError(f"文件 {expected_file_name} 未找到在目录 {data_folder} 中")

        try:
            # 读取 xlsx 文件
            df = pd.read_excel(excel_file_path)
            logging.info("文件读取成功")
        except Exception as e:
            logging.error(f"读取 xlsx 文件时发生错误: {e}")
            raise Exception(f"读取 xlsx 文件时发生错误: {e}")

        # 将数据转换成字典格式并返回
        return df.to_dict(orient='records')

get_arxiv_database = ArxivDatabase()
