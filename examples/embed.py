# import the client and embed class ⬆️
from sentinel import SentinelClient, Embed


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOTS_TOKEN", app_id=123456789).build()


# create a new slash command ✏️
@client.slash_command(name="embed", guild=123456789, description="📦 Sends an embed")
def ping(ctx):

    # define the embed with 
    # its color, title, and
    # description
    embed = Embed(
        color=0x7289da,
        title="This is the title! ⭐️",
        description="This is a short desription! 📝"
    )

    # set a thumbnail (you can use any image url)
    embed.thumbnail(
        url=ctx.author.avatar
    )

    # add the first field
    embed.field(
        name="Field number 1 📚",
        value="I like slash commands!",
        inline=False
    )

    # add a second field
    embed.field(
        name="Field number 2 📚",
        value="I also like normal commands!",
        inline=False
    )

    # send the embed 
    # (we don't send any normal content, just the embed)
    ctx.respond(content=None, embeds=[embed])