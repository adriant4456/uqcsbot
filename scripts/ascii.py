from uqcsbot import bot, Command
from requests import get
from requests.exceptions import RequestException
from uqcsbot.utils.command_utils import loading_status
import random

NO_QUERY_MESSAGE = "Can't ASCIIfy nothing... try `!asciify <TEXT>`"
BOTH_OPTIONS_MESSAGE = "Font can only be random OR specified"
ERROR_MESSAGE = "Trouble with HTTP Request, can't ASCIIfy :("

ASCII_URL = "http://artii.herokuapp.com/make?text="
FONT_URL = "http://artii.herokuapp.com/fonts_list"

#TODO: FIX RETURNING ONLY FONTSLIST - SHOULD NOT PASS NOTHING INTO ASCIIFY
@bot.on_command("asciify")
@loading_status
def handle_asciify(command: Command):
    """
    `!asciify [--fontslist] [--randomfont | --<CUSTOM FONT>] <TEXT>` - Returns
    ASCIIfyed text. `--fontslist` also returns a URL to available fonts, `--randomfont`
    returns, well... a random font. A custom font from the fonts list can also be
    specified.
    """
    # Makes sure the query is not empty
    if not command.has_arg():
        bot.post_message(command.channel_id, NO_QUERY_MESSAGE)
        return
    command_args = command.arg.split()
    random_font = False
    custom_font = False
    return_fonts = False

    #check for font list option
    if '--fontslist' in command_args:
        return_fonts = True
        command_args.remove('--fontslist')
    #check for custom font option
    fontslist = get_fontslist()
    if not fontslist:
        bot.post_message(command.channel_id, ERROR_MESSAGE)
        return
    for i in fontslist:
        if ('--' + i) in command_args:
            custom_font = True
            selected_font = i
            command_args.remove('--' + selected_font)
    #check for random font option
    if '--randomfont' in command_args:
        random_font = True
        command_args.remove('--randomfont')
    #check for invalid options
    if random_font and custom_font:
        bot.post_message(command.channel_id, BOTH_OPTIONS_MESSAGE)
        return
    if not command_args:
        bot.post_message(command.channel_id, NO_QUERY_MESSAGE)
        text = None
    else: 
        text = ' '.join(command_args)
    #asciification
    if random_font:
        ascii_text = asciify(text, randomfont())
    elif custom_font:
        ascii_text = asciify(text, selected_font)
    else:
        ascii_text = asciify(text, None)
    #message posts
    if ascii_text:
        bot.post_message(command.channel_id, ascii_text)
    else:
        bot.post_message(command.channel_id, ERROR_MESSAGE)
    if return_fonts:
        bot.post_message(command.channel_id, FONT_URL)
    return


def asciify(text: str, font: str) -> str:
    try:
        if font:
            ascii_text = "```\n" + get(ASCII_URL + text + '&font=' + font).text + "\n```"
            return ascii_text
        else:
            ascii_text = "```\n" + get(ASCII_URL + text).text + "\n```"
            return ascii_text
    except RequestException as e:
        bot.logger.error(f"A request error {e.resp.status} occurred:\n{e.content}")
        return None
    

def randomfont() -> str:
    fontslist = get_fontslist()
    if fontslist:
        font_number = random.randint(0, len(fontslist) - 1)
        return fontslist[font_number]
    else:
        return None

def get_fontslist() -> list:
    try:
        fontslist = get('http://artii.herokuapp.com/fonts_list').text.split()
        return fontslist
    except RequestException as e:
        bot.logger.error(f"A request error {e.resp.status} occurred:\n{e.content}")
        return None
    
    