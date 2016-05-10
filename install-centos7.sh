#!/bin/sh

#
# Install Feva, it's dependencies and configuration, ideally resulting in a
# running Feva application.
#
# This script is tailored for Centos 7
#

echo "Becoming root user to install system components..."
su -c './deployment/install_deps-centos7.sh && ./deployment/install_db.sh && ./deployment/install_cronjobs.sh' root
./deployment/install_feva_config.sh
