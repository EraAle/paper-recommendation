import openreview
import os

# Initialize the V2 client
client = openreview.api.OpenReviewClient(
    baseurl='https://api2.openreview.net',
    username=os.environ.get("OPENREVIEW_USERNAME"),
    password=os.environ.get("OPENREVIEW_PASSWORD")
)

# Search for papers with 'GPT' in the title from the ICLR 2024 conference
search_results = client.get_all_notes(
    content={'title': 'GPT'}  # Use the 'content' parameter for keyword search
)

print(f"Found {len(search_results)} papers with 'GPT' in the title.")
for note in search_results[:5]:
    print(f" - Title: {note.content['title']['value']}")