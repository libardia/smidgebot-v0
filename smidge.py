import discord, os, dotenv
from collections import defaultdict

dotenv.load_dotenv()
client = discord.Client()

# Command decorator and storage ============

commands = {}

def command(func):
    commands[func.__name__] = func
    return func

# Commands =================================

@command
async def test(message, string1, string2):
    await message.channel.send(f'String 1: {string1}\nString 2: {string2}')

# ==========================================

@client.event
async def on_ready():
    print(f'We have logged in as "{client.user.name}"')

@client.event
async def on_message(message):
    if message.content.startswith('>>'):
        linetokens = message.content[2:].split(' ')
        command = linetokens[0].lower()
        args = tuple(linetokens[1:])
        try:
            await commands[command](message, *args)
        except KeyError:
            await message.channel.send(f'Command `{command}` not found')

client.run(os.getenv('TOKEN'))
