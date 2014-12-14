#!/bin/bash

SRC="/volumes/Movie-MKV/$1"
DEST="$SRC"
DEST_EXT=mp4
HANDBRAKE_CLI=HandBrakeCLI
PRESET="Apple TV 3 w/De-Interlaces & No Crop"

for FILE in "$SRC"/*
do
filename=$(basename $FILE)
extension=${filename##*.}
filename=${filename%.*}

$HANDBRAKE_CLI -i $FILE -o "$DEST"/"$filename".$DEST_EXT --preset="$PRESET"
done