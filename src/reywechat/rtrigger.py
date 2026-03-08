# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-07-16
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Trigger methods.
"""

from typing import Any, TypedDict, NoReturn
from collections.abc import Callable
from reykit.rbase import catch_exc

from .rbase import WeChatBase, WeChatTriggerContinueExit, WeChatTriggerBreakExit
from .rreceive import WeChatMessage, WechatReceiver

__all__ = (
    'WeChatTrigger',
)

TriggerRule = TypedDict('TriggerRule', {'level': float, 'execute': Callable[[WeChatMessage], None], 'is_reply': bool})

class WeChatTrigger(WeChatBase):
    """
    WeChat trigger type.
    """

    def __init__(
        self,
        receiver: WechatReceiver
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        receiver : `WechatReceiver` instance.
        """

        # Set attribute.
        self.receiver = receiver
        self.rules: list[TriggerRule] = []

        # Add handler.
        self.handler = self.__add_receiver_handler_trigger_by_rule()

        # Add trigger.
        self.__add_trigger_valid()

    def __add_receiver_handler_trigger_by_rule(self) -> Callable[[WeChatMessage], None]:
        """
        Add receiver handler, trigger message by rules.

        Returns
        -------
        Handler.
        """

        def receiver_handler_trigger_by_rule(message: WeChatMessage) -> None:
            """
            Trigger message by rules.

            Parameters
            ----------
            message : `WeChatMessage` instance.
            """

            # Loop.
            for rule in self.rules:
                message.triggering_rule = rule

                # Replied.
                if (
                    message.replied_rule is not None
                    and rule['is_reply']
                ):
                    continue

                # Trigger.
                try:
                    rule['execute'](message)

                # Continue.
                except WeChatTriggerContinueExit:
                    continue

                # Break.
                except WeChatTriggerBreakExit:
                    break

                # Exception.
                except BaseException:

                    ## Catch exception.
                    exc_text, *_ = catch_exc()

                    ## Save.
                    message.exc_reports.append(exc_text)

                finally:
                    message.triggering_rule = None

        # Add handler.
        self.receiver.add_handler(receiver_handler_trigger_by_rule)

        return receiver_handler_trigger_by_rule

    def add_rule(
        self,
        execute: Callable[[WeChatMessage], Any],
        level: float,
        is_reply: bool,
    ) -> None:
        """
        Add trigger rule.

        Parameters
        ----------
        execute : Trigger execute function. The parameter is the `WeChatMessage` instance.
            Function name must start with `reply_` to allow use of `WeChatMessage.reply`.
            When throw `WeChatTriggerContinueExit` type exception, then continue next execution.
            When throw `WeChatTriggerBreakExit` type exception, then stop executes.
        level : Priority level, sort from large to small.
        is_reply : Whehter is reply function, allow call `WeChatMessage.reply`, can only reply once function.
        """

        # Parameter.
        rule: TriggerRule = {
            'level': level,
            'execute': execute,
            'is_reply': is_reply
        }

        # Add.
        self.rules.append(rule)

        # Sort.
        fund_sort = lambda rule: rule['level']
        self.rules.sort(
            key=fund_sort,
            reverse=True
        )

    def continue_(self) -> NoReturn:
        """
        Continue trigger by throwing `WeChatTriggerContinueExit` type exception.
        """

        # Raise.
        raise WeChatTriggerContinueExit

    def break_(self) -> NoReturn:
        """
        Break trigger by throwing `WeChatTriggerBreakExit` type exception.
        """

        # Raise.
        raise WeChatTriggerBreakExit

    def __add_trigger_valid(self) -> None:
        """
        Add trigger, trigger rule judge valid.

        Returns
        -------
        Handler.
        """

        def trigger_valid(message: WeChatMessage) -> None:
            """
            Trigger rule judge valid.

            Parameters
            ----------
            message : `WeChatMessage` instance.
            """

            # Judge.
            if not message.valid:

                # Break.
                message.trigger_break()

        # Add.
        self.add_rule(trigger_valid, float('inf'), False)
