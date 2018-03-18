# -*- coding: utf-8 -*-
"""判题模块.

    Attributes:
        AC (str): 答案正确.
        CE (str): 编译错误.
        WA (str): 答案错误.
        SE (str): 系统错误.
        RE (str): 运行时错误.
        PE (str): 格式错误.
        MLE (str): 使用内存超过限制.
        TLE (str): CPU使用时间超过限制.
        RTLE (str): 程序运行时间超过限制.
        OLE (str): 输出数据长度超过限制.
        GCC_SYSCALL_WHITE_LIST (list): gcc/g++程序系统调用白名单, 发生白名单之外的系统调用结果判为RE.
"""
import logging
import re
import os
import signal
import sys
import time
import uuid
import traceback
import redis
import resource
import ctypes
import errno
import requests
try:
    import cPickle as pickle
except ImportError:
    import pickle
from ctypes.util import find_library
from seccomp import *
from hieuJudge.compiler import *
from hieuJudge.util import *

AC = "ACCEPTED"
CE = "COMPILE_ERROR"
WA = "WRONG_ANSWER"
SE = "SYSTEM_ERROR"
RE = "RUNTIME_ERROR"
PE = "PRESENTATION_ERROR"
MLE = "MEMORY_LIMIT_EXCEEDED"
TLE = "TIME_LIMIT_EXCEEDED"
RTLE = "REAL_TIME_LIMIT_EXCEEDED"
OLE = "OUTPUT_LIMIT_EXCEEDED"

GCC_SYSCALL_WHITE_LIST = [
    "read",
    "fstat",
    "mmap",
    "mprotect",
    "munmap",
    "open",
    "arch_prctl",
    "brk",
    "readlink",
    "sysinfo",
    "lseek",
    "writev",
    "access",
    "exit_group",
    "close",
    "uname"
]

libc = ctypes.cdll.LoadLibrary(find_library('c'))


