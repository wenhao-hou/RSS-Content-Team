# RSS-Content-Team

# RSS Content Processor

This project is a Python-based RSS feed processor that fetches XML content from a given URL, processes the articles using AI-powered summarization and classification, and provides an interactive interface for exploring the processed content.

## Features

- Fetches RSS feed XML from a provided URL
- Parses XML content and extracts article information
- Uses OpenAI's GPT-4 model to summarize articles, classify them, and extract keywords
- Builds a keyword index for quick article lookup
- Provides an interactive command-line interface for exploring processed articles by keyword

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/rss-content-processor.git
   cd rss-content-processor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root directory
   - Add your OpenAI API key to the `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

Run the main script with the URL of the RSS feed you want to process:
For example:
```
python main.py https://example.com/rss-feed.xml
```

This will fetch the XML content, process the articles, and provide an interactive interface for exploring the processed content.

## License
This project is licensed under the MIT License.
