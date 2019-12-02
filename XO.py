# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
import requests
import json
import redis
from bot_move import bot_move
import config

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
app = Flask(__name__)

new_play = {
            '/lt': ' ', '/ct': ' ', '/rt': ' ',
            '/lc': ' ', '/cc': ' ', '/rc': ' ',
            '/lb': ' ', '/cb': ' ', '/rb': ' '
           }

@app.route('/%s/XObot' % config.token, methods=['GET', 'POST'])
def XObot():
    data = request.get_json(force=True)  
    chat_id = return_chat_id(data)
    bot_text = return_bot_text(data)
    # Что хранится в redis:
    # chat_id = {'score_bot': 4, 'score_user': 5, 'xo': 'X/O',
    #            '/lt': ' ', '/ct': 'o', '/rt': ' ',
    #            '/lc': 'x', '/cc': 'x', '/rc': 'o',
    #            '/lb': ' ', '/cb': 'o', '/rb': 'o'}

    #/start /help
    if bot_text[0] in ['/start', '/help']:
        InlineKeyboardMarkup = return_button('play')
        text = "Let's play tic-tac-toe!"
        post_request('sendMessage', {'chat_id': chat_id, 'text': text, 'reply_markup': InlineKeyboardMarkup})
    #/play
    elif bot_text[0] == '/play':
        if r.exists(chat_id):
            # Если были игры, обнулить старую игру
            xo = 'X' if r.hget(chat_id, 'xo') == 'O' else 'O'
            xo_bot = 'O' if xo == 'X' else 'X'
            new_game = {'xo': xo}
            new_game.update(new_play)
            r.hmset(chat_id, new_game)
            if xo == 'O':
                # Сделать ход
                game_field = return_game_field(chat_id)
                index = bot_move(game_field, xo)
                # Записать ход бота в redis
                r.hset(chat_id, list(new_play.keys())[index], xo_bot)
        else:
            # Записать новый чатик в redis
            new_chat = {'score_bot': 0, 'score_user': 0, 'xo': 'X'}
            new_chat.update(new_play)
            r.hmset(chat_id, new_chat)
        InlineKeyboardMarkup = return_keyboard(chat_id)
        text = "Your turn"
        post_request('sendMessage', {'chat_id': chat_id, 'text': text, 'reply_markup': InlineKeyboardMarkup})
    #/lt /ct /rt /lc /cc /rc /lb /cb /rb
    elif bot_text[0] in ['/lt', '/ct', '/rt', '/lc', '/cc', '/rc', '/lb', '/cb', '/rb']:
        # Чел играет xo, бот играет xo_bot
        xo = r.hget(chat_id, 'xo')
        xo_bot = 'O' if xo == 'X' else 'X'
        # Проверить ход игрока
        if r.hget(chat_id, bot_text[0]) != ' ':
            text = 'You are cheating'
            message_id = return_message_id(data)
            InlineKeyboardMarkup = return_keyboard(chat_id)
            post_request('editMessageText', {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': InlineKeyboardMarkup})
        else:
            # Записать ход игрока в redis
            r.hset(chat_id, bot_text[0], xo)
            # Сделать ход
            game_field = return_game_field(chat_id)
            index = bot_move(game_field, xo)
            if type(index) != type(''):
                # Записать ход бота в redis
                try:
                    r.hset(chat_id, list(new_play.keys())[index[0]], xo_bot)
                    index = index[1]
                except TypeError:
                    r.hset(chat_id, list(new_play.keys())[index], xo_bot)
            text = "Next turn"
            InlineKeyboardMarkup = return_keyboard(chat_id)
            message_id = return_message_id(data)
            post_request('editMessageText', {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'reply_markup': InlineKeyboardMarkup})
            if type(index) == type(''):
                if index == 'You win!':
                    r.hincrby(chat_id, 'score_user', amount=1)
                elif index == 'You lose':
                    r.hincrby(chat_id, 'score_bot', amount=1)
                post_request('sendMessage', {'chat_id': chat_id, 'text': index})
                InlineKeyboardMarkup = return_button('play')
                score_user = r.hget(chat_id, 'score_user')
                score_bot = r.hget(chat_id, 'score_bot')
                post_request('sendMessage', {'chat_id': chat_id, 'text': 'Score %s:%s' % (score_bot, score_user), 'reply_markup': InlineKeyboardMarkup})
    else:
        text = bot_text[0]
        post_request('sendMessage', {'chat_id': chat_id, 'text': text})
    answer_callback_query(data)
    return ''

def post_request(method, data):
    url = 'https://api.telegram.org/bot%s/%s' % (config.token, method)
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def answer_callback_query(data):
    callback_query_id = return_callback_query_id(data)
    if callback_query_id:
        post_request('answerCallbackQuery', {'callback_query_id': callback_query_id})

def return_chat_id(data):
    if 'callback_query' not in data.keys():
        return data['message']['chat']['id']
    else:
        return data['callback_query']['message']['chat']['id']

def return_message_id(data):
    if 'callback_query' not in data.keys():
        return data['message']['message_id']
    else:
        return data['callback_query']['message']['message_id']

def return_callback_query_id(data):
    if 'callback_query' not in data.keys():
        return False
    else:
        return data['callback_query']['id']

def return_bot_text(data):
    if 'callback_query' not in data.keys():
        return data['message']['text'].split()
    else:
        return data['callback_query']['data'].split()

def return_button(text):
    InlineKeyboardButton = {'text': text, 'callback_data': '/%s' % text}
    KeyboardRow = [InlineKeyboardButton]
    InlineKeyboardMarkup = {'inline_keyboard': [KeyboardRow]}
    return InlineKeyboardMarkup 

def return_keyboard(chat_id):
    InlineKeyboardMarkup = {'inline_keyboard': []}
    KeyboardRow = []
    for i in new_play.keys():
        text = r.hget(chat_id, i)
        InlineKeyboardButton = {'text': text, 'callback_data': i}
        KeyboardRow.append(InlineKeyboardButton)
        if len(KeyboardRow) == 3:
            InlineKeyboardMarkup['inline_keyboard'].append(KeyboardRow)
            KeyboardRow = []
    return InlineKeyboardMarkup 

def return_game_field(chat_id):
    cur_game = r.hmget(chat_id, new_play.keys())
    game_field = [cur_game[:3], cur_game[3:6], cur_game[6:]]
    return game_field

    
if __name__ == "__main__":
    app.run(host='137.74.150.114', port='8443', ssl_context=('../cert.pem', '../key.pem'))
