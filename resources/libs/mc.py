import os, sys, stat, re
import xbmc, xbmcgui, xbmcaddon
import urllib2, binascii, urllib
from BeautifulSoup import BeautifulStoneSoup
try:
    import cPickle as pickle
except:
    import pickle
#import types

class Window(xbmcgui.WindowXML):
    def __init__( self, start, path, skin):
	xbmcgui.WindowXML.__init__( self, start, path, skin )
        self.doModal()

def load(var):
    if var == 'id':
        fileid = os.path.join(GetTempDir(),'boxee.init')
        if os.access(fileid, os.F_OK):
            return open(fileid, 'r').read()
    elif var == 'windows':
        filewindow = os.path.join(GetTempDir(),'boxee.windows')
        if os.access(filewindow, os.F_OK):
            data = open(filewindow, 'r').read()
            return pickle.loads(binascii.unhexlify(data))
 
def start(addon_id, addon_windows):
    fileid = os.path.join(GetTempDir(),'boxee.init')
    file = open(fileid, 'w')
    file.write(addon_id)
    file.close()

    filewindow = os.path.join(GetTempDir(),'boxee.windows')
    data = pickle.dumps(addon_windows)
    file = open(filewindow, 'w')
    file.write(binascii.hexlify(data))
    file.close()

def ListStart(obj, var):
    settings = GetLocalConfig()
    try: listcontrol = int(settings.GetValue('listcontrol'))
    except: listcontrol = 0
    position = obj.getControl(var).getSelectedPosition()
    if int(position) == 0 and int(position) == listcontrol:
        settings.SetValue('listcontrol', str(position))
        return True
    else:
        settings.SetValue('listcontrol', str(position))
        return False

def ListEnd(obj, var):
    settings = GetLocalConfig()
    try: listcontrol = int(settings.GetValue('listcontrol'))
    except: listcontrol = 0
    position = obj.getControl(var).getSelectedPosition()
    size = obj.getControl(var).size() - 1
    if int(position) == int(size) and int(position) == listcontrol:
        settings.SetValue('listcontrol', str(position))
        return True
    else:
        settings.SetValue('listcontrol', str(position))
        return False

#Boxee mc Emulation
class Http(object):
    def __init__(self):
        self.headers = {}

    def SetUserAgent(self, var):
        self.headers['User-Agent'] = var

    def SetHttpHeader(self, var1, var2):
        self.headers[var1] = var2

    def Post(self, url, params):
        values = params.split('&')
        post = {}
        for value in values:
            id, val = value.split('=')
            post[id] = val
        encoded_params = urllib.urlencode( post )
        
        opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
        urllib2.install_opener( opener )
        headers = [(x, y) for x, y in self.headers.iteritems()]
        opener.addheaders = headers
        _file = opener.open( url, encoded_params )
        response = _file.read()
        _file.close()
        return response

    def Get(self, url):
        opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
        urllib2.install_opener( opener )
        headers = [(x, y) for x, y in self.headers.iteritems()]
        opener.addheaders = headers
        _file = opener.open( url )
        response = _file.read()
        _file.close()
        return response

class GetApp(object):
    def GetLocalConfig(self):
        return GetLocalConfig()

    def GetAppDir(self):
        return os.getcwd().replace(";","")

    def GetId(self):
        return load('id')

def CloseWindow():
    window.close()

def GetActiveWindow():
    return GetWindow()

def GetInfoString(var):
    return xbmc.getInfoLabel(var)

def GetLocalizedString(int):
    return xbmc.getLocalizedString(int)

def ShowDialogWait():
    progress = xbmcgui.DialogProgress()
    progress.create('XBMC - Addon', 'Loading...')
    return progress
    #xbmcgui.lock()

def HideDialogWait(obj):
    #xbmcgui.unlock()
    obj.close()

def ShowDialogNotification(var):
    xbmc.executebuiltin('Notification("Info",'+var+',1500 )')

def ShowDialogOk(title, var):
    dialog = xbmcgui.Dialog()
    return dialog.ok(title, var)

