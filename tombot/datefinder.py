''' Contains date/time finding logic. '''
import re
import datetime
from datetime import timedelta
import dateutil.parser


YEAR_WORDS = ['y', 'j', 'jaar', 'jaren', 'years', 'year']
WEEK_WORDS = ['w', 'weeks', 'week', 'weken']
DAY_WORDS = ['d', 'dag', 'dagen', 'day', 'days']
HOUR_WORDS = ['h', 'hr', 'hrs', 'hours', 'hour', 'u', 'uur', 'uren']
MINUTE_WORDS = ['m', 'min', 'mins', 'minute', 'minutes', 'minuten', 'minuut']
SECOND_WORDS = ['s', 'sec', 'secs', 'second', 'seconds', 'seconden']

WORDS = [YEAR_WORDS, WEEK_WORDS, DAY_WORDS, HOUR_WORDS, MINUTE_WORDS, SECOND_WORDS]
for item in WORDS:
    item.sort(key=len, reverse=True)

SEPARATORS = [r'\s', ',', 'en', 'and', '&']
SEP_PART = '({})*'.format('|'.join(SEPARATORS))

YEAR_PART = r'((?P<years>\d+)\s*?({}){})?'.format('|'.join(YEAR_WORDS), SEP_PART)
WEEK_PART = r'((?P<weeks>\d+)\s*?({}){})?'.format('|'.join(WEEK_WORDS), SEP_PART)
DAY_PART = r'((?P<days>\d+)\s*?({}){})?'.format('|'.join(DAY_WORDS), SEP_PART)
HOUR_PART = r'((?P<hours>\d+)\s*?({}){})?'.format('|'.join(HOUR_WORDS), SEP_PART)
MINUTE_PART = r'((?P<minutes>\d+)\s*?({}){})?'.format('|'.join(MINUTE_WORDS), SEP_PART)
SECOND_PART = r'((?P<seconds>\d+)\s*?({}))?'.format('|'.join(SECOND_WORDS))

DURATION_MARKERS = ['in', 'over', 'na']

MONSTER = ''.join([YEAR_PART, WEEK_PART, DAY_PART, HOUR_PART, MINUTE_PART, SECOND_PART])
REGEX = re.compile(MONSTER, re.IGNORECASE)

def find_timedelta(text):
    '''
    (Attempts to) Find the first readable duration in a text and return it as a datetime.

    Argument: the text to search. The regex is horrible, so take care.
    Returns a timedelta, zero-length if no matches.
    '''
    matches = REGEX.findall(text)
    match = None
    for res in matches:
        if any(res):
            match = res
            break
    if not match:
        raise ValueError('Could not extract duration!')
    years = int(match[1]) if match[1] else 0 # in tdays
    weeks = int(match[5]) if match[5] else 0 # in tdays
    days = int(match[9]) if match[9] else 0 # in tdays
    tdays = days + 7 * weeks + 365 * years
    hours = int(match[13]) if match[13] else 0 # passed
    minutes = int(match[17]) if match[17] else 0 # passed
    seconds = int(match[21]) if match[21] else 0 # passed
    result = timedelta(
        days=tdays, hours=hours, minutes=minutes, seconds=seconds)
    return result

CLOCK_MARKERS = ['om', 'at']
CLOCK_PAT = r'((#!)\s?)?((?P<hour>\d{1,2})(:?((?P<minute>\d{2})(:?(?P<second>\d{2}))?)?))'.replace(
    r'#!', '|'.join(CLOCK_MARKERS))
STRICT_CLOCK_PAT = r'((#@)\s?)?((?P<hour>\d{1,2})(:?(?P<minute>\d{2})|\s?(#!)))(?![-/])'.replace(
    '#!', '|'.join(HOUR_WORDS)).replace('#@', '|'.join(CLOCK_MARKERS))
CLOCK_REGEX = re.compile(CLOCK_PAT, re.IGNORECASE)
STRICT_CLOCK_REGEX = re.compile(STRICT_CLOCK_PAT, re.IGNORECASE)
def find_first_time(text):
    '''
    Find the first occurrence of a clock time, return as datetime in today or tomorrow.
    Raises ValueError if no time is found.
    '''
    match = CLOCK_REGEX.search(text)
    if not match:
        raise ValueError('No time found!')
    hour = int(match.group('hour'))
    minute = int(match.group('minute')) if match.group('minute') else 0
    second = int(match.group('second')) if match.group('second') else 0
    result = datetime.datetime.now().replace(
        hour=hour, minute=minute, second=second)
    if result < datetime.datetime.now():
        result = result + datetime.timedelta(days=1)
    return result

class Biliparserinfo(dateutil.parser.parserinfo):
    ''' Bilingual dutch/english dateutil parserinfo '''
    JUMP = [" ", ".", ",", ";", "-", "/", "'",
            "at", "on", "and", "ad", "m", "t", "of",
            "st", "nd", "rd", "th",
            "op", "en", "de", "ste", "van"]
    WEEKDAYS = [("Mon", "Monday", "Ma", "Maa", "Maandag"),
                ("Tue", "Tuesday", "Di", "Din", "Dinsdag"),
                ("Wed", "Wednesday", "Wo", "Woe", "Woensdag"),
                ("Thu", "Thursday", "Do", "Don", "Donderdag"),
                ("Fri", "Friday", "Vr", "Vri", "Vrijdag"),
                ("Sat", "Saturday", "Za", "Zat", "Zaterdag"),
                ("Sun", "Sunday", "Zo", "Zon", "Zondag")]
    MONTHS = [("Jan", "January", "Januari"),
              ("Feb", "February", "Februari"),
              ("Mar", "March", "Maart"),
              ("Apr", "April"),
              ("May", "May", "Mei"),
              ("Jun", "June", "Juni"),
              ("Jul", "July", "Juli"),
              ("Aug", "August", "Augustus"),
              ("Sep", "Sept", "September"),
              ("Oct", "October", "Oktober"),
              ("Nov", "November"),
              ("Dec", "December")]
    HMS = [("h", "hour", "hours", "uur", "uren", "u"),
           ("m", "minute", "minutes", "minuut", "minuten", "min", "mins"),
           ("s", "second", "seconds", "sec", "seconden", "secondes", "secs")]
    PERTAIN = ["of"]

BPI = Biliparserinfo()
