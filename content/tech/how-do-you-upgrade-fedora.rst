#######################################
How do you keep your Fedora up to date?
#######################################

:date: 2016-10-05
:modified: 2016-10-11
:tags: fedora, update, dnf, systemd

As a sysadmin, my tool of choice has always been the command line under `GNU 
Screen`_ so I've never considered digging into the process until today, 
following a post about the `dnf update X crash`_.  Adam Williamson from `Fedora 
QA`_ gave a good summary in `his blog post`_ about the issue.

As it turns out, Fedora ``systemd`` maintainers decided to compile ``systemd`` 
with the `KillUserProcess`_ property disabled::

   omiday ~ $ loginctl -p KillUserProcesses show-session 
   KillUserProcesses=no

It means that for systems running Fedora <26 the update can be safely applied 
from within the desktop environment. Beyond that, we need to watch for patches 
to ``screen``. From Fedora wiki page `Changes/KillUserProcesses`_::

   [...] work with upstream authors and Fedora maintainers of programs like 
   screen and tmux to implement the ability to automatically start them in a 
   way that survives a user session, and if the system policy does not allow 
   that, to warn the user.  

So when it's time for my next round of updates I will not be using the `Ansible 
dnf module`_ in my network(s), I will not be using the graphical online update 
tool on my workstation(s), rather I will be logging in to each machine remotely 
via SSH and run ``dnf upgrade`` from within a ``screen`` session.

But how? I mean, manual login into each server? FWIW there are tools that can 
trigger a remote update, see `RedHat Satellite`_. I've never used it though.  
Until recently, at my work place we were pushing using `an in-house tool`_ that 
scaled well for the 300+ server farm. The log was the output of ``yum update``, 
just as one would expect when sitting at the console. Having switched to 
Ansible (due to RHEL 7 subscription requirements) I looked for a solution and 
as one would expect `I wasn't the only one`_. The problem with Ansible is that 
``ssh -tt`` is in its blood so to speak so the ``shell`` module would not 
return any output. I ended up forcing the command from the controlling machine, 
just as I would run the SSH command myself:

.. code-block:: yaml

   ---

   # EXTRA_VARS:
   #   update_type -- match /etc/dnf/automatic.conf

   - hosts: mha
   user: root
   roles:
      - role: rpm/dnf-automatic
         when: >
               upgrade_type is defined
               and upgrade_type == 'security'
               and ansible_distribution == 'Fedora'
               and ansible_distribution_version | int > 22
   tasks:
   - name: "(dnf-automatic) Applying security updates to Fedora 22+ hosts"
      shell: 'dnf-automatic'
      when: >
         upgrade_type is defined
         and upgrade_type == 'security'
         and ansible_distribution == 'Fedora'
         and ansible_distribution_version | int > 22
   - name: Applying security updates to Debian hosts
      shell: 'unattended-upgrade'
      when: ansible_os_family == 'Debian'

   - hosts: mha
   user: root
   tasks:
   - name: "Applying all updates"
      when: upgrade_type is defined and upgrade_type == 'default'
      #dnf: name=* state=latest
      delegate_to: localhost
      command: >
         /usr/bin/ssh -tt root@{{inventory_hostname}} \
            'sh -c "exec </dev/tty \
                  && screen -c /dev/null -S ansible \
                           /usr/bin/dnf -y upgrade"'
      changed_when: False
      register: dnf_output
   - debug: var=dnf_output.stdout_lines
      when: dnf_output is defined

Note:
   I must mention that TLDP has a nice documentation about exec_ and `I/O 
   Redirection`_.

To test, I'll start the Ansible playbook and kill it in the middle of the 
execution, while monitoring the process list and ``screen`` sessions on the 
target box.

Start on the controller machine:

