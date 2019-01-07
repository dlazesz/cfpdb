#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

from datetime import date
from urllib.parse import quote
from operator import itemgetter
from calendar import monthrange

import yaml


# Secondary sorting key order...
event_order = ('submission', 'notification', 'camera-ready', 'begin', 'end')
events = {event: i for i, event in enumerate(event_order)}
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


def correct_date(value, far_future_date):
    if value is None:
        value = far_future_date  # Date field emtpy
    elif not isinstance(value, date):
        value = value.split('-')
        if len(value) != 3:  # YYYY-MM-DD
            value = far_future_date  # Totally wrong.
        else:
            value_out = []
            for v in value:  # Fields converted to integer or defaults to 1 (except year which defaults to this_year+10)
                try:
                    v = int(v)
                except ValueError:
                    v = -1
                value_out.append(v)
            if value_out[0] == -1:
                value_out[0] = far_future_date.year  # Totally wrong.
            if value_out[1] == -1:
                value_out[1] = 12  # Last month of the year
            if value_out[2] == -1:
                value_out[2] = monthrange(value_out[0], value_out[1])[1]  # Last day of a month
            value = date(*value_out)

    return value


def sort_confs(confs):
    curr_date = date.today()
    fields = [field for field, _ in sorted(events.items(), key=itemgetter(1), reverse=True)]  # Go backwards

    for name, data in confs.items():
        curr_last_date = correct_date(data.get(event_order[-1], ''), far_future)
        sort_date, sort_field = curr_last_date, event_order[-1]
        for field in fields[1:]:  # The last date is the default
            field_val = correct_date(data.get(field, ''), curr_last_date)
            if curr_date <= field_val < sort_date:  # The field_val is the nearest one in the future if there is any
                sort_date, sort_field = field_val, field  # Refine next upcomming date and event

        data['sort_date_date'] = sort_date
        data['sort_date'] = '{0}_{1}'.format(sort_date, events[sort_field])

    past_confs = []
    future_confs = []
    for name, data in sorted(confs.items(), key=lambda x: x[1]['sort_date']):
        # Conferences which have ended go unconditionally into the past...
        if data['sort_date_date'] < curr_date:
            past_confs.append((name, data))  # TODO: Confs ended on the same date are sorted in random order
        else:
            future_confs.append((name, data))

    # New -> Old
    past_confs.reverse()

    return past_confs, future_confs


def format_alert(sort_date, due_date, color, alert):
    if due_date is not None:
        formatted_field = str(due_date)
    else:
        formatted_field = ''
    if alert and sort_date.startswith(str(correct_date(due_date, far_future))):
        formatted_field = '<span style="background: {0}">{1}</span>'.format(color, due_date)
    return formatted_field


def print_conf(pos, name, data, out_stream=sys.stdout, alert=False):
    background = ''
    if pos % 2 == 0:
        background = 'background: #f4f4f4'

    name_formatted = '<span style="font-style: italic">{0}</span>'.format(name)
    if data['url'] is not None and len(data['url']) > 0:
        name_formatted = '<a href="{0}">{1}</a>'.format(data['url'], name_formatted)

    alert_event = int(data['sort_date'].split('_')[1])
    begin = format_alert(data['sort_date'], data['begin'], '#d0f0d0', alert and alert_event == events['begin'])

    end = ''
    if data['begin'] != data['end']:
        end = format_alert(data['sort_date'], data['end'], '#d0f0d0', alert and alert_event == events['end'])
        end = ' – {0}'.format(end)

    submission = format_alert(data['sort_date'], data['submission'], '#ffd0d0',
                              alert and alert_event == events['submission'])
    notification = format_alert(data['sort_date'], data['notification'], '#f8f8d0',
                                alert and alert_event == events['notification'])
    camera_ready = format_alert(data['sort_date'], data['camera-ready'], '#d0f0d0',
                                alert and alert_event == events['camera-ready'])

    print('<div style="margin-bottom: 0.5em;{0}">{1} ({2}{3}, <a href="http://maps.google.com/maps?q={4}">{5}</a>)'
          .format(background, name_formatted, begin, end, quote(data['location']), data['location']),
          '<br/>',
          '<span style="font-size: smaller">submission:</span> {0} – '.format(submission),
          '<span style="font-size: smaller">notification:</span> {0} – '.format(notification),
          '<span style="font-size: smaller">camera ready:</span> {0}'.format(camera_ready),
          '</div>',
          sep='\n', file=out_stream)


def print_html(confs, out_stream=sys.stdout):
    past_confs, future_confs = confs

    # Header
    print('<!DOCTYPE html>',
          '<html lang="en">',
          '<head>',
          '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/> ',
          '<title>Natural Language Processing (NLP) and Computational Linguistics (CL) Conferences</title>',
          '</head>',
          '<body style="font-family: Verdana, Helvetica, sans-serif; margin: 1em; width: 780px">',
          sep='\n', file=out_stream)

    position = 0
    if len(future_confs) > 0:
        position += 1
        print('<span style="font-size: larger; font-weight: bold">Upcoming...</span>', file=out_stream)

    for pos, (name, data) in enumerate(future_confs, start=position+1):
        print_conf(pos, name, data, out_stream, alert=True)

    position += len(future_confs)
    if len(past_confs) > 0:
        position += 1
        print('<span style="font-size: larger; font-weight: bold">Past...</span>', file=out_stream)

    for pos, (name, data) in enumerate(past_confs, start=position+1):
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
