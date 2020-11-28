import asyncio
import aiohttp
import re
import json

website = "http://api.scryfall.com"

pretty_legals = {
	"legal":	  "Legal",
	"not_legal":  "Not Legal",
	"banned":	  "Banned",
	"restricted": "Restricted",
	}


async def api_call(path, prms):
	
	async with aiohttp.ClientSession() as session:
		async with session.get(f"{website}/{path}", params=prms) as response:
			
			if response.status == 200:
				return await response.json()
			elif response.status == 404:
				error_msg = await response.json()
				return error_msg['details']
			else:
				return "Scryfall.com threw an error. See log for details."



async def random_card():
	
	card = await api_call(f"cards/random", None) 

	if isinstance(card, str):
		return card

	return f"{card['name']}\n{card['image_uris']['normal']}"



async def fetch_card_legalities(card_name):

	card = await api_call(f"cards/named", prms = {"fuzzy":card_name})

	if isinstance(card, str):
		return card

	formats = card['legalities'].keys()
	ret = ["```", f"{card['name']}  -  Format Legalities",]

	for form in formats:
		ret.append(f"  {form.title():<10}-\t{pretty_legals[card['legalities'][form]]}")

	ret.append("```")

	return "\n".join(ret)



async def fetch_card_oracle(card_name):
	
	card = await api_call(f"cards/named", prms = {"fuzzy":card_name})

	if isinstance(card, str):
		return card

	if "card_faces" in card:
		ret = "not yet implemented for DFCs"
	else:

		c_ind = f"({''.join(card['color_indicator'])}) " if 'color_indicator' in card else ""
		pretty_oracle = card['oracle_text'].replace('(', '_(').replace(')', ')_')

		ret = [
			f"\n>>> **{card['name']}**   {card['mana_cost']}",
			f"{c_ind}{card['type_line']}   [{card['rarity'][0].title()}]",
			pretty_oracle,
		]

		if "power" in card:
			ret.append(f"{card['power']} / {card['toughness']}")

	return '\n'.join(ret)



async def fetch_card_image(card_name):
	
	card = await api_call(f"cards/named", prms = {"fuzzy":card_name})

	if isinstance(card, str):
		return card

	if "card_faces" in card:
		faces = card['card_faces']
		 
		ret = [
			f"**{faces[0]['name']}**",
			f"{faces[0]['image_uris']['normal']}",
			f"**{faces[1]['name']}**",
			f"{faces[1]['image_uris']['normal']}",
		]

		return '\n'.join(ret)
	else:
		return f"**{card['name']}**\n{card['image_uris']['normal']}"



async def fetch_card(card_name):

	prefix = card_name[0]

	if   prefix == '!':
		return await fetch_card_oracle(card_name[1:])
	elif prefix == '#':
		return await fetch_card_legalities(card_name[1:])
	elif prefix == '$':
		pass #prices
	elif prefix == '?':
		pass #rulings
	else:
		return await fetch_card_image(card_name)



async def card_search():
	pass

