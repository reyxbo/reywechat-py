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
    'SEND_PORT',
    'RECEIVE_PORT',
    'WeChatBase',
    'WeChatError',
    'WeChatClientErorr',
    'WeChatTriggerError',
    'WeChatTriggerContinueExit',
    'WeChatTriggerBreakExit'
)

SEND_PORT = 49152
'Hook program listening port send message.'
RECEIVE_PORT = 49153
'Main program listening port receive message.'

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