.. code-block:: shell

   omiday ~/work/mha/ansible $ date ; ansible-playbook master.yml -e upgrade_type='default' -l stuff.can.local ; date
   Tue Oct 11 22:17:22 MDT 2016

   PLAY [mha] *********************************************************************

   TASK [setup] *******************************************************************
   ok: [stuff.can.local]

   TASK [rpm/dnf-automatic : [roles/rpm/dnf-automatic] install dnf-automatic] *****

   TASK [rpm/dnf-automatic : [roles/rpm/dnf-automatic] install /etc/dnf/automatic.conf] ***

   TASK [(dnf-automatic) Applying security updates to Fedora 22+ hosts] ***********

   TASK [Applying security updates to Debian hosts] *******************************

   PLAY [mha] *********************************************************************

   TASK [setup] *******************************************************************
   ok: [stuff.can.local]

   TASK [Applying all updates] ****************************************************
   ^C [ERROR]: User interrupted execution

   Tue Oct 11 22:17:52 MDT 2016

Note the time when I killed the Ansible task: ``22:17:52``.

Let's look at the target machine:

.. code-block:: shell

   root@stuff ~]# while : ; do date ; netstat -npeet | grep :22 ; pgrep -f "dnf" -a && pstree -slapA $(pgrep -f "dnf" | tail -n 1) ; screen -ls ; read -p '>>> ' -t 3 ; done
   Tue Oct 11 22:16:57 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   No Sockets found in /var/run/screen/S-root.

   ... waiting for Ansible to kick in ...

...and here's the first connection:

