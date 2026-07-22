import requests
from minsearch import Index

URL_PREFIX = 'https://datatalks.club/faq'

def load_faq_data():
    docs_url = f'{URL_PREFIX}/json/courses.json'
    response = requests.get(docs_url)
    courses_raw = response.json()
    documents = []

    for course in courses_raw:
        course_url = f'{URL_PREFIX}{course["path"]}'
        course_response = requests.get(course_url)
        course_response.raise_for_status()
        course_data = course_response.json()

        documents.extend(course_data)

    return documents

def build_index(documents):
    index = Index(
        text_fields=['question', 'section', 'answer'],
        keyword_fields=['course']
    )
    index.fit(documents)
    return index

