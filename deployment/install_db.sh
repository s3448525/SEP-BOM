#!/bin/sh

#
# Prepare postgresql and create the feva database.
#

# Ensure script is running as the root user to allow configuring system components.
if [ `id -u` -ne 0 ]; then
    echo "Aborting, script expects to run as root to allow configuring system components."
    exit 1
fi

# Check if database already exists.
if (su -c 'psql -l -t --no-align | cut -d"|" -f1 | grep -q feva' - postgres); then
    echo "Aborting, feva database already exists."
    exit 1
fi

# Prompt for DB username.
echo "Enter the DB username, used to create the feva DB and open connections from the application:"
read feva_user
if [ -z "$feva_user" ]; then
    echo "Aborting, username is empty."
    exit 1
fi

# Initialise DB if this is a fresh postgresql installation.
echo "Initialise postgresql using 'postgresql-setup initdb' (y/n)?"
read init_postgre_prompt
if [ "$init_postgre_prompt" == "y" ]; then
    echo "Running 'postgresql-setup initdb'"
    postgresql-setup initdb
else
    echo "Skipping 'postgresql-setup initdb'"
fi

# Disable ident auth on local connections.
sed -i -e's/^\(host .*127\.0\.0\.1\/32.* ident\)$/#\1/' /var/lib/pgsql/data/pg_hba.conf
sed -i -e's/^\(host .*::1\/128.* ident\)$/#\1/' /var/lib/pgsql/data/pg_hba.conf
# Enable md5 passwords for local connections.
echo "host    all    $feva_user    127.0.0.1/32    md5" >>/var/lib/pgsql/data/pg_hba.conf

# Start DBMS running.
systemctl enable postgresql.service
systemctl start postgresql.service

# Create Feva DB and enable postgis extension.
# Create a DB login account.
# Centos7 needed a GRANT ON spatial_ref_sys.
cat - >/tmp/psql_tmp.sql <<EOFEOF
CREATE DATABASE feva;
\\connect feva
CREATE EXTENSION postgis;

CREATE ROLE $feva_user WITH PASSWORD 'password' LOGIN;
GRANT SELECT ON spatial_ref_sys TO $feva_user;
EOFEOF
su -c "psql -e -f /tmp/psql_tmp.sql" - postgres
rm -f /tmp/psql_tmp.sql

