#!/bin/bash

if [ -z "$1" ]; then
	echo "Syntax: ./import-translations.sh launchpad-url"
	exit 1
fi

pushd Koo/l10n

url="$1"

appdir=$(pwd)
tmpdir=$(mktemp -d)

echo "TMP DIR: $tmpdir"

pushd $tmpdir
wget $url
tar zxvf *.tar.gz

# Import translations of koo.pot
for file in $(find -iname "koo-*.po"); do
	lang=$(echo $file | cut -d "-" -f 2 | cut -d "." -f 1)
	cp $file $appdir/$lang.po
done

# Import translations of qt-koo.pot
for file in $(find -iname "qt-koo-*.po"); do
	echo "IMPORTING: ", $file
	lang=$(echo $file | cut -d "-" -f 3 | cut -d "." -f 1)
	cp $file $appdir/qt-koo-$lang.po
	lconvert $appdir/qt-koo-$lang.po -o $appdir/$lang.ts
	echo "CREATED: " $appdir/$lang.ts
done

rm -r $tmpdir

popd

popd
