import os
import re

from test_wrapper import (
    linear_boolean_search,
    load_documents_from_url,
    remove_stopwords_by_frequency,
    remove_stopwords_by_list,
)


def print_menu():
    print("\nMenu:")
    print("1. Load documents from URL")
    print("2. Remove stopwords")
    print("3. Search documents")
    print("4. Exit")


def main():
    docs = []
    stopwords = set()
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            url = input("Enter URL: ")
            author = input("Enter author name: ")
            origin = input("Enter collection title: ")
            start_line = int(input("Start line number: "))
            end_line = int(input("End line number: "))
            pattern_str = input(
                "Enter regex pattern with two capture groups (title and text): "
            )
            try:
                pattern = re.compile(pattern_str)
                docs = load_documents_from_url(
                    url, author, origin, start_line, end_line, pattern
                )
                print(f"Loaded {len(docs)} documents.")
            except re.error:
                print("Invalid regex pattern.")

        elif choice == "2":
            if not docs:
                print("No documents loaded. Please load documents first.")
                continue
            print("\nSelect stopword removal method:")
            print("1. List-based (load from file)")
            print("2. Frequency-based (common/rare thresholds)")
            method = input("Enter method (1/2): ").strip()
            if method == "1":
                path = input("Enter stopword file path (relative or absolute): ")
                # expand '~' and normalize separators for portability
                path = os.path.expanduser(path)
                path = os.path.normpath(path)
                try:
                    with open(path, "r") as f:
                        stopwords = {
                            line.strip().replace(" ", "") for line in f if line.strip()
                        }
                except Exception as e:
                    print(f"Error reading stopword file: {e}")
                    continue
                for doc in docs:
                    remove_stopwords_by_list(doc, stopwords)
                print("Stopwords have been removed (list-based).")
            elif method == "2":
                try:
                    common = float(
                        input("Enter common frequency threshold (e.g. 0.9): ")
                    )
                    rare = float(input("Enter rare frequency threshold (e.g. 0.2): "))
                except ValueError:
                    print("Invalid frequency values.")
                    continue
                for doc in docs:
                    remove_stopwords_by_frequency(doc, docs, common, rare)
                print("Stopwords have been removed (frequency-based).")
            else:
                print("Invalid method selection.")

        elif choice == "3":
            if not docs:
                print("No documents loaded. Please load documents first.")
                continue
            term = input("Enter search term: ").strip()
            use_filtered = input("Use filtered terms? (y/n): ").lower() == "y"
            results = linear_boolean_search(term, docs, stopword_filtered=use_filtered)
            if not results:
                print("No matching documents found.")
            else:
                print(f"Found {len(results)} documents:")
                for score, doc in results:
                    print(f"{doc} - score: {score}")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
