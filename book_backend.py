#Referenced ChatGPT
from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
from surprise import Dataset, Reader
import ast
from collections import Counter
import random
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

dataset = pd.read_csv('books_list.csv')

headers = dataset.columns.tolist()

selected_index = [1, 4, 6, 8, 9]

filtered_dataset = dataset.iloc[:, selected_index]

filtered_headers = filtered_dataset.columns.tolist()

filtered_dataset = filtered_dataset[filtered_dataset['Genres'] != '[]']

filtered_dataset['Publication Date'] = pd.to_datetime(filtered_dataset['Publication Date'], errors='coerce')

filtered_dataset['Publication Date'] = filtered_dataset['Publication Date'].dt.year

filtered_dataset = filtered_dataset[filtered_dataset['Publication Date'] <= 2023]

filtered_dataset['Genres'] = filtered_dataset['Genres'].apply(ast.literal_eval)

flat_genres = [genre for sublist in filtered_dataset['Genres'] for genre in sublist]

unique_genres = list(set(flat_genres))

genre_count = Counter(flat_genres)

genre_count_list = genre_count.most_common()

final_genre_list = ['Fiction', 'Fantasy', 'Romance', 'Contemporary', 'Mystery', 'Young Adult', 'Audiobook', 'Historical Fiction', 'Adult', 'Thriller', 'Historical', 'Science Fiction', 'Mystery Thriller', 'Crime', 'Paranormal', 'Nonfiction', 'Novels', 'Contemporary Romance', 'Adventure', 'Science Fiction Fantasy', 'Classics', 'Suspense', 'Humor', 'Literary Fiction', 'Literature', 'Magic', 'Childrens', 'Urban Fantasy', 'Horror', 'New Adult', 'Chick Lit', 'History', 'Biography', 'Middle Grade', 'Vampires']

filtered_dataset = filtered_dataset[filtered_dataset['Num Pages'] >= 50]

filtered_dataset['Length Category'] = pd.cut(filtered_dataset['Num Pages'], bins=[50,200,800, float('inf')], labels=['Short', 'Medium', 'Long'])

unique_years = filtered_dataset['Publication Date'].unique()

filtered_dataset['Recency'] = pd.cut(filtered_dataset['Publication Date'], bins=[1700,1940,1990,2010, float('inf')], labels=['Ancient', 'Relatively Old', '90s to 00s', '10s onwards'])

def recommend(data, user_preferences):
    filtered_books = data[data.apply(lambda row: all(genre in row['Genres'] for genre in user_preferences['Genres']), axis=1) & (data['Length Category'] == user_preferences['Length Category']) & (data['Recency'] == user_preferences['Recency'])]
    if len(filtered_books) > 5:
        filtered_books = filtered_books.sample(n=5, random_state=random.randint(1, 1000))
    return filtered_books[['Book', 'Author', 'Genres', 'Length Category', 'Recency']]

data_dict = filtered_dataset.to_dict(orient='records')

def random_books(data):
    books = data.sample(n=5, random_state=random.randint(1, 1000))
    return books[['Book', 'Author', 'Genres', 'Recency']]

def get_book_covers(title):
    base_url = "http://covers.openlibrary.org/b/id/"
    search_url = f"http://openlibrary.org/search.json?title={title}&limit=1"
    response = requests.get(search_url)
    data = response.json()

    if 'docs' in data and data['docs']:
        cover_id = data['docs'][0].get('cover_i')
        if cover_id is not None:
            image_url = f"{base_url}{cover_id}-L.jpg"
            return image_url
    return None

def book_of_the_month(data):
    books = data.sample(n=60, random_state=58)
    return books[['Book', 'Author', 'Genres', 'Recency']]

monthly_list = book_of_the_month(filtered_dataset)
monthly_book_titles = monthly_list['Book'].to_list()

book_titles_data = pd.DataFrame({'Book': monthly_book_titles})

book_titles_data['Cover Image'] = book_titles_data['Book'].apply(get_book_covers)

book_titles_data.at[20, 'Cover Image'] = 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1681507578i/61150440.jpg'
book_titles_data.at[21, 'Cover Image'] = 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1660147951l/60114057.jpg'
book_titles_data.at[47, 'Cover Image'] = 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1436735207i/10569.jpg'
book_titles_data.at[53, 'Cover Image'] = 'https://m.media-amazon.com/images/I/61fHmzl4YqL._AC_UF1000,1000_QL80_.jpg'
book_titles_data.at[55, 'Cover Image'] = 'https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1388209925l/29._SY475_.jpg'

last_update_month = datetime.now().strftime("%b")
current_recommendation_start = 0

@app.route('/homepage-recommendations', methods=['GET'])
def homepage_recommendations():
    global last_update_month
    global current_recommendation_start

    current_month = datetime.now().strftime("%b")
    if current_month != last_update_month:
        last_update_month = current_month
        current_recommendation_start = 0
    
    chunk_size = 5
    end_index = current_recommendation_start + chunk_size
    recommendations = book_titles_data[current_recommendation_start: end_index]

    current_recommendation_start + chunk_size

    return jsonify({"month": current_month, "recommendations": recommendations.to_dict(orient='records')})

@app.route('/personalized-recommendations', methods=['POST'])
def personalized_recommendations():
    user_preferences = request.json
    recommendations = recommend(filtered_dataset, user_preferences)
    return jsonify(recommendations.to_dict(orient='records'))

@app.route('/surprise-me', methods=['GET'])
def surprise_me():
    recommendations = random_books(filtered_dataset)
    return jsonify(recommendations.to_dict(orient='records'))

if __name__ == "__main__":
    app.run(debug=True)