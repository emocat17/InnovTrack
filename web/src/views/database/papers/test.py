import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件所在的目录
current_dir = os.path.dirname(current_file_path)

# 计算Data文件夹的路径（假设它在当前文件上五级目录下）
data_folder_path = os.path.join(current_dir, *(os.pardir,) * 5, 'Data')

# 检查Data文件夹是否存在
if os.path.isdir(data_folder_path):
    # 读取Data文件夹下的文件列表
    files = os.listdir(data_folder_path)
    print("Files in the Data directory:", files)
else:
    print("The Data directory does not exist.")
