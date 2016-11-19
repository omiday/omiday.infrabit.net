############################
Mouseless upload to pastebin
############################

:date: 2016-10-19
:tags: pastebin, screen, fpaste, xsel

The tools
=========

fpaste_ can be enhanced when paired with other keyboard based tools such as:

* screen_

* xsel_


Examples
=========

Paste a ``diff`` and save the URL into the clipboard selection (Ctrl-V)::

   $ diff -Naur fabfile.py ~/temp/pelican-upstream/fabfile.py \
      | fpaste -l diff --raw | xsel -ib 

Select the text using the mouse or in case of a ``screen`` session enter the 
copy mode and run::

   $ cat | fpaste -l python --raw | xsel -ib

then paste the text and end with Ctrl-D.

I've got the following Bash aliases::

   # {{{ clipboard
   clippass() {
      #pwgen $@ | tr -d "\n$" | xclip -selection clipboard
      # use xsel as we needed for fpaste anyways
      pwgen ${1:--sy} ${2:-20} 1 | tr -d "\n$" | xsel -ib
   }

   # copy text or 'cat file' for file contents
   clipcp() {
      cat ${1} | xsel -ib
   }

   # sent text to fedora paste ('cat file' to send contents)
   clipfp() {
      cat | fpaste -l ${1:-text} --raw | xsel -ib
   }
   # clipboard }}}


.. _fpaste: https://pagure.io/fpaste
.. _screen: https://www.gnu.org/software/screen/
.. _xsel: http://www.vergenet.net/~conrad/software/xsel/
