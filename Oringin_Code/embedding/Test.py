import nest_asyncio
import time
import os
import json
import openai
from llama_index.core import VectorStoreIndex, Settings
from llama_parse import LlamaParse
from llama_parse.base import ResultType
from llama_index.core.node_parser import MarkdownElementNodeParser

# Apply nest_asyncio to allow event loop nesting
nest_asyncio.apply()

# 设置 OpenAI API 密钥
OPENAI_API_KEY = "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"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 设置 OpenAI GPT 为 LLM
openai.api_key = OPENAI_API_KEY

# 设置工作目录为项目根目录
os.chdir('D:/GitWork/InnovTrack')

# 使用相对路径加载 PDF 文档
pdf_file_name = './Data/chinese_pdf.pdf'

# 设置 LlamaParse 参数
parser = LlamaParse(
    result_type=ResultType.MD,
    language='ch_sim',  # 使用简体中文
    api_key="llx-1qBHA8mqvduJQXTz4VvEdLAZxnI39alxQdx44rR20caeTzwq",  # 提供 LlamaCloud API 密钥
    verbose=True,
    num_workers=1,
)

# 加载 PDF 数据
documents = parser.load_data(pdf_file_name)

# 检查加载的文档
print(f"Number of documents: {len(documents)}")

for doc in documents:
    print(doc.doc_id)
    print(doc.text[:500] + '...')

# 使用 MarkdownElementNodeParser 解析文档
node_parser = MarkdownElementNodeParser(llm=None, num_workers=2)
nodes = node_parser.get_nodes_from_documents(documents)

# 将节点转换为对象
base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

# 检查解析的节点对象
print(f"Number of nodes: {len(base_nodes)}")

TABLE_REF_SUFFIX = '_table_ref'
TABLE_ID_SUFFIX  = '_table'

# 检查解析的对象
print(f"Number of objects: {len(objects)}")

# 遍历所有节点对象并检查其内容
for node in objects:
    print(f"id:{node.node_id}")
    print(f"hash:{node.hash}")
    print(f"parent:{node.parent_node}")
    print(f"prev:{node.prev_node}")
    print(f"next:{node.next_node}")

    # 如果是表格对象
    if node.node_id[-len(TABLE_REF_SUFFIX):] == TABLE_REF_SUFFIX:
        if node.next_node is not None:
            next_node = node.next_node
            print(f"next_node metadata:{next_node.metadata}")

            # Safely access metadata and avoid errors
            try:
                obj_metadata = json.loads(str(next_node.json()))
                print(f"def:{obj_metadata['metadata']['table_df']}")
                print(f"summary:{obj_metadata['metadata']['table_summary']}")
            except KeyError as e:
                print(f"KeyError: Missing expected metadata key - {e}")

    print(f"next:{node.next_node}")
    print(f"type:{node.get_type()}")
    print(f"class:{node.class_name()}")
    print(f"content:{node.get_content()[:200]}")
    print(f"metadata:{node.metadata}")
    print(f"extra:{node.extra_info}")

    node_json = json.loads(node.json())

    print(f"start_idx:{node_json.get('start_char_idx')}")
    print(f"end_idx:{node_json['end_char_idx']}")

    if 'table_summary' in node_json:
        print(f"summary:{node_json['table_summary']}")
    print("=====================================")

