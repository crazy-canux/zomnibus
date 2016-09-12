#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################
# Copyright (C) 2015 Faurecia (China) Holding Co.,Ltd.               #
# All rights reserved                                                #
# Name: remove.py
# Author: Canux canuxcheng@gmail.com                                 #
# Version: V1.0                                                      #
# Time: Fri 25 Sep 2015 01:48:03 AM EDT
######################################################################
# Description:
# Bug need to fix: Can not handle the same family name.
######################################################################

import os
from base import OmnibusAuto


class Remove(OmnibusAuto):
    def __init__(self, *args, **kwargs):
        super(Remove, self).__init__(*args, **kwargs)
        self.remove_file = self.conf + "/remove"
        self.logger.debug("remove_file: {}".format(self.remove_file))

    def define_sub_options(self):
        super(Remove, self).define_sub_options()
        self.remove_parser = self.subparsers.add_parser('remove',
                                                        help='Remove user.',
                                                        description='Options\
                                                        for remove user.')
        self.remove_parser.add_argument("-s", "--string",
                                        action="append",
                                        required=True,
                                        help="Specify user's filename which\
                                        you want to remove.",
                                        dest="string")

    def __check_args(self):
        if not self.args.string:
            self.error("Please use -s to specify the full name string.")

    def find_file(self, filename):
        fr = open(filename, "r")
        lines = fr.readlines()
        for loop in range(0, len(lines)):
            line = lines[loop]
            self.logger.debug("old line: {}".format(line))
            if loop == 2:
                fullname = line.split("'")[1].strip()
                self.logger.debug("fullname: {}".format(fullname))
            elif loop == 6:
                group = line.split("'")[1].strip()
                self.logger.debug("group: {}".format(group))
            else:
                pass
        return fullname, group

    def __remove_file(self, filename):
        try:
            os.remove(filename)
        except Exception as e:
            self.error("remove_file: %s" % e)

    def write_file(self, filename, fullname, group):
        try:
            lastname = os.path.basename(filename)
            self.logger.debug("fullname: {}".format(fullname))
            self.logger.debug("group: {}".format(group))
            self.logger.debug("lastname: {}".format(lastname))
            fr = open(self.remove_file, "r")
            lines = fr.readlines()
            fw = open(filename, "w")
            for line in lines:
                self.logger.debug("new line: {}".format(line))
                if "lastname" in line:
                    fw.write(line.replace("lastname", lastname))
                elif "fullname" in line:
                    fw.write(line.replace("fullname", fullname))
                elif "group" in line:
                    fw.write(line.replace("group", group))
                else:
                    fw.write(line)
        except Exception as e:
            self.error("write_file: %s" % e)

    def remove_user(self):
        self.__check_args()
        for string in self.args.string:
            filename = self.user + "/" + string
            self.logger.debug("old_file: {}".format(filename))
            (fullname, group) = self.find_file(filename)
            self.__remove_file(filename)
            self.write_file(filename, fullname, group)
