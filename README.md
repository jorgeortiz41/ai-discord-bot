# AI Discord Bot

This is a versatile Discord bot leveraging the OpenAI API to provide two distinct functionalities: ChatGPT mode for natural language interactions and a data mode generating CSV outputs based on user-defined rows and columns.

## Features

- **ChatGPT Mode**: Engage in natural language conversations with the bot using the power of OpenAI's ChatGPT model.
- **Data Mode**: Generate CSV outputs based on user-defined rows and columns.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/ai-discord-bot.git
   ```

2. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

3. Set up the necessary environment variables:

   - `DISCORD_TOKEN`: Your Discord bot token.
   - `OPENAI_API_KEY`: Your OpenAI API key.

## Usage

1. Start the bot:

   ```shell
   python bot.py
   ```

2. Invite the bot to your Discord server using the following link:

   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot
   ```

3. Interact with the bot in your Discord server.

## Commands

## Slash Commands

The bot supports the following slash commands:

- `/gpt`: Engage in natural language conversations with the bot.
- `/data`: Generate CSV outputs based on user-defined rows and columns.
- `/ping`: Answers back 'pong' used to test bot behavior in development.

## Configuration

You can customize the behavior of the bot by modifying the `bot.py` file.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