def ShowDialogConfirm(title, var, no='No', yes='Yes'):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading=title, line1=var, nolabel=no, yeslabel=yes)

def LogDebug(var):
    xbmc.log(msg=var,level=xbmc.LOGDEBUG)

def LogError(var):
    xbmc.log(msg=var,level=xbmc.LOGERROR)

def LogInfo(var):
    xbmc.log(msg=var,level=xbmc.LOGINFO)

def ShowDialogKeyboard(title='', var='', bool=False):
    keyboard = xbmc.Keyboard(var, title, bool)
    keyboard.doModal()
    if keyboard.isConfirmed(): return keyboard.getText()
    else: return


class GetLocalConfig(object):
    def __init__(self):
        self.id = load('id')
        if len(self.id) > 2:
            self.settings = xbmcaddon.Addon(id=self.id)

    def GetValue(self, val):
        data = val.split('{')
        i = 0
        if len(data) > 1:
            i = data[1][:-1]
            val_id = data[0]
        else: val_id = val
        return self.settings.getSetting(id=val_id+'{'+str(i)+'}')

    def SetValue(self, val1, val2):
        if not '{' in val1: stringid = val1+'{0}'
        else: stringid = val1
        self.settings.setSetting(id=stringid, value=val2)

    def PushBackValue(self, val1, val2):
        i = 0
        while True:
            if self.settings.getSetting(id=val1+'{'+str(i)+'}') != '':
                i += 1
            else:
                break
        self.settings.setSetting(id=val1+'{'+str(i)+'}', value=val2)
        
    def Reset(self, val):
        if '{' in val: stringid = val.split('{')[0]
        else: stringid = val
        i = 0
        list = []
        while True:
            if self.settings.getSetting(id=stringid+'{'+str(i)+'}') != '':
                list.append(i)
                i += 1
            else:
                break
        if len(list) > 0:
            for i in list:
                self.settings.setSetting(id=stringid+'{'+str(i)+'}', value='')
        
    def ResetAll(self):
        path = os.path.join(xbmc.translatePath('special://userdata'), 'addon_data', self.id, 'settings.xml')
        if os.access(path, os.F_OK):
            os.chmod(path, stat.S_IWUSR)
            os.remove(path)

def GetTempDir():
    return xbmc.translatePath('special://temp')

class ActivateWindow(object):
    def __init__(self, window_id, var=''):
        self.settings = xbmcaddon.Addon(id=load('id'))
        self.modules = {}
        self.windows = load('windows')
        self.load()
        self.run(str(window_id), var)

    def path(self):
        return self.settings.getAddonInfo('path')

    def run(self, id, var):
        ui = self.modules[id].skin( self.windows[id]+'.xml' , self.path(), "Default", var)
        del ui

    def load(self):
        for key in self.windows.keys():
            importstring = 'skin.' + self.windows[key]
            mod = __import__(importstring)
            components = importstring.split('.')
            for comp in components[1:]:
              mod = getattr(mod, comp)
            self.modules[key] = mod

class GetWindow(object):
    def __init__( self, int=''):
        self.xbmc = window

    def GetControl(self, var):
        return Control(self.xbmc, self.xbmc.getControl(var), var)

    def GetLabel(self, var):
        return Control(self.xbmc, self.xbmc.getControl(var), var)

    def GetImage(self, var):
        return Control(self.xbmc, self.xbmc.getControl(var), var)

    def GetList(self, var):
        return Listmc(self.xbmc, self.xbmc.getControl(var), var)

class Control(object):
    def __init__( self, window, control, var):
        self.window = window
        self.control = control
        self.id = var

    def SetVisible(self, var):
        self.control.setVisibleCondition(str(var))

    def SetSelected(self, bool):
        self.control.setSelected(bool)

    def SetTexture(self, var):
        self.control.setImage(var)

    def SetLabel(self, var):
        self.control.setLabel(var)

    def GetLabel(self):
        return self.control.getLabel()

    def SetFocus(self):
        self.window.setFocus(self.control)

    def IsVisible(self):
        return xbmc.getCondVisibility( "Control.IsVisible(%i)" % self.id )


