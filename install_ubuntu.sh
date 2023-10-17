#!/bin/bash
#
##############################################################################################
#
# TopZemen - Floating Pictures on your Screen
#
# For updates see git-repo at
# https://github.com/pronopython/topzemen
#
##############################################################################################
#
# Copyright (C) 2023 PronoPython
#
# Contact me at pronopython@proton.me
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################################
#

NAUTILUSSCRIPTDIR=~/.local/share/nautilus/scripts
INSTALLDIR=""


##################################################################################

link_module () {
	echo "installing $1"
	sudo ln -s $INSTALLDIR/$1 $NAUTILUSSCRIPTDIR/$2
	sudo chown $USER:$USER $NAUTILUSSCRIPTDIR/$2
}

##################################################################################


echo "TopZemen installer"
echo ""
echo "The installer now creates the program dirs."
echo "Sudo is needed for some actions."
echo ""

if ! type "printModuleDir_topzemen" >/dev/null 2>&1; then
	echo "Installing topzemen module via pip"
	pip install .
	echo ""
fi


INSTALLDIR="$(printModuleDir_topzemen)"

echo "TopZemen module installed in: ${INSTALLDIR}"
echo ""


echo ""
echo "TopZemen can work with nautilus file manager through scripts in nautilus' script dir."
echo "You then can open images or crawl directories via a right-click command."
echo "Note that sudo is needed for that action."
echo ""

while true; do

read -p "Do you want to install these scripts? (y/n) " yn

case $yn in 
	[yY] )  link_module open_in_topzemen.sh open-in-topzemen.sh;
	link_module crawl_in_zemenspawner.sh crawl-in-zemenspawner.sh;
		
		break;;

	[nN] )  
		break;;
		
	* ) echo invalid response;;
esac

done

echo "Changing permissions on installed module files"
sudo chmod 0755 $INSTALLDIR/*.py
sudo chmod 0755 $INSTALLDIR/*.sh


echo "done"

