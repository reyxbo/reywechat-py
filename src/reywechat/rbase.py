# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-07-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base methods.
"""

from reykit.rbase import Base, Error, Exit

__all__ = (
    'WeChatBase',
    'WeChatError',
    'WeChatClientErorr',
    'WeChatTriggerError',
    'WeChatTriggerContinueExit',
    'WeChatTriggerBreakExit'
)

class WeChatBase(Base):
    """
    WeChat Base type.
    """

class WeChatError(WeChatBase, Error):
    """
    WeChat error type.
    """

class WeChatExit(WeChatBase, Exit):
    """
    WeChat exit type.
    """

class WeChatClientErorr(WeChatError):
    """
    WeChat client error type.
    """

class WeChatTriggerError(WeChatError):
    """
    WeChat trigger error type.
    """

class WeChatTriggerExit(WeChatExit):
    """
    WeChat trigger exit type.
    """

class WeChatTriggerContinueExit(WeChatTriggerExit):
    """
    WeChat trigger continue exit type.
    """

class WeChatTriggerBreakExit(WeChatTriggerExit):
    """
    WeChat trigger break exit type.
    """
