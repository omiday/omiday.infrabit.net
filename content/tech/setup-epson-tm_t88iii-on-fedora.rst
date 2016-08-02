###############################################################
Setting up the Epson TM-T88III USB receipt printer on Fedora 24
###############################################################

:date: 2016-09-11
:tags: linux, fedora, epson, usb
:url: s1ykO.html
:save_as: s1ykO.html
:authors: omiday

A whole day of Google digging comes down to this:

1. Download the `Epson TM-T88III drivers`_::

       Home
           > Support
               > TM-T88V POS Receipt Printer
                   > Drivers & Downloads

2. Setup the printer in CUPS::

      Local Printers: Epson TM/BA/EU Printer
      Connection: epsontm:/ESDPRT001
      Driver: Epson TM BA Thermal (rastertotmt) (grayscale)

   where:

   * ``Local Printers: Epson TM/BA/EU Printer`` will be displayed in CUPS if 
     the driver installation succeeded.

   * ``Connection: epsontm:/ESDPRT001`` isn't obvious since the only entry will 
     be ``epsontm``. This `superuser post`_ and a `mail on Czech Linux list`_ 
     cleared the confusion. Thanks folks!

   And rather than asking Epson for source code, let's try an explanation for 
   those settings::

      [root@localhost ]# strings /usr/lib/cups/backend/epsontm | grep -i -e epsontm: -e esdprt -e epuerasd
      epsontm:/
      -- epsontm::cups Open(pipe://) <%08X>
      -- epsontm::cups No stack to enumerate.
      -- epsontm::cups No Ports found under TM stack.
      -- epsontm::cups Open(pipe://TM) <%08X

      [root@localhost ~]# strings /usr/sbin/epurasd | grep -i -e epsontm -e esdprt -e 2291
      /ESDPRT
                  <ui language="en" label="Default (Port 2291)"/>
                  <ui language="ja" label="Default (Port 2291)"/>
                  <property id="TCP_COMMUNICATION_PORT" type="number" value="2291"/>
                  <range id="TCP_COMMUNICATION_PORT" default="2291" min="1">

      [root@localhost ~]# netstat -tupeel | grep epura
      tcp  0  0  0.0.0.0:eapsp  0.0.0.0:*  LISTEN  root  63240  8867/epurasd
 
   This doesn't say anything about the ``001`` suffix for ``ESDPRT``. At some 
   point I may try changing that name to something less technically correct as 
   all it appears to be is a named pipe for talking to ``epurasd`` daemon.

.. _`Epson TM-T88III drivers`: 
   https://ftp.epson.com/drivers/pos/tm_ba_series_thermal_printer_driver_1100.zip 
.. _`superuser post`: 
   https://superuser.com/questions/352931/epson-receipt-printer-slow-on-linux 
.. _`mail on Czech Linux list`: 
   http://www.linux.cz/pipermail/linux/2011-October/269827.html 

