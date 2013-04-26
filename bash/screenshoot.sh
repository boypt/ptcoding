#!/bin/bash

#sleep .5;
SCREEN=/tmp/`date '+%Y-%m-%d_%H-%M-%S'`.png
scrot -bs "$SCREEN"

if [[ ! -e "$SCREEN" ]]; then
    zenity --info --text="No image grabbed."
    exit 0
fi

ACTION=$(zenity --list  --height=250 --title="What to do with the image" --column="How" "Save" "Temp" "Upload")

if [[ $ACTION == "Save"* ]]; then
    TO_PATH=$(zenity --file-selection --save --confirm-overwrite --filename "$SCREEN")
    mv "$SCREEN" "$TO_PATH"
    zenity --info --text="$TO_PATH"
elif [[ $ACTION == "Upload"* ]]; then
    #URL=$(curl -F "image=@$SCREEN" -F "key=486690f872c678126a2c09a9e196ce1b" http://imgur.com/api/upload.xml|sed -n "s/^.\+<original_image>\(.\+\)<\/original_image>.\+/\1/p")
    URL=$(curl -F "name=@$SCREEN" http://img.vim-cn.com/)
    zenity --info --text="$URL"
else
    zenity --info --text="$SCREEN"
ri

