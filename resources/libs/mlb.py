# 2011.03.14 14:21:05 CDT
import mc
import re
import urllib
import random
import base64
import datetime as dt
import simplejson as json
import monthdelta as md
from xml.dom.minidom import parse, parseString
status_error = -2
status_valid = 1
status_invalid = 0
status_missing = -1
send_to_server = True
send_to_history = True

def info(func, msg):
    mc.LogInfo(((('@mlb.tv (' + func) + ') ') + str(msg)))



def debug(func, msg):
    mc.LogDebug(((('@mlb.tv (' + func) + ') ') + str(msg)))



def error(func, msg):
    mc.LogError(((('@mlb.tv (' + func) + ') ') + str(msg)))



def raiseError(message = False, log = False, error = False):
    mc.HideDialogWait()
    if (log and error):
        mc.LogError(((('@mlb.tv (' + log) + ') ') + str(error)))
    if message:
        response = message
    else:
        response = 'An error has occurred. Details have been saved in your log. Please notify Boxee support.'
    mc.ShowDialogOk('MLB.TV', response)
    return False



def getJson(url = False, data = False):
    try:
        if url:
            data = mc.Http().Get(url)
        data = re.sub('//.*?\n|/\\*.*?\\*/', '', data, re.S)
        data = json.loads(data)
        return data
    except Exception, e:
        return raiseError(log='getjson', error=e)



def authenticate():
    try:
        content = mc.Http().Get('http://app.boxee.tv/api/get_application_data?id=mlb')
        if content:
            return status_error
        else:
            auth_dom = parseString(content)
            email = auth_dom.getElementsByTagName('email')[0].firstChild.data
            account = auth_dom.getElementsByTagName('rand_account')[0].firstChild.data
            post_data = request({'func': '_login',
             'email': email,
             'pass': account})
            if ((not post_data) or (post_data['data'] == '0')):
                Exception('post request return false')
            cf = mc.GetApp().GetLocalConfig()
            response = getJson(data=post_data['data'])
            response = response.get('identity')
            code = str(response.get('code'))
            if ((code != '1') and info('authenticate.code', code)):
                cf.Reset('fprt')
                cf.Reset('ipid')
                cf.Reset('username')
                cf.Reset('password')
                info('login', 'stored/entered credentials invalid')
                return status_invalid
            mc.HideDialogWait()
    except Exception, e:
        updateArchiveSpoiler()
        return status_invalid



def isLoggedIn():
    cf = mc.GetApp().GetLocalConfig()
    if (cf.GetValue('fprt') and cf.GetValue('ipid')):
        return True



def getCredentials():
    try:
        cf = mc.GetApp().GetLocalConfig()
        if (cf.GetValue('username') and cf.GetValue('password')):
            return {'user': cf.GetValue('username'),
             'pass': cf.GetValue('password')}
    except Exception, e:
        return raiseError(log='getCredentials', error=e)



def userLogout(prompt = True):
    try:
        confirm = True
        if prompt:
            confirm = mc.ShowDialogConfirm('MLB.TV', 'Would you like to sign out of MLB.TV? Your currently stored login information will be lost.', 'Cancel', 'Continue')
        if (confirm and logout()):
            mc.ActivateWindow(10482)
    except Exception, e:
        return raiseError(log='userLogout', error=e)



def launchWithItem(args):
    try:
        item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
        item.SetLabel(args['title'][0])
        item.SetDescription(args['description'][0])
        item.SetThumbnail(args['thumbnail'][0])
        item.SetProperty('alt-label', args['alt-label'][0])
        item.SetProperty('event-id', args['event-id'][0])
        item.SetProperty('content-id', args['content-id'][0])
        item.SetProperty('bx-ourl', args['bx-ourl'][0])
        item.SetProperty('audio-stream', args['audio-stream'][0])
        item.SetProperty('media-state', args['media-state'][0])
        playItem(mlbList=0, playFromListItem=item)
    except Exception, e:
        return raiseError('Unable to play requested stream. If this continues please contact support@boxee.tv', 'launchWithItem', e)



