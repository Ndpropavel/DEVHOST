# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import logging
import os
import random

import hikkatl
from hikkatl.tl.functions.channels import JoinChannelRequest
from hikkatl.tl.functions.messages import (
    GetDialogFiltersRequest,
    UpdateDialogFilterRequest,
)
from hikkatl.tl.types import Message
from hikkatl.utils import get_display_name

from .. import loader, log, main, utils
from .._internal import fw_protect, restart
from ..inline.types import InlineCall
from ..web import core

logger = logging.getLogger(__name__)

ALL_INVOKES = [
    "clear_entity_cache",
    "clear_fulluser_cache",
    "clear_fullchannel_cache",
    "clear_perms_cache",
    "clear_cache",
    "reload_core",
    "inspect_cache",
    "inspect_modules",
]


@loader.tds
class HikkaSettingsMod(loader.Module):
    """Advanced settings for Hikka Userbot"""

    strings = {
        "name": "HikkaSettings",
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Watchers:</b>\n\n<b>{}</b>"
        ),
        "no_args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>No arguments"
            " specified</b>"
        ),
        "invoke404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Internal debug method"
            "</b> <code>{}</code> <b>not found, ergo can't be invoked</b>"
        ),
        "module404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Module</b>"
            " <code>{}</code> <b>not found</b>"
        ),
        "invoke": (
            "<emoji document_id=5215519585150706301>👍</emoji> <b>Invoked internal debug"
            " method</b> <code>{}</code>\n\n<emoji"
            " document_id=5784891605601225888>🔵</emoji> <b>Result:\n{}</b>"
        ),
        "invoking": (
            "<emoji document_id=5213452215527677338>⏳</emoji> <b>Invoking internal"
            " debug method</b> <code>{}</code> <b>of</b> <code>{}</code><b>...</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Watcher {} not"
            " found</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Watcher {} is now"
            " <u>disabled</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Watcher {} is now"
            " <u>enabled</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>You need to specify"
            " watcher name</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick for this user"
            " is now {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Please, specify"
            " command to toggle NoNick for</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick for"
            "</b> <code>{}</code> <b>is now {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Command not found</b>"
        ),
        "inline_settings": "⚙️ <b>Here you can configure your Hikka settings</b>",
        "confirm_update": (
            "🧭 <b>Please, confirm that you want to update. Your userbot will be"
            " restarted</b>"
        ),
        "confirm_restart": "🔄 <b>Please, confirm that you want to restart</b>",
        "suggest_fs": "✅ Suggest FS for modules",
        "do_not_suggest_fs": "🚫 Suggest FS for modules",
        "use_fs": "✅ Always use FS for modules",
        "do_not_use_fs": "🚫 Always use FS for modules",
        "btn_restart": "🔄 Restart",
        "btn_update": "🧭 Update",
        "close_menu": "😌 Close menu",
        "custom_emojis": "✅ Custom emojis",
        "no_custom_emojis": "🚫 Custom emojis",
        "suggest_subscribe": "✅ Suggest subscribe to channel",
        "do_not_suggest_subscribe": "🚫 Suggest subscribe to channel",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>This command must be"
            " executed in chat</b>"
        ),
        "nonick_warning": (
            "Warning! You enabled NoNick with default prefix! "
            "You may get muted in Hikka chats. Change prefix or "
            "disable NoNick!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Reply to a message"
            " of user, which needs to be added to NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>This action will fully remove Hikka from this account and can't be"
            " reverted!</b>\n\n<i>- Hikka chats will be removed\n- Session will be"
            " terminated and removed\n- Hikka inline bot will be removed</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>Are you really sure you want to delete Hikka?</b>"
        ),
        "deauth_yes": "I'm sure",
        "deauth_no_1": "I'm not sure",
        "deauth_no_2": "I'm uncertain",
        "deauth_no_3": "I'm struggling to answer",
        "deauth_cancel": "🚫 Cancel",
        "deauth_confirm_btn": "😢 Delete",
        "uninstall": "😢 <b>Uninstalling Hikka...</b>",
        "uninstalled": (
            "😢 <b>Hikka uninstalled. Web interface is still active, you can add another"
            " account</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick is enabled"
            " for these commands:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick is enabled"
            " for these users:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick is enabled"
            " for these chats:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Nothing to"
            " show...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>This command gives access to your Hikka web interface. It's not"
            " recommended to run it in public group chats. Consider using it in <a"
            " href='tg://openmessage?user_id={}'>Saved messages</a>. Type"
            "</b> <code>{}proxypass force_insecure</code> <b>to ignore this warning</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>This command gives access to your Hikka web interface. It's not"
            " recommended to run it in public group chats. Consider using it in <a"
            " href='tg://openmessage?user_id={}'>Saved messages</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Opening tunnel to Hikka web interface...</b>",
        "tunnel_opened": "🎉 <b>Tunnel opened. This link is valid for about 1 hour</b>",
        "web_btn": "🌍 Web interface",
        "btn_yes": "🚸 Open anyway",
        "btn_no": "🔻 Cancel",
        "lavhost_web": (
            "✌️ <b>This link leads to your Hikka web interface on lavHost</b>\n\n<i>💡"
            " You'll need to authorize using lavHost credentials, specified on"
            " registration</i>"
        ),
        "disable_debugger": "✅ Debugger enabled",
        "enable_debugger": "🚫 Debugger disabled",
    }

    strings_ru = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Смотрители:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Смотритель {} не"
            " найден</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Смотритель {} теперь"
            " <u>выключен</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Смотритель {} теперь"
            " <u>включен</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Укажи имя"
            " смотрителя</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Состояние NoNick для"
            " этого пользователя: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Укажи команду, для"
            " которой надо включить\\выключить NoNick</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Состояние NoNick для"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Команда не найдена</b>"
        ),
        "inline_settings": "⚙️ <b>Здесь можно управлять настройками Hikka</b>",
        "confirm_update": "🧭 <b>Подтвердите обновление. Юзербот будет перезагружен</b>",
        "confirm_restart": "🔄 <b>Подтвердите перезагрузку</b>",
        "suggest_fs": "✅ Предлагать сохранение модулей",
        "do_not_suggest_fs": "🚫 Предлагать сохранение модулей",
        "use_fs": "✅ Всегда сохранять модули",
        "do_not_use_fs": "🚫 Всегда сохранять модули",
        "btn_restart": "🔄 Перезагрузка",
        "btn_update": "🧭 Обновление",
        "close_menu": "😌 Закрыть меню",
        "custom_emojis": "✅ Кастомные эмодзи",
        "no_custom_emojis": "🚫 Кастомные эмодзи",
        "suggest_subscribe": "✅ Предлагать подписку на канал",
        "do_not_suggest_subscribe": "🚫 Предлагать подписку на канал",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Эту команду нужно"
            " выполнять в чате</b>"
        ),
        "_cls_doc": "Дополнительные настройки Hikka",
        "nonick_warning": (
            "Внимание! Ты включил NoNick со стандартным префиксом! "
            "Тебя могут замьютить в чатах Hikka. Измени префикс или "
            "отключи глобальный NoNick!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Ответь на сообщение"
            " пользователя, для которого нужно включить NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Это действие полностью удалит Hikka с этого аккаунта! Его нельзя"
            " отменить</b>\n\n<i>- Все чаты, связанные с Hikka будут удалены\n- Сессия"
            " Hikka будет сброшена\n- Инлайн бот Hikka будет удален</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Ты точно уверен, что хочешь удалить Hikka?</b>",
        "deauth_yes": "Я уверен",
        "deauth_no_1": "Я не уверен",
        "deauth_no_2": "Не точно",
        "deauth_no_3": "Нет",
        "deauth_cancel": "🚫 Отмена",
        "deauth_confirm_btn": "😢 Удалить",
        "uninstall": "😢 <b>Удаляю Hikka...</b>",
        "uninstalled": (
            "😢 <b>Hikka удалена. Веб-интерфейс все еще активен, можно добавить другие"
            " аккаунты!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих команд:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих пользователей:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick включен для"
            " этих чатов:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Нечего"
            " показывать...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Эта команда дает доступ к веб-интерфейсу Hikka. Ее выполнение в"
            " публичных чатах является угрозой безопасности. Предпочтительно выполнять"
            " ее в <a href='tg://openmessage?user_id={}'>Избранных сообщениях</a>."
            " Выполни</b> <code>{}proxypass force_insecure</code> <b>чтобы отключить"
            " это предупреждение</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Эта команда дает доступ к веб-интерфейсу Hikka. Ее выполнение в"
            " публичных чатах является угрозой безопасности. Предпочтительно выполнять"
            " ее в <a href='tg://openmessage?user_id={}'>Избранных сообщениях</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Открываю тоннель к веб-интерфейсу Hikka...</b>",
        "tunnel_opened": (
            "🎉 <b>Тоннель открыт. Эта ссылка будет активна не более часа</b>"
        ),
        "web_btn": "🌍 Веб-интерфейс",
        "btn_yes": "🚸 Все равно открыть",
        "btn_no": "🔻 Закрыть",
        "lavhost_web": (
            "✌️ <b>По этой ссылке ты попадешь в веб-интерфейс Hikka на"
            " lavHost</b>\n\n<i>💡 Тебе нужно будет авторизоваться, используя данные,"
            " указанные при настройке lavHost</i>"
        ),
        "disable_debugger": "✅ Отладчик включен",
        "enable_debugger": "🚫 Отладчик выключен",
    }

    strings_fr = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Les observateurs:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>L'observateur {} n'est"
            " pas trouvé</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>L'observateur {} est"
            " maintenant <u>désactivé</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>L'observateur {} est"
            " maintenant <u>activé</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Indiquez le nom"
            " de l'observateur</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>L'état de NoNick pour"
            " cet utilisateur: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Indiquez la commande"
            " pour laquelle vous souhaitez activer\\désactiver NoNick</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>L'état de NoNick"
            " pour</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Commande non"
            " trouvée</b>"
        ),
        "inline_settings": "⚙️ <b>Vous pouvez gérer les paramètres Hikka ici</b>",
        "confirm_update": (
            "🧭 <b>Confirmez la mise à jour. L'utilisateur-bot sera redémarré</b>"
        ),
        "confirm_restart": "🔄 <b>Confirmez le redémarrage</b>",
        "suggest_fs": "✅ Suggérer l'enregistrement des modules",
        "do_not_suggest_fs": "🚫 Suggérer l'enregistrement des modules",
        "use_fs": "✅ Toujours enregistrer les modules",
        "do_not_use_fs": "🚫 Toujours enregistrer les modules",
        "btn_restart": "🔄 Redémarrer",
        "btn_update": "🧭 Mise à jour",
        "close_menu": "😌 Fermer le menu",
        "custom_emojis": "✅ Émoticônes personnalisées",
        "no_custom_emojis": "🚫 Émoticônes personnalisées",
        "suggest_subscribe": "✅ Suggérer l'abonnement au canal",
        "do_not_suggest_subscribe": "🚫 Suggérer l'abonnement au canal",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Vous devez exécuter"
            " cette commande dans un chat</b>"
        ),
        "_cls_doc": "Paramètres supplémentaires Hikka",
        "nonick_warning": (
            "Attention! Vous avez activé NoNick avec le préfixe standard! "
            "Vous pouvez être muté dans les chats Hikka. Changez le préfixe ou "
            "désactivez NoNick global!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Répondez au message"
            " de l'utilisateur pour lequel vous devez activer NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Cette action supprimera complètement Hikka de ce compte! Il ne peut"
            " pas être annulé</b>\n\n<i>- Toutes les conversations liées à Hikka seront"
            " supprimées\n- La session Hikka sera réinitialisée\n- Le bot en ligne"
            " Hikka sera supprimé</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Êtes-vous sûr de vouloir supprimer Hikka?</b>",
        "deauth_yes": "Je suis sûr",
        "deauth_no_1": "Je ne suis pas sûr",
        "deauth_no_2": "Pas vraiment",
        "deauth_no_3": "Non",
        "deauth_cancel": "🚫 Annuler",
        "deauth_confirm_btn": "😢 Supprimer",
        "uninstall": "😢 <b>Je supprime Hikka...</b>",
        "uninstalled": (
            "😢 <b>Hikka a été supprimé. L'interface Web est toujours active, vous"
            " pouvez ajouter d'autres comptes!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick est activé pour"
            " ces commandes:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick est activé"
            " pour ces utilisateurs:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick est activé"
            " pour ces groupes:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Rien à"
            " montrer...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Cette commande donne accès à l'interface web de Hikka. L'exécution"
            " dans les groupes est une menace pour la sécurité. Préférez l'exécution"
            " dans <a href='tg://openmessage?user_id={}'>Messages favoris</a>."
            " Exécutez</b> <code>{}proxypass force_insecure</code> <b>pour désactiver"
            " cette alerte</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Cette commande donne accès à l'interface web de Hikka. L'exécution"
            " dans les groupes est une menace pour la sécurité. Préférez l'exécution"
            " dans <a href='tg://openmessage?user_id={}'>Messages favoris</a>.</b>"
        ),
        "opening_tunnel": (
            "🔁 <b>Ouverture du tunnel vers l'interface web de Hikka...</b>"
        ),
        "tunnel_opened": (
            "🎉 <b>Tunnel ouvert. Ce lien ne sera actif que pendant une heure</b>"
        ),
        "web_btn": "🌍 Interface web",
        "btn_yes": "🚸 Ouvrir quand même",
        "btn_no": "🔻 Fermer",
        "lavhost_web": (
            "✌️ <b>En cliquant sur ce lien, tu accèderas à l'interface web de Hikka"
            " sur lavHost</b>\n\n<i>💡 Tu devras t'authentifier avec les données"
            " spécifiées lors de la configuration de lavHost</i>"
        ),
        "disable_debugger": "✅ Débogueur activé",
        "enable_debugger": "🚫 Débogueur désactivé",
    }

    strings_it = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Guardiani:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Il guardiano {} non"
            " è stato trovato</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Il guardiano {} è"
            " <u>disabilitato</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Il guardiano {} è"
            " <u>abilitato</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Specifica il nome del"
            " guardiano</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Stato di NoNick per"
            " questo utente: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Specifica il comando"
            " per cui vuoi abilitare\\disabilitare NoNick</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Stato di NoNick per"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Comando non"
            " trovato</b>"
        ),
        "inline_settings": "⚙️ <b>Qui puoi gestire le impostazioni di Hikka</b>",
        "confirm_update": "🧭 <b>Conferma l'aggiornamento. Il bot verrà riavviato</b>",
        "confirm_restart": "🔄 <b>Conferma il riavvio</b>",
        "suggest_fs": "✅ Suggerisci il salvataggio dei moduli",
        "do_not_suggest_fs": "🚫 Suggerisci il salvataggio dei moduli",
        "use_fs": "✅ Salva sempre i moduli",
        "do_not_use_fs": "🚫 Salva sempre i moduli",
        "btn_restart": "🔄 Riavvia",
        "btn_update": "🧭 Aggiorna",
        "close_menu": "😌 Chiudi il menu",
        "custom_emojis": "✅ Emoji personalizzate",
        "no_custom_emojis": "🚫 Emoji personalizzati",
        "suggest_subscribe": "✅ Suggest subscribe to channel",
        "do_not_suggest_subscribe": "🚫 Non suggerire l'iscrizione al canale",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Questo comando deve"
            " essere eseguito in un gruppo</b>"
        ),
        "_cls_doc": "Impostazioni aggiuntive di Hikka",
        "nonick_warning": (
            "Attenzione! Hai abilitato NoNick con il prefisso predefinito! "
            "Puoi essere mutato nei gruppi di Hikka. Modifica il prefisso o "
            "disabilita NoNick!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Rispondi al messaggio"
            " di un utente per cui vuoi abilitare NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Questa azione rimuoverà completamente Hikka da questo account! Non"
            " può essere annullata</b>\n\n<i>- Tutte le chat associate a Hikka saranno"
            " rimosse\n- La sessione Hikka verrà annullata\n- Il bot inline Hikka verrà"
            " rimosso</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Sei sicuro di voler rimuovere Hikka?</b>",
        "deauth_yes": "Sono sicuro",
        "deauth_no_1": "Non sono sicuro",
        "deauth_no_2": "Non esattamente",
        "deauth_no_3": "No",
        "deauth_cancel": "🚫 Annulla",
        "deauth_confirm_btn": "😢 Rimuovi",
        "uninstall": "😢 <b>Rimuovo Hikka...</b>",
        "uninstalled": (
            "😢 <b>Hikka è stata rimossa. L'interfaccia web è ancora attiva, puoi"
            " aggiungere altri account!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick abilitato"
            " per queste comandi:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick abilitato"
            " per questi utenti:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick abilitato"
            " per queste chat:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Niente"
            " da mostrare...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Questo comando dà accesso all'interfaccia web di Hikka. La sua"
            " esecuzione in chat pubbliche è un pericolo per la sicurezza. E' meglio"
            " eseguirla in <a href='tg://openmessage?user_id={}'>Messaggi"
            " Preferiti</a>. Esegui</b> <code>{}proxypass force_insecure</code> <b>per"
            " disattivare questo avviso</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Questo comando dà accesso all'interfaccia web di Hikka. La sua"
            " esecuzione in chat pubbliche è un pericolo per la sicurezza. E' meglio"
            " eseguirla in <a href='tg://openmessage?user_id={}'>Messaggi"
            " Preferiti</a>.</b>"
        ),
        "opening_tunnel": (
            "🔁 <b>Sto aprendo il tunnel all'interfaccia web di Hikka...</b>"
        ),
        "tunnel_opened": (
            "🎉 <b>Tunnel aperto. Questo link sarà attivo per un massimo di un ora</b>"
        ),
        "web_btn": "🌍 Interfaccia web",
        "btn_yes": "🚸 Comunque apri",
        "btn_no": "🔻 Chiudi",
        "lavhost_web": (
            "✌️ <b>Collegandoti a questo link entrerai nell'interfaccia web di Hikka su"
            " lavHost</b>\n\n<i>💡 Dovrai autenticarti utilizzando le credenziali"
            " impostate su lavHost</i>"
        ),
        "disable_debugger": "✅ Debugger abilitato",
        "enable_debugger": "🚫 Debugger disabilitato",
    }

    strings_de = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Beobachter:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Beobachter {} nicht"
            "gefunden</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Watcher {} ist jetzt"
            " <u>aus</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Watcher {} ist jetzt"
            " <u>aktiviert</u></b>"
        ),
        "arg": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Bitte geben Sie einen"
            " Namen einHausmeister</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick-Status für"
            " dieser Benutzer: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Geben Sie einen Befehl"
            " anwas NoNick aktivieren/\\deaktivieren sollte</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick-Status für"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Befehl nicht"
            " gefunden</b>"
        ),
        "inline_settings": (
            "⚙️ <b>Hier können Sie Ihre Hikka-Einstellungen verwalten</b>"
        ),
        "confirm_update": (
            "🧭 <b>Bestätige das Update. Der Userbot wird neu gestartet</b>"
        ),
        "confirm_restart": "🔄 <b>Neustart bestätigen</b>",
        "suggest_fs": "✅ Speichermodule vorschlagen",
        "do_not_suggest_fs": "🚫 Speichermodule vorschlagen",
        "use_fs": "✅ Module immer speichern",
        "do_not_use_fs": "🚫 Module immer speichern",
        "btn_restart": "🔄 Neustart",
        "btn_update": "🧭 Aktualisieren",
        "close_menu": "😌 Menü schließen",
        "custom_emojis": "✅ Benutzerdefinierte Emojis",
        "no_custom_emojis": "🚫 Benutzerdefinierte Emojis",
        "suggest_subscribe": "✅ Kanalabonnement vorschlagen",
        "do_not_suggest_subscribe": "🚫 Kanalabonnement vorschlagen",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Dieser Befehl benötigt"
            "im Chat ausführen</b>"
        ),
        "_cls_doc": "Erweiterte Hikka-Einstellungen",
        "nonick_warning": (
            "Achtung! Sie haben NoNick mit dem Standard-Präfix eingefügt!Sie sind"
            " möglicherweise in Hikka-Chats stummgeschaltet. Ändern Sie das Präfix oder"
            " schalten Sie das globale NoNick aus!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Auf Nachricht"
            " antwortenBenutzer soll NoNick aktivieren</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Diese Aktion wird Hikka vollständig von diesem Konto entfernen! Er"
            " kann nichtAbbrechen</b>\n\n<i>- Alle Hikka-bezogenen Chats werden"
            " gelöscht\n- SitzungHikka wird zurückgesetzt\n- Hikkas Inline-Bot wird"
            " gelöscht</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>Sind Sie sicher, dass Sie Hikka deinstallieren möchten?</b>"
        ),
        "deauth_yes": "Ich bin sicher",
        "deauth_no_1": "Ich bin mir nicht sicher",
        "deauth_no_2": "Nicht sicher",
        "deauth_no_3": "Nein",
        "deauth_cancel": "🚫 Abbrechen",
        "deauth_confirm_btn": "😢 Löschen",
        "uninstall": "😢 <b>Hikka wird deinstalliert...</b>",
        "uninstalled": (
            "😢 <b>Hikka wurde entfernt. Die Weboberfläche ist noch aktiv, andere können"
            " hinzugefügt werdenKonten!</b>"
        ),
        "cmd_nn_liste": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick aktiviert für"
            " diese Befehle:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick aktiviert für"
            " diese Benutzer:</b>\n\n{}"
        ),
        "chat_nn_liste": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick aktiviert für"
            " diese Chats:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Nichtszeigen...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Dieser Befehl ermöglicht den Zugriff auf die Hikka-Weboberfläche."
            " Seine Ausführung inÖffentliche Chats sind ein Sicherheitsrisiko. Am"
            " besten durchführen es in <a href='tg://openmessage?user_id={}'>Empfohlene"
            " Nachrichten</a>.Führen Sie</b> <code>{}proxypass force_insecure</code><b>"
            " zum Deaktivieren ausDies ist eine Warnung</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Dieser Befehl ermöglicht den Zugriff auf die Hikka-Weboberfläche."
            " Seine Ausführung inÖffentliche Chats sind ein Sicherheitsrisiko. Am"
            " besten durchführen sie in <a"
            " href='tg://openmessage?user_id={}'>Empfohlene Nachrichten</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Öffne einen Tunnel zur Hikka-Weboberfläche...</b>",
        "tunnel_opened": (
            "🎉 <b>Der Tunnel ist offen. Dieser Link ist nicht länger als eine Stunde"
            " aktiv</b>"
        ),
        "web_btn": "🌍 Webinterface",
        "btn_yes": "🚸 Trotzdem geöffnet",
        "btn_no": "🔻 Schließen",
        "lavhost_web": (
            "✌️ <b>Dieser Link führt Sie zur Hikka-Weboberfläche auf"
            " lavHost</b>\n\n<i>💡 Sie müssen sich mit Ihren Zugangsdaten anmelden,"
            "beim Setzen von lavHost angegeben</i>"
        ),
        "disable_debugger": "✅ Debugger aktiviert",
        "enable_debugger": "🚫 Debugger deaktiviert",
    }

    strings_tr = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>İzleyiciler:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>İzleyici {} değil"
            " bulundu</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>İzleyici {} şimdi"
            " <u>kapalı</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>İzleyici {} şimdi"
            " <u>etkin</u></b>"
        ),
        "arg": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Lütfen bir ad girin"
            "bekçi</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick durumu için"
            " bu kullanıcı: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Bir komut belirtin"
            "hangisi NoNick'i etkinleştirmeli/devre dışı bırakmalıdır</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick durumu için"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Komut bulunamadı</b>"
        ),
        "inline_settings": "⚙️ <b>Buradan Hikka ayarlarınızı yönetebilirsiniz</b>",
        "confirm_update": (
            "🧭 <b>Güncellemeyi onaylayın. Kullanıcı robotu yeniden başlatılacak</b>"
        ),
        "confirm_restart": "🔄 <b>Yeniden başlatmayı onayla</b>",
        "suggest_fs": "✅ Kaydetme modülleri öner",
        "do_not_suggest_fs": "🚫 Modüllerin kaydedilmesini öner",
        "use_fs": "✅ Modülleri her zaman kaydet",
        "do_not_use_fs": "🚫 Modülleri her zaman kaydet",
        "btn_restart": "🔄 Yeniden Başlat",
        "btn_update": "🧭 Güncelle",
        "close_menu": "😌 Menüyü kapat",
        "custom_emojis": "✅ Özel emojiler",
        "no_custom_emojis": "🚫 Özel Emojiler",
        "suggest_subscribe": "✅ Kanal aboneliği öner",
        "do_not_suggest_subscribe": "🚫 Kanal aboneliği öner",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Bu komut gerekiyor"
            " sohbette yürüt</b>"
        ),
        "_cls_doc": "Gelişmiş Hikka Ayarları",
        "nonick_warning": (
            "Dikkat! NoNick'i standart önekle eklediniz!"
            "Hikka sohbetlerinde sesiniz kapatılmış olabilir. Ön eki değiştirin veya "
            "küresel NoNick'i kapatın!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Mesajı yanıtla"
            "NoNick'i etkinleştirmek için kullanıcı</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Bu işlem Hikka'yı bu hesaptan tamamen kaldıracak! Yapamaz"
            "iptal</b>\n\n<i>- Hikka ile ilgili tüm sohbetler silinecek\n- Oturum"
            " Hikka sıfırlanacak\n- Hikka'nın satır içi botu silinecek</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>Hikka'yı kaldırmak istediğinizden emin misiniz?</b>"
        ),
        "deauth_yes": "Eminim",
        "deauth_no_1": "Emin değilim",
        "deauth_no_2": "Emin değilim",
        "deauth_no_3": "Hayır",
        "deauth_cancel": "🚫 İptal",
        "deauth_confirm_btn": "😢 Sil",
        "uninstall": "😢 <b>Hikka'yı Kaldırılıyor...</b>",
        "uninstalled": (
            "😢 <b>Hikka kaldırıldı. Web arayüzü hala aktif, başkaları eklenebilir"
            "hesaplar!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick için"
            " etkinleştirildi bu komutlar:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick için"
            " etkinleştirildi bu kullanıcılar:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick için"
            " etkinleştirildi bu sohbetler:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Hiçbir şey"
            "göster...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Bu komut, Hikka web arayüzüne erişim sağlar. YürütülmesiGenel"
            " sohbetler bir güvenlik riskidir. Tercihen gerçekleştirin <a"
            " href='tg://openmessage?user_id={}'>Öne Çıkan Mesajlar</a> içinde.Devre"
            " dışı bırakmak için</b> <code>{}proxypass force_insecure</code><b>"
            " çalıştırınbu bir uyarıdır</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Bu komut, Hikka web arayüzüne erişim sağlar. Yürütülmesi"
            "Genel sohbetler bir güvenlik riskidir. Tercihen gerçekleştirin"
            " onu <a href='tg://openmessage?user_id={}'>Öne Çıkan Mesajlar</a>'da.</b>"
        ),
        "disable_debugger": "✅ Hata ayıklayıcı etkin",
        "enable_debugger": "🚫 Hata Ayıklayıcı devre dışı",
    }

    strings_uz = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Kuzatuvchilar:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Kuzuvchi {} emas"
            " topildi</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Kuzatuvchi {} hozir"
            " <u>o'chirilgan</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Kuzatuvchi {} hozir"
            " <u>yoqilgan</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Iltimos, nom kiriting"
            "qorovul</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick holati uchun"
            " bu foydalanuvchi: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Buyruqni belgilang"
            "bu NoNickni yoqish/o'chirish kerak</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick holati uchun"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Buyruq topilmadi</b>"
        ),
        "inline_settings": (
            "⚙️ <b>Bu yerda siz Hikka sozlamalaringizni boshqarishingiz mumkin</b>"
        ),
        "confirm_update": (
            "🧭 <b>Yangilanishni tasdiqlang. Userbot qayta ishga tushiriladi</b>"
        ),
        "confirm_restart": "🔄 <b>Qayta ishga tushirishni tasdiqlang</b>",
        "suggest_fs": "✅ Modullarni saqlashni taklif qilish",
        "do_not_suggest_fs": "🚫 Modullarni saqlashni taklif qilish",
        "use_fs": "✅ Modullarni doimo saqlash",
        "do_not_use_fs": "🚫 Har doim modullarni saqlang",
        "btn_restart": "🔄 Qayta ishga tushirish",
        "btn_update": "🧭 Yangilash",
        "close_menu": "😌 Menyuni yopish",
        "custom_emojis": "✅ Maxsus emojilar",
        "no_custom_emojis": "🚫 Maxsus kulgichlar",
        "suggest_subscribe": "✅ Kanalga obuna bo'lishni taklif qilish",
        "do_not_suggest_subscribe": "🚫 Kanalga obuna bo'lishni taklif qilish",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Bu buyruq kerak"
            " chatda bajarish</b>"
        ),
        "_cls_doc": "Kengaytirilgan Hikka sozlamalari",
        "nonick_warning": (
            "Diqqat! NoNickni standart prefiks bilan kiritdingiz!Hikka chatlarida"
            " ovozingiz o'chirilgan bo'lishi mumkin. Prefiksni o'zgartiring yoki global"
            " NoNickni o'chiring!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Xatga javob berish"
            "foydalanuvchi NoNick</b>ni yoqish uchun"
        ),
        "deauth_confirm": (
            "⚠️ <b>Bu amal Hikkani ushbu hisobdan butunlay olib tashlaydi! U qila"
            " olmaydiBekor qilish</b>\n\n<i>- Hikka bilan bog'liq barcha chatlar"
            " o'chiriladi\n- Sessiya Hikka qayta tiklanadi\n- Hikkaning ichki boti"
            " o'chiriladi</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>Haqiqatan ham Hikkani o'chirib tashlamoqchimisiz?</b>"
        ),
        "deauth_yes": "Ishonchim komil",
        "deauth_no_1": "Imonim yo'q",
        "deauth_no_2": "Ishonasiz",
        "deauth_no_3": "Yo'q",
        "deauth_cancel": "🚫 Bekor qilish",
        "deauth_confirm_btn": "😢 O'chirish",
        "uninstall": "😢 <b>Hikka o'chirilmoqda...</b>",
        "uninstalled": (
            "😢 <b>Hikka o'chirildi. Veb-interfeys hali ham faol, boshqalarni qo'shish"
            " mumkinhisoblar!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " bu buyruqlar:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " bu foydalanuvchilar:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick yoqilgan"
            " bu chatlar:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Hech narsa"
            "ko'rsatish...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Ushbu buyruq Hikka veb-interfeysiga kirish imkonini beradi. Uning"
            " bajarilishiOmmaviy chatlar xavfsizlikka xavf tug'diradi. Afzal bajaring"
            " Bu <a href='tg://openmessage?user_id={}'>Taniqli xabarlar</a>da.O'chirish"
            " uchun</b> <code>{}proxypass force_insecure</code><b>ni ishga tushiring bu"
            " ogohlantirish</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Ushbu buyruq Hikka veb-interfeysiga kirish imkonini beradi. Uning"
            " bajarilishiOmmaviy chatlar xavfsizlikka xavf tug'diradi. Afzal bajaring u"
            " <a href='tg://openmessage?user_id={}'>Mazkur xabarlarda</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Hikka veb-interfeysiga tunnel ochilmoqda...</b>",
        "tunnel_opened": (
            "🎉 <b>Tunnel ochiq. Bu havola bir soatdan ko'p bo'lmagan vaqt davomida faol"
            " bo'ladi</b>"
        ),
        "web_btn": "🌍 Veb interfeysi",
        "btn_yes": "🚸 Baribir ochiq",
        "btn_no": "🔻 Yopish",
        "lavhost_web": (
            "✌️ <b>Ushbu havola sizni Hikka veb-interfeysiga olib boradi"
            " lavHost</b>\n\n<i>💡 Hisob ma'lumotlaringizdan foydalanib tizimga"
            " kirishingiz kerak,lavHost</i>ni sozlashda ko'rsatilgan"
        ),
        "disable_debugger": "✅ Debugger yoqilgan",
        "enable_debugger": "🚫 Debugger o'chirilgan",
    }

    strings_es = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Los espectadores:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>El espectador {} no"
            " encontrado</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>El espectador {} ahora"
            " <u>desactivado</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>El espectador {} ahora"
            " <u>activado</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Indica el nombre"
            " del espectador</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>El estado de NoNick"
            " para este usuario: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Indica el comando,"
            " para el que se debe habilitar\\deshabilitar NoNick</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>El estado de NoNick"
            " para</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>El comando no se"
            " encuentra</b>"
        ),
        "inline_settings": (
            "⚙️ <b>Aquí puedes administrar las configuraciones de Hikka</b>"
        ),
        "confirm_update": (
            "🧭 <b>Confirma la actualización. El usuario del bot se reiniciará</b>"
        ),
        "confirm_restart": "🔄 <b>Confirma el reinicio</b>",
        "suggest_fs": "✅ Sugerir guardar módulos",
        "do_not_suggest_fs": "🚫 Sugerir guardar módulos",
        "use_fs": "✅ Guardar módulos siempre",
        "do_not_use_fs": "🚫 Guardar módulos siempre",
        "btn_restart": "🔄 Reiniciar",
        "btn_update": "🧭 Actualización",
        "close_menu": "😌 Cerrar menú",
        "custom_emojis": "✅ Emojis personalizados",
        "no_custom_emojis": "🚫 Emojis personalizados",
        "suggest_subscribe": "✅ Sugerir suscribirse al canal",
        "do_not_suggest_subscribe": "🚫 Sugerir suscribirse al canal",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Debes ejecutar este"
            " comando en un chat</b>"
        ),
        "_cls_doc": "Configuración adicional de Hikka",
        "nonick_warning": (
            "¡Atención! ¡Has activado NoNick con el prefijo predeterminado! "
            "Pueden silenciarte en los chats de Hikka. ¡Cambie el prefijo o "
            "desactive NoNick globalmente!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Responde al mensaje"
            " del usuario al que desea activar NoNick</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>¡Esta acción eliminará completamente Hikka de esta cuenta! No se"
            " puede deshacer</b>\n\n<i>- Todos los chats vinculados a Hikka serán"
            " eliminados\n- La sesión de Hikka se restablecerá\n- El bot de línea de"
            " Hikka se eliminará</i>"
        ),
        "deauth_confirm_step2": (
            "⚠️ <b>¿Estás seguro de que quieres eliminar Hikka?</b>"
        ),
        "deauth_yes": "Estoy seguro",
        "deauth_no_1": "No estoy seguro",
        "deauth_no_2": "No es cierto",
        "deauth_no_3": "No",
        "deauth_cancel": "🚫 Cancelar",
        "deauth_confirm_btn": "😢 Eliminar",
        "uninstall": "😢 <b>Eliminando Hikka...</b>",
        "uninstalled": (
            "😢 <b>Hikka eliminada. La interfaz web sigue activa, ¡puedes agregar otras"
            " cuentas!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick activado para"
            " estos comandos:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick activado para"
            " estos usuarios:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick activado para"
            " estos chats:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Nada"
            " para mostrar...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Este comando da acceso al interfaz web de Hikka. Su ejecución en"
            " chats públicos es una amenaza para la seguridad. Es preferible ejecutarlo"
            " en <a href='tg://openmessage?user_id={}'>Mensajes Favoritos</a>."
            " Ejecute</b> <code>{}proxypass force_insecure</code> <b>para desactivar"
            " este aviso</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Este comando da acceso al interfaz web de Hikka. Su ejecución en"
            " chats públicos es una amenaza para la seguridad. Es preferible ejecutarlo"
            " en <a href='tg://openmessage?user_id={}'>Mensajes Favoritos</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Abriendo túnel al interfaz web de Hikka...</b>",
        "tunnel_opened": (
            "🎉 <b>Túnel abierto. Esta enlace estará activo no más de una hora</b>"
        ),
        "web_btn": "🌍 Interfaz Web",
        "btn_yes": "🚸 De todas formas, abrir",
        "btn_no": "🔻 Cerrar",
        "lavhost_web": (
            "✌️ <b>En este enlace entrarás al interfaz web de Hikka en"
            " lavHost</b>\n\n<i>💡 Necesitarás autorizarte con los datos"
            " indicados en la configuración de lavHost</i>"
        ),
        "disable_debugger": "✅ Depurador activado",
        "enable_debugger": "🚫 Depurador desactivado",
    }

    strings_kk = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Қараушылар:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Қараушы {} жоқ"
            " табылды</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Қазір {} бақылаушысы"
            " <u>өшіру</u></b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Қазір {} бақылаушысы"
            " <u>қосылған</u></b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Атын енгізіңіз"
            "қамқоршы</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick күйі үшін"
            " бұл пайдаланушы: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Пәрменді көрсетіңіз"
            "ол NoNick</b>қосу/өшіру керек"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick күйі үшін"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Пәрмен табылмады</b>"
        ),
        "inline_settings": "⚙️ <b>Осында Hikka параметрлерін басқаруға болады</b>",
        "confirm_update": "🧭 <b>Жаңартуды растаңыз. Userbot қайта іске қосылады</b>",
        "confirm_restart": "🔄 <b>Қайта қосуды растау</b>",
        "suggest_fs": "✅ Сақтау модульдерін ұсыну",
        "do_not_suggest_fs": "🚫 Сақтау модульдерін ұсыну",
        "use_fs": "✅ Модульдерді әрқашан сақтау",
        "do_not_use_fs": "🚫 Әрқашан модульдерді сақта",
        "btn_restart": "🔄 Қайта іске қосу",
        "btn_update": "🧭 Жаңарту",
        "close_menu": "😌 Мәзірді жабу",
        "custom_emojis": "✅ Арнайы эмодзилер",
        "no_custom_emojis": "🚫 Арнаулы эмодзилер",
        "suggest_subscribe": "✅ Арнаға жазылуды ұсыну",
        "do_not_suggest_subscribe": "🚫 Арнаға жазылуды ұсыну",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Бұл пәрмен қажет"
            " чатта орындау</b>"
        ),
        "_cls_doc": "Қосымша Hikka параметрлері",
        "nonick_warning": (
            "Назар аударыңыз! Сіз стандартты префикспен NoNick қостыңыз!"
            "Hikka чаттарындағы дыбысыңыз өшірілуі мүмкін. Префиксті өзгертіңіз немесе "
            "жаһандық NoNick өшіріңіз!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Хабарға жауап беру"
            "NoNick</b>қосатын пайдаланушы"
        ),
        "deauth_confirm": (
            "⚠️ <b>Бұл әрекет Хикканы осы есептік жазбадан толығымен жояды! Ол мүмкін"
            " емесбас тарту</b>\n\n<i>- Хиккаға қатысты барлық чаттар жойылады\n- Сеанс"
            " Хикка қалпына келтіріледі\n- Хикканың кірістірілген боты жойылады</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Сіз шынымен Хикканы жойғыңыз келе ме?</b>",
        "deauth_yes": "Мен сенімдімін",
        "deauth_no_1": "Мен сенімді емеспін",
        "deauth_no_2": "Нақты емес",
        "deauth_no_3": "Жоқ",
        "deauth_cancel": "🚫 Болдырмау",
        "deauth_confirm_btn": "😢 Жою",
        "uninstall": "😢 <b>Hikka жойылуда...</b>",
        "uninstalled": (
            "😢 <b>Hikka жойылды. Веб-интерфейс әлі белсенді, басқаларын қосуға болады"
            "шоттар!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick үшін қосылған"
            " мына пәрмендер:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick үшін қосылған"
            " мына пайдаланушылар:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick үшін қосылған"
            " мына чаттар:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Ештеңе"
            "көрсету...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Бұл пәрмен Hikka веб-интерфейсіне қол жеткізуге мүмкіндік береді."
            " Оның орындалуындаАшық чаттар - қауіпсіздікке қауіп төндіреді. Жақсырақ"
            " орындаңыз ол <a href='tg://openmessage?user_id={}'>Таңдаулы хабарлар</a>"
            " ішінде.Өшіру үшін</b> <code>{}proxypass force_insecure</code> <b>іске"
            " қосыңыз бұл ескерту</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Бұл пәрмен Hikka веб-интерфейсіне қол жеткізуге мүмкіндік береді."
            " Оның орындалуындаАшық чаттар - қауіпсіздікке қауіп төндіреді. Жақсырақ"
            " орындаңыз ол <a href='tg://openmessage?user_id={}'>Таңдаулы"
            " хабарларда</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Ашуayu туннелі Хикка веб-интерфейсіне...</b>",
        "tunnel_opened": (
            "🎉 <b>Туннель ашық. Бұл сілтеме бір сағаттан артық емес белсенді болады</b>"
        ),
        "web_btn": "🌍 Веб интерфейсі",
        "btn_yes": "🚸 Әйтеуір ашыңыз",
        "btn_no": "🔻 Жабу",
        "lavhost_web": (
            "✌️ <b>Бұл сілтеме сізді Hikka веб-интерфейсіне апарады"
            " lavHost</b>\n\n<i>💡 Сізге тіркелгі деректерін пайдаланып кіру қажет,"
            "lavHost</i> орнату кезінде көрсетілген"
        ),
        "disable_debugger": "✅ Отладчик қосылған",
        "enable_debugger": "🚫 Түзету құралы өшірілген",
    }

    strings_tt = {
        "watchers": (
            "<emoji document_id=5424885441100782420>👀</emoji>"
            " <b>Сыркәләр:</b>\n\n<b>{}</b>"
        ),
        "mod404": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Сыркә {} табылмады</b>"
        ),
        "disabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Сыркә {} аңланган</b>"
        ),
        "enabled": (
            "<emoji document_id=5424885441100782420>👀</emoji> <b>Сыркә {}"
            " җибәрелгән</b>"
        ),
        "args": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Сыркәнең исемен"
            " күрсәтергә</b>"
        ),
        "user_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Кулланучы өчен NoNick"
            " мөмкинлеге: {}</b>"
        ),
        "no_cmd": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Кулланучы өчен NoNick"
            " мөмкинлеге: {}</b>"
        ),
        "cmd_nn": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Статус NoNick для"
            "</b> <code>{}</code><b>: {}</b>"
        ),
        "cmd404": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>Команда табылмады</b>"
        ),
        "inline_settings": "⚙️ <b>Hikka көйләнмәләрен буенча урнаштыру мөмкин</b>",
        "confirm_update": (
            "🧭 <b>Яңартып торганыгызны растыйсыз. Юзербот яңартылып чыгарылачак</b>"
        ),
        "confirm_restart": "🔄 <b>Тикшереп торганыгызны растыйсыз</b>",
        "suggest_fs": "✅ Модульләрне саклауны төяләтү",
        "do_not_suggest_fs": "🚫 Модульләрне саклауны төяләтү",
        "use_fs": "✅ Әрвайы модульләрне сакларга",
        "do_not_use_fs": "🚫 Әрвайы модульләрне сакларга",
        "btn_restart": "🔄 Тикшереп тору",
        "btn_update": "🧭 Яңарту",
        "close_menu": "😌 Мәзәрләрне ябу",
        "custom_emojis": "✅ Кастом эмодзи",
        "no_custom_emojis": "🚫 Кастом эмодзи",
        "suggest_subscribe": "✅ Каналга абонемент бирүне төяләтү",
        "do_not_suggest_subscribe": "🚫 Каналга абонемент бирүне төяләтү",
        "private_not_allowed": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Бу команда чаттага"
            " кулланыла</b>"
        ),
        "_cls_doc": "Hikka көйләнмәләре",
        "nonick_warning": (
            "Игътибар! Ты килешүсе башкармасыз NoNick кулланган! "
            "Тебя могут замьютить в чатах Hikka. Измени префикс или "
            "отключи глобальный NoNick!"
        ),
        "reply_required": (
            "<emoji document_id=5210952531676504517>🚫</emoji> <b>Пайда булган хисап"
            " язмасы кулланучыса NoNick кулланырга тиешләнгән җавап бирү</b>"
        ),
        "deauth_confirm": (
            "⚠️ <b>Булығыңызды ибергәндә Hikka бу аккаунттан төҙәтеү булыр! Буны кире"
            " кайтара булмай.</b>\n\n<i>- Бул Hikka белән бәйле чаттар үҙгәртелмәй\n-"
            " Hikka сессиясы төшәрелә\n- Hikka бул инлайн-бот күрһәтелмәй</i>"
        ),
        "deauth_confirm_step2": "⚠️ <b>Бул Hikka булырға теләүегездәм?</b>",
        "deauth_yes": "Бәлки",
        "deauth_no_1": "Бәлки емес",
        "deauth_no_2": "Теләмәй",
        "deauth_no_3": "Юҡ",
        "deauth_cancel": "🚫 Баш тартыу",
        "deauth_confirm_btn": "😢 Юйырға",
        "uninstall": "😢 <b>Hikka Юйылырға...</b>",
        "uninstalled": (
            "😢 <b>Hikka Юйылған. Веб-интерфейс һеҙгә булдырылған, башка аккаунттар өҫтә"
            " булған!</b>"
        ),
        "cmd_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick булырға"
            " теләнгән булыр командалар:</b>\n\n{}"
        ),
        "user_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick булырға"
            " теләнгән булыр ҡатнашыусылар:</b>\n\n{}"
        ),
        "chat_nn_list": (
            "<emoji document_id=5469791106591890404>🪄</emoji> <b>NoNick булырға"
            " теләнгән булыр чаттар:</b>\n\n{}"
        ),
        "nothing": (
            "<emoji document_id=5427052514094619126>🤷‍♀️</emoji> <b>Ҡарағыҙ булмай."
            " ...</b>"
        ),
        "privacy_leak": (
            "⚠️ <b>Бу эм команда веб-интерфейс Hikka'га кирәксез. Бу команда"
            " публикаларда җибәрелсә катнашу кертәлә алмый. Бу команданы  <a"
            " href='tg://openmessage?user_id={}'>Избранных сообщениях</a>. Выполни</b>"
            " <code>{}proxypass force_insecure</code> <b>чтобы отключить это"
            " предупреждение</b>"
        ),
        "privacy_leak_nowarn": (
            "⚠️ <b>Бу команда веб-интерфейс Hikka'га кирәксез. Бу команда публикаларда"
            " җибәрелсә катнашу кертәлә алмый. Бу команданы  <a"
            " href='tg://openmessage?user_id={}'>Избранных сообщениях</a>.</b>"
        ),
        "opening_tunnel": "🔁 <b>Веб-интерфейс Hikka'га кирәк тоннель ачылыр...</b>",
        "tunnel_opened": "🎉 <b>Тоннель ачылды. Бу сылтама 1 сәгатьчә кулланыла аласаң.",
        "web_btn": "🌍 Веб-интерфейс",
        "btn_yes": "🚸 Булып табырға",
        "btn_no": "🔻 Ябырға",
        "lavhost_web": (
            "✌️ <b>Бу сылтама Hikka веб-интерфейсына керергә керә."
            " lavHost</b>\n\n<i>💡 Тебе нужно будет авторизоваться, используя данные,"
            " указанные при настройке lavHost</i>"
        ),
        "disable_debugger": "✅ Отладчик включен",
        "enable_debugger": "🚫 Отладчик выключен",
    }

    def get_watchers(self) -> tuple:
        return [
            str(watcher.__self__.__class__.strings["name"])
            for watcher in self.allmodules.watchers
            if watcher.__self__.__class__.strings is not None
        ], self._db.get(main.__name__, "disabled_watchers", {})

    async def _uninstall(self, call: InlineCall):
        await call.edit(self.strings("uninstall"))

        async with self._client.conversation("@BotFather") as conv:
            for msg in [
                "/deletebot",
                f"@{self.inline.bot_username}",
                "Yes, I am totally sure.",
            ]:
                await fw_protect()
                m = await conv.send_message(msg)
                r = await conv.get_response()

                logger.debug(">> %s", m.raw_text)
                logger.debug("<< %s", r.raw_text)

                await fw_protect()

                await m.delete()
                await r.delete()

        async for dialog in self._client.iter_dialogs(
            None,
            ignore_migrated=True,
        ):
            if (
                dialog.name
                in {
                    "hikka-logs",
                    "hikka-onload",
                    "hikka-assets",
                    "hikka-backups",
                    "hikka-acc-switcher",
                    "silent-tags",
                }
                and dialog.is_channel
                and (
                    dialog.entity.participants_count == 1
                    or dialog.entity.participants_count == 2
                    and dialog.name in {"hikka-logs", "silent-tags"}
                )
                or (
                    self._client.loader.inline.init_complete
                    and dialog.entity.id == self._client.loader.inline.bot_id
                )
            ):
                await fw_protect()
                await self._client.delete_dialog(dialog.entity)

        await fw_protect()

        folders = await self._client(GetDialogFiltersRequest())

        if any(folder.title == "hikka" for folder in folders):
            folder_id = max(
                folders,
                key=lambda x: x.id,
            ).id
            await fw_protect()
            await self._client(UpdateDialogFilterRequest(id=folder_id))

        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.CRITICAL)

        await fw_protect()

        await self._client.log_out()

        restart()

    async def _uninstall_confirm_step_2(self, call: InlineCall):
        await call.edit(
            self.strings("deauth_confirm_step2"),
            utils.chunks(
                list(
                    sorted(
                        [
                            {
                                "text": self.strings("deauth_yes"),
                                "callback": self._uninstall,
                            },
                            *[
                                {
                                    "text": self.strings(f"deauth_no_{i}"),
                                    "action": "close",
                                }
                                for i in range(1, 4)
                            ],
                        ],
                        key=lambda _: random.random(),
                    )
                ),
                2,
            )
            + [
                [
                    {
                        "text": self.strings("deauth_cancel"),
                        "action": "close",
                    }
                ]
            ],
        )

    @loader.command(
        ru_doc="Удалить Hikka",
        fr_doc="Désinstaller Hikka",
        it_doc="Disinstalla Hikka",
        de_doc="Hikka deinstallieren",
        tr_doc="Hikka'yı kaldır",
        uz_doc="Hikka'ni o'chirish",
        es_doc="Desinstalar Hikka",
        kk_doc="Hikka'ны жою",
        tt_doc="Hikka'ны юйү",
    )
    async def uninstall_hikka(self, message: Message):
        """Uninstall Hikka"""
        await self.inline.form(
            self.strings("deauth_confirm"),
            message,
            [
                {
                    "text": self.strings("deauth_confirm_btn"),
                    "callback": self._uninstall_confirm_step_2,
                },
                {"text": self.strings("deauth_cancel"), "action": "close"},
            ],
        )

    @loader.command(
        ru_doc="Показать активные смотрители",
        fr_doc="Afficher les observateurs actifs",
        it_doc="Mostra i guardatori attivi",
        de_doc="Aktive Beobachter anzeigen",
        tr_doc="Etkin gözlemcileri göster",
        uz_doc="Faol ko'rib chiqqanlarni ko'rsatish",
        es_doc="Mostrar observadores activos",
        kk_doc="Белсенді көздерді көрсету",
        tt_doc="Актив күзәткәнләрне күрсәтү",
    )
    async def watchers(self, message: Message):
        """List current watchers"""
        watchers, disabled_watchers = self.get_watchers()
        watchers = [
            f"♻️ {watcher}"
            for watcher in watchers
            if watcher not in list(disabled_watchers.keys())
        ]
        watchers += [f"💢 {k} {v}" for k, v in disabled_watchers.items()]
        await utils.answer(
            message, self.strings("watchers").format("\n".join(watchers))
        )

    @loader.command(
        ru_doc="<module> - Включить/выключить смотрителя в текущем чате",
        fr_doc="<module> - Activer / désactiver l'observateur dans ce chat",
        it_doc="<module> - Abilita/disabilita il guardatore nel gruppo corrente",
        de_doc="<module> - Aktiviere/Deaktiviere Beobachter in diesem Chat",
        tr_doc="<module> - Bu sohbetteki gözlemciyi etkinleştirin/devre dışı bırakın",
        uz_doc="<module> - Joriy suhbatda ko'rib chiqqanlarni yoqish/yopish",
        es_doc="<module> - Habilitar / deshabilitar observador en este chat",
        kk_doc="<module> - Бұл сөйлесуде көздерді қосу/өшіру",
        tt_doc="<module> - Бу сөйләшмәде күзәткәнләрне җибәрү/өшерү",
    )
    async def watcherbl(self, message: Message):
        """<module> - Toggle watcher in current chat"""
        if not (args := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("args"))
            return

        watchers, disabled_watchers = self.get_watchers()

        if args.lower() not in map(lambda x: x.lower(), watchers):
            await utils.answer(message, self.strings("mod404").format(args))
            return

        args = next((x.lower() == args.lower() for x in watchers), False)

        current_bl = [
            v for k, v in disabled_watchers.items() if k.lower() == args.lower()
        ]
        current_bl = current_bl[0] if current_bl else []

        chat = utils.get_chat_id(message)
        if chat not in current_bl:
            if args in disabled_watchers:
                for k in disabled_watchers:
                    if k.lower() == args.lower():
                        disabled_watchers[k].append(chat)
                        break
            else:
                disabled_watchers[args] = [chat]

            await utils.answer(
                message,
                self.strings("disabled").format(args) + " <b>in current chat</b>",
            )
        else:
            for k in disabled_watchers.copy():
                if k.lower() == args.lower():
                    disabled_watchers[k].remove(chat)
                    if not disabled_watchers[k]:
                        del disabled_watchers[k]
                    break

            await utils.answer(
                message,
                self.strings("enabled").format(args) + " <b>in current chat</b>",
            )

        self._db.set(main.__name__, "disabled_watchers", disabled_watchers)

    @loader.command(
        ru_doc=(
            "<модуль> - Управление глобальными правилами смотрителя\n"
            "Аргументы:\n"
            "[-c - только в чатах]\n"
            "[-p - только в лс]\n"
            "[-o - только исходящие]\n"
            "[-i - только входящие]"
        ),
        fr_doc=(
            "<module> - Gérer les règles globales de l'observateur\n"
            "Arguments:\n"
            "[-c - uniquement dans les chats]\n"
            "[-p - uniquement dans les messages privés]\n"
            "[-o - uniquement sortant]\n"
            "[-i - uniquement entrant]"
        ),
        it_doc=(
            "<module> - Gestisci le regole globali del guardatore\n"
            "Argomenti:\n"
            "[-c - solo nei gruppi]\n"
            "[-p - solo nei messaggi privati]\n"
            "[-o - solo in uscita]\n"
            "[-i - solo in entrata]"
        ),
        de_doc=(
            "<module> - Verwalte globale Beobachterregeln\n"
            "Argumente:\n"
            "[-c - Nur in Chats]\n"
            "[-p - Nur in privaten Chats]\n"
            "[-o - Nur ausgehende Nachrichten]\n"
            "[-i - Nur eingehende Nachrichten]"
        ),
        tr_doc=(
            "<module> - Genel gözlemci kurallarını yönetin\n"
            "Argümanlar:\n"
            "[-c - Yalnızca sohbetlerde]\n"
            "[-p - Yalnızca özel sohbetlerde]\n"
            "[-o - Yalnızca giden mesajlar]\n"
            "[-i - Yalnızca gelen mesajlar]"
        ),
        uz_doc=(
            "<module> - Umumiy ko'rib chiqqan qoidalarni boshqarish\n"
            "Argumentlar:\n"
            "[-c - Faqat suhbatlarda]\n"
            "[-p - Faqat shaxsiy suhbatlarda]\n"
            "[-o - Faqat chiqarilgan xabarlar]\n"
            "[-i - Faqat kelgan xabarlar]"
        ),
        es_doc=(
            "<module> - Administre las reglas del observador global\n"
            "Argumentos:\n"
            "[-c - Solo en chats]\n"
            "[-p - Solo en chats privados]\n"
            "[-o - Solo mensajes salientes]\n"
            "[-i - Solo mensajes entrantes]"
        ),
        kk_doc=(
            "<module> - Қоғамдық көздерді басқару\n"
            "Аргументтер:\n"
            "[-c - Тек сөйлесуде]\n"
            "[-p - Тек шахси сөйлесуде]\n"
            "[-o - Тек шығарылған хабарлар]\n"
            "[-i - Тек келген хабарлар]"
        ),
        tt_doc=(
            "<module> - Шулай ук глобаль күзәтүче киңәшләрен башкару\n"
            "Аргументлар:\n"
            "[-c - Тек чаттарда]\n"
            "[-p - Тек шәхси чаттарда]\n"
            "[-o - Тек чыгарылган хәбәрләр]\n"
            "[-i - Тек килгән хәбәрләр]"
        ),
    )
    async def watchercmd(self, message: Message):
        """<module> - Toggle global watcher rules
        Args:
        [-c - only in chats]
        [-p - only in pm]
        [-o - only out]
        [-i - only incoming]"""
        if not (args := utils.get_args_raw(message)):
            return await utils.answer(message, self.strings("args"))

        chats, pm, out, incoming = False, False, False, False

        if "-c" in args:
            args = args.replace("-c", "").replace("  ", " ").strip()
            chats = True

        if "-p" in args:
            args = args.replace("-p", "").replace("  ", " ").strip()
            pm = True

        if "-o" in args:
            args = args.replace("-o", "").replace("  ", " ").strip()
            out = True

        if "-i" in args:
            args = args.replace("-i", "").replace("  ", " ").strip()
            incoming = True

        if chats and pm:
            pm = False
        if out and incoming:
            incoming = False

        watchers, disabled_watchers = self.get_watchers()

        if args.lower() not in [watcher.lower() for watcher in watchers]:
            return await utils.answer(message, self.strings("mod404").format(args))

        args = [watcher for watcher in watchers if watcher.lower() == args.lower()][0]

        if chats or pm or out or incoming:
            disabled_watchers[args] = [
                *(["only_chats"] if chats else []),
                *(["only_pm"] if pm else []),
                *(["out"] if out else []),
                *(["in"] if incoming else []),
            ]
            self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
            await utils.answer(
                message,
                self.strings("enabled").format(args)
                + f" (<code>{disabled_watchers[args]}</code>)",
            )
            return

        if args in disabled_watchers and "*" in disabled_watchers[args]:
            await utils.answer(message, self.strings("enabled").format(args))
            del disabled_watchers[args]
            self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
            return

        disabled_watchers[args] = ["*"]
        self._db.set(main.__name__, "disabled_watchers", disabled_watchers)
        await utils.answer(message, self.strings("disabled").format(args))

    @loader.command(
        ru_doc="Включить NoNick для определенного пользователя",
        fr_doc="Activer NoNick pour un utilisateur spécifique",
        it_doc="Abilita NoNick per un utente specifico",
        de_doc="Aktiviere NoNick für einen bestimmten Benutzer",
        tr_doc="Belirli bir kullanıcı için NoNick'i etkinleştirin",
        uz_doc="Belgilangan foydalanuvchi uchun NoNickni yoqish",
        es_doc="Habilitar NoNick para un usuario específico",
        kk_doc="Белгіленген пайдаланушы үшін NoNick түрлендірілген",
        tt_doc="Беләнгән кулланучы өчен NoNick үзгәртелгән",
    )
    async def nonickuser(self, message: Message):
        """Allow no nickname for certain user"""
        if not (reply := await message.get_reply_message()):
            await utils.answer(message, self.strings("reply_required"))
            return

        u = reply.sender_id
        if not isinstance(u, int):
            u = u.user_id

        nn = self._db.get(main.__name__, "nonickusers", [])
        if u not in nn:
            nn += [u]
            nn = list(set(nn))  # skipcq: PTC-W0018
            await utils.answer(message, self.strings("user_nn").format("on"))
        else:
            nn = list(set(nn) - {u})
            await utils.answer(message, self.strings("user_nn").format("off"))

        self._db.set(main.__name__, "nonickusers", nn)

    @loader.command(
        ru_doc="Включить NoNick для определенного чата",
        fr_doc="Activer NoNick pour un chat spécifique",
        it_doc="Abilita NoNick per una chat specifica",
        de_doc="Aktiviere NoNick für einen bestimmten Chat",
        tr_doc="Belirli bir sohbet için NoNick'i etkinleştirin",
        uz_doc="Belgilangan suhbat uchun NoNickni yoqish",
        es_doc="Habilitar NoNick para un chat específico",
        kk_doc="Белгіленген сөйлесу үшін NoNick түрлендірілген",
        tt_doc="Беләнгән сөйләшмә өчен NoNick үзгәртелгән",
    )
    async def nonickchat(self, message: Message):
        """Allow no nickname in certain chat"""
        if message.is_private:
            await utils.answer(message, self.strings("private_not_allowed"))
            return

        chat = utils.get_chat_id(message)

        nn = self._db.get(main.__name__, "nonickchats", [])
        if chat not in nn:
            nn += [chat]
            nn = list(set(nn))  # skipcq: PTC-W0018
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html((await message.get_chat()).title),
                    "on",
                ),
            )
        else:
            nn = list(set(nn) - {chat})
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html((await message.get_chat()).title),
                    "off",
                ),
            )

        self._db.set(main.__name__, "nonickchats", nn)

    @loader.command(
        ru_doc="<команда> - Включить NoNick для определенной команды",
        fr_doc="<commande> - Activer NoNick pour une commande spécifique",
        it_doc="<comando> - Abilita NoNick per un comando specifico",
        de_doc="<Befehl> - Aktiviere NoNick für einen bestimmten Befehl",
        tr_doc="<komut> - Belirli bir komut için NoNick'i etkinleştirin",
        uz_doc="<buyruq> - Belgilangan buyruq uchun NoNickni yoqish",
        es_doc="<comando> - Habilitar NoNick para un comando específico",
        kk_doc="<команда> - Белгіленген команда үшін NoNick түрлендірілген",
        tt_doc="<command> - Билгеле бер боерык өчен NoNick кушу",
    )
    async def nonickcmdcmd(self, message: Message):
        """<command> - Allow certain command to be executed without nickname"""
        if not (args := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("no_cmd"))
            return

        if args not in self.allmodules.commands:
            await utils.answer(message, self.strings("cmd404"))
            return

        nn = self._db.get(main.__name__, "nonickcmds", [])
        if args not in nn:
            nn += [args]
            nn = list(set(nn))
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html(self.get_prefix() + args),
                    "on",
                ),
            )
        else:
            nn = list(set(nn) - {args})
            await utils.answer(
                message,
                self.strings("cmd_nn").format(
                    utils.escape_html(self.get_prefix() + args),
                    "off",
                ),
            )

        self._db.set(main.__name__, "nonickcmds", nn)

    @loader.command(
        ru_doc="Показать список активных NoNick команд",
        fr_doc="Afficher la liste des commandes NoNick actives",
        it_doc="Mostra la lista dei comandi NoNick attivi",
        de_doc="Zeige eine Liste der aktiven NoNick Befehle",
        tr_doc="Etkin NoNick komutlarının listesini göster",
        uz_doc="Yoqilgan NoNick buyruqlar ro'yxatini ko'rsatish",
        es_doc="Mostrar una lista de comandos NoNick activos",
        kk_doc="Қосылған NoNick коммандалар тізімін көрсету",
        tt_doc="Кушылган NoNick боерыклар исемлеген күрсәтү",
    )
    async def nonickcmds(self, message: Message):
        """Returns the list of NoNick commands"""
        if not self._db.get(main.__name__, "nonickcmds", []):
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("cmd_nn_list").format(
                "\n".join(
                    [
                        f"▫️ <code>{utils.escape_html(self.get_prefix() + cmd)}</code>"
                        for cmd in self._db.get(main.__name__, "nonickcmds", [])
                    ]
                )
            ),
        )

    @loader.command(
        ru_doc="Показать список активных NoNick пользователей",
        fr_doc="Afficher la liste des utilisateurs NoNick actifs",
        it_doc="Mostra la lista degli utenti NoNick attivi",
        de_doc="Zeige eine Liste der aktiven NoNick Benutzer",
        tr_doc="Etkin NoNick kullanıcılarının listesini göster",
        uz_doc="Yoqilgan NoNick foydalanuvchilar ro'yxatini ko'rsatish",
        es_doc="Mostrar una lista de usuarios NoNick activos",
        kk_doc="Қосылған NoNick пайдаланушылар тізімін көрсету",
        tt_doc="Кушылган NoNick кулланучылар исемлеген күрсәтү",
    )
    async def nonickusers(self, message: Message):
        """Returns the list of NoNick users"""
        users = []
        for user_id in self._db.get(main.__name__, "nonickusers", []).copy():
            try:
                user = await self._client.get_entity(user_id)
            except Exception:
                self._db.set(
                    main.__name__,
                    "nonickusers",
                    list(
                        (
                            set(self._db.get(main.__name__, "nonickusers", []))
                            - {user_id}
                        )
                    ),
                )

                logger.warning("User %s removed from nonickusers list", user_id)
                continue

            users += [
                '▫️ <b><a href="tg://user?id={}">{}</a></b>'.format(
                    user_id,
                    utils.escape_html(get_display_name(user)),
                )
            ]

        if not users:
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("user_nn_list").format("\n".join(users)),
        )

    @loader.command(
        ru_doc="Показать список активных NoNick чатов",
        fr_doc="Afficher la liste des chats NoNick actifs",
        it_doc="Mostra la lista dei gruppi NoNick attivi",
        de_doc="Zeige eine Liste der aktiven NoNick Chats",
        tr_doc="Etkin NoNick sohbetlerinin listesini göster",
        uz_doc="Yoqilgan NoNick suhbatlar ro'yxatini ko'rsatish",
        es_doc="Mostrar una lista de chats NoNick activos",
        kk_doc="Қосылған NoNick сөйлесушілер тізімін көрсету",
        tt_doc="Кушылган NoNick сөйләшмәләр исемлеген күрсәтү",
    )
    async def nonickchats(self, message: Message):
        """Returns the list of NoNick chats"""
        chats = []
        for chat in self._db.get(main.__name__, "nonickchats", []):
            try:
                chat_entity = await self._client.get_entity(int(chat))
            except Exception:
                self._db.set(
                    main.__name__,
                    "nonickchats",
                    list(
                        (set(self._db.get(main.__name__, "nonickchats", [])) - {chat})
                    ),
                )

                logger.warning("Chat %s removed from nonickchats list", chat)
                continue

            chats += [
                '▫️ <b><a href="{}">{}</a></b>'.format(
                    utils.get_entity_url(chat_entity),
                    utils.escape_html(get_display_name(chat_entity)),
                )
            ]

        if not chats:
            await utils.answer(message, self.strings("nothing"))
            return

        await utils.answer(
            message,
            self.strings("user_nn_list").format("\n".join(chats)),
        )

    async def inline__setting(self, call: InlineCall, key: str, state: bool = False):
        if callable(key):
            key()
            hikkatl.extensions.html.CUSTOM_EMOJIS = not main.get_config_key(
                "disable_custom_emojis"
            )
        else:
            self._db.set(main.__name__, key, state)

        if key == "no_nickname" and state and self.get_prefix() == ".":
            await call.answer(
                self.strings("nonick_warning"),
                show_alert=True,
            )
        else:
            await call.answer("Configuration value saved!")

        await call.edit(
            self.strings("inline_settings"),
            reply_markup=self._get_settings_markup(),
        )

    async def inline__update(
        self,
        call: InlineCall,
        confirm_required: bool = False,
    ):
        if confirm_required:
            await call.edit(
                self.strings("confirm_update"),
                reply_markup=[
                    {"text": "🪂 Update", "callback": self.inline__update},
                    {"text": "🚫 Cancel", "action": "close"},
                ],
            )
            return

        await call.answer("You userbot is being updated...", show_alert=True)
        await call.delete()
        await self.invoke("update", "-f", peer="me")

    async def inline__restart(
        self,
        call: InlineCall,
        confirm_required: bool = False,
    ):
        if confirm_required:
            await call.edit(
                self.strings("confirm_restart"),
                reply_markup=[
                    {"text": "🔄 Restart", "callback": self.inline__restart},
                    {"text": "🚫 Cancel", "action": "close"},
                ],
            )
            return

        await call.answer("You userbot is being restarted...", show_alert=True)
        await call.delete()
        await self.invoke("restart", "-f", peer="me")

    def _get_settings_markup(self) -> list:
        return [
            [
                (
                    {
                        "text": "✅ NoNick",
                        "callback": self.inline__setting,
                        "args": (
                            "no_nickname",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "no_nickname", False)
                    else {
                        "text": "🚫 NoNick",
                        "callback": self.inline__setting,
                        "args": (
                            "no_nickname",
                            True,
                        ),
                    }
                ),
                (
                    {
                        "text": "✅ Grep",
                        "callback": self.inline__setting,
                        "args": (
                            "grep",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "grep", False)
                    else {
                        "text": "🚫 Grep",
                        "callback": self.inline__setting,
                        "args": (
                            "grep",
                            True,
                        ),
                    }
                ),
                (
                    {
                        "text": "✅ InlineLogs",
                        "callback": self.inline__setting,
                        "args": (
                            "inlinelogs",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "inlinelogs", True)
                    else {
                        "text": "🚫 InlineLogs",
                        "callback": self.inline__setting,
                        "args": (
                            "inlinelogs",
                            True,
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("do_not_suggest_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "disable_modules_fs",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "disable_modules_fs", False)
                    else {
                        "text": self.strings("suggest_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "disable_modules_fs",
                            True,
                        ),
                    }
                )
            ],
            [
                (
                    {
                        "text": self.strings("use_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "permanent_modules_fs",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "permanent_modules_fs", False)
                    else {
                        "text": self.strings("do_not_use_fs"),
                        "callback": self.inline__setting,
                        "args": (
                            "permanent_modules_fs",
                            True,
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("suggest_subscribe"),
                        "callback": self.inline__setting,
                        "args": (
                            "suggest_subscribe",
                            False,
                        ),
                    }
                    if self._db.get(main.__name__, "suggest_subscribe", True)
                    else {
                        "text": self.strings("do_not_suggest_subscribe"),
                        "callback": self.inline__setting,
                        "args": (
                            "suggest_subscribe",
                            True,
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("no_custom_emojis"),
                        "callback": self.inline__setting,
                        "args": (
                            lambda: main.save_config_key(
                                "disable_custom_emojis", False
                            ),
                        ),
                    }
                    if main.get_config_key("disable_custom_emojis")
                    else {
                        "text": self.strings("custom_emojis"),
                        "callback": self.inline__setting,
                        "args": (
                            lambda: main.save_config_key("disable_custom_emojis", True),
                        ),
                    }
                ),
            ],
            [
                (
                    {
                        "text": self.strings("disable_debugger"),
                        "callback": self.inline__setting,
                        "args": lambda: self._db.set(log.__name__, "debugger", False),
                    }
                    if self._db.get(log.__name__, "debugger", False)
                    else {
                        "text": self.strings("enable_debugger"),
                        "callback": self.inline__setting,
                        "args": (lambda: self._db.set(log.__name__, "debugger", True),),
                    }
                ),
            ],
            [
                {
                    "text": self.strings("btn_restart"),
                    "callback": self.inline__restart,
                    "args": (True,),
                },
                {
                    "text": self.strings("btn_update"),
                    "callback": self.inline__update,
                    "args": (True,),
                },
            ],
            [{"text": self.strings("close_menu"), "action": "close"}],
        ]

    @loader.command(
        ru_doc="Показать настройки",
        fr_doc="Afficher les paramètres",
        it_doc="Mostra le impostazioni",
        de_doc="Zeige die Einstellungen",
        tr_doc="Ayarları göster",
        uz_doc="Sozlamalarni ko'rsatish",
        es_doc="Mostrar configuración",
        kk_doc="Баптауларды көрсету",
        tt_doc="Көйләнмәләрне күрсәтү",
    )
    async def settings(self, message: Message):
        """Show settings menu"""
        await self.inline.form(
            self.strings("inline_settings"),
            message=message,
            reply_markup=self._get_settings_markup(),
        )

    @loader.command(
        ru_doc="Открыть тоннель к веб-интерфейсу Hikka",
        fr_doc="Ouvrir un tunnel vers l'interface web de Hikka",
        it_doc="Apri il tunnel al web interface di Hikka",
        de_doc="Öffne einen Tunnel zum Hikka Webinterface",
        tr_doc="Hikka Web Arayüzüne bir tünel aç",
        uz_doc="Hikka veb-interfeysi uchun tunel ochish",
        es_doc="Abrir un túnel al interfaz web de Hikka",
        kk_doc="Hikka веб-интерфейсіне тунель ашу",
        tt_doc="Hikka веб-интерфейсенә тунель ачу",
    )
    async def weburl(self, message: Message, force: bool = False):
        """Opens web tunnel to your Hikka web interface"""
        if "LAVHOST" in os.environ:
            form = await self.inline.form(
                self.strings("lavhost_web"),
                message=message,
                reply_markup={
                    "text": self.strings("web_btn"),
                    "url": await main.hikka.web.get_url(proxy_pass=False),
                },
                gif="https://t.me/hikari_assets/28",
            )
            return

        if (
            not force
            and not message.is_private
            and "force_insecure" not in message.raw_text.lower()
        ):
            try:
                if not await self.inline.form(
                    self.strings("privacy_leak_nowarn").format(self._client.tg_id),
                    message=message,
                    reply_markup=[
                        {
                            "text": self.strings("btn_yes"),
                            "callback": self.weburl,
                            "args": (True,),
                        },
                        {"text": self.strings("btn_no"), "action": "close"},
                    ],
                    gif="https://i.gifer.com/embedded/download/Z5tS.gif",
                ):
                    raise Exception
            except Exception:
                await utils.answer(
                    message,
                    self.strings("privacy_leak").format(
                        self._client.tg_id,
                        utils.escape_html(self.get_prefix()),
                    ),
                )

            return

        if not main.hikka.web:
            main.hikka.web = core.Web(
                data_root=main.BASE_DIR,
                api_token=main.hikka.api_token,
                proxy=main.hikka.proxy,
                connection=main.hikka.conn,
            )
            await main.hikka.web.add_loader(self._client, self.allmodules, self._db)
            await main.hikka.web.start_if_ready(
                len(self.allclients),
                main.hikka.arguments.port,
                proxy_pass=main.hikka.arguments.proxy_pass,
            )

        if force:
            form = message
            await form.edit(
                self.strings("opening_tunnel"),
                reply_markup={"text": "🕔 Wait...", "data": "empty"},
                gif=(
                    "https://i.gifer.com/origin/e4/e43e1b221fd960003dc27d2f2f1b8ce1.gif"
                ),
            )
        else:
            form = await self.inline.form(
                self.strings("opening_tunnel"),
                message=message,
                reply_markup={"text": "🕔 Wait...", "data": "empty"},
                gif=(
                    "https://i.gifer.com/origin/e4/e43e1b221fd960003dc27d2f2f1b8ce1.gif"
                ),
            )

        url = await main.hikka.web.get_url(proxy_pass=True)

        await form.edit(
            self.strings("tunnel_opened"),
            reply_markup={"text": self.strings("web_btn"), "url": url},
            gif="https://t.me/hikari_assets/48",
        )

    @loader.loop(interval=1, autostart=True)
    async def loop(self):
        if not (obj := self.allmodules.get_approved_channel):
            return

        channel, event = obj

        try:
            await self._client(JoinChannelRequest(channel))
        except Exception:
            logger.exception("Failed to join channel")
            event.status = False
            event.set()
        else:
            event.status = True
            event.set()

    def _get_all_IDM(self, module: str):
        return {
            getattr(getattr(self.lookup(module), name), "name", name): getattr(
                self.lookup(module), name
            )
            for name in dir(self.lookup(module))
            if getattr(getattr(self.lookup(module), name), "is_debug_method", False)
        }

    @loader.command()
    async def invokecmd(self, message: Message):
        """<module or `core` for built-in methods> <method> - Only for debugging purposes. DO NOT USE IF YOU'RE NOT A DEVELOPER"""
        if not (args := utils.get_args_raw(message)) or len(args.split()) < 2:
            await utils.answer(message, self.strings("no_args"))
            return

        module = args.split()[0]
        method = args.split(maxsplit=1)[1]

        if module != "core" and not self.lookup(module):
            await utils.answer(message, self.strings("module404").format(module))
            return

        if (
            module == "core"
            and method not in ALL_INVOKES
            or module != "core"
            and method not in self._get_all_IDM(module)
        ):
            await utils.answer(message, self.strings("invoke404").format(method))
            return

        message = await utils.answer(
            message, self.strings("invoking").format(method, module)
        )
        result = ""

        if module == "core":
            if method == "clear_entity_cache":
                result = (
                    f"Dropped {len(self._client._hikka_entity_cache)} cache records"
                )
                self._client._hikka_entity_cache = {}
            elif method == "clear_fulluser_cache":
                result = (
                    f"Dropped {len(self._client._hikka_fulluser_cache)} cache records"
                )
                self._client._hikka_fulluser_cache = {}
            elif method == "clear_fullchannel_cache":
                result = (
                    f"Dropped {len(self._client._hikka_fullchannel_cache)} cache"
                    " records"
                )
                self._client._hikka_fullchannel_cache = {}
            elif method == "clear_perms_cache":
                result = f"Dropped {len(self._client._hikka_perms_cache)} cache records"
                self._client._hikka_perms_cache = {}
            elif method == "clear_cache":
                result = (
                    f"Dropped {len(self._client._hikka_entity_cache)} entity cache"
                    " records\nDropped"
                    f" {len(self._client._hikka_fulluser_cache)} fulluser cache"
                    " records\nDropped"
                    f" {len(self._client._hikka_fullchannel_cache)} fullchannel cache"
                    " records"
                )
                self._client._hikka_entity_cache = {}
                self._client._hikka_fulluser_cache = {}
                self._client._hikka_fullchannel_cache = {}
                self._client.hikka_me = await self._client.get_me()
            elif method == "reload_core":
                core_quantity = await self.lookup("loader").reload_core()
                result = f"Reloaded {core_quantity} core modules"
            elif method == "inspect_cache":
                result = (
                    "Entity cache:"
                    f" {len(self._client._hikka_entity_cache)} records\nFulluser cache:"
                    f" {len(self._client._hikka_fulluser_cache)} records\nFullchannel"
                    f" cache: {len(self._client._hikka_fullchannel_cache)} records"
                )
            elif method == "inspect_modules":
                result = (
                    "Loaded modules: {}\nLoaded core modules: {}\nLoaded user"
                    " modules: {}"
                ).format(
                    len(self.allmodules.modules),
                    sum(
                        module.__origin__.startswith("<core")
                        for module in self.allmodules.modules
                    ),
                    sum(
                        not module.__origin__.startswith("<core")
                        for module in self.allmodules.modules
                    ),
                )
        else:
            result = await self._get_all_IDM(module)[method](message)

        await utils.answer(
            message,
            self.strings("invoke").format(method, utils.escape_html(result)),
        )
