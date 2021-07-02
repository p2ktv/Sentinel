<p align="center">
    <img src="https://miro.medium.com/max/4000/1*yheNL5Q0ZoZPtnKvLKj4zQ.png" alt="banner"/>
    <h2 align="center">⚡️ Discord slash command handler written in Python</h2>
</p>

## Information
This handler is just used internally for [AutoMod](https://github.com/TeamAutoMod/AutoMod) 
and therefore not really meant to be publicly used. It's very far from done or even
being particularly good, however, it's good for what we need it. I'm still planning on 
working on this and maybe release a more stable version in the future.

## Usage
I wouldn't recommend using this, thoogh if you want to to test it, copy the project
into your working directory and import the modules respectively. You can check out the example below.

## Examples
### Ping command
The classic ping command, that every bot has.
```py
# import the client and embed class ⬆️
from sentinel import SentinelClient


# define the classic client ⚙️
client = SentinelClient(token="YOUR_BOTS_TOKEN", app_id=123456789).build()


# create a new slash command ✏️
@client.slash_command(name="ping", guild=123456789, description="⏳ Shows the bot's latency")
def ping(ctx):
    # Send the response using an f-string
    ctx.respond(f"🏓 Pong! {client.latency}ms")
```

### Help command
A simple help command providing a user with the command and
its respective description.
```py
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
```