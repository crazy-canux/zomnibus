#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################################################################
# Copyright (C) 2015 Canux CHENG               #
# All rights reserved                                                #
# Name: deploy.py
# Author: Canux canuxcheng@gmail.com                                 #
# Version: V1.0                                                      #
# Time: Mon 10 Aug 2015 10:18:25 PM EDT
######################################################################
# Description:
######################################################################

import commands
import os
from base import OmnibusAuto


class Deploy(OmnibusAuto):
    def __init__(self, *args, **kwargs):
        """Define variables."""
        super(Deploy, self).__init__(*args, **kwargs)
        self.parent = "master"
        self.prefix = "request"
        if self.args.branch:
            if self.args.branch == self.parent:
                self.branch = self.args.branch
            else:
                self.branch = "%s/%s" % (self.prefix, self.args.branch)

    def define_sub_options(self):
        """Define arguments."""
        super(Deploy, self).define_sub_options()
        self.deploy_parser.add_argument("-b", "--branch",
                                        required=True,
                                        help="The branch you want to switch.",
                                        dest="branch")
        self.deploy_parser.add_argument("-c", "--comment",
                                        default="",
                                        required=True,
                                        help="Commit comment like [APP]comments.",
                                        dest="comment")

    def create_one_branch(self, branch):
        """Create new branch or checkout to old branch."""
        try:
            cmd = "git checkout %s" % branch
            (status, output) = commands.getstatusoutput(cmd)
            self.logger.debug("{0}: {1}".format(cmd, output))
            # If this branch is not exist.
            if status:
                cmd = "git checkout %s" % self.parent
                (status, output) = commands.getstatusoutput(cmd)
                self.logger.debug("{0}: {1}".format(cmd, output))
                # Checkout to master, you need to git pull.
                self.asyn_branch(self.parent, output)
                cmd1 = "git checkout -b %s %s" % (branch, self.parent)
                (status1, output1) = commands.getstatusoutput(cmd1)
                self.logger.debug("{0}: {1}".format(cmd1, output1))
                if not status1:
                    return output1
            # If this branch exist.
            else:
                self.already_exist(branch)
                return output
        except Exception as e:
            self.error("create_one_branch: %s" % e)

    def delete_one_branch(self, branch):
        """Delete a branch."""
        try:
            # Checkout to master to delete other branch.
            self.create_one_branch(self.parent)
            cmd1 = "git branch -D %s" % branch
            (status1, output1) = commands.getstatusoutput(cmd1)
            self.logger.debug("{0}: {1}".format(cmd1, output1))
            if status1:
                self.not_exist(branch)
        except Exception as e:
            self.error("delete_one_branch: %s" % e)

    def commit_one_branch(self, comment):
        """Use git add and git commit to commit changes."""
        try:
            cmd = "git add -A"
            (status, output) = commands.getstatusoutput(cmd)
            self.logger.debug("{0}: {1}".format(cmd, output))
            if not status:
                cmd1 = "git commit -a -m '%s'" % comment
                (status1, output1) = commands.getstatusoutput(cmd1)
                self.logger.debug("{0}: {1}".format(cmd1, output1))
        except Exception as e:
            self.error("commit_branch: %s" % e)

    def conflict_branch(self, output):
        if "Automatic merge failed" in output:
            cmd1 = "git mergetool --tool=meld"
            status1 = os.system(cmd1)
            self.logger.debug("{0}: ".format(cmd1))
            # Delete the *.cfg.orig file.
            # Some other file have to be deleted?
            if not status1:
                cmd2 = "find . -name '*.orig' | xargs rm -f"
                (status2, output2) = commands.getstatusoutput(cmd2)
                self.logger.debug("{0}: {1}".format(cmd2, output2))
                # Commit.
                if not status2:
                    self.commit_one_branch("")

    def asyn_branch(self, branch, output):
        """After checkout to a branch, synchronous to remote branch."""
        if branch == "master":
            try:
                if "have diverged" in output:
                    cmd = "git reset --hard origin/%s" % branch
                    (status, output) = commands.getstatusoutput(cmd)
                    self.logger.debug("{0}: {1}".format(cmd, output))
                else:
                    pass
                cmd1 = "git fetch -p"
                (status1, output1) = commands.getstatusoutput(cmd1)
                self.logger.debug("{0}: {1}".format(cmd1, output1))
                cmd2 = "git pull"
                (status2, output2) = commands.getstatusoutput(cmd2)
                self.logger.debug("{0}: {1}".format(cmd2, output2))
                # if "Automatic merge failed" in output2:
                self.conflict_branch(output2)
            except Exception as e:
                self.error("asyn_branch %s" % e)

    def merge_branch(self, branch):
        """Merge branch and fix conflict."""
        try:
            cmd = "git merge --no-ff %s" % branch
            (status, output) = commands.getstatusoutput(cmd)
            self.logger.debug("{0}: {1}".format(cmd, output))
            # If conflict.
            self.conflict_branch(output)
        except Exception as e:
            self.error("merge_branch: %s" % e)

    def push_branch(self):
        try:
            cmd = "git push"
            (status, output) = commands.getstatusoutput(cmd)
            self.logger.debug("{0}: {1}".format(cmd, output))
        except Exception as e:
            self.error("push_branch: %s" % e)

    def create_branch(self):
        """Create branch from -b."""
        try:
            if self.args.branch:
                self.create_one_branch(self.branch)
            else:
                self.error("Please use -b specify the branch number")
        except Exception as e:
            self.error("create_branch: %s" % e)

    def commit_branch(self):
        try:
            choice = self.input("Are you sure commit this changes? ")
            if choice == 0:
                if self.args.comment:
                    self.commit_one_branch(self.args.comment)
                else:
                    self.error("Please use -c to specify commit comment.")
            else:
                self.error("Exit without commit.")
        except Exception as e:
            self.error("commit_branch: %s" % e)

    def deploy_branch(self):
        """After you finish the request use this function to deploy to nagios."""
        output = self.create_one_branch(self.parent)
        self.asyn_branch(self.parent, output)
        self.merge_branch(self.branch)
        self.push_branch()
        try:
            cmd = "fab deploy"
            os.system(cmd)
            self.logger.debug("{0}: ".format(cmd))
        except Exception as e:
            self.error("deploy_branch: %s" % e)

    def delete_branch(self):
        """Delete branch."""
        try:
            self.delete_one_branch(self.branch)
        except Exception as e:
            self.error("delete_branch: %s" % e)
