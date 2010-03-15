from __future__ import with_statement
import os
import sys
import csv
import datetime


class VacalcError(Exception): pass
class DuplicateUser(VacalcError): pass


class UserStore(object):

    def __init__(self, db_file='db.csv'):
        self._db_file = db_file
        if db_file and os.path.isfile(db_file):
            self._users = self._read_users(db_file)
        else:
            self._users = {}

    def _read_users(self, path):
        users = {}
        with open(path) as db:
            for row in csv.reader(db):
                user = User(row[0], row[1])
                users[user.name] = user
        return users

    def get_user(self, name):
        for row in csv.reader(open(self._db_file)):
            if row[0] == name:
                return User(row[0], row[1])

    def add_user(self, name, startdate):
        if name in self._users:
            raise DuplicateUser(name)
        user = User(name, startdate)
        self._users[user.name] = user
        self._serialize(user)
        return user

    def _serialize(self, user):
        with open(self._db_file, 'a') as db:
            writer = csv.writer(db, lineterminator='\n')
            writer.writerow([user.name, user.startdate.isoformat()])


class VacationCalculator(object):

    def __init__(self, userstore):
        self._userstore = userstore

    def vacation(self, name, year):
        user = self._userstore.get_user(name, year)
        return user.count_vacation(year)

    def add_user(self, name, startdate):
        user = self._userstore.add_user(name, startdate)
        return "Successfully added user '%s'." % user.name


class User(object):

    def __init__(self, name, startdate):
        self.name = name
        self.startdate = self._parse_date(startdate)

    def _parse_date(self, datestring):
        year, month, day = datestring.split('-')
        return datetime.date(int(year), int(month), int(day))

    def count_vacation(self, year):
        fail


def main(args):
    try:
        return getattr(VacationCalculator(UserStore()), args[0])(*args[1:])
    except (AttributeError, TypeError):
        raise VacalcError('invalid command or arguments')


if __name__ == '__main__':
    try:
        print main(sys.argv[1:])
        sys.exit(0)
    except VacalcError, err:
        print err
        sys.exit(1)