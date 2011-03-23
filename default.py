#--------------------------------------
#--------- Main Config ----------------
id = 'plugin.video.mlbtv'
init = '14000'
windows = { '14000' : 'main',
 	    '14001' : 'calendar',
            '14003' : 'settings',
            '14002' : 'standings' }


#--------------------------------------
#--------- Do not change ----------------
import sys, os
path = os.path.join(os.getcwd().replace(";",""),'resources','libs')
sys.path.append(path)

import mc
mc.start(id, windows)

if ( __name__ == "__main__" ):
    mc.ActivateWindow(init)
