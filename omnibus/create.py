#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################
# Copyright (C) 2015 Canux CHENG               #
# All rights reserved                                                #
# Name: create.py
# Author: Canux canuxcheng@gmail.com                                 #
# Version: V1.0                                                      #
# Time: Thu 24 Sep 2015 05:21:31 AM EDT
######################################################################
# Description:
# Bug need to fix: Can not create multi users one time.
######################################################################

import os
import commands
from base import OmnibusAuto


class Create(OmnibusAuto):
    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)
        self.create_file = self.conf + "/create"
        self.logger.debug("create_file: {}".format(self.create_file))

    def define_sub_options(self):
        super(Create, self).define_sub_options()
        self.create_parser = self.subparsers.add_parser('create',
                                                        help='Create user.',
                                                        description='Options\
                                                        for create users.')
        self.create_parser.add_argument("-l", "--lastname",
                                        required=True,
                                        help="lastname=familyname=filename",
                                        dest="lastname")
        self.create_parser.add_argument("-f", "--firstname",
                                        required=True,
                                        help="firstname",
                                        dest="firstname")
        self.create_parser.add_argument("-g", "--group",
                                        required=True,
                                        help="group, [Helpdesk, Administrator,\
                                        Manager]",
                                        dest="group")

    def __check_args(self):
        if self.args.lastname and self.args.firstname and self.args.group:
            self.user_file = self.user + "/" + self.args.lastname.lower()
            self.fullname = self.args.firstname.capitalize() + " " \
                + self.args.lastname.upper()
            self.logger.debug("user_file: {}".format(self.user_file))
            self.logger.debug("fullname: {}".format(self.fullname))
        else:
            self.error("Please use -l -f -g to specify the arguments.")

    def get_id(self):
        try:
            cmd = "expr `egrep '\sID\s10[0-9]*' %s/* \
                | awk '{print $NF}'| sort -u \
                | awk 'END {print $0}'` + 1" % self.user
            (status, output) = commands.getstatusoutput(cmd)
            self.logger.debug("{0}: {1}".format(cmd, output))
            if not status:
                return output
        except Exception as e:
            self.error("get_id: %s" % e)

    def write_user(self):
        new_id = self.get_id()
        self.logger.debug("new_id: {}".format(new_id))
        try:
            fr = open(self.create_file, "r")
            lines = fr.readlines()
            fr.close()
            fw = open(self.user_file, "w")
            for line in lines:
                self.logger.debug("line: {}".format(line))
                if "lastname" in line:
                    fw.write(line.replace("lastname",
                                          self.args.lastname.lower()))
                elif "FULL NAME" in line:
                    fw.write(line.replace("fullname", self.fullname))
                elif "group" in line:
                    fw.write(line.replace("group",
                                          self.args.group.capitalize()))
                elif "VALUES" in line:
                    fw.write((line.replace("%d", str(new_id))).replace(
                        "fullname", self.fullname))
                elif "%d" in line:
                    fw.write(line.replace("%d", str(new_id)))
                else:
                    fw.write(line)
            fw.close()
        except Exception as e:
            self.error("write_user: %s" % e)

    def create_user(self):
        self.__check_args()
        if os.path.isfile(self.user_file):
            self.already_exist(self.user_file)
            if self.args.force:
                self.write_user()
        else:
                self.write_user()