def init(args = False):
    try:
        info('init', 'mlb launched, checking authentication')
        auth = authenticate()
        if ((auth == status_valid) and mc.ShowDialogNotification('Welcome to MLB.TV!', 'mlb-icon.png')):
            if (args and launchWithItem(args)):
                pass
        return False
    except Exception, e:
        return raiseError(False, True)



def populateTodayScreen():
    try:
        w = mc.GetWindow(14000)
        w.GetList(120).SetFocusedItem(0)
        w.GetControl(120).SetFocus()
        w.GetList(120).SetFocusedItem(0)
        dt = getMonth(0)
        w.GetLabel(101).SetLabel(dt.strftime('%B %d, %Y'))
        games = getGames()
        if (games and w.GetList(120).SetItems(games)):
            pass
    except Exception, e:
        if (('AppException' in str(e)) and info('populateTodayScreen', e)):
            return False



def setUpCalendar():
    try:
        mc.GetWindow(14001).GetList(121).SetFocus()
        setMonth(0, False)
    except Exception, e:
        return raiseError(log='setUpCalendar', error=e)



def request(data):
    try:
        info('request', 'processing post request to boxee.tv')
        if ((not data) or (str(type(data)) != "<type 'dict'>")):
            return raiseError(log='request', error='data passed is not usable. contact support@boxee.tv')
        try:
            params = urllib.urlencode(data)
        except:
            return raiseError(log='request', error='data passed is not usable. contact support@boxee.tv')
        http = mc.Http()
        result = http.Post('http://dir.boxee.tv/apps/mlb/mlb.php', params)
        code = http.GetHttpResponseCode()
        http.Reset()
        if ((code != 200) and debug('request', ('post returned response code ' + str(code)))):
            pass
        if (result or debug('request', 'post return zero bytes')):
            pass
        if ((code == 200) and result):
            info('request', 'post was successfull')
        response = {'data': result,
         'code': code}
        return response
    except Exception, e:
        return raiseError(log='request', error=e)



def callService(func, values = {}, authenticated = True, content = False):
    try:
        info('callservice', ('calling the boxee_mlb service w/%s, authentication/%s' % (func,
         str(authenticated).lower())))
        params = {}
        http_service = mc.Http()
        url_base = 'http://dir.boxee.tv/apps/mlb/mlb.php?func=%s&%s'
        if authenticated:
            app = mc.GetApp()
            cf = app.GetLocalConfig()
            params['nsfp'] = cf.GetValue('fprt')
            params['nsid'] = cf.GetValue('ipid')
        if values:
            for i in values:
                params[i] = values[i]

        url_base = underscore((url_base % (func,
         urllib.urlencode(params))))
        query_result = http_service.Get(url_base)
        if (content == 'json'):
            query_result = re.sub('//.*?\n|/\\*.*?\\*/', '', query_result, re.S)
            query_result = json.loads(query_result)
        return query_result
    except Exception, e:
        return raiseError(log='callservice', error=e)



def getGames(year = False, month = False, day = False):
    try:
        mc.ShowDialogWait()
        if isLoggedIn():
            params = {}
            if (year and (month and day)):
                params['year'] = year
                params['month'] = month
                params['day'] = day
            try:
                games = callService('today', params, content='json').get('games')
            except:
                try:
                    games = callService('today', params, content='json').get('games')
                except:
                    return raiseError('Unable to fetch games list. Please try again later.', 'getgames', 'unable to fetch game list.')
            list = mc.ListItems()
            for game in games:
                item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
                item.SetLabel(str(game.get('title')))
                item.SetThumbnail(str(game.get('thumbnail')))
                item.SetDescription(str(game.get('description')))
                custom = game.get('custom:items')
                for value in custom:
                    item.SetProperty(str(value), str(custom.get(str(value))))

                images = game.get('image:items')
                for (key, value,) in enumerate(images):
                    item.SetImage(key, str(value))

                media_string = ''
                audio_string = ''
                media = game.get('media:items')
                if bool(media.get('has_video')):
                    video = media.get('video')
                    for stream in video:
                        if media_string:
                            media_string = (media_string + '||')
                        media_string = (((((media_string + str(stream.get('title'))) + '|') + str(stream.get('contentid'))) + '|') + str(stream.get('eventid')))

                if (media_string and item.SetProperty('media-string', media_string)):
                    pass
                if bool(media.get('has_audio')):
                    audio = media.get('audio')
                    for stream in audio:
                        if audio_string:
                            audio_string = (audio_string + '||')
                        audio_string = (((((audio_string + str(stream.get('title'))) + '|') + str(stream.get('contentid'))) + '|') + str(stream.get('eventid')))

                if (audio_string and item.SetProperty('audio-string', audio_string)):
                    pass
                list.append(item)

            mc.HideDialogWait()
            return list
        mc.HideDialogWait()
    except Exception, e:
        return raiseError('Unable to fetch game list! Please wait and try again. If problem persists contact support@boxee.tv!', 'getgames', e)



