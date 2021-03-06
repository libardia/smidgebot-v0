from dateutil.relativedelta import relativedelta
from datetime import date, datetime

def englishArray(list, empty='none'):
    if len(list) == 0:
        return empty
    elif len(list) == 1:
        return list[0]
    elif len(list) == 2:
        return f'{list[0]} and {list[1]}'
    else:
        string = ''
        for i, item in enumerate(list):
            if i != 0:
                string += ', '
            if i == len(list)-1:
                string += 'and '
            string += item
        return string

_DAYS_ITOD = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
_DAYS_DTOI = {d : i for i, d in enumerate(_DAYS_ITOD)}
_TZS = {'pst': 2, 'cst': 0, 'est': -1}
def timecodeToTuple(code):
    # DDD HH:MM [AM/PM] ZZZ
    try:
        dow, hm, ampm, tz = code.lower().split(' ')
        hours, minutes = (int(i) for i in hm.split(':'))
        if ampm == 'pm' and hours != 12:
            hours += 12
        hours += _TZS[tz]
        return _DAYS_DTOI[dow], hours, minutes
    except:
        return None

def tupleToEnglish(tup):
    dow, hours, minutes = tup
    ampm = ['am', 'am', 'am']
    hours = [hours, hours, hours]
    for i in range(len(hours)):
        hours[i] -= list(_TZS.values())[i]
        if hours[i] >= 12:
            ampm[i] = 'pm'
        if hours[i] > 12:
            hours[i] -= 12
    return f'{_DAYS_ITOD[dow]}:\n{hours[0]:02}:{minutes:02} {ampm[0]} PST\n{hours[1]:02}:{minutes:02} {ampm[1]} CST\n{hours[2]:02}:{minutes:02} {ampm[2]} EST'.upper()

def tupleToNearestTimestamp(tup):
    dow, hours, minutes = tup
    now = datetime.now()
    sched = now + relativedelta(weekday=dow)
    sched = sched.replace(hour=hours, minute=minutes, second=0)
    return int(sched.timestamp())

def testTime(remtime):
    d, h, m = remtime
    dt = datetime.now()
    return dt.weekday() == d and dt.hour == h and dt.minute == m and dt.second == 0

def etb(orig):
    return orig.replace('```', '`\u200d`\u200d`')

def discordEscape(orig):
    esc = ('\\', '*', '_', '|', '`', '~')
    escaped = orig
    for c in esc:
        escaped = escaped.replace(c, f'\\{c}')
    return escaped
