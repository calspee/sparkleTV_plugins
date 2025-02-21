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

*I added a comskip.ini file which can also be added to the video base folder which will allow for easier tweaks to comskip for commercial detection.   Hopefully it imporves success.  There are other tweaks available besides what is in the ini file, but from what I noticed some of the commercials that it wasn't seeing before were extremely long 'infomercial' type commercials longer than 60 seconds, so these are the simple tweaks that seemed to help these situations.  For information on more acurate tuning visit the following link for a coplete guide:  https://www.kaashoek.com/files/tuning.htm

Note:   this script does nothing to ensure comskip itself is removing commercials effectively.   In my experience comskip can work 95+% but does requite some tweaking to be able to effectively remove commercials and different IPTV services may require different tweaks to be able to work.   More information on how comskip scans your video and the methods it uses to 'find' commercials is available in their documentation and suggestions can be found there or on their forum on how you can try to tweak the settings to yield better results.   Good luck!