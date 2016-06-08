#!/bin/bash

#Create some test entries in the database
#The default DBNAME is 'feva' which is the actual database
#It can be another dummy datdabase which has the same 
 

DBNAME=$1 

if [ ! "$DBNAME" ]
	then
		DBNAME="feva"
fi
##for observation data

for i in {28..31}
 do
  timestamp="2016-05-$i 17:00:00"
  str1="0101000020E610000031ED9BFBAB27194058C7F143A5"
  str2="54A40"
  for j in {1..9}
	do
		location="$str1$j$str2"
		value="0.0000"
		#echo $location
		sqlcmd="psql -t -d $DBNAME -c $'INSERT INTO tbl_rainfall_observations VALUES (\'$timestamp\', \'$location\', $value, \'WOW\');'"
		#un-comment the bellow line to put some data into database
		su -c "$sqlcmd" - postgres
	done
 done

 
##for forecast data
for i in {28..31}
 do
  timestamp="2016-05-$i 17:00:00"
  timestamp2="2016-05-$i 20:00:00"
  name="BOM Official Rain VIC"
  creationdate="2016-05-$i 18:00:00"
  daterange="[\"$timestamp\",\"$timestamp2\")"
  sqlcmd="psql -t -d $DBNAME -c $'INSERT INTO tbl_forecasts \
  (name,creation_date,date_range) \
  VALUES (\'$name\',\'$creationdate\',\'$daterange\');'"
  #un-comment the bellow line to put some data into database
  su -c "$sqlcmd" - postgres
 done

for id in `su -c "psql -t -d $DBNAME -c $'select id from tbl_forecasts;'" - postgres`
	do
		str1="0101000020E610000031ED9BFBAB27194058C7F143A5"
		str2="54A40"
		for j in {1..4}
			do
				location="$str1$j$str2"
				value="0.0000"
				sqlcmd="psql -t -d $DBNAME -c $'INSERT INTO \
				tbl_forecast_values (id_forecast,location,value) VALUES ($id,\'$location\',$value);'"
				#echo $sqlcmd
				#un-comment the bellow line to put some data into database
		        su -c "$sqlcmd" - postgres
				#echo $sqlcmd
			done
		for j in {5..9}
			do
				location="$str1$j$str2"
				value="70.0000"
				sqlcmd="psql -t -d $DBNAME -c $'INSERT INTO \
				tbl_forecast_values (id_forecast,location,value) VALUES ($id,\'$location\',$value);'"
				#un-comment the bellow line to put some data into database
		        su -c "$sqlcmd" - postgres
			done
		
	done
 
 
