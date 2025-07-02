from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import json
from pathlib import Path


def build_rag_store(examples):
    print("Building Rag store....")
    docs = load_docs_from_labeled_json(examples)
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(docs, embeddings)


def load_docs_from_labeled_json(json_path: str) -> list[Document]:
    with open(json_path, "r") as f:
        data = json.load(f)

    all_docs = []

    for label, examples in data.items():
        for entry in examples:
            file_path = Path(entry["formatted_file_path"])
            comments = entry.get("comments", [])

            print("Encoding file: ", file_path)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8").strip()
                doc = Document(
                    page_content=content,
                    metadata={
                        "label": label,  # "Good" or "Bad"
                        "comments": comments,
                        "source": str(file_path)
                    }
                )
                all_docs.append(doc)
            else:
                print(f"⚠️ Warning: File not found: {file_path}")
    
    return all_docs


