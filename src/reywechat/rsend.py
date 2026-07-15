# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-03
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Send methods.
"""

from typing import Any, Literal, overload
from collections.abc import Callable
from enum import StrEnum
from functools import wraps as functools_wraps
from queue import Queue
from reykit.rbase import throw, catch_exc, get_arg_info
from reykit.rtime import now, sleep
from reykit.rwrap import wrap_thread, wrap_exc

from .rbase import WeChatBase, WeChatTriggerContinueExit, WeChatTriggerBreakExit
from .rwechat import WeChat

__all__ = (
    'WeChatSendTypeEnum',
    'WeChatSendParameters',
    'WeChatSender'
)

class WeChatSendTypeEnum(WeChatBase, StrEnum):
    """
    WeChat send type enumeration type.
    """

    TEXT = 'text'
    'Send text message.'
    FILE = 'file'
    'Send file message.'
    IMAGE = 'image'
    'Send image message.'
    VIDEO = 'video'
    'Send video message.'
    EMOTION = 'emotion'
    'Send emotion message.'
    SHARE = 'share'
    'Send share link message.'
    CARD = 'card'
    'Send contact name card message.'
    FORWARD = 'forward'
    'Send forward message.'
    XML = 'xml'
    'Send `xml` format content message.'

class WeChatSenderStatusEnum(WeChatBase, StrEnum):
    """
    WeChat sender status enumeration type.
    """

    INIT = 'init'
    'After initialization, before inserting into the database queue.'
    WAIT = 'wait'
    'After get from database queue, before sending.'
    SENT = 'sent'
    'After sending.'

class WeChatSendParameters(WeChatBase):
    """
    WeChat send parameters type.
    """

    SendTypeEnum = WeChatSendTypeEnum
    SendStatusEnum = WeChatSenderStatusEnum

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.TEXT],
        receive_id: str,
        send_id: int | None = None,
        *,
        text: str,
        at_id: str | list[str] | Literal['all'] | None = None
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.FILE, WeChatSendTypeEnum.IMAGE, WeChatSendTypeEnum.VIDEO, WeChatSendTypeEnum.EMOTION],
        receive_id: str,
        send_id: int | None = None,
        *,
        file_id: str
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.FILE, WeChatSendTypeEnum.IMAGE, WeChatSendTypeEnum.VIDEO, WeChatSendTypeEnum.EMOTION],
        receive_id: str,
        send_id: int | None = None,
        *,
        file_path: str,
        file_name: str | None = None
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.SHARE],
        receive_id: str,
        send_id: int | None = None,
        *,
        page_url: str,
        title: str,
        text: str,
        image_url: str | None = None
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.CARD],
        receive_id: str,
        send_id: int | None = None,
        *,
        contact_id: str
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.FORWARD],
        receive_id: str,
        send_id: int | None = None,
        *,
        message_id: str
    ) -> None: ...

    @overload
    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: Literal[WeChatSendTypeEnum.XML],
        receive_id: str,
        send_id: int | None = None,
        *,
        xml: str
    ) -> None: ...

    def __init__(
        self,
        sender: 'WeChatSender',
        send_type: WeChatSendTypeEnum,
        receive_id: str,
        send_id: int | None = None,
        **params: Any
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        sender : `WeChatSender` instance.
        send_type : Send type.
        receive_id : User ID or chat room ID of receive message.
        send_id : Send ID of database.
            - `None`: Not inserted into the database.
        params : Send parameters.
        """

        # Set attribute.
        self.sender = sender
        self.send_type = send_type
        self.receive_id = receive_id
        self.send_id = send_id
        self.params = params
        self.exc_reports: list[str] = []
        self.status: WeChatSenderStatusEnum

        ## Cache.
        self._cache: dict[str, Any] = {}

    @property
    def text(self) -> str:
        """
        Text description of parameter content.

        Returns
        -------
        Text.
        """

        # Cache.
        if 'text' in self._cache:
            return self._cache['text']

        # Get.
        match self.send_type:
            case WeChatSendTypeEnum.TEXT:
                self._cache['text'] = self.params['text']
            case WeChatSendTypeEnum.FILE:
                file_name = self.params.get('file_name')
                file_name_text = f'"{file_name}"' if file_name else ''
                self._cache['text'] = f'[发送文件{file_name_text}]'
            case WeChatSendTypeEnum.IMAGE:
                file_name = self.params.get('file_name')
                file_name_text = f'"{file_name}"' if file_name else ''
                self._cache['text'] = f'[发送图片{file_name_text}]'
            case WeChatSendTypeEnum.VIDEO:
                file_name = self.params.get('file_name')
                file_name_text = f'"{file_name}"' if file_name else ''
                self._cache['text'] = f'[发送视频{file_name_text}]'
            case WeChatSendTypeEnum.EMOTION:
                file_name = self.params.get('file_name')
                file_name_text = f'"{file_name}"' if file_name else ''
                self._cache['text'] = f'[发送动画表情{file_name_text}]'
            case WeChatSendTypeEnum.SHARE:
                title = self.params.get('title')
                title_text = f'"{title}"' if title else ''
                self._cache['text'] = f'[分享链接{title_text}]'
                text = self.params.get('text')
                if text is not None:
                    self._cache['text'] += f' {text}'
            case WeChatSendTypeEnum.CARD:
                self._cache['text'] = '[发送联系人名片]'
            case WeChatSendTypeEnum.FORWARD:
                self._cache['text'] = '[转发消息]'
            case WeChatSendTypeEnum.XML:
                self._cache['text'] = '[发送消息]'

            ## Throw exception.
            case send_type:
                throw(ValueError, send_type)

        return self._cache['text']

