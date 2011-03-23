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
	mc.GetActiveWindow().GetControl(121).SetFocus()



    #This function should house the boxee code that should execute on keyboard actions
    #For the boxee skin this could be an python action that was situated in <ondown><ondown> or <onup><onup>
    #You can find all the keyboard shortcuts in the end of the mc file
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
 
        if controlID == 90:
		if mc.GetPlayer().IsPlayingAudio(): mc.ActivateWindow(12006)
		elif mc.GetPlayer().IsPlayingVideo(): mc.ActivateWindow(12005)

        if controlID == 1004:	
		mc.ActivateWindow(14000)

	if controlID == 1005:
		mc.ActivateWindow(14001)

	if controlID == 1006:
		mc.ActivateWindow(14002)

	if controlID == 1007:
		mc.ActivateWindow(14000)

	if controlID == 121:
		mlb.loadFavorites()

	if controlID == 122:
		mlb.updateArchiveSpoiler()
		mc.GetActiveWindow().PushState()
		mc.GetActiveWindow().GetControl(5000).SetVisible(True)
		mc.GetActiveWindow().GetControl(5050).SetFocus()

	if controlID == 123:
		mc.GetActiveWindow().PushState()
		mc.GetActiveWindow().GetControl(5600).SetVisible(True)
		mc.GetActiveWindow().GetControl(5600).SetFocus()

	
	if controlID == 5060:
		mc.GetActiveWindow().PopState()

	if controlID == 5051:
		mlb.saveArchiveSpoiler('F')
		mc.GetActiveWindow().PopState()

	if controlID == 5052:
		mlb.saveArchiveSpoiler('T')
		mc.GetActiveWindow().PopState()

	if controlID == 5660:
		mc.GetActiveWindow().PopState()

	if controlID == 5651:
		mc.GetActiveWindow().PopState()

	if controlID == 5652:
		mc.GetActiveWindow().PopState()

	if controlID == 5653:
		mc.GetActiveWindow().PopState()

	if controlID == 200:
		mlb.selectFavorite(200)

	if controlID == 202:
		mlb.selectFavorite(202)

	if controlID == 201:
		mlb.selectFavorite(201)

	if controlID == 203:
		mlb.selectFavorite(203)

	if controlID == 205:
		mlb.selectFavorite(205)

	if controlID == 204:
		mlb.selectFavorite(204)

	if controlID == 3101:
		mlb.saveFavorites()
		mc.GetActiveWindow().PopState()

	if controlID == 3102:
		mc.GetActiveWindow().PopState()

	


    #No equivilent in boxee code, but can execute code if a control is focussed
    def onFocus(self, controlId):

        """start your code"""

        """end your code"""
        
