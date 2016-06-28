#!/system/bin/sh
# for Nexus 7 2013
# change for other screen resolutions
lasttime=0
nc 192.168.1.123 5678 | tr -d '\15' | tr ',' ' ' | while read line ; do
   echo $line
   data=($line)
   t=${data[1]}
   if [[ $line == RC6*42c ]] 
   then
      if [ $(( $lasttime + 500 )) -lt $t ] 
      then
         echo pause/play
         input tap 59 1030
         sleep 0.5
         input tap 59 1030
      else
         echo skipped repeat
      fi
   elif [[ $line == RC6*458 ]]
   then
      echo volume up
      input keyevent "KEYCODE_VOLUME_UP"
   elif [[ $line == RC6*459 ]]
   then
      echo volume down
      input keyevent "KEYCODE_VOLUME_DOWN"
   fi
   lasttime=$t
done