class Judge(object):
    """判题类, 使用沙箱运行用户程序.

    Attributes:
        result (str): 判断结果.
        cpu_time (int): CPU使用时间, 单位MS.
        real_time (int): 用户程序运行时间, 单位MS.
        memory (int): 用户程序占用内存大小, 单位Byte.
    """

    logger = logging.getLogger('JudgeTask')

    def __init__(self, *args, **kwargs):
        """初始化.

        Args:
            work_dir (str): 工作目录.
            command (tuple): 运行命令行.
            input: 问题输入.
            output: 问题输出.
            memory_upper_bound (int): 可用内存上界, 单位Byte.
            max_memory_size (int): 内存限制, 单位Byte, 用户程序使用的内存超过此值判为MLE.
            max_cpu_time (int): CPU使用时间限制, 单位MS, 用户程序使用CPU的时间超过此值判为TLE.
            max_real_time (int): 用户程序运行时间(包括IO等待时间和CPU使用时间),
            单位MS, 用户程序运行时间超过此值判为RTLE.
            max_output_size (int): 用户程序输出限制, 单位Byte, 用户程序输出数据的大小抄过此值判为OLE.
            syscall_white_list (list): 系统调用白名单, 空列表或者 ``None`` 表示允许所有系统调用.
        """
        self._work_dir = kwargs.get('work_dir')
        self._command = kwargs.get('command')
        self._input = kwargs.get('input')
        self._output = kwargs.get('output')
        self._memory_upper_bound = kwargs.get('memory_upper_bound')
        self._max_memory_size = kwargs.get('max_memory_size')
        self._max_cpu_time = kwargs.get('max_cpu_time')
        self._max_real_time = kwargs.get('max_real_time')
        self._max_output_size = kwargs.get('max_output_size')
        self._syscall_white_list = GCC_SYSCALL_WHITE_LIST#kwargs.get('syscall_white_list')
        self._rule = kwargs.get('rule')
        # 运行结果
        self.result = None

        # CPU使用时间
        self.cpu_time = None

        # 运行时间
        self.real_time = None

        # 占用内存
        self.memory = None

        # 结束信号
        self.signum = None

    def run(self):
        self._judge()
        if self.result is None:
            if get_file_size(os.path.join(self._work_dir, STDOUT_FILENAME)) > len(self._output):
                self.result = OLE
            else:
                with open(os.path.join(self._work_dir, STDOUT_FILENAME), 'r') as f:
                    user_output = f.read()
                if user_output.replace('\r\n','\n') == self._output.replace('\r\n','\n'):
                    self.result = AC
                elif re.sub(r'\s', "", user_output) == re.sub(r'\s', "", self._output):
                    self.result = PE
                else:
                    self.result = WA

    def _judge(self):
        """运行用户程序"""
        filename, compile_cmd, run_cmd = self._command
        with open(os.path.join(self._work_dir, STDIN_FILENAME), 'w+') as f:
            f.write(self._input)
        pid = os.fork()
        if pid == 0:
            resource.setrlimit(resource.RLIMIT_CPU, ((self._max_cpu_time + 1000) / 1000 * 1.5,) * 2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (self._max_output_size,) * 2)
            # if self._lang in ['GCC', 'G++']:
            #    resource.setrlimit(resource.RLIMIT_AS, (self._memory_upper_bound, ) * 2)
            os.chdir(self._work_dir)
            redirect_std_stream(True, True, True)
            path = ctypes.create_string_buffer(os.path.abspath(run_cmd[0]))
            arglist = run_cmd[1:]
            array_cls = ctypes.POINTER(ctypes.c_char) * (len(arglist) + 1)
            args = array_cls(*map(ctypes.create_string_buffer, arglist))
            args[len(arglist)] = None
            try:
                if (self._syscall_white_list is not None) and (len(self._syscall_white_list) > 0) and self._rule == 'c_cpp':
                    f = SyscallFilter(KILL)
                    for call_name in self._syscall_white_list:
                        f.add_rule_exactly(ALLOW, call_name)
                    f.add_rule_exactly(ALLOW, "execve", Arg(0, EQ, ctypes.addressof(path)))
                    f.add_rule_exactly(ALLOW, "write", Arg(0, EQ, sys.stdin.fileno()))
                    f.add_rule_exactly(ALLOW, "write", Arg(0, EQ, sys.stdout.fileno()))
                    f.add_rule_exactly(ALLOW, "write", Arg(0, EQ, sys.stderr.fileno()))
                    f.load()
                if self._rule == 'general':
                    f = SyscallFilter(ALLOW)
                    for call_name in ['kill']:
                        f.add_rule_exactly(KILL, call_name)

                    f.add_rule_exactly(ERRNO(errno.EACCES), 'socket')
                    #f.add_rule_exactly(KILL, 'clone', Arg(2, MASKED_EQ, 32768))
                    f.add_rule_exactly(KILL, 'execve', Arg(0, NE, ctypes.addressof(path)))
                    f.add_rule_exactly(ERRNO(errno.EACCES), 'open', Arg(1, MASKED_EQ, os.O_WRONLY, os.O_WRONLY))
                    f.add_rule_exactly(ERRNO(errno.EACCES), 'open', Arg(1, MASKED_EQ, os.O_RDWR, os.O_RDWR))
                    f.add_rule_exactly(ERRNO(errno.EACCES), 'openat', Arg(2, MASKED_EQ, os.O_WRONLY, os.O_WRONLY))
                    f.add_rule_exactly(ERRNO(errno.EACCES), 'openat', Arg(2, MASKED_EQ, os.O_RDWR, os.O_RDWR))
                    f.load()
                libc.execve(path, args, None)
            finally:
                os.kill(os.getpid(), signal.SIGUSR1)
        elif pid > 0:
            used_mem = 0
            cpu_time = 0
            start_time = time.time()
            real_time = 0
            while True:
                real_time = (time.time() - start_time) * 1000
                proc_pid, proc_status, proc_usage = os.wait4(pid, os.WNOHANG)
                used_mem = max(used_mem, int(get_proc_status(pid).get('VmHWM', 0)) * KB)
                if (proc_pid, proc_status) != (0, 0):
                    used_mem = max(used_mem, proc_usage.ru_maxrss * KB)
                    cpu_time = (proc_usage.ru_utime + proc_usage.ru_stime) * 1000
                    if os.WIFSIGNALED(proc_status):
                        self.signum = os.WTERMSIG(proc_status)
                        if self.signum == signal.SIGUSR1:
                            raise JudgeSystemError('execve函数调用失败')
                        elif self.signum in [signal.SIGKILL, signal.SIGXCPU]:
                            self.result = TLE
                        elif self.signum == signal.SIGXFSZ:
                            self.result = OLE
                        else:
                            self.result = RE
                    break
                elif used_mem > self._max_memory_size:
                    os.kill(pid, signal.SIGKILL)
                elif real_time > self._max_real_time:
                    os.kill(pid, signal.SIGKILL)
                elif get_file_size(os.path.join(self._work_dir, STDOUT_FILENAME)) > len(self._output):
                    self.result = OLE
                    os.kill(pid, signal.SIGKILL)

            self.memory = used_mem
            self.cpu_time = cpu_time
            self.memory = used_mem
            self.real_time = real_time
            if get_file_size(os.path.join(self._work_dir, STDERR_FILENAME)) > 0:
                self.result = RE
            elif used_mem > self._max_memory_size:
                self.result = MLE
            elif real_time > self._max_real_time:
                self.result = RTLE
            elif cpu_time > self._max_cpu_time:
                self.result = TLE

            # 处理一下JAVA和MONO的内存溢出错误
            with open(os.path.join(self._work_dir, STDERR_FILENAME), 'r') as f:
                data = f.read()
                if 'java.lang.OutOfMemoryError' in data or 'System.OutOfMemoryException' in data:
                    self.result = MLE

            with open(os.path.join(self._work_dir, STDIN_FILENAME), 'r') as f:
                data = f.read()
                if 'java.lang.OutOfMemoryError' in data or 'System.OutOfMemoryException' in data:
                    self.result = MLE

        else:
            raise JudgeSystemError('fork函数调用失败')


