# import the client and embed class ⬆️
from sentinel import SentinelClient


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOT_TOKEN", app_id=123456789).build()


@client.slash_command(name="help", guild=123456789, description="📌 Shows a list of all commands")
def help(ctx):
    # define a list for all the help strings
    output = []

    # loop over all the commands
    for command, info in client.commands.items():
        # get the description for the command
        description = info["description"]

        # add it to the list of help strings
        output.append(f"/{command} - {description}")

    # send the message using the join() method to 
    # make it display 1 command per line
    ctx.respond("**__Commands__** \n" + "\n".join(output))
