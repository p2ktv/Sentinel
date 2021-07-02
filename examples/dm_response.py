# import the client and embed class ⬆️
from sentinel import SentinelClient


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOT_TOKEN", app_id=123456789).build()


@client.slash_command(name="dm", guild=123456789, description="🎉 Sends a simple DM to the author")
def dm(ctx):
    ctx.dm("Only you can see this message!")