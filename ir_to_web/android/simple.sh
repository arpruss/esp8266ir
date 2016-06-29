#!/system/bin/sh
nc 192.168.1.123 5678 | while read line ; do
  if [[ $line == *458? ]]
  then
    echo "Volume Up"
    input keyevent KEYCODE_VOLUME_UP
  elif [[ $line == *459? ]]
  then
    echo "Volume Down"
    input keyevent KEYCODE_VOLUME_DOWN
  else
    echo $line
  fi
done
