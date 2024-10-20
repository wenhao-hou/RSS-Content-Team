import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from parsers.xml_parser import parse_user_xml

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_summarize(content):
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
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

def process_user_feed(xml_content):
    articles = parse_user_xml(xml_content)
    processed_articles = []

    for article in articles:
        summary = ai_summarize(article['content'])
        processed_article = {
            'title': article['title'],
            'content': article['content'],
            'summary': summary,
            'url': article['url']
        }
        processed_articles.append(processed_article)

    return processed_articles

def translate_feed(articles, target_language):
    translated_articles = []
    for article in articles:
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a translator. Translate the following text to {target_language}. Maintain the original structure with 'Title:', 'Content:', and 'Summary:' labels."},
                    {"role": "user", "content": f"Title: {article['title']}\n\nContent: {article['content']}\n\nSummary: {article['summary']}"}
                ]
            )
            translated_text = chat_completion.choices[0].message.content
            logging.info(f"Received translation:\n{translated_text}")
            
            # Split the text and handle potential formatting issues
            parts = translated_text.split('\n\n')
            translated_article = {
                'title': article['title'],
                'content': article['content'],
                'summary': article['summary'],
                'url': article['url']
            }
            
            for part in parts:
                if part.startswith('Title:'):
                    translated_article['title'] = part.replace('Title:', '').strip()
                elif part.startswith('Content:'):
                    translated_article['content'] = part.replace('Content:', '').strip()
                elif part.startswith('Summary:'):
                    translated_article['summary'] = part.replace('Summary:', '').strip()
            
            translated_articles.append(translated_article)
            
        except Exception as e:
            logging.error(f"Error during translation: {e}")
            translated_articles.append(article)  # Keep the original article if translation fails
    return translated_articles

def apply_slang(articles, slang_style):
    slang_articles = []
    for article in articles:
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are an expert in {slang_style} slang. Rewrite the following text in {slang_style} style."},
                    {"role": "user", "content": f"Title: {article['title']}\n\nSummary: {article['summary']}"}
                ]
            )
            slang_text = chat_completion.choices[0].message.content
            title, summary = slang_text.split('\n\n')
            slang_articles.append({
                'title': title.replace('Title: ', ''),
                'content': article['content'],
                'summary': summary.replace('Summary: ', ''),
                'url': article['url']
            })
        except Exception as e:
            logging.error(f"Error during slang application: {e}")
            slang_articles.append(article)
    return slang_articles

def filter_feed(articles, keyword):
    filtered_articles = []
    for article in articles:
        try:
            chat_completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that determines if an article is relevant to a given keyword. Respond with 'Yes' if relevant, 'No' if not."},
                    {"role": "user", "content": f"Keyword: {keyword}\n\nArticle Title: {article['title']}\n\nArticle Content: {article['content']}\n\nIs this article relevant to the keyword?"}
                ]
            )
            response = chat_completion.choices[0].message.content.strip().lower()
            if response == 'yes':
                filtered_articles.append(article)
        except Exception as e:
            logging.error(f"Error during relevance check: {e}")
            filtered_articles.append(article)  # Include the article if there's an error, to be safe
    return filtered_articles
