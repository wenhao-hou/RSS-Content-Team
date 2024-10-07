class KeywordIndex:
    def __init__(self, keyword_index):
        self.keyword_index = keyword_index

    def interactive_selection(self):
        while True:
            print("\nAvailable Keywords:")
            sorted_keywords = sorted(self.keyword_index.keys())
            for idx, keyword in enumerate(sorted_keywords, 1):
                print(f"{idx}. {keyword} ({len(self.keyword_index[keyword])} articles)")
            print("0. Exit")

            try:
                choice = input("\nSelect a keyword by number (or 0 to exit): ")
                if choice.lower() == 'exit' or choice == '0':
                    print("Exiting.")
                    break
                
                choice = int(choice)
                if 1 <= choice <= len(sorted_keywords):
                    selected_keyword = sorted_keywords[choice - 1]
                    relevant_articles = self.keyword_index[selected_keyword]
                    print(f"\nArticles related to '{selected_keyword}':")
                    if relevant_articles:
                        for article in relevant_articles:
                            print(f"\nTitle: {article['title']}")
                            print(f"Summary: {article['summary']}")
                            print(f"URL: {article['url']}")
                    else:
                        print("No articles found for this keyword.")
                else:
                    print("Choice out of range. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            
            print("\nPress Enter to continue...")
            input()