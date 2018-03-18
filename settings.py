# -*- coding: utf-8 -*-
"""配置文件.

    .. seealso:: :py:func:`hieuJudge.util.load_settings`
"""
import logging

KB = 1 << 10
MB = 1 << 20

# 启用ZLIB压缩
ENABLE_ZLIB = False

# 允许使用的语言列表
ALLOW_LANG_LIST = ['JAVA', 'MONO', 'GCC', 'G++']

# 工作目录
ROOT_WORK_DIR = './work_dir'

# 最长代码长度
MAX_CODE_LENGTH = 4 * MB

# 用户程序输出数据大小
MAX_OUTPUT_SIZE = 64 * MB

# 用户程序输入数据大小
MAX_INPUT_SIZE = 64 * MB

# 任务队列名称
TASK_QUEUE_NAME = 'judge_task_queue'

# 任务队列长度设置
TASK_QUEUE_MAX_NUM = 50

# REDIS服务器配置
REDIS_SERVER_URL = 'redis://localhost:6379/0'

# 日志输出格式
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# 日期格式
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志级别
LOG_LEVEL = logging.DEBUG

# 可使用内存上界
MEMORY_UPPER_BOUND = 512 * MB

# 编译器输出的目标文件大小
TARGET_FILE_SIZE = 64 * MB

# 命令行
COMMANDS = {
    'GCC': (
        'Main.c',
        ('/usr/bin/gcc', 'Main.c', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-std=c99',
         '-DONLINE_JUDGE'),
        ('./Main', 'Main'),
    ),
    'G++': (
        'Main.cc',
        ('/usr/bin/g++', 'Main.cc', '-o', 'Main', '-O2', '-fno-asm', '-w', '-lm', '--static', '-DONLINE_JUDGE'),
        ('./Main', 'Main'),
    ),
    'JAVA': (
        'Main.java',
        ('/usr/bin/javac', '-J-Xmx256m', 'Main.java'),
        ('/usr/bin/java', 'java', '-Xms32m', '-Xmx%sm' % (MEMORY_UPPER_BOUND / MB,), 'Main'),
    ),
    'MONO': (
        'Main.cs',
        ('/usr/bin/mcs', 'Main.cs', '-out:Main.exe'),
        ('/usr/bin/mono', 'mono', '--debug', 'Main.exe')
    )
}
