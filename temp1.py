import os
from dotenv import load_dotenv

import asyncio
import contextlib
import logging
from typing import NoReturn

from telegram import __version__ as TG_VER
from telegram import Bot
from telegram.error import Forbidden, NetworkError

def get_bot_key():
    load_dotenv(dotenv_path='./.env')
    BOT_KEY = os.getenv('BOT_KEY')
    return BOT_KEY


async def main() -> NoReturn:
    """Run the bot."""
    # Here we use the `async with` syntax to properly initialize and shutdown resources.
    async with Bot(get_bot_key()) as bot:
        # get the first pending update_id, this is so we can skip over it in case
        # we get a "Forbidden" exception.
        try:
            update_id = (await bot.get_updates())[0].update_id
        except IndexError:
            update_id = None

        logger.info("listening for new messages...")
        while True:
            try:
                update_id = await echo(bot, update_id)
            except NetworkError:
                await asyncio.sleep(1)
            except Forbidden:
                # The user has removed or blocked the bot.
                update_id += 1


async def echo(bot: Bot, update_id: int) -> int:
    """Echo the message the user sent."""
    # Request updates after the last update_id
    updates = await bot.get_updates(offset=update_id, timeout=10)
    for update in updates:
        next_update_id = update.update_id + 1

        # your bot can receive updates without messages
        # and not all messages contain text
        if update.message and update.message.text:
            # Reply to the message
            if update.message.text == "!servers":
                msg = servers_list()
                logger.info("msg: %s!", msg)
                await update.message.reply_text(msg)
            else:
                logger.info("Found message %s!", update.message.text)
                await update.message.reply_text(update.message.text)
        return next_update_id
    return update_id

def servers_list():
    out= "=============\n1)192.168.1.1\n2)192.168.1.2\n3)...\n============="
    return out
if __name__ == "__main__":
    #Some preparation
    try:
        from telegram import __version_info__
    except ImportError:
        __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]  # type: ignore[assignment]

    if __version_info__ < (20, 0, 0, "alpha", 1):
        raise RuntimeError(
            f"This example is not compatible with your current PTB version {TG_VER}. To view the "
            f"{TG_VER} version of this example, "
            f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
        )

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    #run the bot
    with contextlib.suppress(KeyboardInterrupt):  # Ignore exception when Ctrl-C is pressed
        asyncio.run(main())