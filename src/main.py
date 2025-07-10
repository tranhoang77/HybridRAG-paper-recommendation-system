import os
import csv
from dotenv import load_dotenv
from process import System
from hybrid_search import HybridSearcher
from send_email import GmailMailer
from download_paper import ArxivPaperDownloader

load_dotenv()
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "papers")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")

if __name__ == "__main__":
    data_dir = 'data/arxiv_papers'
    user_info = 'data/user/infor.csv'
    downloader = ArxivPaperDownloader(data_dir,4)
    #downloader.run()
    
    # Initialize the system
    rag_system = System(collection_name=MILVUS_COLLECTION, openai_api_key=OPENAI_API_KEY, openai_model=OPENAI_MODEL)
    
    # Example usage
    print("\n" + "="*60)
    print("ENHANCED PAPER RAG SYSTEM")
    print("="*60)
    
    paper_list = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.pdf')]
    if not paper_list:
        print("No PDF papers found in the specified directory.")
        exit(1)
    rag_system.process_paper(paper_list, downloader)
    print("\nAll papers processed and stored in the vector database.")
    
    #search
    css_style = """
    <style>
      body { font-family: Arial, sans-serif; line-height: 1.5; }
      .paper-container {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 12px;
          margin-bottom: 20px;
          background-color: #f9f9f9;
      }
      .paper-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px; }
      .paper-novelty { font-size: 14px; font-style: italic; color: #555; margin-bottom: 8px; }
      .paper-content { font-size: 14px; color: #444; white-space: pre-wrap; }
    </style>
    """
    
    mailer = GmailMailer()
    searcher = HybridSearcher(collection_name=MILVUS_COLLECTION, openai_api_key=OPENAI_API_KEY, openai_model=OPENAI_MODEL)
    with open(user_info, mode='r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Name']
            email = row['email']
            topic = row['topic']
            results = searcher.search(topic, top_k=10)

            papers_html_fragment = mailer.format_results_fragment(results)

            html_body = f"""
            <html>
            <head>
              <meta charset="UTF-8">
              {css_style}
            </head>
            <body>
              <p>Xin chào <strong>{name}</strong>!</p>
              <p>Dưới đây là tóm tắt paper liên quan đến từ khóa: <em>{topic}</em>.</p>
              {papers_html_fragment}
              <p>Trân trọng,<br>Đội ngũ Summary Paper</p>
            </body>
            </html>
            """

            # Send email
            success = mailer.send_email_html(
                recipient_email=email,
                subject="Thông báo paper mới",
                html_content=html_body
            )
            if not success:
                print(f"[ERROR] Gửi email cho {email} thất bại.")
 