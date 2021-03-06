import csv
import datetime
import os

import arrow
from ics import Calendar, Event

from course_time import detect
from get_course import get_course


def convert(username: str, password: str, filename: str, type_: str ='csv', port: int =80, weeks: int =10, first_day: datetime.date =None) -> None:
    if(os.path.isfile(filename)):
        print('File {0} already exists. Overwrite it? <y/N> '.format(filename), end = '')
        if(input().lower() != 'y'):
            return
    courses_list = get_course(username, password, port)
    if(type_ == 'csv'):
        with open(filename, 'w', newline='') as f:
            fieldnames = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Description', 'Location']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in courses_list:
                time_list = detect(i['time'], first_day=first_day, weeks=weeks)
                row = {
                    'Subject': i['name'],
                    'Description': '教师：{0}'.format(i['teacher']),
                    'Location': i['location']
                }
                for j in time_list:
                    row['Start Date'] = j['start_time'].date().isoformat()
                    row['End Date'] = j['end_time'].date().isoformat()
                    row["Start Time"] = j['start_time'].time().strftime("%H:%M")
                    row["End Time"] = j['end_time'].time().strftime("%H:%M")
                    writer.writerow(row)
        return
    if(type_ == 'ics'):
        c = Calendar()
        for i in courses_list:
            time_list = detect(i['time'], first_day=first_day, weeks=weeks)
            for j in time_list:
                e = Event(
                    name=i['name'],
                    begin=arrow.get(j['start_time'], 'Asia/Shanghai'),
                    end=arrow.get(j['end_time'], 'Asia/Shanghai'),
                    description='教师：{0}'.format(i['teacher']),
                    location=i['location']
                )
                c.events.add(e)
        with open(filename, 'w') as f:
            f.writelines(c)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Your student ID.', required=True)
    parser.add_argument('-p', '--password', help='Your password.', required=True)
    parser.add_argument('-P', '--port', type=int, help='Th port of xk.shu.edu.cn, 80 or 8080. The default is 80.')
    parser.add_argument('-w', '--weeks', type=int, help='The weeks of this semester, 10 for the general semester or 2 for the short semester. The default is 10.')
    parser.add_argument('-f', '--first-day', help='The first day of this semester. Like 2018-06-18. The default is this Monday.')
    parser.add_argument('-t', '--type', help='The type of output file, csv or ics. The default is csv.')
    parser.add_argument('filename', help='filename')
    args = parser.parse_args()
    convert(
        username=args.username,
        password=args.password,
        filename=args.filename,
        type_=args.type if args.type in ['csv', 'ics'] else 'csv',
        port=args.port if args.port else 80,
        weeks=args.weeks if args.weeks else 10,
        first_day=datetime.datetime.strptime(args.first_day, '%Y-%m-%d') if args.first_day else None
    )
