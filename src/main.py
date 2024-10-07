import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import argparse
import requests
from parsers.xml_parser import parse_user_xml
from ai.openai_utils import process_user_feed
from utils.logging_config import setup_logging
from data_structures.keyword_index import KeywordIndex

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Process RSS feed XML files.")
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
    processed_articles, keyword_index, data_for_infrastructure = process_user_feed(xml_content)

    print(f"Processed {len(processed_articles)} articles")
    print(f"Number of unique keywords: {len(keyword_index)}")

    # Interactive Keyword Selection
    keyword_index_obj = KeywordIndex(keyword_index)
    keyword_index_obj.interactive_selection()

if __name__ == '__main__':
    main()