.. code-block:: shell

   >>> Tue Oct 11 22:17:22 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   No Sockets found in /var/run/screen/S-root.

   >>> Tue Oct 11 22:17:25 MDT 2016
   tcp        0    324 192.168.0.9:22          192.168.0.11:55472      ESTABLISHED 0          2573935    15512/sshd: root [p
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   No Sockets found in /var/run/screen/S-root.

   ... waiting for Ansible to start the upgrade  under a 'screen' session

Surely enough, it didn't take long:

.. code-block:: shell

   >>> Tue Oct 11 22:17:46 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   tcp        0      0 192.168.0.9:22          192.168.0.11:55494      ESTABLISHED 0          2576460    16125/sshd: root [p
   16145 sh -c exec </dev/tty && screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16162 screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-sshd,30323
         `-sshd,16125
            `-sshd,16135
               `-sh,16145 -c exec </dev/tty && screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                     `-screen,16162 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                        `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                           `-dnf,16164 /usr/bin/dnf -y upgrade
   There is a screen on:
         16163.ansible   (Attached)
   1 Socket in /var/run/screen/S-root.

Now that we've got the ``screen`` session it's time to kill the Ansible task on 
the controller box:

.. code-block:: shell

   >>> Tue Oct 11 22:17:49 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   tcp        0      0 192.168.0.9:22          192.168.0.11:55494      ESTABLISHED 0          2576460    16125/sshd: root [p
   16145 sh -c exec </dev/tty && screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16162 screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-sshd,30323
         `-sshd,16125
            `-sshd,16135
               `-sh,16145 -c exec </dev/tty && screen -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                     `-screen,16162 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                        `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
                           `-dnf,16164 /usr/bin/dnf -y upgrade
                                 `-etckeeper,16193 /usr/bin/etckeeper pre-install
                                    `-10packagelist,16198 /etc/etckeeper/pre-install.d/10packagelist
                                       `-etckeeper,16200 /usr/bin/etckeeper list-installed
                                             `-50list-installe,16205 /etc/etckeeper/list-installed.d/50list-installed
                                                |-rpm,16206 -qa --qf %|epoch?{%{epoch}}:{0}|:%{name}-%{version}-%{release}.%{arch}\\n
                                                `-sort,16207
   There is a screen on:
         16163.ansible   (Attached)
   1 Socket in /var/run/screen/S-root.
   >>> Tue Oct 11 22:17:52 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            `-etckeeper,16193 /usr/bin/etckeeper pre-install
               `-10packagelist,16198 /etc/etckeeper/pre-install.d/10packagelist
                     `-etckeeper,16200 /usr/bin/etckeeper list-installed
                        `-50list-installe,16205 /etc/etckeeper/list-installed.d/50list-installed
                           |-rpm,16206 -qa --qf %|epoch?{%{epoch}}:{0}|:%{name}-%{version}-%{release}.%{arch}\\n
                           `-sort,16207
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.

There! The ``screen`` session is now *detached*. Same time: ``22:17:52``.

Now that we've disconnected it's time for the coffee break until we can check 
that the upgrade completed:

.. code-block:: shell

   >>> Tue Oct 11 22:17:55 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            `-etckeeper,16193 /usr/bin/etckeeper pre-install
               `-10packagelist,16198 /etc/etckeeper/pre-install.d/10packagelist
                     `-etckeeper,16200 /usr/bin/etckeeper list-installed
                        `-50list-installe,16205 /etc/etckeeper/list-installed.d/50list-installed
                           |-rpm,16206 -qa --qf %|epoch?{%{epoch}}:{0}|:%{name}-%{version}-%{release}.%{arch}\\n
                           `-sort,16207
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.

   ... more like those ...

Here's one process list where we actually see package names:

.. code-block:: shell

   >>> Tue Oct 11 22:18:13 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   16304 /usr/bin/applydeltarpm -a noarch /var/cache/dnf/updates-testing-648243a4cddd356c/packages/ibus-typing-booster-1.5.7-1.fc24_1.5.8-1.fc24.noarch.drpm /var/cache/dnf/updates-testing-648243a4cddd356c/packages/ibus-typing-booster-1.5.8-1.fc24.noarch.rpm
   16308 /usr/bin/applydeltarpm -a x86_64 /var/cache/dnf/updates-testing-648243a4cddd356c/packages/gnutls-3.4.15-1.fc24_3.4.16-1.fc24.x86_64.drpm /var/cache/dnf/updates-testing-648243a4cddd356c/packages/gnutls-3.4.16-1.fc24.x86_64.rpm
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            `-applydeltarpm,16308 -a x86_64 /var/cache/dnf/updates-testing-648243a4cddd356c/packages/gnutls-3.4.15-1.fc24_3.4.16-1.fc24.x86_64.drpm /var/cache/dnf/updates-testing-648243a4cddd356c/packages/gnutls-3.4.16-1.fc24.x86_64.rpm
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.
   >>> Tue Oct 11 22:18:17 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            |-(applydeltarpm,16304)
            `-(applydeltarpm,16308)
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.

...and there's also a kernel upgrade going on:

.. code-block:: shell

   >>> Tue Oct 11 22:20:32 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            `-sh,16940 /var/tmp/rpm-tmp.hlgpOL 3
               `-kernel-install,16942 /bin/kernel-install add 4.7.7-200.fc24.x86_64 /lib/modules/4.7.7-200.fc24.x86_64/vmlinuz
                     `-new-kernel-pkg,16984 /sbin/new-kernel-pkg --package kernel --mkinitrd --dracut --depmod --update 4.7.7-200.fc24.x86_64
                        `-depmod,17003 -ae -F /boot/System.map-4.7.7-200.fc24.x86_64 4.7.7-200.fc24.x86_64
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.

Last bit:

.. code-block:: shell

   >>> Tue Oct 11 22:21:46 MDT 2016
   tcp        0     68 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   16163 SCREEN -c /dev/null -S ansible /usr/bin/dnf -y upgrade
   16164 /usr/bin/python3 /usr/bin/dnf -y upgrade
   systemd,1 --system --deserialize 21
   `-screen,16163 -c /dev/null -S ansible /usr/bin/dnf -y upgrade
         `-dnf,16164 /usr/bin/dnf -y upgrade
            `-sh,20108 -c etckeeper post-install > /dev/null
               `-etckeeper,20109 /usr/bin/etckeeper post-install
                     `-50vcs-commit,20114 /etc/etckeeper/post-install.d/50vcs-commit
                        |-50vcs-commit,20135 /etc/etckeeper/post-install.d/50vcs-commit
                        |   |-diff,20138 -U0 /var/cache/etckeeper/packagelist.pre-install -
                        |   |-etckeeper,20137 /usr/bin/etckeeper list-installed
                        |   |   `-50list-installe,20149 /etc/etckeeper/list-installed.d/50list-installed
                        |   |       |-rpm,20151 -qa --qf %|epoch?{%{epoch}}:{0}|:%{name}-%{version}-%{release}.%{arch}\\n
                        |   |       `-sort,20152
                        |   |-grep,20140 -E ^[-+]
                        |   `-tail,20139 -n+4
                        `-etckeeper,20136 /usr/bin/etckeeper commit --stdin
                           `-50vcs-commit,20179 /etc/etckeeper/commit.d/50vcs-commit --stdin
                                 `-cat,20181
   There is a screen on:
         16163.ansible   (Detached)
   1 Socket in /var/run/screen/S-root.
   >>> Tue Oct 11 22:21:49 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   No Sockets found in /var/run/screen/S-root.

So that's it folks! Let's confirm:

.. code-block:: shell

   >>> Tue Oct 11 22:21:55 MDT 2016
   tcp        0      0 192.168.0.9:22          192.168.0.11:55462      ESTABLISHED 0          2570992    15285/sshd: root [p
   No Sockets found in /var/run/screen/S-root.

   >>> ^C
   [root@stuff ~]# dnf history list | head
   ID     | Command line             | Date and time    | Action(s)      | Altered
   -------------------------------------------------------------------------------
      144 | -y upgrade               | 2016-10-11 22:19 | E, I, O, U     |   40
      143 | -y upgrade               | 2016-10-08 18:07 | I, U           |   66
      142 | -y upgrade               | 2016-10-05 21:47 | E, I, U        |   89 EE
      141 |                          | 2016-10-04 22:39 | E, I, O, U     |  168 EE
      140 |                          | 2016-10-04 22:27 | Install        |    1
      139 | upgrade                  | 2016-09-23 14:07 | E, I, O, U     |  179
      138 | upgrade                  | 2016-09-15 20:23 | E, I, U        |  313 EE
      137 | upgrade                  | 2016-09-03 21:18 | E, I, U        |  355

   [root@stuff ~]# dnf history info last
   Transaction ID : 144
   Begin time     : Tue Oct 11 22:19:05 2016
   Begin rpmdb    : 3446:a212d092b65d6d67d1c1c61b1ab0f0f354244810
   End time       :            22:21:37 2016 (152 seconds)
   End rpmdb      : 3447:de07737f44b22676b0ff08b704556491658c531a
   User           : root <root>
   Return-Code    : Success
   Command Line   : -y upgrade
   Transaction performed with:
      Installed     dnf-1.1.10-1.fc24.noarch        @updates
      Installed     rpm-4.13.0-0.rc1.27.fc24.x86_64 @@commandline
   Packages Altered:
      Upgraded   ghostscript-9.16-5.fc24.x86_64                      @updates-testing
      Upgrade                9.20-2.fc24.x86_64                      @updates-testing
      Upgraded   ghostscript-core-9.16-5.fc24.x86_64                 @updates-testing
      Upgrade                     9.20-2.fc24.x86_64                 @updates-testing
      Upgraded   ghostscript-x11-9.16-5.fc24.x86_64                  @updates-testing
      Upgrade                    9.20-2.fc24.x86_64                  @updates-testing
      Upgraded   gnutls-3.4.15-1.fc24.i686                           @updates
      Upgraded   gnutls-3.4.15-1.fc24.x86_64                         @updates
      Upgrade           3.4.16-1.fc24.i686                           @updates-testing
      Upgrade           3.4.16-1.fc24.x86_64                         @updates-testing
      Upgraded   gnutls-dane-3.4.15-1.fc24.x86_64                    @updates
      Upgrade                3.4.16-1.fc24.x86_64                    @updates-testing
      Upgraded   gnutls-utils-3.4.15-1.fc24.x86_64                   @updates
      Upgrade                 3.4.16-1.fc24.x86_64                   @updates-testing

      ... etc. etc. etc. ...

But what about rebooting the system after every update [1]_ [2]_? Or maybe just 
restarting services will do...?
::

   [root@omiday ~]# dnf tracer 
   You should restart:
     + Some applications using:
         service ModemManager restart
         service NetworkManager restart
         service abrtd restart
         service accounts-daemon restart
         service atd restart
         service auditd restart
         service crond restart
         service dnsmasq restart
         service firewalld restart
         service gssproxy restart
         service httpd restart
         service irqbalance restart
         service libvirtd restart
         service lightdm restart
         service mcelog restart
         service smartd restart
         service sshd restart
         service systemd-journald restart
         service systemd-logind restart
         service systemd-udevd restart
         service wpa_supplicant restart

     + These applications manually:
         Xorg
         abrt-dbus
         abrt-dump-journal-xorg
         alsactl
         audispd
         bluetoothd
         cupsd
         master
         rpc.gssd
         rsyslogd
         sedispatch
         systemd
         x2gocleansessio

   Additionally to those process above, there are:
     1. 2 processes requiring reboot

And let's verify that again::

   [root@omiday ~]# dnf needs-restarting
   1 : /usr/lib/systemd/systemd --system --deserialize 23
   1064 : /usr/lib64/thunderbird/thunderbird
   4913 : /usr/sbin/httpd -DFOREGROUND
   6885 : /usr/libexec/gconfd-2
   10530 : kwalletmanager
   10534 : kdeinit4: kdeinit4 Runnin e
   10536 : kdeinit4: klauncher [kdei e
   10538 : kdeinit4: kded4 [kdeinit]
   10540 : /usr/libexec/gam_server
   10544 : kdeinit4: kwalletd [kdein e
   11901 : /usr/libexec/gvfsd-http --spawner :1.4 /org/gtk/gvfs/exec_spaw/1
   13548 : /usr/sbin/sshd
   16643 : /usr/bin/python3 -Es /usr/sbin/setroubleshootd -f
   16803 : /usr/libexec/postfix/master -w
   16805 : qmgr -l -t unix -u
   17209 : /usr/libexec/colord
   17538 : /usr/lib/systemd/systemd-journald
   17765 : /sbin/auditd -n
   17779 : /usr/sbin/sedispatch
   17789 : /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
   17791 : /usr/sbin/rsyslogd -n
   17800 : /usr/lib/systemd/systemd-logind
   17804 : /usr/libexec/rtkit-daemon
   17806 : /usr/sbin/ModemManager
   17809 : /usr/bin/python3 -Es /usr/sbin/firewalld --nofork --nopid
   17813 : /usr/sbin/smartd -n -q never
   17815 : /usr/libexec/accounts-daemon
   17834 : /usr/sbin/ntpd -u ntp:ntp -g
   17845 : /usr/sbin/abrtd -d -s
   17853 : /usr/sbin/gssproxy -D
   17871 : /usr/sbin/rpc.gssd
   17874 : /usr/lib/polkit-1/polkitd --no-debug
   17890 : /usr/bin/perl /usr/sbin/x2gocleansessions
   17894 : /usr/bin/abrt-dump-journal-xorg -fxtD
   17895 : /usr/bin/abrt-dump-journal-oops -fxtD
   17910 : /usr/sbin/NetworkManager --no-daemon
   17928 : /usr/sbin/libvirtd
   17935 : /usr/sbin/httpd -DFOREGROUND
   17951 : /usr/sbin/atd -f
   17976 : /usr/sbin/lightdm
   18006 : /usr/libexec/Xorg -background none :0 -seat seat0 -auth /var/run/lightdm/root/:0 -nolisten tcp vt1 -novtswitch
   18097 : /usr/sbin/wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -u -s
   18177 : /sbin/dnsmasq --conf-file=/var/lib/libvirt/dnsmasq/default.conf --leasefile-ro --dhcp-script=/usr/libexec/libvirt_leaseshelper
   18178 : /sbin/dnsmasq --conf-file=/var/lib/libvirt/dnsmasq/default.conf --leasefile-ro --dhcp-script=/usr/libexec/libvirt_leaseshelper
   18255 : lightdm --session-child 12 19
   18377 : /usr/lib/systemd/systemd --user
   18380 : (sd-pam)
   18384 : /bin/sh /etc/xdg/xfce4/xinitrc -- vt
   18395 : /usr/bin/dbus-daemon --session --address=systemd: --nofork --nopidfile --systemd-activation
   18459 : /usr/libexec/imsettings-daemon
   18462 : /usr/libexec/gvfsd
   18528 : /usr/bin/ssh-agent /bin/sh -c exec -l /bin/bash -c "startxfce4"
   18563 : xfce4-session
   18567 : /usr/lib64/xfce4/xfconf/xfconfd
   18570 : /usr/bin/gpg-agent --sh --daemon --write-env-file /home/omiday/.cache/gpg-agent-info
   18572 : xfwm4
   18576 : xfce4-panel
   18578 : Thunar --daemon
   18580 : xfdesktop
   18581 : xfce4-clipman
   18582 : xfsettingsd
   18587 : python3 /usr/bin/blueman-applet
   18593 : abrt-applet
   18596 : /usr/libexec/xfce-polkit
   18601 : /usr/bin/seapplet
   18606 : /usr/libexec/at-spi-bus-launcher
   18613 : xscreensaver -no-splash
   18617 : /usr/bin/pulseaudio --start --log-target=syslog
   18633 : /bin/dbus-daemon --config-file=/usr/share/defaults/at-spi2/accessibility.conf --nofork --print-address 3
   18646 : /usr/libexec/at-spi2-registryd --use-gnome-session
   18647 : nm-applet
   18675 : xfce4-power-manager
   18686 : /usr/libexec/dconf-service
   18703 : /usr/lib64/xfce4/panel/wrapper-1.0 /usr/lib64/xfce4/panel/plugins/libwhiskermenu.so 2 12582945 whiskermenu Whisker Menu Show a menu to easily access installed applications
   18713 : /usr/lib64/xfce4/panel/wrapper-1.0 /usr/lib64/xfce4/panel/plugins/libsystray.so 6 12582956 systray Notification Area Area where notification icons appear
   18715 : /usr/libexec/upowerd
   18716 : /usr/lib64/xfce4/panel/wrapper-2.0 /usr/lib64/xfce4/panel/plugins/libpulseaudio-plugin.so 9 12582957 pulseaudio PulseAudio Plugin Adjust the audio volume of the PulseAudio sound system
   18733 : /usr/libexec/gvfs-udisks2-volume-monitor
   18737 : /usr/sbin/abrt-dbus -t133
   18743 : /usr/libexec/udisks2/udisksd --no-debug
   18926 : /usr/libexec/gvfsd-metadata
   18931 : /usr/libexec/gvfsd-trash --spawner :1.5 /org/gtk/gvfs/exec_spaw/0
   19355 : /usr/bin/Xvnc :1 -auth /var/run/lightdm/omiday/xauthority -desktop omiday.can.local:1 (omiday) -fp catalogue:/etc/X11/fontpath.d -geometry 1600x900 -pn -rfbauth /home/omiday/.vnc/passwd -rfbport 5901 -rfbwait 30000
   19373 : /usr/bin/vncconfig -nowin
   19375 : /bin/sh /etc/xdg/xfce4/xinitrc -- vt
   19388 : dbus-launch --sh-syntax --exit-with-session
   19389 : /usr/bin/dbus-daemon --fork --print-pid 5 --print-address 7 --session
   19465 : /usr/libexec/imsettings-daemon
   19469 : /usr/libexec/gvfsd
   19548 : xfce4-session
   19552 : /usr/lib64/xfce4/xfconf/xfconfd
   19555 : /bin/bash
   19557 : xfwm4
   19561 : xfce4-panel
   19565 : xfdesktop
   19566 : xfsettingsd
   19567 : xfce4-clipman
   19574 : abrt-applet
   19586 : /usr/bin/seapplet
   19594 : xscreensaver -no-splash
   19604 : nm-applet
   19665 : /usr/libexec/dconf-service
   19675 : /usr/libexec/gvfs-udisks2-volume-monitor
   19680 : /usr/libexec/at-spi-bus-launcher
   19681 : /usr/lib64/xfce4/panel/wrapper-1.0 /usr/lib64/xfce4/panel/plugins/libwhiskermenu.so 2 14680097 whiskermenu Whisker Menu Show a menu to easily access installed applications
   19687 : /bin/dbus-daemon --config-file=/usr/share/defaults/at-spi2/accessibility.conf --nofork --print-address 3
   19689 : /usr/lib64/xfce4/panel/wrapper-1.0 /usr/lib64/xfce4/panel/plugins/libsystray.so 6 14680108 systray Notification Area Area where notification icons appear
   19692 : /usr/lib64/xfce4/panel/wrapper-2.0 /usr/lib64/xfce4/panel/plugins/libpulseaudio-plugin.so 9 14680109 pulseaudio PulseAudio Plugin Adjust the audio volume of the PulseAudio sound system
   19698 : /usr/libexec/at-spi2-registryd --use-gnome-session
   19709 : /usr/libexec/gvfsd-trash --spawner :1.4 /org/gtk/gvfs/exec_spaw/0
   19726 : /usr/libexec/gvfsd-metadata
   19815 : /usr/bin/gnome-keyring-daemon --start --foreground --components=secrets
   20074 : pidgin
   20154 : /usr/libexec/gconfd-2
   20365 : /usr/bin/python3 /usr/bin/bpython3
   20416 : xfce4-appfinder --collapsed
   20450 : /usr/bin/xfce4-terminal
   20556 : SCREEN -R omiday
   20557 : /bin/bash
   20662 : bash
   21220 : /usr/bin/vim +75 /home/omiday/.irssi/config-omiday
   21626 : /usr/libexec/gvfsd-network --spawner :1.4 /org/gtk/gvfs/exec_spaw/2
   21633 : /usr/libexec/gvfsd-dnssd --spawner :1.4 /org/gtk/gvfs/exec_spaw/3
   22023 : /usr/sbin/httpd -DFOREGROUND
   22024 : /usr/sbin/httpd -DFOREGROUND
   22035 : /usr/sbin/httpd -DFOREGROUND
   22038 : /usr/sbin/httpd -DFOREGROUND
   22040 : /usr/sbin/httpd -DFOREGROUND
   23229 : less /home/omiday/.irssi/config /home/omiday/.irssi/config-omiday /home/omiday/.irssi/config-test
   23621 : irssi --config /home/omiday/.irssi/config-omiday
   24322 : /usr/libexec/bluetooth/bluetoothd
   25405 : gvim content/tech/how-do-you-upgrade-fedora.rst
   25573 : bash
   25686 : screen -R python
   25687 : SCREEN -R python
   25688 : /bin/bash
   25693 : /bin/bash
   26696 : /bin/bash
   28205 : gvim playbooks/update.yml
   28703 : /usr/lib64/firefox/firefox
   30546 : bash

Since I've already restarted Remmina_ a few times while writing this post, I am 
going to reboot right now...No wait, it's been an hour now and no issues...Or 
maybe yes, what if there was a security update...


~~~~~

.. [1] 
   https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/DM5RZR2FIFUHQ7FXOBM6LKUTC6EOKN46/
.. [2] 
   https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/MXBK6OCWRLETVJGEOGGKXV3TBYSOSJDA/

.. _`KillUserProcess`: https://bugzilla.redhat.com/show_bug.cgi?id=1357426
.. _`dnf update X crash`: https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/7ULAG243UNGTOSL6URGNG23GC4B6X5GB/
.. _`Fedora QA`: https://fedoraproject.org/wiki/QA
.. _`his blog post`: https://www.happyassassin.net/2016/10/04/x-crash-during-fedora-update-when-system-has-hybrid-graphics-and-systemd-udev-is-in-update/
.. _`Changes/KillUserProcesses`: https://fedoraproject.org//wiki/Changes/KillUserProcesses_by_default 
.. _`GNU Screen`: https://www.gnu.org/software/screen/
.. _`Ansible dnf module`: https://docs.ansible.com/ansible/dnf_module.html
.. _Remmina: https://github.com/FreeRDP/Remmina
.. _`RedHat Satellite`: https://access.redhat.com/documentation/en-US/Red_Hat_Network_Satellite/5.3/html/Installation_Guide/s1-maintenance-push-clients.html
.. _`an in-house tool`: http://cpacman.sourceforge.net/
.. _`I wasn't the only one`: https://github.com/docker/docker/issues/728
.. _`I/O Redirection`: http://www.tldp.org/LDP/abs/html/ioredirintro.html
.. _exec: http://www.tldp.org/LDP/abs/html/x17974.html
