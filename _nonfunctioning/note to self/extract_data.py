import requests
import json
from bs4 import BeautifulSoup

url = "https://example.com"
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find the script tag (refine by ID or type if necessary)
# Example: <script id="data-container" type="application/json">...</script>
script_tag = soup.find('script', {'id': 'data-container'})

if script_tag:
    # Extract text and convert to a dictionary
    json_data = json.loads(script_tag.string)
    print(json_data)