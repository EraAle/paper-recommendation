import openreview
import os

# Initialize the V2 client
client = openreview.api.OpenReviewClient(
    baseurl='https://api2.openreview.net',
    username=os.environ.get("OPENREVIEW_USERNAME"),
    password=os.environ.get("OPENREVIEW_PASSWORD")
)

# Search for papers with 'GPT' in the title from the ICLR 2024 conference
search_iterator = client.search_notes(
    term="GPT"
)

print(f"Found {len(search_results)} papers with 'GPT' in the title.")
for note in search_results[:5]:
    print(f" - Title: {note.content['title']['value']}")