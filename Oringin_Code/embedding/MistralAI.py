import nest_asyncio
nest_asyncio.apply()

import os

# API access to llama-cloud
LLAMA_CLOUD_API_KEY = "llx-1qBHA8mqvduJQXTz4VvEdLAZxnI39alxQdx44rR20caeTzwq"
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY

# 使用你的 MISTRAL_API_KEY 和 OPENAI_API_KEY
MISTRAL_API_KEY = "KWTv8FvTh4kOZ5Hgpihbfaev4zvQ6L44"
OPENAI_API_KEY = "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"

from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings

EMBEDDING_MODEL  = "mistral-embed"
GENERATION_MODEL = "open-mistral-7b"

llm = MistralAI(model=GENERATION_MODEL, api_key=MISTRAL_API_KEY)

Settings.llm = llm

from llama_parse import LlamaParse
from llama_parse.base import ResultType

# 设置工作目录为项目根目录
os.chdir('D:/GitWork/InnovTrack')

# 使用相对路径
pdf_file_name = './Data/chinese_pdf.pdf'

# 传递 API 密钥
parser = LlamaParse(
    result_type=ResultType.MD,
    language='ch_sim',  # 使用简体中文
    api_key=LLAMA_CLOUD_API_KEY,  # 提供 API 密钥
    verbose=True,
    num_workers=1,
)

documents = parser.load_data(pdf_file_name)

# 检查加载的文档
print(f"Number of documents: {len(documents)}")

for doc in documents:
    print(doc.doc_id)
    print(doc.text[:500] + '...')

# Parse the documents using MarkdownElementNodeParser

from llama_index.core.node_parser import MarkdownElementNodeParser

node_parser = MarkdownElementNodeParser(llm=llm, num_workers=2)
nodes = node_parser.get_nodes_from_documents(documents)

# Convert nodes into objects
base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

import json


# Check parsed node objects 
print(f"Number of nodes: {len(base_nodes)}")

TABLE_REF_SUFFIX = '_table_ref'
TABLE_ID_SUFFIX  = '_table'

# Check parsed objects 

print(f"Number of objects: {len(objects)}")

for node in objects: 
    print(f"id:{node.node_id}")
    print(f"hash:{node.hash}")
    print(f"parent:{node.parent_node}")
    print(f"prev:{node.prev_node}")
    print(f"next:{node.next_node}")

    # Object is a Table
    if node.node_id[-1 * len(TABLE_REF_SUFFIX):] == TABLE_REF_SUFFIX:

        if node.next_node is not None:
            next_node = node.next_node
        
            print(f"next_node metadata:{next_node.metadata}")
            print(f"next_next_node:{next_next_nod_id}")

            obj_metadata = json.loads(str(next_node.json()))

            print(str(obj_metadata))

            print(f"def:{obj_metadata['metadata']['table_df']}")
            print(f"summary:{obj_metadata['metadata']['table_summary']}")


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