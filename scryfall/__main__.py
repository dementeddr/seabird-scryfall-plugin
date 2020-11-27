import os
import sys
import traceback
import numpy
import asyncio
import seabird
import aiohttp
import re
import scryfall
from dotenv import load_dotenv


command_list={
	"card": seabird.seabird.CommandMetadata(
		name="card",
		short_help="Fetch an MtG card",
		full_help="Fetch a Magic card's oracle text from Scryfall",
	),
	"cards": seabird.seabird.CommandMetadata(
		name="cards",
		short_help="Seach for list of MtG cards",
		full_help="Alias for 'search' command. Syntax reference: http://scryfall.com/docs/syntax",
	),
	"search": seabird.seabird.CommandMetadata(
		name="search",
		short_help="Search for list of MtG cards",
		full_help="Takes a scryfall search string and returns a list of matching Magic cards. Syntax reference: http://scryfall.com/docs/syntax",
	)
}

card_pattern = re.compile(r"\[\[([\w '!?\",.|()#$&]+)\]\]")


async def reply_to(client, event, text):
	await client.send_message(
		channel_id=event.source.channel_id,
		text=f"{event.source.user.display_name}: {text}",
	)
	
	
async def handle_card_command(client, command):
	print(command.command)

	card_text =""

	if command.arg != "":
		await reply_to(client, command, "Cracking a fetch for your card")
		card_text = await scryfall.fetch_card(command.arg)
	else:
		await reply_to(client, command,  "Cascading into a random card")
		card_text = await scryfall.random_card()

	await reply_to(client, command, card_text)
		

async def handle_card_fetch(client, message):
	card_names = card_pattern.findall(message.text)
	print(card_names)

	if len(card_names) > 0:
		await reply_to(client, message, "Tutoring your card(s)")

		'''
		other_thing = await asyncio.gather((await scryfall.fetch_card(name)) 
			for name in card_names)

		for thing in other_thing:
			await reply_to(client, message, thing)

		'''
		for name in card_names:
			card = await scryfall.fetch_card(name)
			await reply_to(client, message, card)
		

async def main():

	async with seabird.Client(
		os.getenv("SEABIRD_HOST_DEV", "https://seabird-core.elwert.cloud"),
		os.getenv("SEABIRD_TOKEN"),
	) as client:

		print("Connected to Seabird Core")

		async for event in client.stream_events(commands=command_list):

			command = event.command
			message = event.message

			if message.source.user.display_name == "seabird":
				continue

			if command.command != "":
				print(f"{command.source.channel_id} $ {command.source.user.display_name}: {command.command} {command.arg}")
			elif message.text != "":
				print(f"{message.source.channel_id} {message.source.user.display_name}: {message.text}")

			try:
				if command.command == "card":
					await handle_card_command(client, command)
				if command.command in ("cards", "search"):
					pass
				else:
					await handle_card_fetch(client, message)

			except Exception as ex:
				print("Shit's on fire yo")
				print("-"*60)
				traceback.print_exc()
				print("-"*60)


if __name__ == "__main__":
	load_dotenv()
	asyncio.run(main())
