check_video.py


- check to see if the file duration for eash .ts file approximately matches what the file length should be in the recordings json file
- if it is withing a preset tollerance then skip the file and do nothing
- if the video file is outside the tollerance then:
		1) backup the original file to the repaired_videos folder 
		2) make a copy of the file with ffmpeg to correct the header or timestamp issues that are causing it to play inproperly in Sparkle TV app
		3) rename the fixed file in the original folder so the Sparkle TV app will play the fixed file when you select to play it in the apps dvr section
- The script creates a json file to store in the files have already been checked so you can run it anytime you want without it rechecking files and making duplicates
- This script has a limited fix ability that is just meant to correct the issues the files were having playing properly and does NOT renecode the video.  It seems that Sparlke TV doesn't not always record streams reliabily if there are any delays or interrruptions in the stream or in saving data to the drive.  These issues I suspect are even more prevelant when saving recordings to network drives over ethernet or wifi.  This fix method does work to correct these issues about 95% of the time, and the script can be run scheduled in the background.   
