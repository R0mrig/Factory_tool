import os
import sys
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
from urllib.parse import urlparse

# Configuration du chemin vers le module settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factoryapp.settings')

import django
django.setup()

# Maintenant, vous pouvez importer en toute sécurité vos modèles Django
from database.models import Company

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Initialisation de l'environnement
BASE_PATH = open_file("Chemin.txt")
PROMPT_PATH = os.path.join(BASE_PATH, 'Prompts')
SCRAPED_CONTENT_PATH = os.path.join(BASE_PATH, 'Scraped_Content')
CLEANED_CONTENT_PATH = os.path.join(BASE_PATH, 'Cleaned_Content')
ANALYZED_CONTENT_PATH = os.path.join(BASE_PATH, 'Analyzed_Content')
os.makedirs(SCRAPED_CONTENT_PATH, exist_ok=True)
os.makedirs(CLEANED_CONTENT_PATH, exist_ok=True)
os.makedirs(ANALYZED_CONTENT_PATH, exist_ok=True)

print(f"Dossiers créés pour les contenus scrappés, nettoyés, et analysés dans {BASE_PATH}")


# Configuration du client OpenAI
client = OpenAI(api_key=open_file("openaiapikey.txt"))

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def scraper_page_et_liens(url):
    print(f"Scraping du site : {url}")
    valid_liens = set()
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erreur lors de l'accès à l'URL {url} : Statut {response.status_code}")
            return valid_liens

        soup = BeautifulSoup(response.text, 'html.parser')
        for lien in soup.find_all('a', href=True):
            href = lien['href']
            url_complet = requests.compat.urljoin(url, href)
            if is_valid_url(url_complet):
                valid_liens.add(url_complet)

        print(f"Liens extraits et validés : {valid_liens}")
        return valid_liens
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à {url} : {e}")
        return valid_liens

def classifier_liens(liens):
    print("Classification des liens...")
    prompt_path = os.path.join(PROMPT_PATH, 'ClassifyAI.txt')
    classify_prompt = open_file(prompt_path)
    
    messages = [{"role": "system", "content": classify_prompt},
                {"role": "user", "content": json.dumps(list(liens))}]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages
    )

    if response.choices:
        classification_result = json.loads(response.choices[0].message.content)
        print("Classification terminée avec succès : ", classification_result)
        return classification_result.get('Important company business content', [])
    else:
        print("Erreur lors de la classification des liens.")
        return []

def scrape_to_json(link, json_filename):
    print(f"Scraping du contenu de {link}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text(strip=True)
            data = {'url': link, 'content': content}
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file)
            print(f"Contenu scrappé avec succès et sauvegardé dans {json_filename}")
            return True
        else:
            print(f"Erreur lors de l'accès à {link}: Statut {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à {link} : {e}")
        return False

def analyze_content_with_cleanergpt(file_path):
    prompt_path = os.path.join(PROMPT_PATH, 'CleanerGPT.txt')
    prompt_cleanergpt = open_file(prompt_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
        content = json_content.get('content', '')
        print(f"Analyse du contenu nettoyé pour {file_path}")
    except json.JSONDecodeError as e:
        print(f"Erreur de lecture JSON dans {file_path} : {e}")
        return ""

    messages = [{"role": "system", "content": prompt_cleanergpt},
                {"role": "user", "content": content}]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages
    )

    if response.choices:
        print(f"Réponse OpenAI pour le nettoyage : {response.choices[0].message.content}")
        return response.choices[0].message.content
    else:
        return ""

def compile_and_analyze_business_content():
    global_file_path = os.path.join(BASE_PATH, 'Global.txt')
    with open(global_file_path, 'w', encoding='utf-8') as global_file:
        for file_name in sorted(os.listdir(CLEANED_CONTENT_PATH)):
            if file_name.endswith('.txt') and not file_name.startswith('.'):
                file_path = os.path.join(CLEANED_CONTENT_PATH, file_name)
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()
                    global_file.write(content + '\n\n')

    with open(global_file_path, 'r', encoding='utf-8') as global_file:
        content = global_file.read()

    # Lire les informations supplémentaires à partir de informations.txt situé dans le dossier de base
    informations_path = os.path.join(BASE_PATH, 'informations.txt')
    with open(informations_path, 'r', encoding='utf-8') as info_file:
        informations_content = info_file.read()

    prompt_business_setupgpt_path = os.path.join(PROMPT_PATH, 'Business_setupGPT.txt')
    prompt_business_setupgpt = open_file(prompt_business_setupgpt_path)

    # Concaténer le contenu global avec les informations supplémentaires
    user_content = f"{content}\n\nVoici quelques informations supplémentaires : {informations_content}"

    messages = [
        {"role": "system", "content": prompt_business_setupgpt},
        {"role": "user", "content": user_content}
    ]

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages
    )

    # Nouveau: Imprimez la réponse brute pour voir ce qui est reçu
    print("Réponse brute reçue d'OpenAI:", response.choices[0].message.content)

    try:
        analyzed_content = json.loads(response.choices[0].message.content)
        print("Réponse d'analyse Business_setupGPT :")
        print(json.dumps(analyzed_content, indent=2))
        return analyzed_content
    except json.JSONDecodeError as e:
        print("Erreur de décodage JSON:", e)
        # Affichez davantage de la réponse pour aider au débogage
        print("Partie problématique de la réponse:", response.choices[0].message.content[:1000])
        return None



from database.models import Company

from database.models import Company

def main():
    print("Veuillez entrer l'URL à analyser :")
    url = input().strip()

    liens = scraper_page_et_liens(url)
    if not liens:
        print("Aucun lien à classifier.")
        return

    important_business_links = classifier_liens(liens)

    for i, link in enumerate(important_business_links):
        json_filename = os.path.join(SCRAPED_CONTENT_PATH, f'scraped_{i+1}.json')
        if scrape_to_json(link, json_filename):
            cleaned_content = analyze_content_with_cleanergpt(json_filename)
            txt_file_name = f"cleaned_{i+1}.txt"
            cleaned_file_path = os.path.join(CLEANED_CONTENT_PATH, txt_file_name)
            with open(cleaned_file_path, 'w', encoding='utf-8') as result_file:
                result_file.write(cleaned_content)
            print(f"Contenu nettoyé enregistré dans {cleaned_file_path}")
        else:
            print(f"Échec du scraping pour {link}, le fichier JSON n'a pas été créé.")

    analyzed_data = compile_and_analyze_business_content()
    if analyzed_data:
        company = Company(
        url=url,
        summary=analyzed_data['summary']['text'],
        products_services=analyzed_data['products_services'],
        strengths=[value for key, value in analyzed_data['strengths'].items()],
        keywords=[value for key, value in analyzed_data['keywords'].items()],
        company_specific_keywords=[value for key, value in analyzed_data['company_specific_keywords'].items()]
    )
    company.save()
    print("Données sauvegardées dans la base de données.")


if __name__ == "__main__":
    main()