#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################
# Copyright (C) 2015 Faurecia (China) Holding Co.,Ltd.               #
# All rights reserved                                                #
# Name: nrobot.py
# Author: Canux canuxcheng@gmail.com                                 #
# Version: V1.0                                                      #
# Time: Fri 14 Aug 2015 01:51:44 AM EDT
######################################################################
# Description:
######################################################################

import os
import sys
from create import Create
from remove import Remove
from deploy import Deploy


class Omnibus(Create, Remove, Deploy):
    def __init__(self, *args, **kwargs):
        super(Omnibus, self).__init__(*args, **kwargs)


def main():
    robot = Omnibus()
    os.chdir(robot.args.path)

    if 'create' in sys.argv[1:]:
        robot.create_branch()
        robot.create_user()
        robot.commit_branch()
        robot.deploy_branch()
        robot.delete_branch()
    elif 'remove' in sys.argv[1:]:
        robot.create_branch()
        robot.remove_user()
        robot.commit_branch()
        robot.deploy_branch()
        robot.delete_branch()
    else:
        robot.error("Please choose your action.")
    robot.logger.debug("==== END DEBUG ====")


if __name__ == "__main__":
    main()
