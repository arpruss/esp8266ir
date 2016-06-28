#!/system/bin/sh
nc 192.168.1.123 5678 | tr -d '\15' | while read line ; do
   echo $line
   if [[ $line == MAGIQUEST* ]]
   then
      echo magic
      input tap 800 800
      sleep 0.25
      input swipe 600 1000 600 500
      sleep 0.25
      input tap 10 10
      sleep 0.25
      input tap 800 800
      sleep 0.25
      input swipe 600 500 600 1000 
      sleep 0.25
      input tap 10 800
      sleep 0.25
      input tap 800 800
      sleep 0.25
   elif [[ $line == RC6*45a ]]
   then
      echo right
      input swipe 800 500 300 500
   elif [[ $line == RC6*45b ]]
   then
      echo left
      input swipe 300 500 800 500 
   elif [[ $line == RC6*458 ]]
   then
      echo up
      input swipe 600 1000 600 500
   elif [[ $line == RC6*459 ]]
   then
      echo down
      input swipe 600 500 600 1000 
   elif [[ $line == RC6*454 ]]
   then
      echo volume up
      input keyevent "KEYCODE_VOLUME_UP"
   elif [[ $line == RC6*421 ]]
   then
      echo volume down
      input keyevent "KEYCODE_VOLUME_DOWN"
   fi
done
