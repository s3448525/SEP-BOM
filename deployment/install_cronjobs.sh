#!/bin/sh

#
# Setup cron jobs to keep the DB forecasts and observations fresh.
#

# Ensure script is running as the root user to allow configuring system components.
if [ `id -u` -ne 0 ]; then
    echo "Aborting, script expects to run as root to allow configuring system components."
    exit 1
fi

# Determine where to run scripts from.
feva_path=`pwd`
if [ ! -f "$feva_path/feva.py" ]; then
    echo "Failed to determine feva file path, tried: $feva_path"
    exit 1
fi

# Prompt for username.
echo "Enter the username who will run the cron jobs:"
read feva_user
if [ -z "$feva_user" ]; then
    echo "Aborting, username is empty."
    exit 1
fi

# Append load_observation job if not already in the crontab.
if ! (crontab -u "$feva_user" -l | grep -F -q 'model.load_observation'); then
    echo "Appending load_observation job."
    (
        crontab -u "$feva_user" -l;
        echo 'MAILTO=""';
        echo "5,20,35,50 * * * *  PYTHONPATH='$feva_path' python3 -m model.load_observation"
    ) | crontab -u "$feva_user" -
else
    echo "load_observation job already installed."
fi

# Append load_forecast job if not already in the crontab.
if ! (crontab -u "$feva_user" -l | grep -F -q 'model.load_forecast'); then
    echo "Appending load_forecast job."
    (
        crontab -u "$feva_user" -l;
        echo 'MAILTO=""';
        echo "0 7,20 * * *  PYTHONPATH='$feva_path' python3 -m model.load_forecast"
    ) | crontab -u "$feva_user" -
else
    echo "load_forecast job already installed."
fi