def standings(league):
    try:
        mc.ShowDialogWait()
        if (league == 'national'):
            league = 0
        elif (league == 'american'):
            league = 1
        data = getJson('http://mlb.mlb.com/lookup/json/named.standings_all_league_repeater.bam?sit_code=%27h0%27&league_id=104&league_id=103&season=2010')
        data = data.get('standings_all_league_repeater').get('standings_all')[league]
        stand = data.get('queryResults').get('row')
        east = mc.ListItems()
        west = mc.ListItems()
        central = mc.ListItems()
        for team in stand:
            item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            item.SetLabel(str(team.get('team_short')))
            item.SetThumbnail(('http://mlb.mlb.com/images/logos/200x200/200x200_%s.png' % str(team.get('team_abbrev'))))
            item.SetProperty('games-back', str(team.get('gb')))
            item.SetProperty('wild-card', str(team.get('wild_card')))
            item.SetProperty('elim-wildcard', str(team.get('elim_wildcard')))
            details = (((((((((((((((('Steak (' + team.get('streak')) + '), Home (') + team.get('home')) + '), Away (') + team.get('away')) + '), Vs Division (') + team.get('vs_division')) + '), Last Ten (') + team.get('last_ten')) + ')[CR]Winning Percentage (') + team.get('pct')) + '%), Wildcard (') + team.get('wild_card')) + '), Elimination Wildcard (') + team.get('elim_wildcard')) + ')')
            item.SetDescription(str(details))
            division = str(team.get('division'))
            if (('East' in division) and east.append(item)):
                pass

        mc.GetActiveWindow().GetList(3002).SetItems(west)
        mc.GetActiveWindow().GetList(3003).SetItems(central)
        mc.GetActiveWindow().GetList(3004).SetItems(east)
        mc.HideDialogWait()
    except Exception, e:
        return raiseError(message='There was a problem accessing standings. Please try again later.', log='league', error=e)



def favoriteTeams():
    try:
        mc.ShowDialogWait()
        data = getJson('http://mlb.mlb.com/lookup/json/named.team_all.bam?sport_code=%27mlb%27&active_sw=%27Y%27&all_star_sw=%27N%27')
        data = data.get('team_all').get('queryResults').get('row')
        teamList = mc.ListItems()
        for team in data:
            item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            item.SetLabel(str(team.get('name_display_full')))
            item.SetThumbnail(('http://mlb.mlb.com/images/logos/200x200/200x200_%s.png' % str(team.get('name_abbrev'))))
            item.SetProperty('team-id', str(team.get('team_id')))
            item.SetProperty('team-abbrev', str(team.get('team_abbrev')))
            teamList.append(item)

        favList = []
        for (index, team,) in enumerate(teamList):
            if ((team.GetProperty('team-id') in favList) and teamList.SetSelected(index, True)):
                pass

        mc.HideDialogWait()
        return teamList
    except Exception, e:
        raiseError(log='favoriteteams', error=e)



def getMonth(month = 0, formatted = False):
    try:
        date = (dt.date.today() + md.monthdelta(month))
        if formatted:
            return date
        else:
            return date.strftime('%B %Y')
    except Exception, e:
        raiseError(log='getmonth', error=e)
        return dt.date.today()



