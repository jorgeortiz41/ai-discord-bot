import settings
import discord
import openai
import io
import asyncio
import csv
from discord.ext import commands



def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix=settings.PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user.name} has connected to Discord!')
        print(f'{bot.user.id} is the bot id')
        print(settings.DISCORD_TOKEN)
        print(settings.OPENAI_API_KEY)
        #print all of the permissions the bot has
        # perms = discord.Permissions()
        # for perm in perms:
        #     print(perm)

    @bot.command(name='ping', help='Responds with pong')
    async def ping(ctx):
        await ctx.send('pong')
        print('bot has executed command ping')

    @bot.command(name='data', help='Responds with ChatGPT generated table in CSV format')
    async def data(ctx):
        await ctx.send("Please specify topic and columns separated by commas (Example: <topic>,  <col1>, <col2>, <col3>). Example: 'cars, make, model, year'")

        def check(m):
            return m.author == ctx.author

        try:
            text_input = await bot.wait_for('message', check=check, timeout=60)
            await ctx.send("Generating your CSV file...")
            text = text_input.content.split(',')
            text = [col.strip() for col in text]
            print(text)
            topic = text[0]
            print("topic: "+ topic)
            columns = text[1:]
            print("columns: ".join(columns))

            # Initialize an empty string to accumulate content from ChatGPT
            generated_content = ""

            #Enter openai key here
            openai.api_key = settings.OPENAI_API_KEY

            generated_content = []

            # Define the total number of tokens you want
            total_tokens = 5000  # You can adjust this value as needed

            # Define the number of tokens per request (e.g., a safe limit is 4096 tokens)
            max_tokens_per_request = 4000  # Adjust as needed

            prompt = "Using ; as a delimiter, create a CSV of 50" + topic +" along with: " + ", ".join(columns)+ "\n EXCLUDE COLUMN NAMESAND KEEP EXACTLY IN THAT ORDER OF COLUMNS."
            print(prompt)

            while total_tokens > 0:
                tokens_to_request = min(total_tokens, max_tokens_per_request)
                gpt_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role': 'system', 'content': "You are an assitant specializing in data entry. You are tasked with creating a CSV of the user's input topic with the user's input columns. Omit the column headers. You will ONLY answer with the desired CSV."},
                              {'role': 'user', 'content': prompt}
                              ],
                    temperature=1,
                    max_tokens=tokens_to_request,
                    presence_penalty=0.6,
                )
                print(gpt_response.usage.completion_tokens)

                generated_content.append(gpt_response.choices[0].message.content)

                total_tokens -= gpt_response.usage.completion_tokens
                print(total_tokens)
                asyncio.sleep(1)

            # calculate the time it took to receive the response
            completed_content = "".join(generated_content)


            # Create a CSV file with the specified columns and generated content
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows([row.split(';') for row in completed_content.strip().split('\n')])

            filename = topic.strip() + ".csv"
            output.seek(0)
            await ctx.send("Here's your CSV file:")
            await ctx.send(file=discord.File(output, filename=filename))

        except asyncio.TimeoutError:
            await ctx.send("Request timed out. Please try again.")
            



    bot.run(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    run() 