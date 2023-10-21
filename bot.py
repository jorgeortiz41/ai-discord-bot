import settings
import discord
import openai
import io
import asyncio
import csv
from discord.ext import commands

#TODO: Use tokenizer(tiktoken) for message/history tokens and completion tokens to calc limit
#TODO: Research into how to implement chat history correctly

openai.api_key = settings.OPENAI_API_KEY
SYSTEM = "You are a helpful assitant and you are tasked with creating a CSV of the user's input topic with the user's input columns. Omit the column headers.You will maintain the column order with the same topic. You will ONLY answer with the desired CSV."
TEMPERATURE = 1
PRESENCE_PENALTY = 0.6
NUKE = False

async def get_response(system, history, prompt, tokens):
    print("running completion")
    total_tokens = tokens
    run = True

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
    while run == True and total_tokens > 0:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=1000,
            presence_penalty=PRESENCE_PENALTY,
        )
        total_tokens -= gpt_response.usage.completion_tokens
        print("total tokens left: ", total_tokens)
        print("completion tokens used: ", gpt_response.usage.completion_tokens)

        if NUKE == True:
            run = True
        else:
            run = False
    
    return gpt_response.choices[0].message.content

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

    @bot.command(name='ping', help='Responds with pong')
    async def ping(ctx):
        await ctx.send('pong')

    @bot.command(name='data', help='Responds with ChatGPT generated table in CSV format')
    async def data(ctx):
        await ctx.send("Please specify topic and columns separated by commas.\nExample: 'top 50 books, sales, ratings, short summary'\nNOTE: SPECIFY AMOUNT OF ROWS IN TOPIC. Example: '100 video games' or esle chatgpt will generate fewer rows than possible.")

        def check(m):
            return m.author == ctx.author
        
        def check_fire_mode(m):
            return m.author == ctx.author and (m.content == 'come' or m.content == 'nuke')
        
        def keep_going(m):
            return m.author == ctx.author and (m.content == 'yes' or m.content == 'no')

        try:
            #TOPIC AND COLUMNS
            text_input = await bot.wait_for('message', check=check, timeout=60)

            #FIRE OR NUKE MODE
            await ctx.send("Do you want to see your entries as they come💦 or do you want to NUKE💥 it all at once? Type 'come' for as they come or 'nuke' for all at once.")
            fire_mode = await bot.wait_for('message', check=check_fire_mode, timeout=60)
            if fire_mode.content == 'come':
                NUKE = False
                await ctx.send("Firing up the CSV generator🔫😂...")
            elif fire_mode.content == 'nuke':
                NUKE = True
                await ctx.send("You chose death💀...")

            #GENERATE PROMPT
            await ctx.send("Generating your CSV file...")
            text = text_input.content.split(',')
            text = [col.strip() for col in text]
            topic = text[0]
            columns = text[1:]

            history = []

            prompt = "Using ; as a delimiter, create a CSV of " + topic +" along with: " + ", ".join(columns)+ "\n EXCLUDE COLUMN NAMES, DO NOT REPEAT ENTRIES, GIVE ME AS MANY ENTRIES AS POSSIBLE."

            #GENERATE RESPONSE
            generated_content = []
            total_tokens = 2000
            run = True
            while run == True:
                response = await get_response(SYSTEM, history , prompt, total_tokens)
                history.append((prompt, response))
                generated_content.append(response)
                if NUKE == False:
                    await ctx.send(response)
                    await ctx.send("Do you want more entries u little bitch🍭? Type 'yes' or 'no'.")
                    status = await bot.wait_for('message', check=keep_going, timeout=60)
                    if status.content == 'yes':
                        await ctx.send("Firing up the CSV generator🔫😂...again")
                        continue
                    else: 
                        run = False
                        await ctx.send("Finishing up👅...")

            #OUTPUT CSV            
            complete_content = ''.join(generated_content)
            output = await response_to_csv(complete_content)

            filename = topic.strip() + ".csv"
            await ctx.send("Here's your CSV file:")
            await ctx.send(file=discord.File(output, filename=filename))

        except asyncio.TimeoutError:
            await ctx.send("Request timed out. Please try again.")
            



    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    run() 