def setMonth(active, setList = True):
    try:
        window = mc.GetActiveWindow()
        cf = mc.GetApp().GetLocalConfig()
        cf.SetValue('calendar', str(active))
        if setList:
            month = getMonth(active, False)
            if (active == 0):
                url = month.strftime('rss://dir.boxee.tv/apps/mlb/feed/%Y/%m')
            else:
                url = 'rss://dir.boxee.tv/apps/mlb/feed/calendar'
            mc.GetActiveWindow().GetList(121).SetContentURL(url)
        window.GetLabel(102).SetLabel((('[UPPERCASE]' + getMonth(active, True)) + '[/UPPERCASE]'))
        window.GetLabel(103).SetLabel((('[UPPERCASE]' + getMonth((active + 1), True)) + '[/UPPERCASE]'))
        window.GetLabel(101).SetLabel((('[UPPERCASE]' + getMonth((active - 1), True)) + '[/UPPERCASE]'))
    except Exception, e:
        return raiseError(log='nextmonth', error=e)



def nextMonth():
    try:
        cf = mc.GetApp().GetLocalConfig()
        if cf.GetValue('calendar'):
            active = 0
        else:
            active = int(cf.GetValue('calendar'))
        setMonth((active + 1))
    except Exception, e:
        return raiseError(log='nextmonth', error=e)



def prevMonth():
    try:
        cf = mc.GetApp().GetLocalConfig()
        if cf.GetValue('calendar'):
            active = 0
        else:
            active = int(cf.GetValue('calendar'))
        setMonth((active - 1))
    except Exception, e:
        return raiseError(log='prevmonth', error=e)



def mediaServiceResponseCodes(id = -9999):
    if (id == -1000):
        return 'The requested media is not currently available.'
    elif (id == -2000):
        return 'invalid app account/partner'
    elif (id == -2500):
        return 'system error determining blackouts'
    elif (id == -3500):
        return 'too many active sessions/devices, this account is temporarily locked.'
    elif (id == -4000):
        return 'general system error'
    elif (id == -9999):
        return 'an unknown error'
    elif (id != -3000):
        return 'an unknown error'
    elif (id == -3000):
        return 'authentication key expired. please log in again to refresh.'



def queryMediaService(media_request, isAudio = False):
    try:
        http = mc.Http()
        cf = mc.GetApp().GetLocalConfig()
        rand_number = str(random.randint(10000, 100000000))
        http.Get((('http://mlbglobal08.112.2o7.net/b/ss/mlbglobal08/1/H.19--NS/' + rand_number) + '?ch=Media&pageName=BOXEE%20Request&c1=BOXEE'))
        http.Reset()
        media_service = http.Get(media_request)
        status_code = ''
        if ('status-code' in media_service):
            status_code = int(re.compile('<status-code>(.*?)<').findall(media_service)[0])
        if ('notAuthorizedStatus' in media_service):
            return {'playlist_url': -2,
             'media_state': ''}
        if (media_service and ('<url>' in media_service)):
            base_encoded_string = re.compile('<url>(.*?)<').findall(media_service)[0]
        media_state = ''
        if (media_service and ('<state>' in media_service)):
            media_state = re.compile('<state>(.*?)<').findall(media_service)[0]
        content_id = ''
        if (media_service and ('<content-id>' in media_service)):
            content_id = re.compile('<content-id>(.*?)<').findall(media_service)[0]
        event_id = ''
        if (media_service and ('<event-id>' in media_service)):
            event_id = re.compile('<event-id>(.*?)<').findall(media_service)[0]
        startDate = '0'
        innings_index = ''
        if (media_service and ('<innings-index>' in media_service)):
            innings_index = re.compile('<innings-index>(.*?)<').findall(media_service)[0]
            info('innings_index', innings_index)
            if innings_index.startswith('http'):
                http = mc.Http().Get(innings_index)
                if http:
                    startDate = '0'
                elif ('start_timecode' in http):
                    startDate = re.compile('start_timecode="(.*?)">').findall(http)[0]
                else:
                    startDate = '0'
        if (media_service and ('<session-key>' in media_service)):
            old_session = cf.GetValue('sessionid')
            session_key = re.compile('<session-key>(.*?)<').findall(media_service)[0]
            cf.SetValue('sessionid', session_key)
        if ((not isAudio) and ((not base_encoded_string.startswith('http://')) and (not base_encoded_string.startswith('rtmp://')))):
            request_params = base64.b64decode(base_encoded_string).split('|')
            (stream_url, stream_fingerprint, stream_params,) = request_params
            rand_number = str(random.randint(10000, 100000000))
            bx_ourl = ('http://mlb.mlb.com/media/player/entry.jsp?calendar_event_id=%s&source=boxeeRef' % event_id)
            tracking_url = (((('http://mlbglobal08.112.2o7.net/b/ss/mlbglobal08/1/G.5--NS/' + rand_number) + '?ch=Media&pageName=BOXEE%20Media%20Return&c25=') + content_id) + '%7CHTTP%5FCLOUD%5FWIRED&c27=Media%20Player&c43=BOXEE')
            params = {'stream-fingerprint': stream_fingerprint,
             'tracking-url': tracking_url,
             'startDate': startDate,
             'stream-params': stream_params}
            playlist_url = ('playlist://%s?%s' % (urllib.quote_plus(stream_url),
             urllib.urlencode(params)))
        data = {'playlist_url': playlist_url,
         'media_state': media_state}
        return data
    except Exception, e:
        raiseError(log='querymediaservice', error=e)
        return {'playlist_url': False,
         'media_state': ''}



