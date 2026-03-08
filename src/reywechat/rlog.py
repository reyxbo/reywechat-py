# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-19
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Log methods.
"""

from reykit.rlog import Log
from reykit.ros import Folder, join_path

from .rbase import WeChatBase
from .rreceive import WeChatMessage
from .rsend import WeChatSendParameters
from .rwechat import WeChat

__all__ = (
    'WeChatLog',
)

class WeChatLog(WeChatBase):
    """
    WeChat log type.
    """

    def __init__(
        self,
        wechat: WeChat,
        dir_path: str
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        wechat : `WeChatClient` instance.
        dir_path : Log directory.
        """

        # Set attribute.
        self.wechat = wechat
        self.dir_path = dir_path

        # Make directory.
        self.folder = self.__make_dir()

        # Logger.
        self.rrlog = Log('WeChat')
        self.rrlog_print = Log('WeChat.WeChatPrint')
        self.rrlog_file = Log('WeChat.WeChatFile')

        # Add handler.
        self.__add_handler()

    def __make_dir(self) -> Folder:
        """
        Make directory 'project_dir/log'.

        Parameters
        ----------
        project_dir: Project directory.

        Returns
        -------
        Folder instance.
        """

        # Make.
        folder = Folder(self.dir_path)
        folder.make()

        return folder

    def __add_handler(self) -> None:
        """
        Add log handler.
        """

        # Parameter.
        format_ = (
            '%(format_time)s | '
            '%(format_levelname)s | '
            '%(format_message_)s'
        )

        # Add.

        ## Reset.
        self.rrlog_print.clear_handler()

        ## Add handler print.
        self.rrlog_print.add_print(format_=format_)

        ## Add handler file.
        file_path = self.folder + 'wechat'
        self.rrlog_file.add_file(
            file_path,
            time='m',
            format_=format_
        )

    @property
    def print_colour(self) -> bool:
        """
        Whether print colour.

        Returns
        -------
        Result.
        """

        # Parameter.
        result = self.rrlog.print_colour

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
        self.rrlog.print_colour = value
        self.rrlog_print.print_colour = value
        self.rrlog_file.print_colour = value

    def log_receive(
        self,
        message: WeChatMessage
    ) -> None:
        """
        Log receive message.

        Parameters
        ----------
        message : `WeChatMessage` instance.
        """

        # Generate record.
        if message.room is None:
            message_object = message.user
        else:
            message_object = message.room
        content_print = 'RECEIVE | %-20s' % message_object
        content_file = 'RECEIVE | %s' % message.params
        if message.exc_reports == []:
            level = self.rrlog.INFO
        else:
            level = self.rrlog.ERROR
            exc_text = '\n'.join(message.exc_reports)
            content_print = '%s\n%s' % (content_print, exc_text)
            content_file = '%s\n%s' % (content_file, exc_text)

        ## Add color.
        if self.rrlog.print_colour:
            color_code = self.rrlog.get_level_color_ansi(level)
            content_print = f'{color_code}{content_print}\033[0m'

        # Log.
        self.rrlog_print.log(
            format_message_=content_print,
            level=level
        )
        self.rrlog_file.log(
            format_message_=content_file,
            level=level
        )

    def log_send(
        self,
        send_params: WeChatSendParameters
    ) -> None:
        """
        Log send message.

        Parameters
        ----------
        send_params : `WeChatSendParameters` instance.
        """

        # Generate record.
        content_print = 'SEND    | %-20s' % send_params.receive_id
        content_file = 'SEND    | %s' % {
            'receive_id': send_params.receive_id,
            **send_params.params
        }
        if send_params.exc_reports == []:
            level = self.rrlog.INFO
        else:
            level = self.rrlog.ERROR
            exc_text = '\n'.join(send_params.exc_reports)
            content_print = '%s\n%s' % (content_print, exc_text)
            content_file = '%s\n%s' % (content_file, exc_text)

        ## Add color.
        if self.rrlog.print_colour:
            color_code = self.rrlog.get_level_color_ansi(level)
            content_print = f'{color_code}{content_print}\033[0m'

        # Log.
        self.rrlog_print.log(
            format_message_=content_print,
            level=level
        )
        self.rrlog_file.log(
            format_message_=content_file,
            level=level
        )
