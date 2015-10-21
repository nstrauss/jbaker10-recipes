#!/usr/bin/python

import os
import os.path

# Check if EndNote Cite While You Write is already installed
endnote_bundle_2011 = os.path.exists("/Applications/Microsoft Office 2011/Office/Startup/Word/EndNote CWYW Word 2011.bundle")
endnote_bundle_2008 = os.path.exists("/Applications/Microsoft Office 2008/Office/Startup/Word/EndNote CWYW Word 2008.bundle")

def check_endnote_2011:
	# If the CWYW bundle is installed for Office 2011, then remove it
	if endnote_bundle_2011:
		print "EndNote bundle is installed for Office 2011"
		os.remove("/Applications/Microsoft Office 2011/Office/Startup/Word/EndNote CWYW Word 2011.bundle")
	else:
		print "EndNote bundle is not installed for Office 2011"
		print "Proceeding with installation"

def check_endnote_2008:
	# If the CWYW bundle is installed for Office 2008, then remove it
	if endnote_bundle_2008:
		print "EndNote bundle is installed for Office 2008"
		os.remove("/Applications/Microsoft Office 2008/Office/Startup/Word/EndNote CWYW Word 2008.bundle")
	else:
		print "EndNote bundle is not installed for Office 2008"
		print "Proceeding with installation"