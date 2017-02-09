###########################
Fiddling with MP3s and MP4s
###########################

:date: 2016-11-28
:tags: mp3, mp4, ffmpeg, eyeD3, kid3


Adding audio into video
=======================

Tip picked up from this `Ask Ubuntu post`_. Note that the text below is not 
verbatim::

   ffmpeg -i video.mp4 -i audio.aac -map 0:0 -map 1:0 -vcodec copy \
      -acodec copy newvideo.mp4

   ffmpeg -i video.mp4 -i audio.aac -map 0:1 -map 1:0 -vcodec copy \
      -acodec copy newvideo.mp4

   Explanation:
      -i video.mp4  -> first media file
      -i audio.aac  -> second media file
      -map 0:1      -> use the second stream from the first mediafile
      -map 1:0      -> use the first stream from the second mediafile
      -vcodec copy  -> leave the video as is
      -acodec copy  -> leave the audio as is
      newvideo      -> resulting videofile 

   Note:
      Use 'mediainfo' to confirm that the audiofile and videofile have the same 
      duration.  Not every player is accepting tracks with huge duration 
      differences.


Mass changing tags
==================

Out of the many alternatives I've settled on:

* eyeD3_

* kid3_


.. _`Ask Ubuntu post`: https://askubuntu.com/questions/369947/how-to-add-an-audio-file-aac-or-mp3-to-a-mp4-video-file
.. _kid3: http://kid3.sourceforge.net/ 
.. _eyeD3: http://eyed3.nicfit.net/ 
