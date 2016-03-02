'''
ABAS: Automated Birthday Announcement System
'''
from apscheduler.jobstores.base import JobLookupError
from .registry import get_easy_logger, register_startup, register_shutdown
from tombot.rpc import remote_send


LOGGER = get_easy_logger('plugins.abas')

def announce_bday(recipient, name):
    LOGGER.info('Congratulating %s', name)
    body = 'Gefeliciteerd, {}!'.format(name)
    remote_send(recipient, body)

@register_startup
def abas_register_cb(bot, *args, **kwargs):
    LOGGER.info('Registering ABAs.')
    try:
        bot.cursor.execute('SELECT primary_nick,bday FROM users WHERE bday IS NOT NULL')
    except TypeError:
        LOGGER.error('Invalid date found, fix your database!')
        return
    results = bot.cursor.fetchall()
    for person in results:
        LOGGER.info('Scheduling ABA for %s', person[0])
        bot.scheduler.add_job(
            announce_bday,
            'cron', month=person[1].month, day=person[1].day,
            hour=15, minute=0, second=0,
            id='abas.{}'.format(person[0]),
            args=(bot.config['Jids']['announce-group'], person[0]),
            replace_existing=True, misfire_grace_time=86400
            )

@register_shutdown
def abas_register_cb(bot, *args, **kwargs):
    LOGGER.info('Deregistering ABAs.')
    bot.cursor.execute('SELECT primary_nick FROM users WHERE bday IS NOT NULL')
    results = bot.cursor.fetchall()
    for person in results:
        try:
            bot.scheduler.remove_job('abas.{}'.format(person[0]))
        except JobLookupError:
            pass
    LOGGER.info('Done.')
