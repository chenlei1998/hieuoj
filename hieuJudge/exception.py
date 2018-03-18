# -*- coding: utf-8 -*-
"""异常定义.
"""


class NotSupportLangException(Exception):
    """语言不支持"""
    pass


class JudgeSystemError(Exception):
    """系统错误"""
    pass
