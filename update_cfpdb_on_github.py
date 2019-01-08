#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys
import shutil
from datetime import date

from git import Repo, Actor

git_work_dir = 'repo_test'


def run_update(work_dir):
    # Compute absolute path for working dir for later use
    abs_work_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), work_dir)

    # Clean work_dir
    shutil.rmtree(abs_work_dir, ignore_errors=True)

    # Clone master
    repo = Repo.clone_from('git@github.com:dlazesz/cfpdb.git', abs_work_dir, branch='master')

    # Clone the other branches
    repo.git.checkout('--track', 'origin/conferences')
    repo.git.checkout('--track', 'origin/gh-pages')

    # Get back to master branch
    repo.git.checkout('master')

    # Get the lastest YAML file but remove it from index
    repo.git.checkout('conferences', '--', 'conferences.yaml')
    repo.git.reset()

    # Go into the git working dir and also add it to modulepath!
    os.chdir(abs_work_dir)
    sys.path.append(abs_work_dir)

    # Create HTML from YAML file
    from generate_calendar import main as gen_html
    gen_html()

    # Get to master branch
    repo.git.checkout('gh-pages')

    # Overwrite old HTML file
    os.rename('cfps.html', 'index.html')
    os.rename('cfps.ics', 'conferences.ics')

    # add result
    repo.index.add(['index.html', 'conferences.ics'])

    if len(repo.index.diff('HEAD')) > 0:
        # commit result
        author = Actor("CFP Updater Bot", "this.bot.h@s.no.email")
        repo.index.commit('Update on {0}'.format(date.today().isoformat()), author=author, committer=author)
        # push result
        repo.remotes['origin'].push()
        print('Pushed!')
    else:
        print('Nothing to commit')


if __name__ == '__main__':
    run_update(git_work_dir)