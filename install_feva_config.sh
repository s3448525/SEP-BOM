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

# Create main config file.
cp -v './config.py' './feva.cfg'
echo "Enter DB username, Feva will connect using this:"
read db_username
echo "Enter DB host:"
read db_host
sed -i -e"s/^DB_USERNAME =.*/DB_USERNAME = '$db_username'/" './feva.cfg'
sed -i -e"s/^DB_HOST =.*/DB_HOST = '$db_host'/" './feva.cfg'
sed -i -e"s/^DB_PASSWORD =.*/DB_PASSWORD = 'password'/" './feva.cfg'

# Inform user about forecast and observation configuration.
echo "Forecast and observation configs may need manual adjustment, eg passwords."
echo "  see: model/forecast_config.py"
echo "  see: model/observation_config.py"