class Listmc(object):
    def __init__( self, window, control, var):
        self.window = window
        self.list = control
        self.id = var
        self.infolabels = {'genre':'genre','year':'year','episode':'episode','season':'season','top250':'top250','tracknumber':'tracknumber','contentrating':'rating','watched':'watched','viewcount':'playcount',
            'overlay':'overlay','cast':'cast','castandrole':'castandrole','director':'director','mpaa':'mpaa','plot':'plot','plotoutline':'plotoutline','title':'title','duration':'duration','studio':'studio',
            'tagline':'tagline','writer':'writer','tvshowtitle':'tvshowtitle','premiered':'premiered','status':'status','code':'code','aired':'aired','credits':'credits','lastplayed':'lastplayed','album':'album','votes':'votes','trailer':'trailer',
            'artist':'artist','lyrics':'lyrics', 'picturepath':'picturepath', 'exif':'exif'}

    def SetContentURL(url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        soup = BeautifulStoneSoup(link, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        channel = soup.channel.title.string
        channel_link = soup.channel.link.string
        channel_description = soup.channel.description.string
        try:
            channel_image = soup.channel.image.string
        except:
            channel_image = ''
        try:
            channel_language = soup.channel.language.string
        except:
            channel_language = ''
        try:
            channel_expiry = soup.channel('boxee:expiry')[0].string
        except:
            channel_expiry = ''
        items = soup('item')
        for item in items:
            try:
                title = item.title.string
            except:
                title = ''
            try:
                link = item.link.string
            except:
                link = ''
            try:
                guid = item.guid.string
            except:
                guid = ''
            try:
                description = item.description.string
            except:
                description = ''
            try:
                custom_display = item('boxee:property',attrs={'name' : "custom:display"})[0].string
            except:
                custom_display = ''
            try:
                custom_myteam = item('boxee:property', attrs={'name' : "custom:myteam"})[0].string
            except:
                custom_myteam = ''
            try:
                thumbnail = item('media:thumbnail')[0]['url']
            except:
                thumbnail = ''
            try:
                genre = item('media:category', attrs={'scheme' : 'urn:boxee:genre'})[0].string
            except:
                genre = ''
            try:
                boxee_type = item('boxee:media-type')[0]['type']
            except:
                boxee_type = ''
            try:
                release_date = item('boxee:release-date')[0].string
            except:
                release_date = ''
            try:
                episode = item('media:category', attrs={'scheme' : "urn:boxee:episode"})[0].string
            except:
                episode = ''
            try:
                season = item('media:category', attrs={'scheme' : "urn:boxee:season"})[0].string
            except:
                season = ''
            try:
                media_url = item('media:content')[0]['url']
            except:
                media_url = ''
            try:
                media_duration = item('media:content')[0]['duration']
            except:
                media_duration = ''
            try:
                media_type = item('media:content')[0]['type']
            except:
                media_type = ''
            try:
                media_height = item('media:content')[0]['height']
            except:
                media_height = ''
            try:
                media_width = item('media:content')[0]['width']
            except:
                media_width = ''
            try:
                media_lang = item('media:content')[0]['lang']
            except:
                media_lang = ''
		
    def GetFocusedItem(self):
        return self.list.getSelectedPosition()

    def SetItems(self, lst):
        xbmcgui.lock()
        self.list.reset()
        for i in lst:
            itm = i.list
            item=xbmcgui.ListItem(label=itm['Label'])
            infolist = {}
            for key in itm.keys():
                if key == 'Label':
                    item.setLabel(itm[key])
                elif key == 'Thumbnail':
                    item.setThumbnailImage(itm[key])
                elif key == 'Icon':
                    item.setIconImage(itm[key])
                else:
                    if key == 'path':
                        item.setPath(itm[key])
                    if key in self.infolabels.keys():
                        infolist[self.infolabels[key]] = itm[key]
                    item.setProperty(key, itm[key])
            self.list.addItem(item)
        xbmcgui.unlock()
    
    def SetFocusedItem(self, int):
        self.list.selectItem(int)

    def GetItem(self, int):
        return ListInfo(self.list.getListItem(int))

    def GetItems(self):
        listitems = []
        for i in range(self.list.size()):
            listitems.append(ListInfo((self.list.getListItem(i))))
        return listitems

    def GetSelected(self):
        return ListInfo(self.list.getSelectedItem().isSelected())

def ListItems():
    return []

class ListInfo(object):
    def __init__( self, item):
        self.item = item

    def GetLabel(self):
        try:
            return self.item.getLabel()
        except:
            return ""

    def GetThumbnail(self):
        try:
            return self.item.getProperty('Thumbnail')
        except:
            return ""

    def GetPath(self):
        try:
            return self.item.getProperty('path')
        except:
            return ""

    def GetAlbum(self):
        try:
            return self.item.getProperty('album')
        except:
            return ""

    def GetArtist(self):
        try:
            return self.item.getProperty('artist')
        except:
            return ""

    def GetAuthor(self):
        try:
            return self.item.getProperty('author')
        except:
            return ""

    def GetComment(self):
        try:
            return self.item.getProperty('comment')
        except:
            return ""

    def GetContentType(self):
        try:
            return self.item.getProperty('mime')
        except:
            return ""

    def GetDate(self):
        try:
            return self.item.getProperty('date')
        except:
            return ""

    def GetDescription(self):
        try:
            return self.item.getProperty('description')
        except:
            return ""

    def GetDirector(self):
        try:
            return self.item.getProperty('director')
        except:
            return ""

    def GetDuration(self):
        try:
            return self.item.getProperty('duration')
        except:
            return ""

    def GetEpisode(self):
        try:
            return self.item.getProperty('episode')
        except:
            return ""

    def GetGenre(self):
        try:
            return self.item.getProperty('genre')
        except:
            return ""

    def GetIcon(self):
        try:
            return self.item.getProperty('Icon')
        except:
            return ""

    def GetKeywords(self):
        try:
            return self.item.getProperty('keywords')
        except:
            return ""

    def GetProviderSource(self):
        try:
            return self.item.getProperty('providersource')
        except:
            return ""

    def GetContentRating(self):
        try:
            return self.item.getProperty('contentrating')
        except:
            return ""

    def GetSeason(self):
        try:
            return self.item.getProperty('season')
        except:
            return ""

    def GetStarRating(self):
        try:
            return self.item.getProperty('starrating')
        except:
            return ""

    def GetStudio(self):
        try:
            return self.item.getProperty('studio')
        except:
            return ""

    def GetTagLine(self):
        try:
            return self.item.getProperty('tagline')
        except:
            return ""

    def GetTrackNumber(self):
        try:
            return self.item.getProperty('tracknumber')
        except:
            return ""

    def GetTVShowTitle(self):
        try:
            return self.item.getProperty('tvshowtitle')
        except:
            return ""

    def GetTiSetViewCounttle(self):
        try:
            return self.item.getProperty('viewcount')
        except:
            return ""

    def GetWriter(self):
        try:
            return self.item.getProperty('writer')
        except:
            return ""

    def GetYear(self):
        try:
            return self.item.getProperty('year')
        except:
            return ""

    def GetProperty(self, var):
        try:
            return self.item.getProperty(var)
        except:
            return ""

class ListItem(object):
    MEDIA_UNKNOWN = 'video'
    MEDIA_AUDIO_MUSIC = 'music'
    MEDIA_AUDIO_SPEECH = 'music'
    MEDIA_AUDIO_RADIO = 'music'
    MEDIA_AUDIO_OTHER = 'music'
    MEDIA_VIDEO_MUSIC_VIDEO = 'video'
    MEDIA_VIDEO_FEATURE_FILM = 'video'
    MEDIA_VIDEO_TRAILER = 'video'
    MEDIA_VIDEO_EPISODE = 'video'
    MEDIA_VIDEO_CLIP = 'video'
    MEDIA_VIDEO_OTHER = 'video'
    MEDIA_PICTURE = 'pictures'
    MEDIA_FILE = 'pictures'
    
    def __init__( self, var ):
        self.list = {}
        self.type = var

    def SetLabel(self, var):
        self.list['Label'] = var

    def SetTitle(self, var):
        self.list['title'] = var

    def SetThumbnail(self, var):
        self.list['Thumbnail'] = var

    def SetPath(self, var):
        self.list['path'] = var

    def SetProperty(self, var1, var2):
        self.list[var1] = var2

    def SetAddToHistory(self, var):
        pass

    def SetAlbum(self, var):
        self.list['album'] = var

    def SetArtist(self, var):
        self.list['artist'] = var

    def SetAuthor(self, var):
        self.list['author'] = var

    def SetComment(self, var):
        paself.list['comment'] = varss

    def SetContentType(self, var):
        self.list['mime'] = var

    def SetDate(self, var):
        self.list['date'] = var

    def SetDescription(self, var):
        self.list['description'] = var

    def SetDirector(self, var):
        self.list['director'] = var

    def SetDuration(self, var):
        self.list['duration'] = var

    def SetEpisode(self, var):
        self.list['episode'] = var

    def SetGenre(self, var):
        self.list['genre'] = var

    def SetIcon(self, var):
        self.list['Icon'] = var

    def SetKeywords(self, var):
        self.list['keywords'] = var

    def SetProviderSource(self, var):
        self.list['providersource'] = var

    def SetContentRating(self, var):
        self.list['contentrating'] = var

    def SetExternalItem(self, var):
        pass

    def SetReportToServer(self, var):
        pass

    def SetSeason(self, var):
        self.list['season'] = var

    def SetStarRating(self, var):
        self.list['starrating'] = var

    def SetStudio(self, var):
        self.list['studio'] = var

    def SetTagLine(self, var):
        self.list['tagline'] = var

    def SetTrackNumber(self, var):
        self.list['tracknumber'] = var

    def SetTVShowTitle(self, var):
        self.list['tvshowtitle'] = var

    def SetTiSetViewCounttle(self, var):
        self.list['viewcount'] = var

    def SetWriter(self, var):
        self.list['writer'] = var

    def SetYear(self, var):
        self.list['year'] = var


def GetPlayer(var=xbmc.PLAYER_CORE_AUTO):
    return Player(var)

class Player(object):
    def __init__( self, var):
        self.xbmc = xbmc.Player(var)
        self.infolabels = {'genre':'genre','year':'year','episode':'episode','season':'season','top250':'top250','tracknumber':'tracknumber','contentrating':'rating','watched':'watched','viewcount':'playcount',
            'overlay':'overlay','cast':'cast','castandrole':'castandrole','director':'director','mpaa':'mpaa','plot':'plot','plotoutline':'plotoutline','title':'title','duration':'duration','studio':'studio',
            'tagline':'tagline','writer':'writer','tvshowtitle':'tvshowtitle','premiered':'premiered','status':'status','code':'code','aired':'aired','credits':'credits','lastplayed':'lastplayed','album':'album','votes':'votes','trailer':'trailer',
            'artist':'artist','lyrics':'lyrics', 'picturepath':'picturepath', 'exif':'exif'}

    def Play(self, obj):
        #if isinstance(lst, types.ListType):
        #    for i in lst:
        #        items.append(self.convertitem(i.list))
        #else:
        url, item = self.convertitem(obj)
        self.xbmc.play(url, item, False)

    def convertitem(self, i):
        itm = i.list
        item=xbmcgui.ListItem(label=itm['Label'])
        infolist = {}

        try: type = itm['mime']
        except: type = ''
        if type in ('video/x-ms-asf', 'video/x-ms-asx'):
            itm['path'] = self.CheckAsx(itm['path'])
        if ('.asx' or '.asf') in itm['path']:
            itm['path'] = self.CheckAsx(itm['path'])

        for key in itm.keys():
            if key == 'Label':
                item.setLabel(itm[key])
            elif key == 'Thumbnail':
                item.setThumbnailImage(itm[key])
            elif key == 'Icon':
                item.setIconImage(itm[key])
            else:
                if key == 'path':
                    item.setPath(itm[key])
                if key in self.infolabels.keys():
                    infolist[self.infolabels[key]] = itm[key]
                item.setProperty(key, itm[key])
        if infolist:
            item.setInfo(i.type, infolist)
        return itm['path'], item

    def CheckAsx(self, url):
        http = Http()
        data = http.Get(url).decode('utf-8')
        try:
            urlplay = re.compile('[Rr]ef href="mms://([^"]+)"', re.DOTALL + re.IGNORECASE + re.M).findall(data)[0]
            urlplay = 'mms://'+ urlplay
        except:
            try:
                urlplay = re.compile('http\://(.*?)"', re.DOTALL + re.IGNORECASE + re.M).findall(data)[0]
                urlplay = 'http://'+ urlplay
            except:
                urlplay = url
        return urlplay

    def GetPlayingItem(self):
        return self.xbmc.getPlayingFile()

    def GetTime(self):
        return self.xbmc.getTime()

    def GetTotalTime(self):
        return self.xbmc.getTotalTime()

    def GetVolume(self):
        #possibility to use JSON_RPC - http://wiki.xbmc.org/index.php?title=JSON_RPC#XBMC.GetVolume
        pass

    def IsCaching(self):
        pass

    def IsForwarding(self):
        pass

    def IsPaused(self):
        pass

    def IsPlaying(self):
        return self.xbmc.isPlaying()

    def IsPlayingAudio(self):
        return self.xbmc.isPlayingAudio()

    def IsPlayingVideo(self):
        return self.xbmc.isPlayingVideo()

    def LockPlayerAction(self):
        pass

    def Pause(self):
        return self.xbmc.pause()

    def Player():
        return Player()

    def PlayInBackground(self):
        pass

    def PlayNext(self):
        return self.xbmc.playnext()

    def PlayPrevious(self):
        return self.xbmc.playprevious()

    def PlaySelected(self):
        return self.xbmc.playselected()

    def PlayWithActionMenu(self):
        pass

    def SeekTime(self):
        return self.xbmc.seekTime()

    def SetLastPlayerAction(self):
        pass

    def SetLastPlayerEvent(self):
        pass

    def SetVolume(self, int):
        xbmc.executebuiltin('SetVolume('+str(int)+')')

    def Stop(self):
        return self.xbmc.stop()

    def ToggleMute(self):
        xbmc.executebuiltin('Mute')

#Keyboard variables
ACTION_MOVE_LEFT       =  1
ACTION_MOVE_RIGHT      =  2
ACTION_MOVE_UP         =  3
ACTION_MOVE_DOWN       =  4
ACTION_PAGE_UP         =  5
ACTION_PAGE_DOWN       =  6
ACTION_SELECT_ITEM     =  7
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9
ACTION_PREVIOUS_MENU   = 10
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_CONTEXT_MENU    = 117
ACTION_MOUSE_MOVE      = 90
ACTION_MOUSE_MOVE_WIN  = 107
ACTION_MOUSE_SCROLL_UP = 104
ACTION_MOUSE_SCROLL_DOWN = 105
ACTION_MOUSE_SCROLL_BAR = 106

ACTION_UPDOWN                   = (ACTION_MOVE_UP, ACTION_MOVE_DOWN, ACTION_PAGE_DOWN, ACTION_PAGE_UP)
ACTION_LEFTRIGHT                = (ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT)
ACTION_EXIT_CONTROLS            = (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR)
ACTION_CONTEXT_MENU_CONTROLS    = (ACTION_CONTEXT_MENU, ACTION_SHOW_INFO)
ACTION_MOUSE_MOVEMENT           = (ACTION_MOUSE_MOVE, ACTION_MOUSE_MOVE_WIN, ACTION_MOUSE_SCROLL_DOWN, ACTION_MOUSE_SCROLL_UP, ACTION_MOUSE_SCROLL_BAR)

#Load init
window = ''