def underscore(string):
    return string.replace('_', '%5F')



def promptQuality():
    try:
        cf = mc.GetApp().GetLocalConfig()
        q_ask = bool(cf.GetValue('ask_quality'))
        q_high = bool(cf.GetValue('high_quality'))
        q_default = bool(cf.GetValue('default_quality'))
        if ((not q_ask) and ((not q_high) and (not q_default))):
            q_ask = True
            cf.SetValue('ask_quality', '1')
        if q_ask:
            q_message = 'Please select your video quality (manage this and other options in the settings tab):'
            quality = mc.ShowDialogConfirm('MLB.TV', q_message, 'Normal', 'High')
            quality = int(quality)
        elif q_high:
            quality = 1
        else:
            quality = 0
        return str(quality)
    except Exception, e:
        return raiseError(log='promptquality', error=e)



def parseAudioStreams(item):
    try:
        play_audio = False
        audio_string = item.GetProperty('audio-string')
        audio_items = audio_string.split('||')
        if (len(audio_items) == 0):
            return raiseError('Unable to located proper audio items. This may be an error, please contact support@boxee.tv. We apologize for the inconvenience.', 'playitem', 'problem locating audio streams, audio-string property is empty or malformed')
        elif (len(audio_items) == 1):
            stream_1 = audio_items[0]
            stream_1 = stream_1.split('|')
            play_audio = stream_1
        elif (len(audio_items) > 1):
            stream_1 = audio_items[0]
            stream_2 = audio_items[1]
            stream_1 = stream_1.split('|')
            stream_2 = stream_2.split('|')
            confirm = mc.ShowDialogConfirm('MLB.TV', 'Please select the audio stream you wish to listen to...', stream_1[0], stream_2[0])
            if confirm:
                play_audio = stream_1
            else:
                play_audio = stream_2
        if (play_audio or raiseError()):
            return False
        return play_audio
    except Exception, e:
        return raiseError(log='parseaudiostreams', error=e)



