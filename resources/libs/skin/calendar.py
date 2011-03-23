import os, sys, mc

import mlb

class skin(mc.Window):

    #Leave this function as is it will initiate the window
    def __init__(self, start, path, skin, var):
        self.var = var
        self.get = mc.Window.__init__(self, start, path, skin)
		
    #The function resables the 'onload' section of boxee
    #it will be executed on the window launch
    def onInit(self):
        mc.window = self

	mlb.setUpCalendar()


    def onAction(self, action):

        controlID = self.getFocusId()

        #makes sure the window closes when the user presses 'back'
        if action.getId() in ( mc.ACTION_PARENT_DIR, mc.ACTION_PREVIOUS_MENU ):
            self.close()

        """start your code"""

        """end your code"""

    #This function will excute code when a control is clicked
    #it passes the controls id as variable 'controlID'
    #it would resemble th boxee code 'onclick'
    def onClick(self, controlID):
 
        """start your code"""

        """end your code"""

	if controlID == 91:
            mlb.prevMonth()

	if controlID == 92:
            mlb.nextMonth()

	if controlID == 90:
            if mc.GetPlayer().IsPlayingAudio(): mc.ActivateWindow(12006)
            elif mc.GetPlayer().IsPlayingVideo(): mc.ActivateWindow(12005)

	if controlID == 1001:
            if mlb.isLoggedIn():
                #mc.GetActiveWindow().ClearStateStack()
                mc.ActivateWindow(14003)
            else:
                mc.ShowDialogNotification("You must be logged in to make changes to your settings.", "mlb-icon.png")

	if controlID == 1003:
            mc.ActivateWindow(14000)

	if controlID == 121:
            clear = mc.ListItems()
            mc.GetActiveWindow().GetList(4002).SetItems(clear)
            list =  mc.GetActiveWindow().GetList(121)
            item = list.GetItem( list.GetFocusedItem() )
            if item.GetProperty('today'):
                mc.ActivateWindow(14000)
            elif not item.GetProperty('display') or not item.GetDescription():
                mc.ShowDialogNotification('No games available for this day.', 'mlb-icon.png')
            else:
                date = item.GetPath()
                date = date.split(':')
                games = mlb.getGames(date[0], date[1], date[2])
                if games:
                    mc.GetActiveWindow().PushState()
                    mc.GetActiveWindow().GetList(4002).SetItems(games)
                    mc.GetActiveWindow().GetControl(4000).SetVisible(True)
                    mc.GetActiveWindow().GetList(4002).SetFocusedItem(0)
                    mc.GetActiveWindow().GetControl(4002).SetFocus()
                    mc.GetActiveWindow().GetList(4002).SetFocusedItem(0)
                else:
                    mc.ShowDialogOk("MLB.TV", "To view MLB Post Season content, please disconnect and reconnect your MLB.TV account at http://boxee.tv/services.")
                    item.Dump()

        if controlID == 4002:
            mlb.playList(4002)

	if controlID == 4003:
            mc.GetActiveWindow().PopState()

	if controlID == 501:
            mlb.playItem(501)

    #No equivilent in boxee code, but can execute code if a control is focussed
    def onFocus(self, controlId):

        """start your code"""

        """end your code"""
