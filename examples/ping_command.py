# import the client and embed class ⬆️
from sentinel import SentinelClient


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOTS_TOKEN", app_id=123456789).build()


# create a new slash command ✏️
@client.slash_command(name="ping", guild=123456789, description="⏳ Shows the bot's latency")
def ping(ctx):
    # Send the response using an f-string
    ctx.respond(f"🏓 Pong! {client.latency}ms")