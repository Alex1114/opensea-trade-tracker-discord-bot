import discord
import os
from discord.ext import commands
import json
import keep_alive
import requests
import asyncio
# from faunadb import query as q
# from faunadb.client import FaunaClient

osapikey = os.environ['osapikey']
discord_token = os.environ['discord_token']

# adminClient = FaunaClient(secret="")

bot = commands.Bot(
	command_prefix="k!",
	case_insensitive=True, 
    help_command=None 
)

@bot.event
async def on_ready():
  print("Ready!")
  while True:
    ################################################################################# 
    # List event 
    #################################################################################
    l_url = "https://api.opensea.io/api/v1/events?asset_contract_address=0x88b7063107d2cf7fac83e30b37c938fe42c56040&event_type=created&only_opensea=false&limit=1"
    l_headers = {
        "Accept": "application/json",
        "X-API-KEY": osapikey
    }
    l_response = requests.request("GET", l_url, headers=l_headers)
    l_data = json.loads(l_response.text)

    l_name = l_data['asset_events'][0]['asset']['name']
    l_id = l_data['asset_events'][0]['asset']["token_id"]
    #price
    l_starting_price = int(l_data['asset_events'][0]['starting_price'])/1000000000000000000
    #seller address
    l_seller_address = l_data['asset_events'][0]['from_account']['address']
    #os link
    l_permalink = l_data['asset_events'][0]['asset']['permalink']
    #image
    l_image_url = l_data['asset_events'][0]['asset']['image_url']
    
    file = open("temp.json", "r")
    p = json.load(file)
    listed = p['listed']
    file.close()   
    ################################################################################# 
    # Sold event  
    #################################################################################
    s_url = "https://api.opensea.io/api/v1/events?asset_contract_address=0x88b7063107d2cf7fac83e30b37c938fe42c56040&event_type=successful&only_opensea=false&limit=1"

    s_headers = {
        "Accept": "application/json",
        "X-API-KEY": osapikey
    }
    s_response = requests.request("GET", s_url, headers=s_headers)
    s_data = json.loads(s_response.text)

    #NFT name
    s_name = s_data['asset_events'][0]['asset']['name']
    s_id = s_data['asset_events'][0]['asset']["token_id"]
    #price
    s_starting_price = int(s_data['asset_events'][0]['total_price'])/1000000000000000000
    #seller address
    s_seller_address = s_data['asset_events'][0]['seller']['address']
    #buyer address
    s_buyer_address = s_data['asset_events'][0]['winner_account']['address']
    #os link
    s_permalink = s_data['asset_events'][0]['asset']['permalink']
    #image
    s_image_url = s_data['asset_events'][0]['asset']['image_url'] 
    
    file = open("temp.json", "r")
    p = json.load(file)
    sold = p['sold']
    file.close()

    ################################################################################# 
    # Embed and Faunadb 
    #################################################################################
    if listed != l_name:
      jsonObject = {
          "listed": l_name,
          "sold": s_name,
      }
      file = open("temp.json", "w")
      json.dump(jsonObject, file)
      file.close()

      channel=bot.get_channel(944846007051620404)
      embed=discord.Embed(title=" ", description=" ", color=0xe8006f)
      embed.set_author(name=F"[list] {l_name}")
      embed.set_image(url=l_image_url)
      embed.add_field(name="price", value=f"{l_starting_price} ETH", inline=False) 
      embed.add_field(name="seller", value=f"{l_seller_address}", inline=False) 
      embed.add_field(name="OpenSea", value=f"{l_permalink}", inline=False) 
      await channel.send(embed=embed)

      #listing tracking (faunadb)
      # try:
      #   result = adminClient.query(q.delete(q.ref(q.collection("Listing-Tracker"), l_id)))
      # except Exception as e:
      #   result = e
      # print(result)
    
    await asyncio.sleep(20)

    if sold != s_name:
      jsonObject = {
          "listed": l_name,
          "sold": s_name,
      }
      file = open("temp.json", "w")
      json.dump(jsonObject, file)
      file.close()

      channel=bot.get_channel(944846007051620404)
      embed=discord.Embed(title=" ", description=" ", color=0x00ff00)
      embed.set_author(name=F"[sold] {s_name}")
      embed.set_image(url=s_image_url)
      embed.add_field(name="price", value=f"{s_starting_price} ETH", inline=False) 
      embed.add_field(name="seller", value=f"{s_seller_address}", inline=False) 
      embed.add_field(name="buyer", value=f"{s_buyer_address}", inline=False) 
      embed.add_field(name="OpenSea", value=f"{s_permalink}", inline=False) 
      await channel.send(embed=embed)
      
      #listing tracking (faunadb)
      # try:
      #   result = adminClient.query(q.delete(q.ref(q.collection("Listing-Tracker"), s_id)))
      # except Exception as e:
      #   result = e
      # print(result)
      
    await asyncio.sleep(20) 
    #################################################################################

keep_alive.keep_alive()
discord_token = os.environ['discord_token']
bot.run(discord_token)