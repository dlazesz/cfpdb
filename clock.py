#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

from update_cfpdb_on_github import run_update, git_work_dir

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=1)
def scheduled_job():
    run_update(git_work_dir)


sched.start()
