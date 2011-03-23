import tracker
import mlb
import cgi
import sys
import mc

wait = mc.ShowDialogWait()

args = False
myTracker = tracker.Tracker()
myTracker.trackView("Launch")

if sys.argv[1]:
   args = cgi.parse_qs(sys.argv[1])

if not mlb.init(args):
   mc.HideDialogWait(wait)
