'''
Do the bellowing before run this file
export   PYTHONPATH=/opt/feva/model:$PYTHONPATH
'''
import datetime
from datetime import timedelta
from model.evaluator import Evaluator
import re
import getopt
import sys


def main(argv):
	lat = 144.9643
	lon = -37.8099
	maxd = 10000
	day = 0
	starttime = datetime.datetime.now()
	try:
		opts,args = getopt.getopt(argv,"hla:lo:m:d:",["lat","lon","maxdistance","day"])
	except getopt.GetoptError:
		print ('evaluator.py -la <latitude> -lo <longitude> -m <max distance> -d <day>')
		sys.exit(2)
	for opt,arg in opts:
		if opt == '-h':
			print ('evaluator.py -la <latitude> -lh <longitude> -m <max distance> -d <day>')
			sys.exit()
		elif opt == '-la':
			lat = arg
		elif opt == '-lo':
			lon = arg
		elif opt == '-m':
			maxd = arg
		elif opt == '-d':
			day = arg
	from feva import db
	expr1 = "True"
	split1 = ","
	eva = Evaluator(db)
	print ('Start time: ',starttime)
	print ('latitude is: ',lat)
	print ('longitude is: ',lon)
	print ('max distance: ',maxd)
	lat = float (lat)
	long = float (lon)
	maxd = float (maxd)
	day = int (day)
	time = datetime.datetime.now() - datetime.timedelta(day)
	print ('The date to be queried is: ',time)
	results = eva.evaluate_lat_lon(lat, lon, time, maxd)
	i = 0
	for result in results:
		result = str (result)
		slist1 = result.split(split1)
		if re.search(expr1,result):
			print (i,"True")
			print (slist1)
		else:
			print (i,"False")
			print (slist1)
		i += 1
	
	finishtime = datetime.datetime.now()
	duration1 = finishtime - starttime
	duration = duration1 / timedelta(minutes=1)
	print ('Finish time: ',finishtime)
	print ('Duraton: ',duration,' minutes')
			
if __name__ == '__main__':
    # Connect to the db.
	main(sys.argv[1:])
	
