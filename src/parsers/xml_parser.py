import xml.etree.ElementTree as ET
import html
import re
import logging

def parse_user_xml(xml_string):
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        logging.info("Attempting to unescape and parse again...")
        try:
            unescaped_xml = html.unescape(xml_string)
            root = ET.fromstring(unescaped_xml)
        except ET.ParseError as e:
            logging.error(f"Failed to parse XML after unescaping: {e}")
            logging.info("Attempting to remove problematic characters...")
            cleaned_xml = re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;)', '&amp;', unescaped_xml)
            try:
                root = ET.fromstring(cleaned_xml)
            except ET.ParseError as e:
                logging.error(f"Failed to parse XML after cleaning: {e}")
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