def playItem(mlbList, forceAudioCheck = False, playFromListItem = False):
    if mc.ShowDialogWait():
        play_audio = False
        if playFromListItem:
            window = mc.GetActiveWindow()
            list = window.GetList(mlbList)
            index = list.GetFocusedItem()
            item = list.GetItem(index)
        else:
            item = playFromListItem
        session_id = 'null'
        cf = mc.GetApp().GetLocalConfig()
        if cf.GetValue('sessionid'):
            session_id = cf.GetValue('sessionid')
        if isLoggedIn():
            return raiseError('You must first log in before you can watch this game.')
        video_request_type = 'HTTP_CLOUD_WIRED'
        audio_request_type = 'AUDIO_SHOUTCAST_32K'
        audio_set_shout_protocol = False
        simulate_blackout = False
        simulate_not_authorized = False
        mr_url = 'https://secure.mlb.com/pubajaxws/bamrest/MediaService2_0/op-findUserVerifiedEvent/v-2.1?%s'
        params = {'subject': 'LIVE_EVENT_COVERAGE',
         'playbackScenario': video_request_type,
         'eventId': item.GetProperty('event-id'),
         'contentId': item.GetProperty('content-id'),
         'sessionKey': session_id,
         'fingerprint': cf.GetValue('fprt'),
         'identityPointId': cf.GetValue('ipid'),
         'platform': 'BOXEE'}
        web_url = ('http://mlb.mlb.com/media/player/entry.jsp?calendar_event_id=%s&source=boxeeRef' % item.GetProperty('event-id'))
        media_request = underscore((mr_url % urllib.urlencode(params)))
        if simulate_blackout:
            playlist_url = -1
        elif simulate_not_authorized:
            playlist_url = -2
        else:
            media_data = queryMediaService(media_request)
            playlist_url = media_data['playlist_url']
            update_media_state = media_data['media_state']
            if (bool(update_media_state) and (str(update_media_state).lower() != item.GetProperty('media-state').lower())):
                info('playitem', ('updating media_state (%s)' % update_media_state.lower()))
                item.SetProperty('media-state', update_media_state.lower())
        if (playlist_url == -3000):
            check_auth = authenticate()
            if (check_auth == status_valid):
                media_data = queryMediaService(media_request)
                playlist_url = media_data['playlist_url']
                update_media_state = media_data['media_state']
                if (bool(update_media_state) and (str(update_media_state).lower() != item.GetProperty('media-state').lower())):
                    info('playitem', ('updating media_state (%s)' % update_media_state.lower()))
                    item.SetProperty('media-state', update_media_state.lower())
            else:
                raiseError('Unable to validate your account. Please make sure your mlb.tv account is linked with Boxee! See boxee.tv/services.', 'playitem', 'lost users login credentials')
                mc.HideDialogWait()
                return False
        if ((playlist_url == -1) and ((not item.GetProperty('audio-string')) and (item.GetProperty('media-state') != 'media_on'))):
            return raiseError('No available audio streams found for this game. We apologize for the inconvenience.')
        confirm = mc.ShowDialogConfirm('MLB.TV', 'Video is not currently available for this game. Would you like to listen to the live audio broadcast?', 'No', 'Yes')
        if confirm:
            play_audio = parseAudioStreams(item)
            if play_audio:
                return False
            params = {'subject': 'LIVE_EVENT_COVERAGE',
             'playbackScenario': audio_request_type,
             'eventId': item.GetProperty('event-id'),
             'contentId': play_audio[1],
             'sessionKey': session_id,
             'fingerprint': cf.GetValue('fprt'),
             'identityPointId': cf.GetValue('ipid'),
             'platform': 'BOXEE'}
            del params['platform']
            media_request = underscore((mr_url % urllib.urlencode(params)))
            media_data = queryMediaService(media_request)
            playlist_url = media_data['playlist_url']
            update_media_state = media_data['media_state']
            if (bool(update_media_state) and (str(update_media_state).lower() != item.GetProperty('media-state').lower())):
                info('playitem', ('updating media_state (%s)' % update_media_state.lower()))
                item.SetProperty('media-state', update_media_state.lower())
        else:
            mc.HideDialogWait()
            return False
    if ((playlist_url == -2) and mc.GetActiveWindow().ClearStateStack()):
        return raiseError('You must own MLB.TV to watch live baseball. Please go to mlb.com/boxee to sign up.')
    if play_audio:
        content_type = 'audio/mpeg'
        stream_type = mc.ListItem.MEDIA_AUDIO_OTHER
        playlist_url = playlist_url.replace('http://', 'shout://')
    else:
        live = 0
        playlist_url = (playlist_url + ('&quality=%s' % promptQuality()))
        if (item.GetProperty('media-state') == 'media_on'):
            confirm = mc.ShowDialogConfirm('MLB.TV', 'Would you like to watch this game from the start or jump into the live broadcast?', 'Start', 'Live')
            live = int(confirm)
        playlist_url = ((playlist_url + '&live=') + str(live))
        content_type = 'application/vnd.apple.mpegurl'
        stream_type = mc.ListItem.MEDIA_VIDEO_OTHER
    alt_label = item.GetProperty('alt-label')
    title = alt_label.replace('#', '').replace('@mlbtv', '')
    title = (title.replace(' v ', ' @ ') + ' on MLB.TV')
    playlist_url = ((playlist_url + '&bx-ourl=') + urllib.quote_plus(web_url))
    ext = mc.ListItem(stream_type)
    ext.SetTitle(alt_label)
    ext.SetLabel(title)
    ext.SetDescription(item.GetDescription(), False)
    ext.SetContentType(content_type)
    ext.SetThumbnail(item.GetThumbnail())
    ext.SetProviderSource('MLB.TV')
    params = {'title': title,
     'alt-label': alt_label,
     'event-id': item.GetProperty('event-id'),
     'content-id': item.GetProperty('content-id'),
     'description': item.GetDescription(),
     'bx-ourl': web_url,
     'thumbnail': item.GetThumbnail(),
     'audio-stream': play_audio,
     'media-state': item.GetProperty('media-state')}
    if play_audio:
        params['audio-string'] = item.GetProperty('audio-string')
        rand_number = str(random.randint(10000, 100000000))
        tracking_url = (((((('http://mlbglobal08.112.2o7.net/b/ss/mlbglobal08/1/G.5--NS/' + rand_number) + '?ch=Media&pageName=BOXEE%20Media%20Return&c25=') + str(play_audio[2])) + '%7C') + underscore(audio_request_type)) + '&c27=Media%20Player&c43=BOXEE')
        notify = mc.Http().Get(tracking_url)
        del notify
    ext.SetPath(('app://mlb/launch?%s' % urllib.urlencode(params)))
    new_item = mc.ListItem(stream_type)
    new_item.SetLabel(title)
    new_item.SetTitle(alt_label)
    new_item.SetDescription(item.GetDescription(), False)
    new_item.SetPath(playlist_url)
    new_item.SetProviderSource('MLB.TV')
    new_item.SetContentType(content_type)
    new_item.SetThumbnail(item.GetThumbnail())
    if (play_audio and new_item.SetAddToHistory(False)):
        new_item.SetReportToServer(False)
    new_item.SetExternalItem(ext)
    mc.GetActiveWindow().ClearStateStack()
    try:
        track_label = generateTrackerGameString(item)
        if (track_label and myTracker.trackEvent('Video', 'Play', track_label)):
            pass
    except:
        myTracker.trackEvent('Video', 'Play', title)
    mc.HideDialogWait()
    mc.GetPlayer().Play(new_item)



