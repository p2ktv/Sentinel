# import the client and embed class ⬆️
from sentinel import SentinelClient, Embed

# import the requests and json module ⬆️
import requests
import json


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOTS_TOKEN", app_id=123456789).build()


# create a new slash command ✏️
@client.slash_command(name="stats", guild_id=123456789, description="⚔️ View your Clash Royale stats!")
def stats(ctx, player_tag):
    # make the request to the clash royale api
    response = requests.get(f"https://api.clashroyale.com/v1/players/%23{player_tag}", headers={"Authorization": "Bearer YOUR_CLASH_ROYALE_API_TOKEN"})
    
    # convert the response text (string) to a dict
    # and store it in the data variable
    data = json.loads(response.text)

    # if an error occurred (for example the user passed an invalid tag)
    # the response will only containing a reason key.
    # we can use this key to return an error message
    if "reason" in data:
        ctx.respond(f"❌ Looks like there was an error: {data['reason']}")
        return

    # define a new embed with a blue side color
    e = Embed(color=0x3388ff)

    # set the thumbnail to be the users favorite card
    e.thumbnail(
        url=[x for x in data["cards"] if x["name"] == data["currentFavouriteCard"]["name"]][0]["iconUrls"]["medium"]
    )

    # add the first field containing information about the user
    # you can access all the things from the data dict
    e.field(
        name="❯ Information", 
        value="• Name: {} \n• Level: {} \n• Trophies: {} \n• Best: {} \n• Clan: {} ({})"\
        .format(
            data["name"],
            data["expLevel"],
            data["trophies"], 
            data["bestTrophies"],
            data["clan"]["name"], 
            data["clan"]["tag"]
        )
    )

    # add a second field showing some battle stats
    e.field(
        name="❯ Battle Stats", 
        value="• Games: {} \n• Wins {} \n• Losses: {} \n• Win Ratio: {}%"\
        .format(
            data["battleCount"],
            data["wins"],
            data["losses"],
            round((data["wins"] / data["battleCount"]) * 100, 0)
        )
    )
    
    ctx.respond(content=None, embeds=[e])