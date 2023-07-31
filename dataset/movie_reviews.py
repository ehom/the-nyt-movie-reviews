import requests
import json
import os

def save_to_file(object, filename="dataset/movie_reviews.json"):
    with open(filename, "w") as f:
        json.dump(object, f, indent=4)


def load():
    API_KEY = os.environ['NYT_API_KEY']
    url = f"https://api.nytimes.com/svc/topstories/v2/movies.json?api-key={API_KEY}"
    response = requests.get(url)

    object = {}
    
    if response.status_code == 200:
        object = response.json();
        save_to_file(object)

    return object
