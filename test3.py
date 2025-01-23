from apify import Actor
from bs4 import BeautifulSoup
from httpx import AsyncClient


async def main() -> None:
    async with Actor:
        # Retrieve the Actor input, and use default values if not provided.
        actor_input = await Actor.get_input() or {}
        start_urls = actor_input.get('start_urls', [{'url': 'https://apify.com'}])

        # Open the default request queue for handling URLs to be processed.
        request_queue = await Actor.open_request_queue()

        # Enqueue the start URLs.
        for start_url in start_urls:
            url = start_url.get('url')
            await request_queue.add_request(url)

        # Process the URLs from the request queue.
        while request := await request_queue.fetch_next_request():
            Actor.log.info(f'Scraping {request.url} ...')

            # Fetch the HTTP response from the specified URL using HTTPX.
            async with AsyncClient() as client:
                response = await client.get(request.url)

            # Parse the HTML content using Beautiful Soup.
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the desired data.
            data = {
                'url': actor_input['url'],
                'title': soup.title.string,
                'h1s': [h1.text for h1 in soup.find_all('h1')],
                'h2s': [h2.text for h2 in soup.find_all('h2')],
                'h3s': [h3.text for h3 in soup.find_all('h3')],
            }

            # Store the extracted data to the default dataset.
            await Actor.push_data(data)