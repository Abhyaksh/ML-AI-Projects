from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def build_vector_store(
    docs_folder="docs",
    index_folder="faiss_index"
):
    """
    Build FAISS vector database from text documents.
    """

    # Load documents
    loader = DirectoryLoader(
        docs_folder,
        glob="*.txt",
        loader_cls=TextLoader
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} documents")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # Embedding Model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create FAISS
    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    # Save Index
    vectorstore.save_local(index_folder)

    print("✅ FAISS Vector Store Created Successfully!")

    return vectorstore


# ---------------------------------
# Run directly
# ---------------------------------

if __name__ == "__main__":

    build_vector_store()