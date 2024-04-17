import os
import requests
import django
import json
from bs4 import BeautifulSoup
from openai import OpenAI


# Initialisation de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factoryapp.settings')
django.setup()

from database.models import Article


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Initialisation du client OpenAI
api_key = open_file("openaiapikey.txt")
client = OpenAI(api_key=api_key)
BASE_PATH = open_file("Chemin.txt")
TEMP_DIR = os.path.join(BASE_PATH, 'Temp')

def scrape_content(url):
    print(f"Scraping content from: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text_content = soup.get_text()
    return text_content

def save_content_to_file(content, filename):
    file_path = os.path.join(TEMP_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    return file_path

def process_with_openai(file_path, prompt_name):
    prompt_text = open_file(os.path.join(BASE_PATH, 'Prompts', prompt_name))
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": content}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        
    )
    
    if response.choices and len(response.choices) > 0:
        return response.choices[0].message.content
    else:
        print("No valid response received from OpenAI.")
        return None

def main():
    urls = []
    print("Enter URLs to analyze (type 'done' to finish):")
    while True:
        url = input()
        if url == 'done':
            break
        urls.append(url)

    for url in urls:
        content = scrape_content(url)
        content_file = save_content_to_file(content, f"{os.path.basename(url)}.txt")
        
        # Process content with CleanerGPT
        cleaner_result = process_with_openai(content_file, 'CleanerGPT.txt')
        cleaner_result_file = save_content_to_file(cleaner_result, f"cleaned_{os.path.basename(url)}.txt")
        
        # Analyze content with AnalystGPT
        analysis_result = process_with_openai(cleaner_result_file, 'AnalystGPT.txt')
        if analysis_result:
            analysis_data = json.loads(analysis_result)
            article = Article(
                title=analysis_data.get('titre', ''),
                url=analysis_data.get('lien', url),  # Utilisez l'URL d'entrée si le lien n'est pas fourni
                date=analysis_data.get('date', ''),
                main_topics=analysis_data.get('Main_topics', ''),
                secondary_topics=analysis_data.get('Topics_secondaires', ''),
                keywords=analysis_data.get('mots_clés', ''),
                summary=analysis_data.get('Résumé', '')
            )
            article.save()
            print(f"Article saved to the database: {article.title}")
        else:
            print(f"Failed to analyze content for URL: {url}")

if __name__ == "__main__":
    main()

    