def generateTrackerGameString(item):
    try:
        desc = item.GetDescription()
        event = item.GetProperty('event-id')
        desc = desc.split('[CR]')[0]
        event = event.split('-')[-3:]
        title = desc.replace(')', ((' ' + '-'.join(event)) + ')'))
        info('generateTrackerGameString', title)
        return title
    except:
        return False



def playList(mlbList):
    try:
        cf = mc.GetApp().GetLocalConfig()
        list = mc.GetActiveWindow().GetList(mlbList)
        item = list.GetItem(list.GetFocusedItem())
        if (isLoggedIn() or mc.ShowDialogNotification('You must first log in before you can watch this game.', 'mlb-icon.png')):
            pass
    except Exception, e:
        error('playlist', e)
        mc.ShowDialogNotification('Sorry, we are currently unable to play this game.', 'mlb-icon.png')
        return False



def logout():
    try:
        cf = mc.GetApp().GetLocalConfig()
        cf.Reset('fprt')
        cf.Reset('ipid')
        cf.Reset('username')
        cf.Reset('password')
        cf.Reset('hide_scores')
        return True
    except Exception, e:
        return raiseError(log='logout', error=e)



def updateArchiveSpoiler():
    try:
        mc.ShowDialogWait()
        if isLoggedIn():
            response = callService('showhide')
            if ((response == 'T') and mc.GetApp().GetLocalConfig().SetValue('hide_scores', 'true')):
                pass
        else:
            mc.GetApp().GetLocalConfig().Reset('hide_scores')
        mc.HideDialogWait()
    except Exception, e:
        mc.GetApp().GetLocalConfig().Reset('hide_scores')
        return raiseError(log='updatearchivespoiler', error=e)



