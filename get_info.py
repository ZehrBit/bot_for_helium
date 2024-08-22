import aiohttp
from bs4 import BeautifulSoup


async def get_info():
    """Возвращает последюю дату и цену, которые есть на сайте"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://gnpholding.gazprom.ru/processed-gas-products/helium/results-auction/') as resp:
            resp = await resp.text()
            soup = BeautifulSoup(resp, 'html.parser')
            tables = soup.find_all('table', class_='data')
            rows = tables[0].find_all('tr')
            data = rows[1].find_all('td')
            date = data[0].get_text()
            price = data[-1].get_text()
            return date, price
