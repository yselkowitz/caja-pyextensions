#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module adds menu items to the caja right-click menu which allows to compare
   the selected files/folder using Kdiff3 (Diff and merge tool) just through the right-clicking"""

#   kdiff3-compare.py version 1.2.2
#
#   Copyright 2009-2011 Giuseppe Penone <giuspen@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

import mateconf
import caja, urllib, os, subprocess, re
import locale, gettext

APP_NAME = "caja-pyextensions"
LOCALE_PATH = "/usr/share/locale/"
MATECONF_PATH = "/apps/caja-pyextensions/kdiff3_save"
# internationalization
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP_NAME, LOCALE_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
# post internationalization code starts here


class Kdiff3Actions(caja.MenuProvider):
    """Implements the 'Kdiff3 Compare' extension to the caja right-click menu"""

    def __init__(self):
        """Caja crashes if a plugin doesn't implement the __init__ method"""
        self.mateconf_client = mateconf.client_get_default()
        self.mateconf_client.add_dir("/apps/caja-pyextensions", mateconf.CLIENT_PRELOAD_NONE)

    def run(self, menu, element_1, element_2):
        """Runs the Kdiff3 Comparison of selected files/folders"""
        subprocess.call("kdiff3 %s %s &" % (element_1, element_2), shell=True)

    def kdiff3_save(self, menu, element):
        """Save the File/Folder Path for Future Use"""
        self.mateconf_client.set_string(MATECONF_PATH, element)

    def get_file_items(self, window, sel_items):
        """Adds the 'Add To Audacious Playlist' menu item to the Caja right-click menu,
           connects its 'activate' signal to the 'run' method passing the list of selected Audio items"""
        num_paths = len(sel_items)
        if num_paths == 0 or num_paths > 2: return
        uri_raw = sel_items[0].get_uri()
        if len(uri_raw) < 7: return
        element_1 = urllib.unquote(uri_raw[7:])
        if num_paths == 2:
            uri_raw = sel_items[1].get_uri()
            if len(uri_raw) < 7: return
            element_2 = urllib.unquote(uri_raw[7:])
            if os.path.isfile(element_1):
                if not os.path.isfile(element_2): return
                element_1 = re.escape(element_1)
                filetype = subprocess.Popen("file -i %s" % element_1, shell=True, stdout=subprocess.PIPE).communicate()[0]
                if "text" not in filetype and "xml" not in filetype: return
                element_2 = re.escape(element_2)
                filetype = subprocess.Popen("file -i %s" % element_2, shell=True, stdout=subprocess.PIPE).communicate()[0]
                if "text" not in filetype and "xml" not in filetype: return
            elif os.path.isdir(element_1):
                if not os.path.isdir(element_2): return
                element_1 = re.escape(element_1)
                element_2 = re.escape(element_2)
            else: return
            item = caja.MenuItem('Kdiff3::kdiff3',
                                     _('Kdiff3 Compare'),
                                     _('Compare the selected Files/Folders using Kdiff3 (Diff and merge tool)') )
            item.set_property('icon', 'kdiff3')
            item.connect('activate', self.run, element_1, element_2)
            return item,
        # only one item selected
        if os.path.isfile(element_1):
            filetype = subprocess.Popen("file -i %s" % re.escape(element_1), shell=True, stdout=subprocess.PIPE).communicate()[0]
            if "text" not in filetype and "xml" not in filetype: return
        # top menuitem
        top_menuitem = caja.MenuItem('Kdiff3::actions',
                                         _('Kdiff3 Actions'),
                                         _('Kdiff3 (Diff and merge tool) Actions') )
        top_menuitem.set_property('icon', 'kdiff3')
        # creation of submenus
        submenu = caja.Menu()
        top_menuitem.set_submenu(submenu)
        # submenu items save
        sub_menuitem_save = caja.MenuItem('Kdiff3::save',
                                              _('Save Path for Future Use'),
                                              _('Save the Selected File/Dir Path for Future Use') )
        sub_menuitem_save.set_property('icon', 'gtk-save')
        sub_menuitem_save.connect('activate', self.kdiff3_save, element_1)
        submenu.append_item(sub_menuitem_save)
        # submenu items compare with saved
        stored_path = self.mateconf_client.get_string(MATECONF_PATH)
        if stored_path and stored_path != element_1 and ( (os.path.isfile(stored_path) and os.path.isfile(element_1) ) or (os.path.isdir(stored_path) and os.path.isdir(element_1) ) ):
            sub_menuitem_compare_saved = caja.MenuItem('Kdiff3::compare_saved',
                                                           _('Compare with %s' % stored_path.replace("_", " ") ),
                                                           _('Compare the Selected File/Dir with %s' % stored_path) )
            sub_menuitem_compare_saved.set_property('icon', 'gtk-execute')
            sub_menuitem_compare_saved.connect('activate', self.run, re.escape(element_1), re.escape(stored_path))
            submenu.append_item(sub_menuitem_compare_saved)
        return top_menuitem,
