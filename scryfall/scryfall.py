import asyncio
import aiohttp
import re
import json

website = "http://api.scryfall.com"

async def api_call(url, prms):
	
	async with aiohttp.ClientSession() as session:
		async with session.get(url, params=prms) as response:
			
			if response.status == 200:
				return await response.json()
			elif response.status == 404:
				error_msg = await response.json()
				return error_msg['details']
			else:
				return "Scryfall.com threw an error. See log for details."


async def random_card():
	
	card = await api_call(f"{website}/cards/random", None) 

	if isinstance(card, str):
		return card

	return f"{card['name']}\n{card['image_uris']['normal']}"


async def fetch_card(card_name):
	
	card = await api_call(f"{website}/cards/named", prms = {"fuzzy":card_name})

	if isinstance(card, str):
		return card

	return f"{card['name']}\n{card['image_uris']['normal']}"


async def card_search():
	pass

