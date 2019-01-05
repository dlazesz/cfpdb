#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys

sys.stdout = sys.stderr

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

activate_this = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from update_cfpdb_on_github import run_update, git_work_dir

run_update(git_work_dir)
