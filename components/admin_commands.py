import traceback

import hikari
import lightbulb
import json
from urllib.request import Request, urlopen
from PrefixDatabase import PrefixDatabase, prefix_dictionary
from lightbulb.ext import tasks

plugin = lightbulb.Plugin("Admin Commands")
plugin.add_checks(lightbulb.checks.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))


@tasks.task(s=3600, pass_app=True)
async def floor_price_tasks(self):

    req = Request('https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/vaxxed_doggos',
                  headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    data = json.loads(webpage)

    floor_price = data['results']['floorPrice'] / 1000000000
    listed = data['results']['listedCount']
    volume = data['results']['volumeAll'] / 1000000000

    await self.update_presence(
        activity=hikari.Activity(
            name=f"Listed: {listed:,} | Volume: {volume:,.2f} SOL",
            type=hikari.ActivityType.WATCHING,
        )
    )

    try:
        async for guild in self.rest.fetch_my_guilds():
            await self.rest.edit_my_member(nickname=f'{floor_price:.2f} SOL', guild=guild)

    except:
        traceback.print_exc()
    print("Successfully updated NFT Collection Data")


@plugin.listener(hikari.StartedEvent)
async def on_ready(event: hikari.StartedEvent) -> None:
    floor_price_tasks.start()

@plugin.command()
@lightbulb.option("prefix", "The new prefix of your server.", str)
@lightbulb.command("setprefix", "Updates the server's prefix. Administrator Only.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def setprefix(ctx: lightbulb.Context) -> None:
    PrefixDatabase.execute('UPDATE prefix SET prefix = ? WHERE guild_id = ? ', ctx.options.prefix, ctx.guild_id)
    embed = hikari.Embed(title="Prefix Successfully Updated",
                         description=f"Prefix for **{ctx.get_guild()}** is now set to `{ctx.options.prefix}`")
    prefix_dictionary.update({ctx.guild_id: ctx.options.prefix})
    await ctx.respond(embed=embed)


@plugin.command()
@lightbulb.command("myprefix", "Checks for the server's prefix. Administrator Only.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def myprefix(ctx: lightbulb.Context) -> None:
    prefix = [i[0] for i in PrefixDatabase.get('SELECT prefix FROM prefix WHERE guild_id = ? ', ctx.guild_id)][0]
    embed = hikari.Embed(description=f"Prefix for **{ctx.get_guild()}** is `{prefix}`")
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
