import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from collections import defaultdict
from parsers.xml_parser import parse_user_xml

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    logging.info(f"Keyword index contains {len(keyword_index)} unique keywords")
    return processed_articles, keyword_index, data_for_infrastructure