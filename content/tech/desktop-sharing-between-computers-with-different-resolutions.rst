############################################################
Desktop Sharing between computers with different resolutions
############################################################

:date: 2016-07-31 21:31:16 UTC-06:00
:tags: vnc, xrandr pR3wo
:authors: omiday

``xrandr`` allows selecting the display modes (a.k.a resolutions) however due 
to modelines being `hard coded`_ any additional modeline such as "2560x1600" or 
"1600x900" would need to be `added into the code`_.  I think the developers who 
wrote the code are much smarter and the hard coded list is just a sample of 
values. It leads to the conclusion that there must be a way to add custom 
modelines and ``man xrandr`` confirms it.

With that background if the goal is to share a VNC session between two 
computers with the above resolutions and assuming that the VNC server is the 
computer with the resolution of "1600x900":

1. Start a VNC session with a geometry matching the physical display:

   .. code-block: shell

      $ vncserver -geometry 1600x900 :1

2. On the "2560x1600" computer start the VNC viewer (Remmina_ has been working 
   fine for me thus far) and connect to the remote VNC session::

       host:5901
       
3. Once inside the VNC session start up a terminal window.

4. Confirm that the new geometry is available in the VNC session:

   .. code-block: shell

      $ xrandr
      Screen 0: minimum 32 x 32, current 1600 x 900, maximum 32768 x 32768
      VNC-0 connected 1600x900+0+0 0mm x 0mm
         1600x900      60.00 +
         1920x1200     60.00  
         1920x1080     60.00  
         1600x1200     60.00  
         1680x1050     60.00  
         1400x1050     60.00  
         1360x768      60.00  
         1280x1024     60.00  
         1280x960      60.00  
         1280x800      60.00  
         1280x720      60.00  
         1024x768      60.00  
         800x600       60.00  
         640x480       60.00  

   and you'll notice the screen being quite small.

5. List the `modeline <https://wiki.archlinux.org/index.php/xrandr>`_ for the 
   "2560x1600" resolution:

   .. code-block: shell

      $ cvt 2560 1600
      # 2560x1600 59.99 Hz (CVT 4.10MA) hsync: 99.46 kHz; pclk: 348.50 MHz
      Modeline "2560x1600_60.00"  348.50  2560 2760 3032 3504  1600 1603 1609 1658 -hsync +vsync

   or if the monitor is old get the GTF timings::

      $ gtf 2560 1600 60
      # 2560x1600 @ 60.00 Hz (GTF) hsync: 99.36 kHz; pclk: 348.16 MHz
      Modeline "2560x1600_60.00"  348.16  2560 2752 3032 3504  1600 1601 1604 1656 -HSync +Vsync

6. Add the new modeline to the current VNC session::

      $ xrandr --newmode "2560x1600_60.00"  348.16  2560 2752 3032 3504  1600 1601 1604 1656 -HSync +Vsync

7. In the above ``xrandr`` output look for the display name on the second 
   line::

      VNC-0 connected 1600x900+0+0 0mm x 0mm

8. Bind the new modeline to the current VNC virtual monitor::

      $ xrandr --addmode VNC-0 "2560x1600_60.00"

9. Use it::

      $ xrandr -s "2560x1600_60.00"


.. Links:
.. _`added into the code`: https://marc.info/?l=tigervnc-users&m=130721748515934&w=2 
.. _`hard coded`: https://github.com/TigerVNC/tigervnc/blob/master/unix/xserver/hw/vnc/xvnc.c
.. _Remmina: http://www.remmina.org/wp/
