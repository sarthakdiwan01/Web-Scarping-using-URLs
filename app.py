import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import urllib.robotparser
import urllib.parse

# Function definitions for the tasks
def extract_information(url):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extract headlines
        headlines = []
        for i in range(1, 7):
            headlines.extend([h.get_text() for h in soup.find_all(f'h{i}')])
        
        # Extract links
        links = [(link.get('href'), link.get_text()) for link in soup.find_all('a') if link.get('href')]
        
        # Extract images
        images = [(img.get('src'), img.get('alt')) for img in soup.find_all('img')]
        
        return headlines, links, images
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return None, None, None

def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def make_request(url, retries=3):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        st.error(f"Error: {err}")
        if retries > 0:
            time.sleep(2)
            return make_request(url, retries - 1)
        else:
            return None

def extract_all_links(url):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        links = [(link.get('href'), link.get_text()) for link in soup.find_all('a') if link.get('href')]
        return links
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return []

def search_for_text(url, keyword):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        occurrences = soup.body.find_all(string=lambda text: keyword.lower() in text.lower())
        return occurrences
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return []

def use_css_selectors(url, selector):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        elements = soup.select(selector)
        return elements
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return []

def count_elements(url, tag):
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        elements = soup.find_all(tag)
        return len(elements)
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return 0

def follow_links(url, depth=1):
    if depth < 0:
        return []
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').startswith('/wiki')]
        return links
    else:
        st.error(f"Request failed with status code: {page.status_code}")
        return []

def can_fetch(url, user_agent='*'):
    parsed_url = urllib.parse.urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url)
    rp.read()
    return rp.can_fetch(user_agent, url)

# Streamlit app interface
st.title("Web Scraping Utility")

url = st.text_input("Enter URL:", "https://en.wikipedia.org/wiki/Main_Page")

if url:
    if can_fetch(url):
        st.success("Allowed to scrape")

        if st.button("Extract Information"):
            headlines, links, images = extract_information(url)
            st.subheader("Headlines")
            st.write(headlines)
            st.subheader("Links")
            st.write(links)
            st.subheader("Images")
            st.write(images)

        keyword = st.text_input("Enter keyword to search:")
        if st.button("Search for Text"):
            results = search_for_text(url, keyword)
            st.subheader(f"Occurrences of '{keyword}'")
            st.write(results)

        tag = st.text_input("Enter HTML tag to count:", "p")
        if st.button("Count Elements"):
            count = count_elements(url, tag)
            st.subheader(f"Number of '{tag}' elements")
            st.write(count)

        depth = st.number_input("Enter depth to follow links:", min_value=1, value=1)
        if st.button("Follow Links"):
            links = follow_links(url, depth)
            st.subheader("Followed Links")
            st.write(links)
    else:
        st.error("Not allowed to scrape")
