from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient

from JDatabase import JsonDatabase
import zipfile
import os
import infos
import xdlink
import mediafire
import datetime
import time
import requests
from bs4 import BeautifulSoup

from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
import moodlews
import moodle_client
from moodle_client import MoodleClient2
from yarl import URL
import re
import random
from draft_to_calendar import send_calendar

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def short_url(url):
    api = 'https://shortest.link/es/'
    resp = requests.post(api,data={'url':url})
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,'html.parser')
        shorten = soup.find('input',{'class':'short-url'})['value']
        return shorten
    return url

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        name = filename
        nam = name[0:15]
        zip = str(name).split('.')[-1]
        name2 = nam+'.'+zip
        if '7z' in name:     
            name2 = nam+'.7z.'+zip
        filename = name2   
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        name = filename
        nam = name[0:15]
        zip = str(name).split('.')[-1]
        name2 = nam+'.'+zip
        if '7z' in name:     
            name2 = nam+'.7z.'+zip
        filename = name2   
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        err = None
        bot.editMessageText(message,'Iniciando Sesión')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        draftlist=[]
        if cloudtype == 'moodle':
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            repoid = user_info['moodle_repo_id']
            token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)
            if token == None:
                token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)
                if token == None:
                    token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)
            print(token)
            for file in files:
                    data = asyncio.run(moodlews.webservice_upload_file(host,token,file,progressfunc=uploadFile,proxy=proxy,args=(bot,message,filename,thread)))
                    while not moodlews.store_exist(file):pass
                    data = moodlews.get_store(file)
                    if data[0]:
                        urls = moodlews.make_draft_urls(data[0])
                        draftlist.append({'file':file,'url':urls[0]})
                        file_size = None
                        name = file
                        nam = name[0:15]
                        zip = str(name).split('.')[-1]
                        name2 = nam+'.'+zip
                        if '7z' in name:     
                            name2 = nam+'.7z.'+zip
                        file = name2  
                        urls = short_url(urls[0])
                        #urls = moodlews.make_draft_urls(data[0])
                        finishInfo = infos.createFinishUploading(file,file_size,urls,update.message.sender.username)
                        bot.sendMessage(message.chat.id,finishInfo,parse_mode='html')
                    else:
                        err = data[1]
                        print(err)
                        bot.editMessageText(message,'Error\n' + str(err))
        return draftlist,err
    except Exception as ex:
        bot.editMessageText(message,'Error:\n1-Compruebe que la nube esta activa\n2-Verifique su proxy\n3-O revise su cuenta')

def processFile(update,bot,message,file,thread=None,jdb=None):
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(file).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        name = file
        data,err = processUploadFiles(name,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(file)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        name = file
        data,err = processUploadFiles(name,file_size,[name],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'📄Creando TxT📄')
    bot.deleteMessage(message.chat.id,message.message_id)
    files = []
    if data:
        for draft in data:
            files.append({'name':draft['file'],'directurl':draft['url']})
    i=0
    while i < len(files):
        if i+1 < len(files):
            print('Más de 1 Links ')
        i+=2            
    if len(files)>0:    
        txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
        txtname = txtname.replace(' ','')
        sendTxt(txtname,files,update,bot)
    else:
        bot.editMessageText(message,'❌Error en la nube❌')    
   
def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    host = f['directurl'].split('/draftfile')[0]+'/'
                    linkdraft = f['directurl'].split(host)[1]
                    token = '?token=489802772f67104f0c11536d140f8322'
                    link = host+'webservice/'+linkdraft+token
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(link+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        #tl_admin_user = os.environ.get('admin')

        #set in debug
        tl_admin_user = 'shadowalh'
        path = '.'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = '❌No tiene contrato en este bot, o su contrato a finalizado❌\n👤Contactar: @nautaii si desea hacer un nuevo contrato💳\n'
            intento_msg = "💢El usuario @"+username+ "💢"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(1759969205,intento_msg)
            return

        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add_admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = '🎩Admin @'+user+' agregado'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'❌Error en el comando /add_admin user❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No tiene acceso a este comando❌')
            return

        if '/add_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '👤Usuario @'+user+' agregado'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'❌Error en el comando /add_admin user❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No tiene acceso a este comando❌')
            return

        if '/ban_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'❌No se puede banear usted❌')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '❌Usuario @'+user+' baneado'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /ban_user user❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No tiene acceso a este comando❌')
            return

        if '/get_db' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'❌No tiene acceso a este comando❌')
            return
        # end

        # comandos de usuario
        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'📄Guía de Usuario:')
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return

        if '/myuser' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStatUser(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return

        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = '🗜️Zips configurados '+ sizeof_fmt(size*1024*1024)+' cada parte📚'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'❌Error en el comando /zips size❌')    
                return

        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStatUser(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error en el comando /acc user,password❌')
            return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStatUser(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error en el comando /host host❌')
            return

        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStatUser(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error en el comando /repo repo❌')
            return

        if '/' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🛰️Proxy guardado'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStatUser(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'❌Error en el comando /proxy proxy❌')
            return

        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'❌Descarga cancelada❌')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'🎐Analizyng...')

        thread.store('msg',message)

        if '/start' in msgText:
            start_msg = '📤DM Uploader Free📤\n\n🔰Bot de descargas gratis de la cadena 📤 nautaii📤\n#DescargasGratis\n#Velocidad'
            bot.editMessageText(message,start_msg)
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'🤖Getting token, please wait...')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'🔮Su token es: '+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'⚠️The moodle '+client.path+' does not have token⚠️')
            except Exception as ex:
                bot.editMessageText(message2,'⚠️The moodle '+client.path+' does not have token or check out your account⚠️')       
        elif '/delete' in msgText:
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "Archivo eliminado con exito...")
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            bot.editMessageText(message,'❌Error❌')
    except Exception as ex:
           print(str(ex))
  
def main():
    bot_token = '5606890553:AAEW6mmPmcGmj3CsvYgjmGNP_jRMuMpink0'
    

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
