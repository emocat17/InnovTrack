import os
import json
import time
from zhipuai import ZhipuAI
from pathlib import Path
import sys

# 填写您的API Key
client = ZhipuAI(api_key="af8ccdc4e0697edc168bdf43415a22e1.vfsnxMp5H9QB1uQH")


# 删除已有的 "file-extract" 的文件
try:
    # 请求文件列表，筛选出 purpose 为 "file-extract" 的文件
    result = client.files.list(purpose="file-extract")
    file_list = result.data  # 获取 data 列表，其中包含每个文件的详细信息

    print("准备删除的 file-extract 文件：")

    # 遍历文件列表，逐个删除
    for file in file_list:
        file_id = file.id
        filename = file.filename

        # 删除该文件
        delete_result = client.files.delete(file_id=file_id)
        print(f"已删除 file-extract 文件 - 文件名: {filename}, 文件ID: {file_id}, 删除结果: {delete_result}")

except Exception as e:
    print(f"出现错误: {e}")


def get_pdf_files_and_names(folder_path):
    pdf_paths = []
    pdf_names = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_paths.append(os.path.join(root, file))
                pdf_names.append(file.split(".pdf")[0])
    return pdf_paths, pdf_names


folder_path = "C:\\Users\\yry\\Desktop\\zero trust(arxiv)"  # 替换为文件夹路径
pdf_paths, pdf_names = get_pdf_files_and_names(folder_path)
print("PDF 文件路径：", pdf_paths)
print("PDF 文件名：", pdf_names)

output_filename = "extracted_content.txt"  # 输出文件名

# print(len(pdf_paths))
# for i in range(len(pdf_names)):
#     if(pdf_names[i] == "LIPSTICK  Corruptibility-Aware and Explainable Graph Neural   Network-based Oracle-Less Attack on Logic Locking"):
#         print(i)
#         break

#批量上传文件并提取文本内容
for idx, file_path in enumerate(pdf_paths, start=0):
    if idx >= len(pdf_paths):
        print("发送数据完毕，程序结束。")
        sys.exit()
    retries = 3  # 最大重试次数e
    for attempt in range(retries):
        try:
            # 上传PDF文件并提取内容
            file = client.files.create(file=Path(file_path), purpose="file-extract")
            content = json.loads(client.files.content(file.id).content)["content"]

            # 创建分析请求内容
            message_content = (
                    "请对以下论文进行分析，并按点回答，给出序号，"
                    "1. 请提炼一下这篇文章的核心观点。 "
                    "2. 这篇文章的主题是什么？ "
                    "3. 作者在哪些方面提供了新颖的见解？ "
                    "4. 这篇文章主要采用了什么研究方法？ "
                    "5. 文献中的数据支持了哪些观点？ "
                    "6. 作者使用了哪些重要论据来支持观点？ "
                    "7. 这篇文章对该领域有何贡献？ "
                    "8. 能帮我找出文献的论文陈述吗？ "
                    "9. 这篇文章的主要结论是什么？：\n\n"
                    + "".join(content)
            )

            # 调用API生成综述
            response = client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": message_content}]
            )

            # 获取并处理API响应
            content_text = response.choices[0].message.content

            # 使用不同的变量名来避免与API文件对象冲突
            with open(output_filename, "a", encoding="utf-8") as output_file:
                output_file.write(pdf_names[idx] + "\n" + content_text + "\n\n")

            print(f"数据已追加到 TXT 文件：{pdf_names[idx]}")

            # 删除已上传的 `file-extract` 文件
            client.files.delete(file.id)
            print(f"文件 {file.id} 已删除")

            break  # 成功完成后跳出重试循环

        except Exception as e:
            print(f"尝试 {attempt + 1} 时出错: {e}")
            if attempt < retries - 1:  # 如果还没达到最大重试次数，延迟后重试
                time.sleep(2)  # 延迟2秒
            else:
                print(f"文件 {pdf_names[idx]} 的处理失败，已达到最大重试次数。")
