from telethon import events
from config import bot
from mutualfund import Holdings, Stakeholders
import json

@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply("Hello!!")

@bot.on(events.NewMessage(pattern="/add_stakeholder"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    stakeholder_id = await Stakeholders.db.count() + 1
    await Stakeholders.add_stakeholder(stakeholder_id, data[0].strip(), int(data[1]), json.loads(data[2].strip()))
    await event.reply("Added stakeholder successfully")

@bot.on(events.NewMessage(pattern="/update_stakeholder"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    await Stakeholders.update_stakeholder(int(data[0]), int(data[1]), data[3].strip())
    await event.reply("Updated stakeholder successfully")

@bot.on(events.NewMessage(pattern="/remove_stakeholder"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.strip()
    await Stakeholders.remove_stakeholder(int(data))
    await event.reply("Removed stakeholder successfully")


@bot.on(events.NewMessage(pattern="/view_stakeholders"))
async def _(event):
    data = await Stakeholders.get_all_stakeholders()
    res_str = ""
    for i in data:
        res_str += f'{i["stakeholder_id"]}, {i["stakeholder_name"]}\nAmount: {i["investment"]}\nProfit Shares: {i["profit_shares"]}\n\n'

    try:
        await event.reply(res_str)
    except:
        with open('Stakeholders.txt', 'w') as f:
            f.write(res_str)
        await event.reply('stakeholders', file='Stakeholders.txt')   

@bot.on(events.NewMessage(pattern="/add_holding"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    await Holdings.add_holding(data[0].strip(), int(data[1]), int(data[2]))
    await event.reply("Added holding successfully")

@bot.on(events.NewMessage(pattern="/update_holding"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    await Holdings.update_holding(data[0].strip(), int(data[1]), int(data[2]))
    await event.reply("Updated holding successfully")

@bot.on(events.NewMessage(pattern="/reduce_holding"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    await Holdings.reduce_holding(data[0].strip(), int(data[1]), int(data[2]))
    await event.reply("Reduced holding successfully")

@bot.on(events.NewMessage(pattern="/close_holding"))
async def _(event):
    msg = await event.get_reply_message()
    data = msg.raw_text.split('\n')
    await Holdings.close_holding(data[0].strip(), int(data[1]))
    await event.reply("Closed holding successfully")

@bot.on(events.NewMessage(pattern="/view_holdings"))
async def _(event):
    data = await Holdings.get_all_holdings()
    res_str = ""
    for i in data:
        res_str += f'{i["coin_name"]}, {i["amount"]}$\nEntry Price: {i["avg_price"]}\n\n'

    try:
        await event.reply(res_str)
    except:
        with open('Holdings.txt', 'w') as f:
            f.write(res_str)
        await event.reply('holdings', file='Holdings.txt')


bot.start()

bot.run_until_disconnected()