def unit_test():
    """单元测试.
    """
    settings = load_settings()
    init_logging_module(settings)
    commands = settings.get('COMMANDS')
    compiler = CodeCompiler(commands=commands, target_file_size=settings.get('TARGET_FILE_SIZE'),
                            memory_upper_bound=settings.get('MEMORY_UPPER_BOUND'))

    work_dir = settings.get('ROOT_WORK_DIR')
    ac_code = """
        #include <iostream>
        int main() {
            std::cout << "yes" << std::endl;
            return 0;
        }
    """

    wa_code = """
        #include <iostream>
        int main() {
            std::cout << "wa" << std::endl;
            return 0;
        }
    """

    pe_code = """
        #include <iostream>
        int main() {
            std::cout << "yes" << std::endl << std::endl;
            return 0;
        }
    """

    tle_code = """
        int main() {
            while(1);
            return 0;
        }
    """

    rtle_code = """
        #include <iostream>
        #include <unistd.h>
        int main() {
            sleep(10);
            return 0;
        }
    """

    re_code = """
        #include <iostream>
        #include <signal.h>
        int main() {
            raise(SIGSEGV);
            return 0;
        }
    """

    work_dir = os.path.abspath(os.path.join(work_dir, 'unit_test'))

    os.system('mkdir %s -p' % (work_dir,))

    task = {
        'input': 'test' * 1000000,
        'output': 'yes\n',
        'work_dir': work_dir,
        'command': commands['G++'],
        'max_memory_size': 128 * MB,
        'max_output_size': settings.get('MAX_OUTPUT_SIZE'),
        'max_cpu_time': 1000,
        'max_real_time': 5000,
        'memory_upper_bound': settings.get('MEMORY_UPPER_BOUND'),
    }

    for code, result in zip([ac_code, wa_code, tle_code, rtle_code, re_code], [AC, WA, TLE, RTLE, RE]):
        print 'TEST:', result
        ret, msg = compiler.compile('G++', work_dir, code)
        if ret:
            judge = Judge(**task)
            judge.run()
            if judge.result == result:
                print 'YES'
            else:
                print judge.result
        else:
            print msg

    os.system('rm -r ' + work_dir)


def process_task(redis_server=None):
    settings = load_settings()
    init_logging_module(settings)
    logger = logging.getLogger('ProcessTask')
    if redis_server is None:
        redis_server = settings['REDIS_SERVER_URL']
    rclient = redis.StrictRedis.from_url(redis_server)
    commands = settings.get('COMMANDS')
    root_work_dir = settings.get('ROOT_WORK_DIR')
    compiler = CodeCompiler(commands=commands, target_file_size=settings.get('TARGET_FILE_SIZE'),
                            memory_upper_bound=settings.get('MEMORY_UPPER_BOUND'))
    while True:
        try:
            _, task = rclient.brpop(settings.get('TASK_QUEUE_NAME'))
            task = pickle.loads(task.decode("zlib"))
            work_dir = os.path.join(root_work_dir, task['id'])
            if task['lang'] in ['GCC', 'G++']:
                task['rule'] = 'c_cpp'
            else:
                task['rule'] = 'general'
            task['work_dir'] = work_dir
            task['command'] = commands[task['lang']]
            task['max_output_size'] = settings.get('MAX_OUTPUT_SIZE')
            task['memory_upper_bound'] = settings.get('memory_upper_bound')
            try:
                os.system('mkdir -p {}'.format(task['work_dir']))
                logger.info(u'<%s>正在编译, 语言:%s, 代码长度:%sB', task['id'], task['lang'], len(task['code']))
                ret = compiler.compile(task['lang'], work_dir, task['code'])
                if ret:
                    judge = Judge(**task)
                    logger.info(u'<%s>正在运行, 内存限制:%.2fMB, CPU时间限制:%sMS, 运行时间限制:%sMS',
                                task['id'], task['max_memory_size'] / MB, task['max_cpu_time'], task['max_real_time'])

                    requests.get(task['report_url'], params={ 'task_id': task['id'], 'status': 'RUNNING'})

                    judge.run()
                    logger.info(u'<%s>运行完成, 结果:%s, 退出信号:%s, 占用内存:%sMB, 占用CPU:%sMS, 运行时间:%.2fMS',
                                task['id'], judge.result, signum2str(judge.signum), judge.memory / MB, judge.cpu_time,
                                judge.real_time)
                    data = {'task_id': task['id'], 'status': judge.result}
                    if judge.result == AC:
                        data['used_time'] = judge.cpu_time
                        data['used_memory'] = judge.memory / MB
                    requests.get(task['report_url'], params=data)
                else:
                    logger.info(u'<%s>编译失败, 语言: %s', task['id'], task['lang'])
                    requests.get(task['report_url'], params={'task_id': task['id'], 'status': CE})
            except Exception as ex:
                requests.get(task['report_url'], params={'task_id': task['id'], 'status': SE})
            finally:
                os.system('rm -r {}'.format(os.path.join(root_work_dir, task['id'])))
        except Exception as ex:
            traceback.print_exc()
