import logging
from telegram import __version__ as TG_VER
from telegram import ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler)
import pandas as pd
import math
import ifttt
#Setup
TG_bot = "TG_API KEY"
#----------------------------------------------------------
#Block files:
file442 = "git.xlsx"
file443 = "msk.xlsx"
# Enable logging
logging.basicConfig(filename='logging.log', level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
#----------------------------------------------------------

info = {
    "subject": "",
    "lecture": "",
    "file_path": "",
    "file_name": "",
    "batch" : 0,
    "female" : False
    }
file = ""
SUBJECT, LECTURE = range(2)

ids = []
male442_ids = []
female442_ids = []
male443_ids = []
female443_ids = []
ids.extend(male442_ids)
ids.extend(female442_ids)
ids.extend(male443_ids)
ids.extend(female443_ids)
#------442 Male----------------
#------442 Female--------------
#------443 Male----------------)
#------443 Female--------------
def check_id(id):
    #Batch check
    if id in female442_ids or id in male442_ids:
         info.update({"batch" : 442})
    elif id in male443_ids or id in female443_ids:
        info.update({"batch" : 443})
    #Gender check
    if id in female442_ids or id in female443_ids:
        info.update({"female" : True})
    else:
        info.update({"female" : False})


async def attachment_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(update.message)
    if(update.message.chat_id in ids): 
        check_id(update.message.chat_id)
        await update.message.reply_text("اختار المادة:")
        print(update.message.document)
        global file
        file = await update.message.document.get_file()
        info.update({"file_name" : update.message.document["file_name"]})
        return SUBJECT
    

def subjects(meesage):
    info.update({"subject" : meesage[1:]})
    button_list = []
    try:
        file_block = file443 if info["batch"] == 443 else file442
        print(f"Subject seleceted {meesage[1:]}")
        xl_file = pd.read_excel(file_block,meesage[1:])
        lectures_list = xl_file["Lecture"].tolist()
        print(f"List seleceted {lectures_list}")
        counter = 1
        for each in lectures_list:
            digit = int(math.log10(counter))+1
            lecture_number = "L0{})".format(counter) if math.log10(digit) +1 == 1 else "L{})".format(counter)
            response = "{}{}".format(lecture_number, each).strip()
            button_list.append(InlineKeyboardButton(response, callback_data = response))
            counter = counter + 1
    except Exception as e: 
        print(f"EROOR:{e}")
        file_name = info["file_name"]
        button_list.append(InlineKeyboardButton(file_name, callback_data = file_name))
    button_list.append(InlineKeyboardButton("🚫cancel🚫", callback_data = "cancel"))
    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
    return reply_markup



def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

async def lectures(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Subject picked: %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(text="أختار المحاضرة", reply_markup=subjects(update.message.text))
    if update.message.text == "/cancel":
        return ConversationHandler.END 
    else:
        print(f"NOT cancel! {update.message.text}")
        return LECTURE
   

async def download():
    global file
    file_to_download = file
    file_name = info["file_name"]
    file_path = await file_to_download.download_to_drive(f"./downloadedpttx/{file_name}")
    info.update({"file_path": file_path})
    print(file_path)
    batch = info["batch"]
    female = info["female"]
    print(f"FEMALE ? {female}")
    ifttt.upload(str(file_path), file_name, info["subject"], info["lecture"], batch, female)



async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(f"QUERY IS: {query.data}")
    if(query.data == "cancel"):
        await query.answer()
        await query.edit_message_text(text="🚫تم الالغاء🚫.")
        return ConversationHandler.END
    else:
        info.update({"lecture": query.data})
        await query.answer()
        await query.edit_message_text(text=f"المادة: {info['subject']} \n المحاضرة: {info['lecture']}")
        await download()
        await query.edit_message_text(text=f"✅")
        return ConversationHandler.END




async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "🚫تم الالغاء🚫.", reply_markup=ReplyKeyboardRemove()
    )


    return ConversationHandler.END

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(update.message.chat_id)
    logger.info(update.message)



def main() -> None:
    application = Application.builder().token(TG_bot).build()
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters=filters.ATTACHMENT, callback=attachment_received)],
        states={

            SUBJECT: [MessageHandler(filters.Command() ^ filters.Regex("/cancel"), lectures)],
            LECTURE: [CallbackQueryHandler(button)],
        },

        fallbacks=[CommandHandler("cancel", cancel)],
    )
    log_handler = CommandHandler("start", log)
    application.add_handler(log_handler)
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":

    main()
