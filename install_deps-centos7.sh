#!/bin/sh

#
# Install Feva dependencies on Centos 7
#

# Ensure script is running as the root user to allow installing system components.
if [ `id -u` -ne 0 ]; then
    echo "Aborting, script expects to run as root to allow installing system components."
    exit 1
fi

# Activate the EPEL YUM repo.
yum install epel-release

# Install dependencies supplied by YUM repos.
yum install postgresql postgresql-devel postgresql-server postgis netcdf netcdf-devel hdf5-devel

# Install python 3
yum install python34 python34-devel python34-numpy

# Install pip for python 3
# Method 2 from http://ask.xmodulo.com/install-python3-centos.html
curl -O https://bootstrap.pypa.io/get-pip.py
python3.4 get-pip.py
rm -fv get-pip.py

# Install python dependencies.
pip3 install psycopg2 sqlalchemy geoalchemy2 voluptuous netCDF4 flask
