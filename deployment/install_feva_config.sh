#!/bin/sh

#
# Setup Feva configuration.
#
echo "Setting up Feva config..."

# Check if main config already exists.
if [ -e './feva.cfg' ]; then
    echo "Aborting, feva.cfg already exists."
    exit 1
fi

# Prompt for the DB password.
echo -n 'Enter password for connecting to the DB:'
stty -echo
read db_passwd
stty echo
echo ''

# Prompt for the DB host.
echo -n "Enter DB host:"
read db_host
echo ''

# Create main config file.
cp -v './config.py' './feva.cfg'
sed -i -e"s/^DB_USERNAME =.*/DB_USERNAME = 'feva_user'/" './feva.cfg'
sed -i -e"s/^DB_HOST =.*/DB_HOST = '$db_host'/" './feva.cfg'
sed -i -e"s/^DB_PASSWORD =.*/DB_PASSWORD = '$db_passwd'/" './feva.cfg'

# Inform user about forecast and observation configuration.
echo "Forecast and observation configs may need manual adjustment, eg passwords."
echo "  see: model/forecast_config.py"
echo "  see: model/observation_config.py"
