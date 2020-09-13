import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram.bot
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request


redis_db = None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def _start(update, context):
    keyboard = [[InlineKeyboardButton("Subscribe", callback_data='subscribe'),
                 InlineKeyboardButton("Unsubscribe", callback_data='unsubscribe')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('You can subscribe (or unsubscribe) to notifications from this bot:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query

    chat_id = update.effective_chat.id
    query_data = query.data
    if query_data == 'subscribe':
        ans = _subscribe(chat_id)
    elif query_data == 'unsubscribe':
        ans = _unsubscribe(chat_id)
    else:
        ans = 'Something goes wrong! Please, contat us - neurus.ru'

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=ans)


def _subscribe(user_id):
    global redis_db
    redis_db.insert_subscriber(user_id)
    return "You're subscribed"


def _unsubscribe(user_id):
    global redis_db
    redis_db.remove_subscriber(user_id)
    return "You're unsubscribed"


class MQBot(telegram.bot.Bot):
    """
    A subclass of Bot which delegates send method handling to MQ
    https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    """
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_photo(*args, **kwargs)


class TgBot:
    def __init__(self, token, redis):
        global redis_db
        redis_db = redis

        # the maximum amount of messages being sent by bots
        # is limited to 30 messages/second for all ordinary messages
        # and 20 messages/minute for group messages.
        q = mq.MessageQueue(all_burst_limit=2, all_time_limit_ms=5000)
        request = Request(con_pool_size=8)
        self.mbk_bot = MQBot(token, request=request, mqueue=q)
        self.updater = telegram.ext.updater.Updater(bot=self.mbk_bot, use_context=True)

        self.dispatcher = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        # register start() handler for '/start' command
        self.dispatcher.add_handler(CommandHandler('start', _start))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(button))

    def start_polling(self):
        self.updater.start_polling()

        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        #self.updater.idle()

    def send_notification(self, chat_id, msg):
        self.mbk_bot.send_message(chat_id=chat_id, text=msg)
        #self.mbk_bot.send_message(chat_id=chat_id, text='test')
        #self.mbk_bot.send_photo(chat_id, open(msg, 'rb'))