def saveArchiveSpoiler(value):
    try:
        mc.ShowDialogWait()
        if isLoggedIn():
            response = callService('showhidesave', {'value': value})
            if ((response == '1') and mc.ShowDialogNotification('Score spoiler settings saved successfully!', 'mlb-icon.png')):
                pass
        else:
            mc.ShowDialogNotification('You must be logged in to modify settings.', 'mlb-icon.png')
        mc.HideDialogWait()
    except Exception, e:
        return raiseError(log='savearchivespoiler', error=e)



def selectFavorite(listId):
    try:
        found = False
        list = mc.GetActiveWindow().GetList(listId)
        itemNumber = list.GetFocusedItem()
        item = list.GetItem(itemNumber)
        selectedItems = list.GetSelected()
        for team in selectedItems:
            if (team.GetProperty('team-id') == item.GetProperty('team-id')):
                found = True
                list.SetSelected(itemNumber, False)

        if (found or list.SetSelected(itemNumber, True)):
            pass
    except Exception, e:
        return raiseError(log='selectfavorite', error=e)



def saveFavorites():
    try:
        mc.ShowDialogWait()
        favs = []
        for div in range(200, 206):
            items = mc.GetActiveWindow().GetList(div).GetSelected()
            for team in items:
                favs.append(team.GetProperty('team-id'))


        favs = ';'.join(favs)
        response = callService('setfavorites', {'teamids': favs})
        if ((response == '1') and mc.ShowDialogNotification('Your favorite teams have been saved successfully.', 'mlb-icon.png')):
            pass
        mc.HideDialogWait()
    except Exception, e:
        mc.GetActiveWindow().PopState()
        return raiseError(log='savefavorites', error=e)



def loadFavorites():
    try:
        mc.ShowDialogWait()
        mc.GetActiveWindow().PushState()
        if isLoggedIn():
            response = callService('teams')
            data = json.loads(response)
            data = data.get('teams')
            division = {'200': mc.ListItems(),
             '201': mc.ListItems(),
             '202': mc.ListItems(),
             '203': mc.ListItems(),
             '204': mc.ListItems(),
             '205': mc.ListItems()}
            for team in data:
                item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                item.SetLabel(str(team.get('title')))
                item.SetThumbnail(str(team.get('thumb')))
                item.SetProperty('team-id', str(team.get('team-id')))
                item.SetProperty('team-abbrev', str(team.get('team-abbrev')))
                item.SetProperty('team-leauge', str(team.get('team-leauge')))
                item.SetProperty('team-division', str(team.get('team-division')))
                item.SetProperty('team-fav', str(team.get('team-fav')))
                div = str(team.get('team-division'))
                division[div].append(item)

            for div in division:
                mc.GetActiveWindow().GetList(int(div)).SetItems(division[div])
                list = mc.GetActiveWindow().GetList(int(div))
                for (i, v,) in enumerate(list.GetItems()):
                    if ((v.GetProperty('team-fav') == '1') and list.SetSelected(i, True)):
                        pass


            mc.GetActiveWindow().GetControl(3000).SetVisible(True)
            mc.GetActiveWindow().GetList(200).SetFocusedItem(0)
            mc.GetActiveWindow().GetControl(200).SetFocus()
            mc.GetActiveWindow().GetList(200).SetFocusedItem(0)
        else:
            return raiseError('You must be logged in to access your favorite teams!')
        mc.HideDialogWait()
    except Exception, e:
        mc.GetActiveWindow().PopState()
        return raiseError('An error occured while accessing your favorite team settings. Are you logged in?', log='loadfavorites', error=e)
