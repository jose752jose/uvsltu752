from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os
from os import walk

def text_progres(index,max):
	try:
		if max<1:
			max += 1
		porcent = index / max
		porcent *= 100
		porcent = round(porcent)
		make_text = ''
		index_make = 1
		make_text += ' 【 '
		while(index_make<21):
			if porcent >= index_make * 5: make_text+='◆'
			else: make_text+='◇'
			index_make+=1
		make_text += ' 】 '
		return make_text
	except Exception as ex:
			return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = "▶️Descargando archivo...\n"
    msg += "📔: "+filename+'\n'
    msg += "⬇️𝐃𝐞𝐬𝐜𝐚𝐫𝐠𝐚𝐝𝐨: "+sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
    msg += "⚡️𝐒𝐏𝐃: "+sizeof_fmt(speed)+'/s ''| ''⏰𝐄𝐓𝐀: '+str(datetime.timedelta(seconds=int(time)))+'s\n'
    if tid!='':
        msg+= '🚫 /cancel_' + tid
    return msg

def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = "▶️ Subiendo Archivo...\n"
    msg += '📄: '+filename+'\n'
    msg += "⬆️𝐒𝐮𝐛𝐢𝐝𝐨: "+sizeof_fmt(currentBits) + ' de ' + sizeof_fmt(totalBits) + '\n'
    msg += "⚡️𝐒𝐏𝐃: "+sizeof_fmt(speed)+'/s ''| ''⏰𝐄𝐓𝐀: '+str(datetime.timedelta(seconds=int(time)))+'s\n\n'
    return msg

def createCompresing(filename,filesize,splitsize):
    msg  = "▶️Comprimiendo Archivo...\n\n"
    msg += "🗜Comprimiendo "+ str(round(int(filesize/splitsize)+1,1))+" en partes de "+str(sizeof_fmt(splitsize))+'\n\n'
    return msg

def createFinishUploading(filename,filesize,urls,username):
    msg = "▶️Subida finalizada✅...\n"
    msg += "~~"+ str(filename)+'\n'
    #msg += '<b>🔗𝐄𝐧𝐥𝐚𝐜𝐞 𝐝𝐞 𝐝𝐞𝐬𝐜𝐚𝐫𝐠𝐚:</b>\n'
    #msg += urls
    msg += "⚡️¡Siempre su mejor opción!⚡️\n"
    return msg

def createFileMsg(urls):
    import urllib
    if len(files)>0:
        msg = '<b>🔗𝐄𝐧𝐥𝐚𝐜𝐞 𝐝𝐞 𝐝𝐞𝐬𝐜𝐚𝐫𝐠𝐚:</b>\n'
        for f in files:
            url = urllib.parse.unquote(furlsencoding='utf-8', errors='replace')
            msg+= urls
        msg += "\n⚡️¡Siempre su mejor opción!⚡️\n\n"
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = '➣ Archivos ('+str(len(evfiles))+')\n\n'
    i = 0
    for f in evfiles:
            try:
                fextarray = str(f['files'][0]['name']).split('.')
                fext = ''
                if len(fextarray)>=3:
                    fext = '.'+fextarray[-2]
                else:
                    fext = '.'+fextarray[-1]
                fname = f['name'] + fext
                msg+= '/txt_'+ str(i) + ' /del_'+ str(i) + '\n' + fname +'\n\n'
                i+=1
            except:pass
    return msg
    
def files(username, path):
    listado=os.listdir(path)
    dir, subdirs, archivos = next(walk(path))
    sms = f'🆔Sesión: @{username}\n'
    sms += f'📂Archivos: {str(len(listado))}\n'
    sn = -1
    for s in subdirs:
        sn += 1
        sms +=f'\n/cdir_{sn} 📁 {s}'
    an = -1
    for a in archivos:
        an += 1
        size=(a,os.stat(os.path.join(path, a)).st_size)
        size=(size[1] / 1024 / 1024)
        sms +=f'\n◈━━━━━━━/up_{an}━━━━━━━━◈'
        sms +=f'\n/rm_{an} - {a}\n📦{str(size)[:4]}MB\n╰────────────────'
    return sms
    
def createStatAdmin(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = "👥Usuario: "+str(userdata['moodle_user'])+'\n'
    msg += "🔑Contraseña: "+str(userdata['moodle_password'])+'\n'
    msg += "☁️Página: "+ str(userdata['moodle_host'])+'\n'
    msg += "🗜Tamaño por archivo: "+ sizeof_fmt(userdata['zips']*1024*1024) + '\n\n'
    proxy = '❌'
    if userdata['proxy'] !='':
       proxy = '✅'
    msg += "🔌 Proxy: " + proxy +"\n"
    msgAdmin = '❌'
    if isadmin:
        msgAdmin = '✅'
    msg+= '🦾Admin : ' + msgAdmin + '\n\n'
    return msg

def createStatUser(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = "📚Tamaño por archivo: "+ sizeof_fmt(userdata['zips']*1024*1024) + '\n'
    msgAdmin = '❌'
    if isadmin:
        msgAdmin = '✅'
    msg+= '👤🔑Administrador: ' + msgAdmin + '\n\n'
    
    return msg