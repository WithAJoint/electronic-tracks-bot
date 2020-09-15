from functools import singledispatchmethod
from electronictracksbot.config_reader import ConfigReader
from electronictracksbot.tracks_collector import TracksCollector
from telegram import Update, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, Filters, \
    MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext


def _insert_context_property(context: CallbackContext, properties: dict):
    for key, value in properties.items():
        context.user_data[key] = value


def _format_dialog_text(dialog, *entries):
    formatted_dialog = dict(dialog)
    formatted_dialog['TEXT'].format(*entries)
    return formatted_dialog


class ElectronicTracksBot:
    _MAIN_MENU, _EDIT_PROPERTY, _SET_NEW_VALUE = range(3)

    _MAIN_DIALOG = {
        'TEXT': '- Author -\n{}\n- Title -\n{}\n',
        'KEYBOARD': InlineKeyboardMarkup([[InlineKeyboardButton('Edit', callback_data='EDIT'),
                                           InlineKeyboardButton('Download', callback_data='DOWNLOAD')]]),
    }

    _EDIT_DIALOG = {
        'TEXT': '- Author -\n{}\n- Title -\n{}\n',
        'KEYBOARD': InlineKeyboardMarkup([[InlineKeyboardButton('Author', callback_data='AUTHOR'),
                                           InlineKeyboardButton('Title', callback_data='TITLE'),
                                           InlineKeyboardButton('Back', callback_data='BACK')]])
    }

    _SET_DIALOG = {
        'TEXT': 'Send new {}\n',
        'KEYBOARD': InlineKeyboardMarkup([])
    }

    def __init__(self, api_token, db_path, download_path):
        self._updater = Updater(api_token, use_context=True)
        self._tracks_collector = TracksCollector(db_path, download_path)
        self._init_handlers(self._updater.dispatcher)

    def _init_handlers(self, dispatcher: Dispatcher):
        dispatcher.add_handler(ConversationHandler(
            entry_points=[MessageHandler(Filters.entity('url'), self._init_collection_process)],
            states={
                self._MAIN_MENU: [CallbackQueryHandler(self._enter_edit_mode, pattern='^EDIT?'),
                                  CallbackQueryHandler(self._collect_track, pattern='^DOWNLOAD?')],
                self._EDIT_PROPERTY: [CallbackQueryHandler(self._return_to_main_menu, pattern='^BACK?'),
                                      CallbackQueryHandler(self._select_property_to_edit, pattern='^AUTHOR?|^TITLE?')],
                self._SET_NEW_VALUE: [MessageHandler(Filters.all, self._set_new_value)]
            },
            fallbacks=[]
        ))

    def _init_collection_process(self, update: Update, context: CallbackContext):
        track_link = update.message.text
        try:
            self._tracks_collector.acquire_metadata(track_link)
        except RuntimeError as ex:
            self._reply(update.message, str(ex))
            return None
        author = self._tracks_collector.get_author()
        title = self._tracks_collector.get_title()
        _insert_context_property(context, {'AUTHOR': author, 'TITLE': title})
        reply_dialog = _format_dialog_text(self._MAIN_DIALOG, author, title)
        self._reply(update.message, reply_dialog)
        return self._MAIN_MENU

    def _enter_edit_mode(self, update: Update, context: CallbackContext):
        reply_dialog = _format_dialog_text(self._EDIT_DIALOG, context.user_data['AUTHOR'], context.user_data['TITLE'])
        self._reply(update.callback_query, reply_dialog)
        return self._EDIT_PROPERTY

    def _return_to_main_menu(self, update: Update, context: CallbackContext):
        reply_dialog = _format_dialog_text(self._MAIN_DIALOG, context.user_data['AUTHOR'], context.user_data['TITLE'])
        self._reply(update.callback_query, reply_dialog)
        return self._MAIN_MENU

    def _select_property_to_edit(self, update: Update, context: CallbackContext):
        query = update.callback_query
        context.user_data['EDIT'] = query.data
        reply_dialog = _format_dialog_text(self._SET_DIALOG, query.data)
        self._reply(query, reply_dialog)
        return self._SET_NEW_VALUE

    def _set_new_value(self, update: Update, context: CallbackContext):
        new_value = update.message.text
        property_to_edit = context.user_data['EDIT']
        context.user_data[property_to_edit] = new_value
        self._reply(update.message, self._MAIN_DIALOG, context.user_data['AUTHOR'], context.user_data['TITLE'])
        return self._MAIN_MENU

    @singledispatchmethod
    def _reply(self, obj, dialog):
        raise NotImplementedError('\'obj\' type must be telegram.Message or telegram.CallbackQuery')

    @_reply.register
    def _(self, message: Message, dialog):
        message.reply_text(dialog['TEXT'], reply_markup=dialog['KEYBOARD'])

    @_reply.register
    def _(self, query: CallbackQuery, dialog):
        query.answer()
        query.edit_message_text(dialog['TEXT'], reply_markup=dialog['KEYBOARD'])

    def _collect_track(self, update: Update, text: CallbackContext):
        # check out how to send files
        pass

    def start_accepting_requests(self):
        self._updater.start_polling()
        self._updater.idle()


if __name__ == '__main__':
    config_reader = ConfigReader()
    api_token = config_reader.get('TELEGRAM', 'api-token')
    db_path = config_reader.get("DATABASE", 'path')
    download_path = config_reader.get("DOWNLOAD", 'folder')
    electronic_tracks_bot = ElectronicTracksBot(api_token, db_path, download_path)
    electronic_tracks_bot.start_accepting_requests()
