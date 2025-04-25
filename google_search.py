import requests

# Function for searching in google using API's
def search_google(query, api_key, search_engine_id):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}&num=5"
    response = requests.get(url)

    if response.status_code == 200:
        results = response.json()
        links = [{
            'title': item.get('title'),
            'link': item.get('link'),
            'snippet': item.get('snippet')
        } for item in results.get('items', []) if item.get('snippet') and item.get('title')]
        return links
    else:
        print("Search API Error:", response.status_code, response.text)
        return []
