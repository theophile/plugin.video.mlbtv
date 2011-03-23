import mlb
import cgi
import sys
import mc

mc.ShowDialogWait()

args = False

if sys.argv[1]:
   args = cgi.parse_qs(sys.argv[1])

if not mlb.init(args):
   mc.HideDialogWait()
