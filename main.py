import os
import xml.etree.ElementTree as ET
from openai import OpenAI
from collections import defaultdict
import argparse
import logging
import unittest
import re
import html
import requests
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Initialize OpenAI client

def parse_user_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        print("Attempting to unescape and parse again...")
        try:
            unescaped_xml = html.unescape(xml_string)
            root = ET.fromstring(unescaped_xml)
        except ET.ParseError as e:
            print(f"Failed to parse XML after unescaping: {e}")
            print("Attempting to remove problematic characters...")
            cleaned_xml = re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;)', '&amp;', unescaped_xml)
            try:
                root = ET.fromstring(cleaned_xml)
            except ET.ParseError as e:
                print(f"Failed to parse XML after cleaning: {e}")
                raise
    articles = []
    for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else ''
        content = entry.find('{http://www.w3.org/2005/Atom}content').text if entry.find('{http://www.w3.org/2005/Atom}content') is not None else ''
        link = entry.find('{http://www.w3.org/2005/Atom}link').get('href') if entry.find('{http://www.w3.org/2005/Atom}link') is not None else ''
        articles.append({
            "title": title,
            "content": content,
            "url": link
        })
    return articles

def ai_summarize(content):
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize this article in 2-3 sentences: {content}"}
            ]
        )
        summary = chat_completion.choices[0].message.content
        logging.info("Summarization successful.")
        return summary
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return "Summary not available."

def ai_classify(title, content):
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies articles."},
                {"role": "user", "content": f"Classify this article into 2-3 categories based on its title and content. Respond with only the category names, separated by commas.\n\nTitle: {title}\n\nContent: {content}"}
            ]
        )
        return chat_completion.choices[0].message.content.strip().split(', ')
    except Exception as e:
        logging.error(f"Error during classification: {e}")
        return []

def ai_extract_keywords(title, content):
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts keywords from articles."},
                {"role": "user", "content": f"Extract 5-7 important keywords from this article. Respond with only the keywords, separated by commas.\n\nTitle: {title}\n\nContent: {content}"}
            ]
        )
        return chat_completion.choices[0].message.content.strip().split(', ')
    except Exception as e:
        logging.error(f"Error during keyword extraction: {e}")
        return []

def process_user_feed(xml_content):
    articles = parse_user_xml(xml_content)
    processed_articles = []
    keyword_index = defaultdict(list)
    data_for_infrastructure = []

    for article in articles:
        summary = ai_summarize(article['content'])
        categories = ai_classify(article['title'], article['content'])
        keywords = ai_extract_keywords(article['title'], article['content'])

        processed_article = {
            'title': article['title'],
            'summary': summary,
            'categories': categories,
            'keywords': keywords,
            'url': article['url']
        }
        processed_articles.append(processed_article)

        for keyword in keywords:
            keyword_index[keyword].append(processed_article)

        data_for_infrastructure.append({
            'title': article['title'],
            'url': article['url'],
            'categories': categories
        })

    print(f"Keyword index contains {len(keyword_index)} unique keywords")
    return processed_articles, keyword_index, data_for_infrastructure

def main():
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
    while True:
        print("\nAvailable Keywords:")
        sorted_keywords = sorted(keyword_index.keys())
        for idx, keyword in enumerate(sorted_keywords, 1):
            print(f"{idx}. {keyword} ({len(keyword_index[keyword])} articles)")
        print("0. Exit")

        try:
            choice = input("\nSelect a keyword by number (or 0 to exit): ")
            if choice.lower() == 'exit' or choice == '0':
                print("Exiting.")
                break
            
            choice = int(choice)
            if 1 <= choice <= len(sorted_keywords):
                selected_keyword = sorted_keywords[choice - 1]
                relevant_articles = keyword_index[selected_keyword]
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

if __name__ == '__main__':
    main()