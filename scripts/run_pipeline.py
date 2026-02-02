from scripts.ingest_pdfs_to_mongo import ingest_all_pdfs
from scripts.chunks_to_es import index_all_documents

def main():
    print("\nSTEP 1 → Ingest PDFs to mongodb")
    ingest_all_pdfs()

    print("\nSTEP 2 → Index pending docs")
    index_all_documents()

    print("\nDONE ✓")

if __name__ == "__main__":
    main()
