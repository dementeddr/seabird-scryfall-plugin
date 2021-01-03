import os
import sys
import traceback
import numpy
import asyncio
import seabird
import aiohttp
import re
import scryfall
import logging as log
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

card_pattern = re.compile(r"\[\[([\w '!?\",.|()#$&\\]+)\]\]")



async def reply_to(client, event, text):
	await client.send_message(
		channel_id=event.source.channel_id,
		text=f"{event.source.user.display_name}: {text}",
	)



async def fetch_and_reply(client, message, name):
	card = await scryfall.fetch_card(name)
	await reply_to(client, message, card)



async def handle_card_command(client, command):
	
	log.info(f"{command.command} {command.arg}")

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
	
	if len(card_names) > 0:
		log.info(card_names)

	if len(card_names) > 0:
		await reply_to(client, message, "Tutoring your card(s)")

		for name in card_names:
			asyncio.create_task(fetch_and_reply(client, message, name))



async def process_event(client, event):

	command = event.command
	message = event.message

	if message.source.user.display_name == "seabird":
		return

	if command.command != "":
		log.info(f"{command.source.channel_id:<40} $ {command.source.user.display_name:<14}: {command.command} {command.arg}")
	elif message.text != "":
		log.info(f"{message.source.channel_id:<40} - {message.source.user.display_name:<14}: {message.text}")
	else:
		return

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
		log.error(ex)

		await reply_to(client, event, f"ERROR: {ex}")



async def main(host="SEABIRD_HOST", token="SEABIRD_TOKEN_PROD"):
	
	log.info(host)
	log.info(token)

	async with seabird.Client(
		os.getenv(host),
		os.getenv(token),
	) as client:

		log.info("Connected to Seabird Core")

		async for event in client.stream_events(commands=command_list):
			asyncio.create_task(process_event(client, event))



if __name__ == "__main__":
	load_dotenv()

	host = "SEABIRD_HOST"
	token = "SEABIRD_TOKEN_PROD"

	#log.basicConfig(filename="/var/log/seabird/scryfall.log")
	log.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=log.INFO)

	if len(sys.argv) > 1 and sys.argv[1] == 'dev':
		host = "SEABIRD_HOST_DEV"
		token = "SEABIRD_TOKEN_DEV"
	
	asyncio.run(main(host, token))
