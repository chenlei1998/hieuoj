# -*- coding: utf-8 -*-
import redis
try:
    import cPickle as pickle
except ImportError:
    import pickle
from django.conf import settings


def problems_to_ab_map(problems):
    return dict([(problem.id, ab) for ab, problem in zip([chr(ch) for ch in xrange(65, 65+26)], problems)])


def submit_task(task_id, lang, code, input, output, memory_limit, time_limit, report_url):
    rclient = redis.StrictRedis.from_url(settings.REDIS_SERVER_URL)
    if lang == 'C#':
        lang = 'MONO'
    task = {
        'id': str(task_id),
        'lang': lang,
        'code': code,
        'input': input.replace('\r\n', '\n'),
        'output': output.replace('\r\n', '\n'),
        'max_memory_size': memory_limit * (1<<20),
        'max_cpu_time': time_limit,
        'max_real_time': time_limit * 4,
        'report_url': settings.HOST_NAME + report_url
    }
    rclient.lpush(settings.TASK_QUEUE, pickle.dumps(task).encode('zlib'))