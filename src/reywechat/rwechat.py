# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : WeChat methods.
"""


from os import getcwd as os_getcwd
from reydb import Database
from reykit.rbase import block
from reyserver.rclient import ServerClient

from .rbase import WeChatBase


__all__ = (
    'WeChat',
)


class WeChat(WeChatBase):
    """
    WeChat type.

    Warnings, only applicable to WeChat clients with version `3.9.12.56`.

    Warnings, must enabled file automatic download.
    """


    def __init__(
        self,
        db: Database,
        sclient: ServerClient,
        max_receiver: int = 2,
        call_name: str | None = None,
        log_dir: str = 'log',
        cache_dir: str = 'cache',
        client_port: int = 1024,
        callback_port: int = 1025
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        db : Database. Note: must include database engine of `wechat` name.
        sclient : Server client.
        max_receiver : Maximum number of receivers.
        call_name : Trigger call name.
            - `None`: Use account nickname.
        log_dir : Log directory.
        cache_dir : Cache directory.
        client_port : Client control API port.
        callback_port : Message callback port.
        """

        # Import.
        from .rcache import WeChatCache
        from .rclient import WeChatClient
        from .rdb import WeChatDatabase
        from .rlog import WeChatLog
        from .rreceive import WechatReceiver
        from .rsend import WeChatSendTypeEnum, WeChatSenderStatusEnum, WeChatSender

        # Build.

        ## Instance.
        self.client = WeChatClient(self, client_port, callback_port)
        self.cache = WeChatCache(self, cache_dir)
        self.error = WeChatLog(self, log_dir)
        self.receiver = WechatReceiver(self, max_receiver, call_name)
        self.trigger = self.receiver.trigger
        self.sender = WeChatSender(self)
        self.db = WeChatDatabase(self, db, sclient)

        ## Receive.
        self.receive_add_handler = self.receiver.add_handler
        self.receive_start = self.receiver.start
        self.receive_stop = self.receiver.stop

        ## Trigger.
        self.trigger_add_rule = self.trigger.add_rule

        ## Send.
        self.SendTypeEnum = WeChatSendTypeEnum
        self.SendstatusEnum = WeChatSenderStatusEnum
        self.send_add_handler = self.sender.add_handler
        self.send = self.sender.send
        self.send_start = self.sender.start
        self.send_stop = self.sender.stop
        self.wrap_try_send = self.sender.wrap_try_send

        ## Database.
        self.database_build = self.db.build_db


    def start(self) -> None:
        """
        Start all methods.
        """

        # Start.
        self.receive_start()
        self.send_start()


    def keep(self) -> None:
        """
        Blocking the main thread to keep running.
        """

        # Report.
        print('Keep runing.')

        # Blocking.
        block()


    @property
    def print_colour(self) -> bool:
        """
        Whether print colour.

        Returns
        -------
        Result.
        """

        # Parameter.
        result = self.error.rrlog.print_colour

        return result


    @print_colour.setter
    def print_colour(self, value: bool) -> None:
        """
        Set whether print colour.

        Parameters
        ----------
        value : Set value.
        """

        # Set.
        self.error.rrlog.print_colour = value
        self.error.rrlog_print.print_colour = value
        self.error.rrlog_file.print_colour = value
