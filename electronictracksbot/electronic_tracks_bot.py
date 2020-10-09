from functools import singledispatchmethod

from telegram import Update, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, Filters, \
    MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext

from electronictracksbot.config_reader import ConfigReader
from electronictracksbot.core import CollectionManager


def _insert_context_property(context: CallbackContext, properties: dict):
    for key, value in properties.items():
        context.user_data[key] = value


class DialogScheme:

    def __init__(self, text_template, keyboard=InlineKeyboardMarkup([])):
        self._text_template = text_template
        self._keyboard = keyboard

    class Dialog:

        def __init__(self, text, keyboard):
            self._text = text
            self._keyboard = keyboard

        def parameterize(self):
            return {
                'text': self._text,
                'reply_markup': self._keyboard
            }

    def finalize(self, *entries):
        return DialogScheme.Dialog(self._text_template.format(*entries), self._keyboard)

    @staticmethod
    def create_fixed(text, keyboard=InlineKeyboardMarkup([])):
        return DialogScheme.Dialog(text, keyboard)


class ElectronicTracksBot:
    _MAIN_MENU, _EDIT_PROPERTY, _SET_NEW_VALUE = range(3)

    _MAIN_DIALOG = DialogScheme('- Author -\n{}\n- Title -\n{}\n',
                                InlineKeyboardMarkup([[InlineKeyboardButton('Edit', callback_data='EDIT'),
                                                       InlineKeyboardButton('Send', callback_data='SEND')]]))

    _EDIT_DIALOG = DialogScheme('- Author -\n{}\n- Title -\n{}\n',
                                InlineKeyboardMarkup([[InlineKeyboardButton('Author', callback_data='AUTHOR'),
                                                       InlineKeyboardButton('Title', callback_data='TITLE'),
                                                       InlineKeyboardButton('Back', callback_data='BACK')]]))

    _SET_DIALOG = DialogScheme('Send new {}\n')

    _DUPLICATE_WARNING_DIALOG = DialogScheme.create_fixed('This track is already in the collection')

    def __init__(self, api_token, collection_manager):
        self._updater = Updater(api_token, use_context=True)
        self._collection_manager = collection_manager
        self._init_handlers(self._updater.dispatcher)

    def _init_handlers(self, dispatcher: Dispatcher):
        dispatcher.add_handler(ConversationHandler(
            entry_points=[MessageHandler(Filters.entity('url'), self._collect_track)],
            states={
                self._MAIN_MENU: [CallbackQueryHandler(self._enter_edit_mode, pattern='^EDIT?'),
                                  CallbackQueryHandler(self._send_track, pattern='^SEND?')],
                self._EDIT_PROPERTY: [CallbackQueryHandler(self._return_to_main_menu, pattern='^BACK?'),
                                      CallbackQueryHandler(self._select_property_to_edit, pattern='^AUTHOR?|^TITLE?')],
                self._SET_NEW_VALUE: [MessageHandler(Filters.all, self._set_new_value)]
            },
            fallbacks=[]
        ))

    def _collect_track(self, update: Update, context: CallbackContext):
        track_link = update.message.text
        try:
            track = self._collection_manager.collectFromYoutube(track_link)
        except RuntimeError as ex:
            self._reply(update.message, str(ex))
            return None
        if not track.is_new():
            self._reply(update.message, self._DUPLICATE_WARNING_DIALOG)
        _insert_context_property(context, {'AUTHOR': track.get_author(), 'TITLE': track.get_title()})
        # reply_dialog = _format_dialog_text(self._MAIN_DIALOG, track.get_author(), track.get_title())
        dialog = self._MAIN_DIALOG.finalize(track.get_author(), track.get_title())
        self._reply(update.message, **dialog.parameterize())
        return self._MAIN_MENU

    def _enter_edit_mode(self, update: Update, context: CallbackContext):
        dialog = self._EDIT_DIALOG.finalize(context.user_data['AUTHOR'], context.user_data['TITLE'])
        self._reply(update.callback_query, **dialog.parameterize())
        return self._EDIT_PROPERTY

    def _return_to_main_menu(self, update: Update, context: CallbackContext):
        dialog = self._MAIN_DIALOG.finalize(context.user_data['AUTHOR'], context.user_data['TITLE'])
        self._reply(update.callback_query, **dialog.parameterize())
        return self._MAIN_MENU

    def _select_property_to_edit(self, update: Update, context: CallbackContext):
        query = update.callback_query
        context.user_data['EDIT'] = query.data
        dialog = self._SET_DIALOG.finalize(query.data)
        self._reply(query, **dialog.parameterize())
        return self._SET_NEW_VALUE

    def _set_new_value(self, update: Update, context: CallbackContext):
        new_value = update.message.text
        property_to_edit = context.user_data['EDIT']
        context.user_data[property_to_edit] = new_value
        dialog = self._MAIN_DIALOG.finalize(context.user_data['AUTHOR'], context.user_data['TITLE'])
        self._reply(update.message, **dialog.parameterize())
        return self._MAIN_MENU

    def _send_track(self, update: Update, context: CallbackContext):
        pass

    @singledispatchmethod
    def _reply(self, obj, **dialog):
        raise NotImplementedError('\'obj\' type must be telegram.Message or telegram.CallbackQuery')

    @_reply.register
    def _(self, message: Message, **dialog):
        message.reply_text(**dialog)

    @_reply.register
    def _(self, query: CallbackQuery, **dialog):
        query.answer()
        query.edit_message_text(**dialog)

    def start_accepting_requests(self):
        self._updater.start_polling()
        self._updater.idle()


if __name__ == '__main__':
    config_reader = ConfigReader()
    api_token = config_reader.get('TELEGRAM', 'api-token')
    db_path = config_reader.get("DATABASE", 'path')
    download_path = config_reader.get("DOWNLOAD", 'folder')

    collection_manager = CollectionManager(db_path, download_path)

    electronic_tracks_bot = ElectronicTracksBot(api_token, collection_manager)
    electronic_tracks_bot.start_accepting_requests()
