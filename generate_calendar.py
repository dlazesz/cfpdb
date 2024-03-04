#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys

from datetime import date, time, datetime
from urllib.parse import quote
from operator import itemgetter
from calendar import monthrange

import yaml
from ics import Calendar, Event

# Secondary sorting key order...
events = {'submission': 0, 'notification': 1, 'camera-ready': 2, 'begin': 3, 'end': 4}


def _load_yaml(cfg_file):
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
        end = None  # Including the last elem
    lines = lines[start:end]

    try:
        ret = yaml.safe_load(''.join(lines))
    except yaml.YAMLError as exc:
        print(exc, file=sys.stderr)
        exit(1)

    return ret


def _correct_date(value):
    if isinstance(value, str):
        value = value.split('-')
        if len(value) != 3:  # YYYY-MM-DD
            value = date.max  # Totally wrong
        else:
            value_out = []
            for v in value:  # Fields converted to integer or defaults to max value of field
                try:
                    v = int(v)
                except ValueError:
                    v = -1
                value_out.append(v)
            if value_out[0] == -1:
                # Compute partial year specification like 201X -> 2019, 20X9 -> 2099
                ret_num = 0
                for num, power in zip(value[0], (3, 2, 1, 0)):
                    try:
                        ret_num += int(num) * (10**power)
                    except ValueError:
                        ret_num += 9 * (10**power)
                value_out[0] = ret_num
            if value_out[1] == -1:
                value_out[1] = 12  # Last month of the year
            if value_out[2] == -1:
                value_out[2] = monthrange(value_out[0], value_out[1])[1]  # Last day of a month
            value = date(*value_out)

    return value


def _sort_confs(confs):
    curr_date = date.today()
    fields = [field for field, _ in sorted(events.items(), key=itemgetter(1), reverse=True)]  # Go backwards
    last_event = fields[0]

    # Find next upcomming date for every event
    for name, data in confs.items():
        if last_event not in data:
            raise ValueError(f'"{last_event}" field not present for "{name}" !')
        last_event_date = _correct_date(data[last_event])
        data['corrected_dates'] = {last_event: last_event_date}  # Store corrected date

        sort_date, sort_field = last_event_date, last_event
        for field in fields[1:]:  # The last date is the default
            if field not in data:
                raise ValueError(f'"{field}" field not present for "{name}" !')
            field_val = _correct_date(data[field])
            data['corrected_dates'][field] = field_val  # Store corrected date

            # The field_val is the nearest one in the future if there is any
            if field_val is not None and curr_date <= field_val <= sort_date:
                sort_date, sort_field = field_val, field  # Refine next upcomming date and event

        data['sort_key'] = (sort_date, events[sort_field], name)  # Stabilize sort

    past_confs = []
    future_confs = []
    for name, data in sorted(confs.items(), key=lambda x: x[1]['sort_key']):
        # Conferences which have ended go into the past...
        if data['sort_key'][0] < curr_date:
            past_confs.append((name, data))
        else:
            future_confs.append((name, data))

    # New -> Old
    past_confs.reverse()

    return past_confs, future_confs


def _format_alert(due_date, color, alert):
    if isinstance(due_date, date):
        formatted_field = due_date.isoformat()
    elif isinstance(due_date, str):
        formatted_field = due_date
    else:
        formatted_field = ''
        due_date = date.max
    if alert:
        formatted_field = f'<span style="background: {color}">{due_date}</span>'

    return formatted_field


def _print_conf(pos, name, data, alert=False, out_stream=sys.stdout):
    background = ''
    if pos % 2 == 0:
        background = 'background: #f4f4f4'

    name_formatted = f'<span style="font-style: italic">{name}</span>'
    if data['url'] is not None and len(data['url']) > 0:
        name_formatted = f'<a href="{data["url"]}">{name_formatted}</a>'

    sort_date, alert_event = data['sort_key'][:2]
    begin = _format_alert(data['begin'], '#d0f0d0', alert and alert_event == events['begin'])

    end = ''
    if data['begin'] != data['end']:
        end = _format_alert(data['end'], '#d0f0d0', alert and alert_event == events['end'])
        end = f' – {end}'

    submission = _format_alert(data['submission'], '#ffd0d0', alert and alert_event == events['submission'])
    notification = _format_alert(data['notification'], '#f1f1a3', alert and alert_event == events['notification'])
    camera_ready = _format_alert(data['camera-ready'], '#d0f0d0', alert and alert_event == events['camera-ready'])

    print(f'<div style="margin-bottom: 0.5em;{background}">{name_formatted} ({begin}{end}, '
          f'<a href="https://maps.google.com/maps?q={quote(data["location"])}">{data["location"]}</a>)',
          '<br/>',
          f'<span style="font-size: smaller">submission:</span> {submission} – ',
          f'<span style="font-size: smaller">notification:</span> {notification} – ',
          f'<span style="font-size: smaller">camera ready:</span> {camera_ready}',
          '</div>',
          sep='\n', file=out_stream)


def _enumerate_confs(confs, label, position, out_stream, alert=False):
    if len(confs) > 0:
        position += 1
        print(f'<span style="font-size: larger; font-weight: bold">{label}</span>', file=out_stream)

        for pos, (name, data) in enumerate(confs, start=position + 1):
            _print_conf(pos, name, data, alert, out_stream)

    return position


def _print_html(confs, out_stream=sys.stdout):
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

    # Upcomming conferences
    position = _enumerate_confs(future_confs, 'Upcoming...', 0, out_stream, alert=True)
    # Past conferences
    _enumerate_confs(past_confs, 'Past...', position + len(future_confs), out_stream)

    # Footer
    print('</body>',
          '</html>',
          sep='\n', file=out_stream)


def _add_event(cal, name, begin_date, end_date, location, url):
    e = Event(name=name, begin=datetime.combine(begin_date, time.min),
              end=datetime.combine(end_date, time.max), location=location, url=url)
    e.make_all_day()
    cal.events.add(e)


def _create_ics(confs, stream):
    cal = Calendar()

    """
    # For standard compliance
    cal.add('prodid', '-//NLP CFP DB calendar//xx.url//')
    cal.add('version', '2.0')
    """

    for name, data in confs.items():
        begin = data['corrected_dates']['begin']
        end = data['corrected_dates']['end']
        location = data['location']
        url = data['url']

        for field_name in ('submission', 'notification', 'camera-ready'):
            due_date = data['corrected_dates'][field_name]
            if due_date is not None and due_date < date.max:
                _add_event(cal, f'{field_name.upper()}: {name}', due_date, due_date, location, url)

        if begin < date.max:
            if end < begin:
                end = begin

            # Conference
            _add_event(cal, name, begin, end, location, url)

    stream.writelines(cal)


def main(inp='conferences.yaml', out='cfps.html', out_ics='cfps.ics'):
    conferences = _load_yaml(inp)
    sorted_conferences = _sort_confs(conferences)
    with open(out, 'w', encoding='UTF-8') as fh:
        _print_html(sorted_conferences, fh)
    with open(out_ics, 'w', encoding='UTF-8') as fh:
        _create_ics(conferences, fh)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
