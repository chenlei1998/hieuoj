# -*- coding: utf-8 -*-
import os
import signal
import resource

from hieuJudge.exception import *
from hieuJudge.util import *


class CodeCompiler(object):
    """代码编译器"""

    def __init__(self, *args, **kwargs):
        """初始化编译器.

        Args:
            kwargs: ``dict``, 键值含义如下:
                  {
                    'target_file_size': ``int``, 编译器输出文件大小,
                    'commands': ``dict``,
                    'memory_upper_bound': ``int``, 编译器可使用内存上限
                  }
        """
        self.target_file_size = kwargs.get('target_file_size')
        self.commands = kwargs.get('commands')
        self.memory_upper_bound = kwargs.get('memory_upper_bound')

    def compile(self, lang, work_dir, code):
        """编译源代码.

        在指定的目录编译源代码

        Args:
            lang: ``str``, 选择的语言.
            work_dir: 编译器工作目录.
            code: 程序源代码

        Returns:
            返回值Tuple(编译结果, 错误原因).

        Raises:
            NotSupportLangException: 编译器不支持所选择的语言
        """
        if lang in self.commands:
            return self._compile_code(self.commands[lang], work_dir, lang, code)
        else:
            raise NotSupportLangException()

    def _compile_code(self, command, task_dir, lang, code):
        filename, compile_cmd, _ = command
        pid = os.fork()
        if pid == 0:
            resource.setrlimit(resource.RLIMIT_FSIZE, (self.target_file_size * 1.5,) * 2)
            if lang != 'JAVA':
                resource.setrlimit(resource.RLIMIT_AS, (self.memory_upper_bound,) * 2)
            os.chdir(task_dir)
            redirect_std_stream(False, True, True)
            with open(filename, 'w+') as f:
                f.write(code)
            try:
                os.execl(compile_cmd[0], *compile_cmd)
            finally:
                os.kill(os.getpid(), signal.SIGUSR1)
        elif pid > 0:
            _, status, usage = os.wait4(pid, 0)
            if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
                return False
            if os.WIFSIGNALED(status):
                if os.WTERMSIG(status) == signal.SIGUSR1:
                    return False
                else:
                    return False
            if get_file_size(os.path.join(task_dir, filename)) > self.target_file_size:
                return False
            return True
        else:
            raise JudgeSystemError()
