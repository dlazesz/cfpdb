#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

from datetime import date
from operator import itemgetter

import yaml


# Secondary sorting key order...
event_order = ('submission', 'notification', 'camera-ready', 'start')
far_past = date.today().replace(year=date.today().year-10)
far_future = date.today().replace(year=date.today().year+10)


def load_yaml(cfg_file):
    lines = open(cfg_file, encoding='UTF-8').readlines()
    try:
        start = lines.index('%YAML 1.1\n')
    except ValueError:
        print('Error in config file: No document start marker found!', file=sys.stderr)
        sys.exit(1)
    rev = lines[start:]
    rev.reverse()
    try:
        end = rev.index('...\n')*(-1)
    except ValueError:
        print('Error in config file: No document end marker found!', file=sys.stderr)
        sys.exit(1)
    if end == 0:
        lines = lines[start:]
    else:
        lines = lines[start:end]

    try:
        yaml.load(''.join(lines))
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        exit(1)

    return yaml.load(''.join(lines))


def correct_date(value, far_future):
    if not isinstance(value, date):
        value = value.split('-')
        if len(value) != 3:  # YYYY-MM-DD
            value = far_future  # Totally wrong.
        else:
            value_out = []
            for v in value:  # Fields converted to integer or defaults to 1 (except year which defaults to this_year+10)
                try:
                    v = int(v)
                except ValueError:
                    v = 1
                value_out.append(v)
            if value_out[0] == 1:
                value_out[0] = far_future.year  # Totally wrong.
            value = date(*value_out)

    return value


def sort_confs(confs):
    curr_date = date.today()
    events = {event: i for i, event in enumerate(event_order)}
    fields = [field for field, _ in sorted(events.items(), key=itemgetter(1))]  # Sorted for stability

    for name, data in confs.items():
        sort_date, sort_field = far_future, None
        newest_date, newest_filed = far_past, None
        for field in fields:
            field_val = correct_date(data.get(field, ''), far_future)
            if curr_date < field_val < sort_date:  # The field_val is the nearest one in the future if there is any...
                sort_date, sort_field = field_val, field  # Refine next upcomming date and event
            if newest_date < field_val:  # Track the last event from a conference even if it is passed
                newest_date, newest_filed = field_val, field

        if sort_date == far_future:  # Keep order even when a conference is over (eg. all dates are in the future)...
            sort_date, sort_field = newest_date, newest_filed

        data['next_event'] = sort_field
        data['{0}_date'.format(sort_field)] = sort_date
        data['sort_date'] = '{0}_{1}'.format(sort_date, events[sort_field])

    past_confs = []
    future_confs = []
    for name, data in sorted(confs.items(), key=lambda x: x[1]['sort_date']):
        if data['{0}_date'.format(data['next_event'])] >= date.today():
            future_confs.append((name, data))
        else:
            past_confs.append((name, data))

    # New -> Old
    past_confs.reverse()

    return past_confs, future_confs


def format_alert(sort_date, due_date, color, alert):
    formatted_field = str(due_date)
    if alert and sort_date.startswith(str(correct_date(due_date, far_future))):
        alert = False
        formatted_field = '<span style="background: {0}">{1}</span>'.format(color, due_date)
    return formatted_field, alert


def print_conf(pos, name, data, out_stream=sys.stdout, alert=False):
    background = ''
    if pos % 2 == 0:
        background = 'background: #f4f4f4'

    name_formatted = '<span style="font-style: italic">{0}</span>'.format(name)
    if len(data['url']) > 0:
        name_formatted = '<a href="{0}">{1}</a>'.format(data['url'], name_formatted)

    begin, alert = format_alert(data['sort_date'], data['start'], '#d0f0d0', alert)

    end = ''
    if data['start'] != data['end']:
        end, alert = format_alert(data['sort_date'], data['end'], '#d0f0d0', alert)
        end = ' – {0}'.format(end)

    submission, alert = format_alert(data['sort_date'], data['submission'], '#ffd0d0', alert)
    notification, alert = format_alert(data['sort_date'], data['notification'], '#f8f8d0', alert)
    camera_ready, alert = format_alert(data['sort_date'], data['camera-ready'], '#d0f0d0', alert)

    print('<div style="margin-bottom: 0.5em;{0}">{1}({2}{3}, <a href="http://maps.google.com/maps?q={4}">{4}</a>)'
          .format(background, name_formatted, begin, end, data['location']),
          '<br/>',
          '<span style="font-size: smaller">submission:</span> {0} – '.format(submission),
          '<span style="font-size: smaller">notification:</span> {0} – '.format(notification),
          '<span style="font-size: smaller">camera ready:</span> {0}'.format(camera_ready),
          '</div>',
          sep='\n', file=out_stream)


def print_html(confs, out_stream=sys.stdout):
    past_confs, future_confs = confs

    # Header
    print('<html>',
          '<title>Natural Language Processing (NLP) and Computational Linguistics (CL) Conferences</title>',
          '<body style="font-family: Verdana, Helvetica, sans-serif; margin: 1em; width: 780px">',
          sep='\n', file=out_stream)

    if len(future_confs) > 0:
        print('<span style="font-size: larger; font-weight: bold">Upcoming...</span>', file=out_stream)

    for pos, (name, data) in enumerate(future_confs, start=1):
        print_conf(pos, name, data, out_stream, alert=True)

    if len(past_confs) > 0:
        print('<span style="font-size: larger; font-weight: bold">Past...</span>', file=out_stream)

    for pos, (name, data) in enumerate(past_confs, start=len(future_confs)+1):
        print_conf(pos, name, data, out_stream)

    # Footer
    print('</body>',
          '</html>',
          sep='\n', file=out_stream)


def main(inp='conferences.yaml', out='cfps.html'):
    conferences = load_yaml(inp)
    sorted_conferences = sort_confs(conferences)
    print_html(sorted_conferences, open(out, 'w', encoding='UTF-8'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
