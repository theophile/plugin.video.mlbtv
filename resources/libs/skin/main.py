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

	mlb.populateTodayScreen()

    def onAction(self, action):

        controlID = self.getFocusId()

        #makes sure the window closes when the user presses 'back'
        if action.getId() in ( mc.ACTION_PARENT_DIR, mc.ACTION_PREVIOUS_MENU ):
            self.close()

        """start your code"""

        """end your code"""

    def onClick(self, controlID):

        if controlID == 90:
            if mc.GetPlayer().IsPlayingAudio(): mc.ActivateWindow(12006)
            elif mc.GetPlayer().IsPlayingVideo(): mc.ActivateWindow(12005)

        if controlID == 1001:
            if mlb.isLoggedIn():
                #mc.GetActiveWindow().ClearStateStack()
                mc.ActivateWindow(14003)
            else:
               mc.ShowDialogNotification("You must be logged in to make changes to your settings.", "mlb-icon.png")

        if controlID == 1002:
            mc.ActivateWindow(14001)

        if controlID == 1003:
            mc.ActivateWindow(14002)

        if controlID == 120:
            mlb.playList(120)

        if controlID == 501:
            mlb.playItem(501)

    #No equivilent in boxee code, but can execute code if a control is focussed
    def onFocus(self, controlId):

        """start your code"""

        """end your code"""

