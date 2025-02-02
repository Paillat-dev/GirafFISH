import logging

logging.basicConfig(level=logging.INFO)
from datetime import datetime
from config import bot, token, ai_name, data_path, user_name, instruction
from utils import (
    add_thread,
    remove_thread,
    get_threads,
    is_thread,
    get_response,
    add_training_data,
)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord! {datetime.now()}")


@bot.command(name="threads", description="Start a conversation with the AI clone")
async def threads(ctx):
    await ctx.defer()
    # create a new thread
    # thread name: Username's conversation on date
    name = f"{ctx.author.name}'s conversation on {datetime.now().strftime('%d/%m/%Y')}"
    # create a new thread
    thread = await ctx.channel.create_thread(name=name)
    # add the thread id to the json file
    await add_thread(thread.id)
    prompt = instruction + f"{ai_name}: Hello,"
    response = await get_response(prompt)
    await thread.add_user(ctx.author)
    await ctx.respond(f"Thread created. <#{thread.id}>", ephemeral=True)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # if the message is in a thread
    if not await is_thread(message.channel.id):
        return
    await message.channel.trigger_typing()
    # in this case, the message is from the user, we get the response from the AI
    history = await message.channel.history(limit=10).flatten()
    history.reverse()
    prompt = instruction
    for message in history:
        if (
            message.author == bot.user
            and message.content != ""
            and message.content != None
        ):
            prompt += f"{ai_name}: {message.content}\n\n"
        elif (
            message.author != bot.user
            and message.content != ""
            and message.content != None
        ):
            prompt += f"{user_name}: {message.content}\n\n"
    prompt = prompt + f"{ai_name}:"
    response = await get_response(prompt)
    await message.channel.send(response)


@bot.command(name="end", description="End the conversation with the AI clone")
async def end(ctx):
    await ctx.defer()
    history = await ctx.channel.history().flatten()
    history.reverse()
    input = ""
    output = ""
    for msg in history:
        input = ""
        output = ""
        if msg.author != bot.user:
            # we add all the messages before the msg
            try:
                history_before = history[: history.index(msg)]
            except:
                continue
            # we now add the messages after the msg
            for msg_before in history_before:
                if (
                    msg_before.author == bot.user
                    and msg_before.content != ""
                    and msg_before.content != None
                ):
                    input += f"{msg_before.content}[EOS]\n"
                elif (
                    msg_before.author != bot.user
                    and msg_before.content != ""
                    and msg_before.content != None
                ):
                    input += f"{msg_before.content}[EOS]\n"
            output = msg.content + "[EOS]"
            add_training_data(output, input)
    # remove the thread from the json file
    await remove_thread(ctx.channel.id)
    prompt = f"""### BEGINNING OF TRANSCRIPT ###
"""
    for msg in history:
        if msg.author == bot.user:
            prompt += f"{user_name}: {msg.content}\n\n"
        else:
            prompt += f"{ai_name}: {msg.content}\n\n"
    prompt = (
        prompt
        + '### END OF TRANSCRIPT ###\n\n### BEGINNING OF SUBJECT ###\n\nSubject is: "'
    )
    name = await get_response(prompt, stopwords='", ### END OF SUBJECT ###')
    try:
        await ctx.channel.edit(name=name)
    except:
        pass
    await ctx.channel.edit(archived=True)
    await ctx.respond("Thread ended. Title: " + name, ephemeral=True)

    # respond to the ctx


bot.run(token)
