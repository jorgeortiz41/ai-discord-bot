import settings
import discord
import openai
import io
import asyncio
import csv
from discord.ext import commands
from discord import app_commands

#TODO: Use tokenizer(tiktoken) for message/history tokens and completion tokens to calc limit
#TODO: Refactor csv gpt code to have history fixed like gpt
#TODO: Add a way to clear history
#TODO: Add a way to change the temperature and presence penalty
#TODO: Add a way to change the max tokens
#TODO: Update gpt_response with new firemodes and command structure
#TODO: CHANGE DATA COMMAND COLUMNS TO OPTIONAL


openai.api_key = settings.OPENAI_API_KEY
SYSTEM_CSV = "You are a helpful assitant and you are tasked with creating a CSV of the user's input topic with the user's input columns. Omit the column headers.You will maintain the column order with the same topic. You will ONLY answer with the desired CSV."
TEMPERATURE = 1
PRESENCE_PENALTY = 0.6
HISTORY = []

async def get_response(system, history, prompt, tokens):
    print(f"running completion of {prompt}")
    total_tokens = tokens
    generated_response = []
    completed_response = ''
    

    messages = [
        { "role": "system", "content": system },
    ]
    # add the previous prompts and answers
    for question, answer in history:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new prompt
    messages.append({ "role": "user", "content": prompt })

    # create the completion
    print("fetching completion...")
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=total_tokens,
        presence_penalty=PRESENCE_PENALTY,
    )
    print("completion fetched")
    generated_response.append(gpt_response.choices[0].message.content)
    print("total tokens left: ", total_tokens)
    print("completion tokens used: ", gpt_response.usage.completion_tokens)
    print("history length: ", len(history))
    
    completed_response = ''.join(generated_response)

    return completed_response

async def response_to_csv(response):
    print("running csv")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows([row.split(';') for row in response.strip().split('\n')])

    output.seek(0)
    return output

def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=settings.PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')
        print(f'{bot.user.id} is the bot id')
        try:
            synced = await bot.tree.sync()
            print('synced commands: ', synced)
        except:
            print("failed to sync commands")

    '''
    PING COMMAND
    '''
    @bot.tree.command(name='ping', description='responds with pong')
    async def ping(ctx: discord.Interaction):
        await ctx.response.send_message(f'{ctx.user.mention} pong', ephemeral=True)

    '''
    GPT COMMAND
    '''
    @bot.tree.command(name='gpt', description='responds with ChatGPT response')
    @app_commands.describe(prompt = 'The prompt to generate a response to')
    async def gpt(ctx: discord.Interaction, prompt: str):
        global HISTORY
        await ctx.response.send_message("Bot is thinking... he's a bit retarded", ephemeral=True)
        
        system_message = 'You are a helpful assitant and you are tasked with answer the user\'s questions. Use chat history to answer the user\'s questions when needed.'
        total_tokens = 600

        if len(HISTORY) >= 6:
            HISTORY = HISTORY[-6:]
                

        response = await get_response(system_message ,HISTORY, prompt, total_tokens)
        HISTORY.append((prompt, response))

        await ctx.edit_original_response(content=response + "\n Message expires after 60 seconds.")
        await asyncio.sleep(300)
        await ctx.delete_original_response()

    '''
    DATA COMMAND
    '''
    @bot.tree.command(name='data', description="responds with ChatGPT output as CSV Spreadsheet")
    async def data(ctx: discord.Interaction, topic: str, entries: int, col1: str, col2: str, col3: str, col4: str, col5: str):
        global HISTORY
        await ctx.response.send_message("Bot is thinking... he's a bit retarded", ephemeral=True)
        columns = [col1, col2, col3, col4, col5]
        for col in columns:
            if col == '':
                columns.remove(col)
        column_names = ', '.join(columns)
        prompt = f'Generate a CSV file with the following data:\nTopic: {topic}\nEntries: {entries}\nColumn Names: {column_names}\nDelimiter: ;\nDo not repeat entries.'
        total_tokens = 4000

        if len(HISTORY) >= 6:
            HISTORY = HISTORY[-6:]
                

        response = await get_response(SYSTEM_CSV ,HISTORY, prompt, total_tokens)
        HISTORY.append((prompt, response))

        output = await response_to_csv(response)
        filename = topic.strip() + ".csv"

        await ctx.edit_original_response(content=f"Here is your {topic} CSV",attachments=[discord.File(output, filename=filename)])

    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    run() 