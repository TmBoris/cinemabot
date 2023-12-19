import aiohttp


async def fetch_movie_info(session, query):
    search_url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword'

    params = {
        'keyword': query,
    }

    headers = {
        'X-API-KEY': '79697c19-ceb6-43e3-98da-71940b7f2a69',
    }

    try:
        async with session.get(search_url, params=params, headers=headers) as response:
            response.raise_for_status()
            result = await response.json()

            if result['films']:
                movie = result['films'][0]
                poster_url = movie['posterUrl']
                release_year = movie['year']
                description = movie['description']
                rating = movie['rating']
                title = movie['nameRu']

                return {
                    'poster_url': poster_url,
                    'release_year': release_year,
                    'description': description,
                    'rating': rating,
                    'title': title,
                }
            else:
                return None

    except aiohttp.ClientError as e:
        print(f"Error during Kinopoisk API request: {e}")
        return None


async def fetch_place_to_watch_movie(session, query, year):
    api_key = 'AIzaSyAcw2nEv9Vct3La2OQBLInI__K4aWitOSA'
    cx = '01cfcc92e76534f06'

    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': cx,
        'q': f'{query} {year} смотреть онлайн бесплатно'
    }

    async with session.get(base_url, params=params) as response:
        data = await response.json()

        if 'items' in data:
            # Возвращаем первую найденную ссылку
            return data['items'][0]['link']
        else:
            return None

