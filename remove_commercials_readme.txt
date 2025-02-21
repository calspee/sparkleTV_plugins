This is a script to remove commercials from .ts files recorded from my IPTV service

This script assumes:
- comskip is installed and asssociated in system variables in PATH
- ffmpeg is installed and asssociated in system variables in PATH

I am using it on a windows environment

The script will:

- backup the original video files appending the filename with _original in an original folder
- copies and does all work on the present file in a created working folder
- use comskip to create an edl file to be used by ffmpeg
- check to make sure a proper edl file has been create otherwise it will cancel the operation and revert files to where they originally were
- use the edl file with mmpeg to encode a version on the video without commercials, it will create it in the original folder with the original filename so sparkleTV will be able to play the commercial skipped version from the DVR section of the app.
- clean up the working forlder deleting all temporary files
- create a json in the video folder called processed_files to check during the next instance of tunning the script so it will skip video files it has already processed

Base folders defined in the script may have to be modified to match the locations of the recordings on your system

**  This script itself doesn't do much to ensure the success of removing commercials from the video files.  It is the settings of Comskip itself that is soley tasked with finding the commercials, different people will have different success in removing all commercials and breaks based on numerous factors, including the settings, what processes and anylytics the software uses to find the commercials, the source of the video files (different IPTV providers), and the channels themselves (channel logos, black space, or tickers in the video feed), etc.  I added a comskip.ini file which can also be added to the video base folder which will allow for easier tweaks to comskip for commercial detection. This ini file could be replaced by a much more detailed one.  Hopefully it imporves success.  For information on more acurate tuning visit the following link for a coplete guide:  https://www.kaashoek.com/files/tuning.htm   In the future this script itself could be modified so that it would take a look in the SparkleTV recordings file t opick out the channel that the video was recorded on and then load a comskip.ini file made specifically for that channel.  In some instances for example one channel has 6-7 minute commercial breaks 2 or 3 times during an hour long program and these are not identified using 'stock' ini settings for comskip and will only work with specific settings that understand commercial breaks can last that long.   You wouldn't want to use those same settings on another channel as it could accidently cut show sections that are around that length.  Adding this would be quite simple but I don't know if I feel like customizing 10-20 different ini files at the moment.   Who knows I do like to tinker around when I am bored so if I make a version of this script that does that I will post it on this github as a seperate file.
