import requests
import os
from decouple import config
import discord
from discord import Embed
from discord.ext.commands import Bot
from discord.ext import tasks
import json
import DiscordUtils
from datetime import datetime
from bs4 import BeautifulSoup
import certifi
import ssl
intents = discord.Intents.default()
intents.members = True

bot = Bot(command_prefix='?', intents=intents)
bot.remove_command('help')

async def techDealsIn():
    channelId = bot.get_channel(1053082212066660395)
    URL = "https://techdeals.in/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'lxml')
    name = soup.find_all('h3', attrs = {'class':'fontnormal mb10 mt0 lineheight25'}) 
    place = soup.find_all('div', attrs = {'class':'mb10 compare-domain-icon'})
    price = soup.find_all('span', attrs = {'class':'woocommerce-Price-amount amount'}) 
    with open("data.json", "r+") as f:
        data = json.load(f)
        for i in range(len(name)):    
            if name[len(name)-1].text == data["lastDeal"]:
                dataEmbed = Embed(title=name[i].text.strip(), description=place[i].text.strip() + " [view more](https://techdeals.in/)", timestamp=datetime.utcnow(), color=0x5865F2)
                dataEmbed.add_field(name="price", value=price[i].text.strip())
                await channelId.send(embed=dataEmbed)
            tempVar = name[len(name)-1].text
            data["lastDeal"] = tempVar
            f.seek(0)
            f.write(json.dumps(data))

@tasks.loop(minutes=1)
async def main():
    await techDealsIn() # calls function that gets data from techdeals.in and sends in teh channel specified
            
@bot.command()
async def amazon(ctx, *, game):
    with open("search_results_urls.txt", "a") as f:
        f.seek(0)
        f.write(str(game))
    import amazon.searchresults
    with open("search_results_output.json", "r+") as f:
        data = json.load(f)
        print(data)
    embed1 = Embed(color=0x5865F2, title="{}".format(data["obj"][0]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 1**".format(data["obj"][0]["price"], "https://amazon.com" + data["obj"][0]["url"], data["obj"][0]["rating"], data["obj"][0]["reviews"]), timestamp=datetime.utcnow())
    embed2 = Embed(color=0x5865F2, title="{}".format(data["obj"][1]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 2**".format(data["obj"][1]["price"], "https://amazon.com" + data["obj"][1]["url"], data["obj"][1]["rating"], data["obj"][1]["reviews"]), timestamp=datetime.utcnow())
    embed3 = Embed(color=0x5865F2, title="{}".format(data["obj"][2]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 3**".format(data["obj"][2]["price"], "https://amazon.com" + data["obj"][2]["url"], data["obj"][2]["rating"], data["obj"][2]["reviews"]), timestamp=datetime.utcnow())
    embed4 = Embed(color=0x5865F2, title="{}".format(data["obj"][3]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 4**".format(data["obj"][3]["price"], "https://amazon.com" + data["obj"][3]["url"], data["obj"][3]["rating"], data["obj"][3]["reviews"]), timestamp=datetime.utcnow())
    embed5 = Embed(color=0x5865F2, title="{}".format(data["obj"][4]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 1**".format(data["obj"][4]["price"], "https://amazon.com" + data["obj"][4]["url"], data["obj"][4]["rating"], data["obj"][4]["reviews"]), timestamp=datetime.utcnow())
    embed6 = Embed(color=0x5865F2, title="{}".format(data["obj"][5]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 2**".format(data["obj"][5]["price"], "https://amazon.com" + data["obj"][5]["url"], data["obj"][5]["rating"], data["obj"][5]["reviews"]), timestamp=datetime.utcnow())
    embed7 = Embed(color=0x5865F2, title="{}".format(data["obj"][6]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 3**".format(data["obj"][6]["price"], "https://amazon.com" + data["obj"][6]["url"], data["obj"][6]["rating"], data["obj"][6]["reviews"]), timestamp=datetime.utcnow())
    embed8 = Embed(color=0x5865F2, title="{}".format(data["obj"][7]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 4**".format(data["obj"][7]["price"], "https://amazon.com" + data["obj"][7]["url"], data["obj"][7]["rating"], data["obj"][7]["reviews"]), timestamp=datetime.utcnow())
    embed9 = Embed(color=0x5865F2, title="{}".format(data["obj"][8]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 3**".format(data["obj"][8]["price"], "https://amazon.com" + data["obj"][8]["url"], data["obj"][8]["rating"], data["obj"][8]["reviews"]), timestamp=datetime.utcnow())
    embed0 = Embed(color=0x5865F2, title="{}".format(data["obj"][9]["title"]), description="for just {} get it [here]({})\nrating: {} ({} reviews)\n **page 4**".format(data["obj"][9]["price"], "https://amazon.com" + data["obj"][9]["url"], data["obj"][9]["rating"], data["obj"][9]["reviews"]), timestamp=datetime.utcnow())
    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")
    embeds = [embed1, embed2, embed3, embed4, embed5, embed6, embed7, embed8, embed9, embed0]
    await paginator.run(embeds)
    with open("search_results_urls.txt", "w+") as f:
        f.seek(0)
        f.write("https://www.amazon.com/s?k=")
        json.dumps(f.read(), f)
        
@bot.event
async def on_ready():
    print("build successfully")
    main.start()
    
bot.run(config("DISCORD-TOKEN")) 