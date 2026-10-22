#!/usr/bin/env bash
for i in {1..5}
do
    text=$(curl -s "https://wttr.in/$1?format=1")
    if [[ $? == 0 ]]
    then
        text=$(echo "$text" | sed -E "s/\s+/ /g")
		  tooltip=$(curl -s "wttr.in/$1?0&Q&T")
		  tooltip=$(echo "$tooltip" | sed 's/\\/\\\\/g' | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g')
		  # tooltip=$(curl -s "https://wttr.in" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
	 if [[ $? == 0 ]]
        then
            echo "{\"text\":\"$text\", \"tooltip\":\"$tooltip\"}"
            exit
        fi
    fi
    sleep 2
done
echo "{\"text\":\"error\", \"tooltip\":\"error\"}"
