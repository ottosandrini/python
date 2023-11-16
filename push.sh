#!/bin/bash

a=`find . -type f -name "*.swp"`
if [ "$a" != "" ]; then
	echo "the repository contains a swap file! Are you sure you want to continue? (y/n)"
	read resp
	if [ "$resp" = "n" ]; then
		echo "canceling push"
		exit
	elif [ "$resp" = "y" ]; then
		echo "continuing to push files"
	else
		echo "not a valid response! canceling push"
		exit
	fi
fi

token=`cat -s ~/Documents/python/telegrambot/token.txt 2>/dev/null`

if [ "$token" = "" ]; then
  echo "error fetching token"
  exit
fi

echo "token fetched succesfully"

git add --all

echo "please enter commit message: "
read msg
echo "$msg"

git commit -m "$msg"

git push -u origin master
