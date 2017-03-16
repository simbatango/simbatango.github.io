""" 
A small plugin to read recording date from the tango.info database


Changelog:

    [2007-08-08] Updated to alpha 14
    [2007-12-05] Updated to change in tracks.csv 
    [2008-05-23] Updated to change in tracks.csv 
    [2008-07-17] Reads header row of tracks.csv
    [2008-07-30] Updated to 0.10
"""

PLUGIN_NAME = 'tango.info (date)'
PLUGIN_AUTHOR = 'Lars Hellemo'
PLUGIN_DESCRIPTION = '<b>Reads recording dates from tango.info</b> <br />Get tracks.csv from <a href="http://open.tango.info/tracks.csv">http://open.tango.info/tracks.csv</a> and put it in the plugins directory together with this plugin.'
PLUGIN_VERSION = "0.2"
PLUGIN_API_VERSIONS = ["0.9.0", "0.10"]


from picard.metadata import register_track_metadata_processor
import re,os

_discnumber_re = re.compile(r"\s+\(disc (\d+)(?::\s+([^)]+))?\)")


def get_data_from_csv():
	HTRACK = "track_num"
	HDISC = "album_side"
	HGENRE = "track_genre"
	HDATE = "track_date"
	HBARCODE = "album_tin"

	idate = {'test':'2007-01-01'}
	header_no = {};
	count = 0;
	try:
		file = open(os.path.dirname(__file__)+'/tracks.csv','r')
		while 1:
			count = count+1
			if (count < 2):#Header row
				line = file.readline()
				if not line:
					break
				list = line.split(';')
				header_index = 0
				for i in list:
					header_no[i] = header_index
					header_index = header_index +1 
			else:
				line = file.readline()
				if not line:
					break
				list = line.split('\";\"')
				list[0]=list[0][1:]


				if is_valid_barcode(list[header_no[HBARCODE]]):
					infobar = int(list[header_no[HBARCODE]])
					if (is_integer(list[header_no[HDISC]])):
						infodisc = int(list[header_no[HDISC]])
					else:
						infodisc = 1
					if (is_integer(list[header_no[HTRACK]])):
						infotrack = int(list[header_no[HTRACK]])
						infodictkey = str(infobar) + "#" + str(infodisc) + "#" + str(infotrack)
						idate[infodictkey] = list[header_no[HDATE]]



	except IOError:
		print "Could not open file: plugins/tracks.csv"
		1

	return idate


def is_valid_barcode(testbarcode):
	return is_integer(testbarcode)

def is_integer(testinteger):
	try:
		int(testinteger)
		return True
	except:
		return False	


ddate = get_data_from_csv()


def get_discnumber(metadata):
    retval = 1
    if (is_integer(metadata["discnumber"])):
	if metadata["discnumber"]>0:
		retval = metadata["discnumber"]
    else:	
	    matches = _discnumber_re.search(metadata["album"])
	    if matches:
        	retval =  matches.group(1)	
    return retval

def set_tangoinfo_date(tagger, metadata, release, track):
	mydiscnumber = get_discnumber(metadata)


	if(len(metadata["barcode"])>0):
		myidk = str(int(metadata["barcode"]))+"#"+str(mydiscnumber)+"#"+metadata["tracknumber"]
		if myidk in ddate:
			metadata['Date'] = ddate[myidk]
			
register_track_metadata_processor(set_tangoinfo_date)
