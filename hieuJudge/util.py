# -*- coding: utf-8 -*-
"""通用工具.
"""

import os
import sys
import signal
import logging

KB = 1 << 10
MB = 1 << 20

STDIN_FILENAME = 'stdin'
STDERR_FILENAME = 'stderr'
STDOUT_FILENAME = 'stdout'
SIGNAL_MAPPING = dict([(v, key) for key, v in signal.__dict__.items() if key.startswith('SIG')])
_root_handler = None


def _get_handler(settings):
    handler = logging.StreamHandler()
    handler.setLevel(settings.get('LOG_LEVEL'))
    formatter = logging.Formatter(fmt=settings.get('LOG_FORMAT'), datefmt=settings.get('LOG_DATE_FORMAT'))
    handler.setFormatter(formatter)
    return handler


def init_logging_module(settings):
    """初始化日志模块.

    Args:
        settings (dict): :py:func:`load_settings`
    """
    global _root_handler
    if _root_handler is not None and _root_handler in logging.root.handlers:
        logging.root.removeHandler(_root_handler)
    logging.root.setLevel(logging.NOTSET)
    _root_handler = _get_handler(settings)
    logging.root.addHandler(_root_handler)


def load_settings(path='.', module='settings'):
    """载入配置文件.

    默认配置::

        {
            # 日志日期输出格式
            'LOG_DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
            # 日志输出
            'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            # 任务队列长度限制
            'TASK_QUEUE_MAX_NUM': 50,
            # 任务队列名称
            'TASK_QUEUE_NAME': 'judge_task_queue',
             # 工作目录
            'ROOT_WORK_DIR': './work_dir',
             # 日志级别
             'LOG_LEVEL': logging.DEBUG,
             # 可用内存上界
             'MEMORY_UPPER_BOUND': 512 * MB,
             # 编译器输出文件大小限制
             'TARGET_FILE_SIZE': 64 * MB,
             # 命令行配置
             'COMMANDS': {
                # 语言名称
                'GCC': (
                    # 源文件名称
                    'Main.c',
                    # 编译命令行
                    ('/usr/bin/gcc', 'Main.c', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-std=c99', '-DONLINE_JUDGE'),
                    # 运行命令行
                    ('./Main', ),
                ),
                'G++': (
                    'Main.cc',
                    ('/usr/bin/g++', 'Main.cc', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-DONLINE_JUDGE'),
                    ('./Main',),
                ),
                'JAVA': (
                    'Main.java',
                    ('/usr/bin/javac', '-J-Xmx256m',  'Main.java'),
                    ('/usr/bin/java', '-Xms32m', '-Xmx512m', 'Main'),
                ),
                'MONO': (
                    'Main.cs',
                    ('/usr/bin/gmcs', 'Main.cs', '-out:Main.exe'),
                    ('/usr/bin/mono', '--debug', 'Main.exe')
                )
             }
        }

    Args:
        path (str): 配置文件位置.
        module (str): 配置文件名称.

    Returns:
        dict: 配置项

    Raises:
        ImportError: 配置文件载入失败.
    """
    try:
        sys.path.append(path)
        settings = {}
        settings.setdefault('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
        settings.setdefault('LOG_FORMAT', '%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        settings.setdefault('TASK_QUEUE_MAX_NUM', 50)
        settings.setdefault('TASK_QUEUE_NAME', 'judge_task_queue')
        settings.setdefault('ROOT_WORK_DIR', os.path.abspath('./work_dir'))
        settings.setdefault('LOG_LEVEL', logging.DEBUG)
        settings.setdefault('MEMORY_UPPER_BOUND', 512 * MB)
        settings.setdefault('TARGET_FILE_SIZE', 64 * MB)
        settings.setdefault('REDIS_SERVER_URL', 'redis://localhost:6379/0')
        commands = {
            'GCC': (
                'Main.c',
                ('/usr/bin/gcc', 'Main.c', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-std=c99',
                 '-DONLINE_JUDGE'),
                ('./Main',),
            ),
            'G++': (
                'Main.cc',
                ('/usr/bin/g++', 'Main.cc', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-DONLINE_JUDGE'),
                ('./Main',),
            ),
            'JAVA': (
                'Main.java',
                ('/usr/bin/javac', '-J-Xmx256m', 'Main.java'),
                ('/usr/bin/java', '-Xms32m', '-Xmx512m', 'Main'),
            ),
            'MONO': (
                'Main.cs',
                ('/usr/bin/gmcs', 'Main.cs', '-out:Main.exe'),
                ('/usr/bin/mono', '--debug', 'Main.exe')
            )
        }
        settings.setdefault('COMMANDS', commands)
       
        settings.update(__import__(module).__dict__)
        return settings
    finally:
        sys.path.remove(path)


def redirect_std_stream(stdin=True, stdout=True, stderr=True):
    """重定向标准流.

    标准输入流重定向到文件 ``stdin``.

    标准输出流重定向到文件 ``stdout``.

    标准错误流重定向到文件 ``stderr``.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

        stdin (bool): 是否重定向标准输入流.

        stdout (bool): 是否重定向标准输出流.

        stderr (bool): 是否重定向标准错误流.

    Raises:
        OSError: 调用 :py:meth:`os.dup2` 失败
    """
    if stdin:
        os.dup2(os.open(STDIN_FILENAME, os.O_RDONLY), sys.stdin.fileno())
    if stdout:
        os.dup2(os.open(STDOUT_FILENAME, os.O_WRONLY | os.O_CREAT), sys.stdout.fileno())
    if stderr:
        os.dup2(os.open(STDERR_FILENAME, os.O_WRONLY | os.O_CREAT), sys.stderr.fileno())


def get_file_size(path):
    """获取文件大小.

    Args:
        path (str): 文件路径.

    Returns:
        int: 文件大小, 单位Byte
    """
    return os.stat(path).st_size


def get_proc_status(pid):
    """根据进程PID获取进程信息.

    Args:
        pid (int): 进程PID.

    Returns:
        dict: 包含进程信息的字典
    """
    ret = {}
    try:
        with open('/proc/%s/status' % (pid,)) as f:
            for line in f:
                name, value = line.split(':')
                ret[name] = value.split()[0]
    except:
        pass
    return ret


def signum2str(signum):
    """signum转换成字符表示"""
    return SIGNAL_MAPPING.get(signum)
