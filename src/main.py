import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import argparse
import requests
from parsers.xml_parser import parse_user_xml
from ai.openai_utils import process_user_feed, translate_feed, apply_slang, filter_feed
from utils.logging_config import setup_logging

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Process and transform RSS feed XML files.")
    parser.add_argument('xml_url', help='URL of the RSS feed XML')
    args = parser.parse_args()

    print(f"Fetching XML from URL: {args.xml_url}")
    try:
        response = requests.get(args.xml_url)
        response.raise_for_status()
        xml_content = response.text
        print(f"Successfully fetched XML. Content length: {len(xml_content)} characters")
    except requests.RequestException as e:
        print(f"Error fetching XML from URL: {e}")
        return

    print("Processing user feed...")
    processed_articles = process_user_feed(xml_content)

    while True:
        action = input("\nWhat would you like to do? (filter/translate/slang/exit): ").lower()
        
        if action == 'exit':
            break
        elif action == 'filter':
            keyword = input("Enter a keyword to filter the feed: ")
            processed_articles = filter_feed(processed_articles, keyword)
        elif action == 'translate':
            language = input("Enter the target language: ")
            processed_articles = translate_feed(processed_articles, language)
        elif action == 'slang':
            slang_style = input("Enter the slang style (e.g., cyberpunk, southern belle): ")
            processed_articles = apply_slang(processed_articles, slang_style)
        else:
            print("Invalid action. Please try again.")

    print("\nFinal processed articles:")
    for article in processed_articles:
        print(f"\nTitle: {article['title']}")
        print(f"Summary: {article['summary']}")
        print(f"URL: {article['url']}")

if __name__ == '__main__':
    main()
