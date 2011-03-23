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

	if controlID == 1001:
            if mlb.isLoggedIn():
                #mc.GetActiveWindow().ClearStateStack()
                mc.ActivateWindow(14003)
            else:
                mc.ShowDialogNotification("You must be logged in to make changes to your settings.", "mlb-icon.png")

	if controlID == 1002:
            #mc.GetActiveWindow().ClearStateStack()
            mc.ActivateWindow(14000)

	if controlID == 120:
            #mc.GetActiveWindow().PushState()

            wait = mc.ShowDialogWait()
            mlb.standings('national')
            mc.GetActiveWindow().GetControl(2000).SetVisible(False)
            mc.GetActiveWindow().GetLabel(3001).SetLabel('National League')
            mc.GetActiveWindow().GetControl(3000).SetVisible(True)
            mc.GetActiveWindow().GetControl(4000).SetFocus()
            mc.GetActiveWindow().GetControl(3002).SetFocus()
            mc.HideDialogWait(wait)

	if controlID == 121:
            #mc.GetActiveWindow().PushState()
            wait = mc.ShowDialogWait()
            mlb.standings('american')
            mc.GetActiveWindow().GetControl(2000).SetVisible(False)
            mc.GetActiveWindow().GetLabel(3001).SetLabel('American League')
            mc.GetActiveWindow().GetControl(3000).SetVisible(True)
            mc.HideDialogWait(wait)

	


    #No equivilent in boxee code, but can execute code if a control is focussed
    def onFocus(self, controlId):

        """start your code"""

        """end your code"""
        