class WeChatSender(WeChatBase):
    """
    WeChat sender type.

    Attribute
    ---------
    WeChatSendTypeEnum : Send type enumeration.
    """

    SendTypeEnum = WeChatSendTypeEnum
    SendStatusEnum = WeChatSenderStatusEnum

    def __init__(self, wechat: WeChat) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        wechat : `WeChatClient` instance.
        """

        # Set attribute.
        self.wechat = wechat
        self.queue: Queue[WeChatSendParameters] = Queue()
        self.handlers: list[Callable[[WeChatSendParameters], Any]] = []
        self.started: bool | None = False

        # Start.
        self.__start_sender()

    @wrap_thread
    def __start_sender(self) -> None:
        """
        Start sender, that will sequentially send message in the send queue.
        """

        # Loop.
        while True:
            match self.started:

                ## Stop.
                case False:
                    sleep(0.1)
                    continue

                ## End.
                case None:
                    break

            send_params = self.queue.get()

            def handle_handler_exception(exc_text: str, *_) -> None:
                send_params.exc_reports.append(exc_text)

            ## Handler.
            for handler in self.handlers:
                handler = wrap_exc(
                    handler,
                    handler=handle_handler_exception
                )
                handler(send_params)

            ## Send.
            try:
                self.__send(send_params)

            ## Exception.
            except BaseException:

                # Catch exception.
                exc_text, *_ = catch_exc()

                # Save.
                send_params.exc_reports.append(exc_text)

            send_params.status = WeChatSenderStatusEnum.SENT

            ## Handler.
            for handler in self.handlers:
                handler = wrap_exc(handler, handler=handle_handler_exception)
                handler(send_params)

            ## Log.
            self.wechat.error.log_send(send_params)

    def __send(
        self,
        send_params: WeChatSendParameters
    ) -> None:
        """
        Send message.

        Parameters
        ----------
        send_params : `WeChatSendParameters` instance.
        """

        # Test.
        if (
            send_params.params.get('is_test')
            and send_params.send_type == WeChatSendTypeEnum.TEXT
        ):
            text: str = send_params.params['text']
            now_time = now('time_str')
            modify_text = text.replace(':time:', now_time, 1)
            send_params.params['text'] = modify_text

        # Method.
        match send_params.send_type:
            case WeChatSendTypeEnum.TEXT:
                send_func = self.wechat.client.send_text
            case WeChatSendTypeEnum.FILE:
                send_func = self.wechat.client.send_file
            case WeChatSendTypeEnum.IMAGE:
                send_func = self.wechat.client.send_image
            case WeChatSendTypeEnum.VIDEO:
                send_func = self.wechat.client.send_video
            case WeChatSendTypeEnum.EMOTION:
                send_func = self.wechat.client.send_emotion
            case WeChatSendTypeEnum.SHARE:
                send_func = self.wechat.client.send_share
            case WeChatSendTypeEnum.CARD:
                send_func = self.wechat.client.send_card
            case WeChatSendTypeEnum.FORWARD:
                send_func = self.wechat.client.send_forward
            case WeChatSendTypeEnum.XML:
                send_func = self.wechat.client.send_xml

            ## Throw exception.
            case send_type:
                throw(ValueError, send_type)

        # Send.
        arg_info = get_arg_info(send_func)
        send_params_keys = [
            item['name']
            for item in arg_info
        ]
        send_func_params = {
            key: value
            for key, value in send_params.params.items()
            if key in send_params_keys
        }
        send_func(
            send_params.receive_id,
            **send_func_params
        )

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.TEXT],
        receive_id: str,
        *,
        text: str,
        at_id: str | list[str] | Literal['all'] | None = None
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.FILE, WeChatSendTypeEnum.IMAGE, WeChatSendTypeEnum.VIDEO, WeChatSendTypeEnum.EMOTION],
        receive_id: str,
        *,
        file_id: str
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.FILE, WeChatSendTypeEnum.IMAGE, WeChatSendTypeEnum.VIDEO, WeChatSendTypeEnum.EMOTION],
        receive_id: str,
        *,
        file_path: str,
        file_name: str | None = None
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.SHARE],
        receive_id: str,
        *,
        page_url: str,
        title: str,
        text: str,
        image_url: str | None = None
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.CARD],
        receive_id: str,
        *,
        contact_id: str
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.FORWARD],
        receive_id: str,
        *,
        message_id: str
    ) -> None: ...

    @overload
    def send(
        self,
        send_type: Literal[WeChatSendTypeEnum.XML],
        receive_id: str,
        *,
        xml: str
    ) -> None: ...

    def send(
        self,
        send_type: WeChatSendTypeEnum,
        receive_id: str | None = None,
        **params: Any
    ) -> None:
        """
        Insert into `wechat.message_send` table of database, wait send.

        Parameters
        ----------
        send_type : Send type.
        receive_id : User ID or chat room ID of receive message.
        params : Send parameters.
        """

        # Parameter.
        send_params = WeChatSendParameters(
            self,
            send_type,
            receive_id,
            **params
        )
        send_params.status = WeChatSenderStatusEnum.INIT
        def handle_handler_exception(exc_text: str, *_) -> None:
            send_params.exc_reports.append(exc_text)

        # Handler.
        for handler in self.handlers:
            handler = wrap_exc(handler, handler=handle_handler_exception)
            handler(send_params)

        # Insert.
        self.wechat.db._insert_send(send_params)

    def add_handler(
        self,
        handler: Callable[[WeChatSendParameters], Any]
    ) -> None:
        """
        Add send handler function.
        Call at the after initialization, before inserting into the database queue.
        Call at the after get from database queue, before sending.
        Call at the after sending.
        Can be use `WeChatSendParameters.status` judge status.

        Parameters
        ----------
        handler : Handler method, input parameter is `WeChatSendParameters` instance.
        """

        # Add.
        self.handlers.append(handler)

    def wrap_try_send(
        self,
        receive_id: str | list[str],
        func: Callable
    ) -> Callable:
        """
        Decorator, send exception information.

        Parameters
        ----------
        receive_id : Receive user ID or chat room ID.
            - `str`: An ID.
            - `list[str]`: Multiple ID.
        func : Function.

        Returns
        -------
        Decorated function.
        """

        # Parameter.
        if type(receive_id) is str:
            receive_ids = [receive_id]
        else:
            receive_ids = receive_id

        @functools_wraps(func)
        def wrap(
            *arg: Any,
            **kwargs: Any
        ) -> Any:
            """
            Decorate.

            Parameters
            ----------
            args : Position arguments of decorated function.
            kwargs : Keyword arguments of decorated function.

            Returns
            -------
            Function execution result.
            """

            # Execute.
            try:
                result = func(
                    *arg,
                    **kwargs
                )
            except BaseException:
                exc_text, exc, _ = catch_exc()

                # Report.
                if not isinstance(
                    exc,
                    (WeChatTriggerContinueExit, WeChatTriggerBreakExit)
                ):
                    text = exc_text
                    for receive_id in receive_ids:
                        self.send(
                            WeChatSendTypeEnum.TEXT,
                            receive_id,
                            text=text
                        )

                # Throw exception.
                raise

            return result

        return wrap

    def start(self) -> None:
        """
        Start sender.
        """

        # Start.
        self.started = True

        # Report.
        print('Start sender.')

    def stop(self) -> None:
        """
        Stop sender.
        """

        # Stop.
        self.started = False

        # Report.
        print('Stop sender.')

    def end(self) -> None:
        """
        End sender.
        """

        # End.
        self.started = None

        # Report.
        print('End sender.')

    __del__ = end
