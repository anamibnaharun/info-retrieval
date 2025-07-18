# Information Retrieval - Practical Task 2
# Console Based user interface

import re
from test_wrapper import (
    load_documents_from_url,
    linear_boolean_search,
    remove_stopwords_by_list,
    remove_stopwords_by_frequency,
    vector_space_search
)

documents = []

def print_menu():
    print("\n=== Information Retrieval System Practical Task 2 ===")
    print("1. Download and parse document collection")
    print("2. Search documents (1-word Boolean query)")
    print("3. Remove stop words (from list)")
    print("4. Remove stop words (by frequency)")
    print("5. Search (Boolean or VSM, all options)")
    print("6. Exit")

def handle_download():
    url = input("Enter the URL of the .txt file: ").strip()
    author = input("Enter author name: ").strip()
    origin = input("Enter source/origin title: ").strip()
    start_line = int(input("Start reading from line: "))
    end_line = int(input("End reading at line: "))

    print("Enter the regular expression for extracting stories.")
    print("Example (title-body capture): r'Title: (.*?)\\n(.*?)(?=Title:|\\Z)'")
    # pattern_str = input("Regex pattern: ").strip()
    pattern_str = r'([^\n]+)\n\n(.*?)(?=\n{5}(?=[^\n]+\n\n))'
    search_pattern = re.compile(pattern_str, re.DOTALL)

    global documents
    documents = load_documents_from_url(url, author, origin, start_line, end_line, search_pattern)
    print(f"\n Loaded {len(documents)} documents.\n")

def ensure_public_filtered_terms(docs):
    for doc in docs:
        if not hasattr(doc, 'filtered_terms') and hasattr(doc, '_filtered_terms'):
            doc.filtered_terms = doc._filtered_terms

def handle_search():
    if not documents:
        print("No documents loaded. Please load a collection first.")
        return
    ensure_public_filtered_terms(documents)

    term = input("Enter search term: ").strip()
    stop_filtered = input("Use stopword-filtered terms? (y/n): ").strip().lower() == "y"
    results = linear_boolean_search(term, documents, stop_filtered)
    matches = [doc for score, doc in results if score == 1]
    print(f"\n🔍 Found {len(matches)} matching documents:\n")
    for doc in matches:
        print(f"- [{doc.document_id}] {doc.title}")

def handle_stopwords_list():
    if not documents:
        print("Load documents first.")
        return
    path = input("Enter stopword list file path: ").strip()
    try:
        with open(path, 'r') as f:
            stopwords = set(line.strip().lower() for line in f)
        for doc in documents:
            remove_stopwords_by_list(doc, stopwords)
        print("Stopword filtering applied to all documents (list-based).")
    except FileNotFoundError:
        print("File not found.")

def handle_stopwords_frequency():
    if not documents:
        print("Load documents first.")
        return
    high = float(input("Enter high-frequency cutoff (e.g., 0.05): "))
    low = float(input("Enter low-frequency cutoff (e.g., 0.0005): "))
    for doc in documents:
        remove_stopwords_by_frequency(doc, documents, common_frequency=high, rare_frequency=low)
    print("Stopword filtering applied to all documents (frequency-based).")



# --- Task 3 full search with evaluation ---

def load_ground_truth(filepath):
    with open(filepath, 'r') as f:
        ids = set(int(line.strip()) for line in f if line.strip().isdigit())
    return ids

def handle_eval_search():
    if not documents:
        print("No documents loaded. Please load a collection first.")
        return
    ensure_public_filtered_terms(documents)
    query = input("Enter search query (1+ terms): ").strip()
    stopword_filtered = input("Use stopword-filtered terms? (y/n): ").strip().lower() == "y"
    stemmed = input("Use stemming? (y/n): ").strip().lower() == "y"
    search_method = input("Search method - (b)oolean or (v)sm: ").strip().lower()
    if search_method == "v":
        results = vector_space_search(query, documents, stopword_filtered=stopword_filtered, stemmed=stemmed)
        matches = [doc for score, doc in results if score > 0]
        matches = sorted(matches, key=lambda d: next(s for s, doc in results if doc == d), reverse=True)
    else:
        results = linear_boolean_search(query, documents, stopword_filtered=stopword_filtered, stemmed=stemmed)
        matches = [doc for score, doc in results if score == 1]
    print(f"\n🔍 Found {len(matches)} matching documents:\n")
    for doc in matches:
        print(f"- [{doc.document_id}] {doc.title}")
    gt_path = input("Ground truth file (leave blank to skip eval): ").strip()
    if gt_path:
        try:
            ground_truth = load_ground_truth(gt_path)
            retrieved = set(doc.document_id for doc in matches)
            from my_module import precision_recall
            precision, recall = precision_recall(retrieved, ground_truth)
            print(f"\nPrecision: {precision:.4f}, Recall: {recall:.4f}")
        except Exception as e:
            print(f"Could not evaluate: {e}")
    else:
        print("(No ground truth file provided; skipping evaluation.)")





def main():
    while True:
        print_menu()
        choice = input("Choose an option (1–6): ").strip()
        if choice == "1":
            handle_download()
        elif choice == "2":
            handle_search()
        elif choice == "3":
            handle_stopwords_list()
        elif choice == "4":
            handle_stopwords_frequency()
        elif choice == "5":
            handle_eval_search()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
