#!/bin/bash

# A simple script that tries out various xarta commands and looks for errors.
# Note that this does not test things like formatting for commands like choose and browse.

function error {
    echo -e "\n\e[1;31m  ERROR \e[0m\n\n"
}

test_open=False


#dont overwrite users ~/.xarta --> use a config file in CWD
XARTACONFIG=$(pwd)
XARTACONFIG+="/xartaconfig"

xarta init || error
xarta init xarta_test.db || error
xarta add 1704.05849 --alias "JohnnyG" leptoquarks neutrino-mass flavour-anomalies || error
xarta add https://arxiv.org/pdf/1911.06334.pdf test || error
xarta add arxiv:1812.02651 || error
xarta alias 1812.02651 alias1 || error
xarta alias alias1 alias2 || error
xarta refresh alias2 || error
xarta browse || error
xarta browse neutrino-mass || error

echo 'this should fail:'
xarta browse --filter="'John' in authors and ('neutrino' in tags or 'leptoquarks' in tags)" && error

#enabling filters
sed 's:False:True:g' -i $XARTACONFIG

xarta browse --filter="'John' in authors and ('neutrino' in tags or 'leptoquarks' in tags)" || error
xarta browse --filter="'John' in authors or 'Reconsidering' in title" || error
xarta browse --filter='"1704" in ref and ("trino" in tags or "lepto" in tags)' || error
xarta browse --filter='"1704" in Ref and ("trino" in Tags or "lepto" in tags)' || error
xarta browse --filter='"John" in authors and "hep-ph" in category' || error
xarta list tags --sort=number || error
xarta list authors --sort=date-added || error
xarta list aliases || error
xarta tags add 1704.05849 self_author || error
xarta tags remove 1704.05849 leptoquarks || error
xarta tags set 1704.05849 something || error
xarta tags add 1911.06334 something_else || error
xarta rename something something_new
xarta rename something_else
xarta hello || error
xarta info 1704.05849 || error
xarta info alias2 || error
xarta export inspire ./xarta.bib --export-alias || error
xarta export arxiv ./xarta2.bib --author='Rebecca' || error
if [ "$test_open" == "True" ]; then
    xarta open 1704.05849 || error
    xarta open 1704.05849 --pdf || error
    xarta open alias2 || error
    xarta open hep-ph || error
    xarta choose something_new || error
fi
xarta delete alias2 || error
xarta delete 1704.05849 || error


read -p 'delete temporary files (Y/n)?' response
if [ "$response" != "n" ]; then
    rm $XARTACONFIG
    rm xarta.bib
    rm xarta2.bib
    rm xarta.db
    rm xarta_test.db
fi

