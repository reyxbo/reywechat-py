# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Client methods.
"""

from typing import TypedDict, Literal
from threading import Event
from queue import Queue
from reykit.rbase import throw
from reykit.ros import File
from reykit.rsys import run_cmd, search_process, popup_select, get_sys_bits
from reykit.rtime import wait, sleep

from .rbase import WeChatBase, WeChatClientErorr
from .rhook import WeChatHook
from .rwechat import WeChat

__all__ = (
    'CallbackData',
    'CallbackParams',
    'PendingCallback',
    'LoginInfo',
    'WeChatClient'
)

type CallbackData = dict[str, str | int]
CallbackParams = TypedDict(
    'CallbackParams',
    {
        'type': int,
        'data': CallbackData
    }
)
"""
Key "type" is request type.
Key "data" is request data.
"""
PendingCallback = TypedDict(
    'PendingCallback',
    {
        'event': Event,
        'data': CallbackData | None
    }
)
"""
Key "event" is threading event instance.
Key "data" is request data.
"""
LoginInfo = TypedDict(
    'LoginInfo',
    {
        'id': str,
        'account': str,
        'name': str,
        'phone': str | None,
        'head_image': str | None,
        'file_dir': str
    }
)
"""
Key "id" is account ID.
Key "account" is account name.
Key "name" is nickname.
Key "phone" is phone number.
Key "head_image" is head image URL.
"""

class WeChatClient(WeChatBase):
    """
    WeChat client type.
    """

    def __init__(
        self,
        wechat: WeChat
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        wechat : `WeChat` instance.
        """

        # Build.
        self.wechat = wechat
        self.queue: Queue[CallbackParams] = Queue()
        self.hook = WeChatHook()
        self.hook_pid: int | None = None
        self.login_info: LoginInfo | None = None
        self._injected: bool = False
        self._initialized: bool = False
        self._logined: bool = False
        self._pending_callbacks: dict[str, PendingCallback] = {}

        # Start.
        self.start()

    def start(self) -> None:
            """
            Start client control API.
            """

            # Check.

            ## System bits.
            sys_bits = get_sys_bits()
            if sys_bits != 32:
                throw(WeChatClientErorr, text='python must be 32-bit')

            ## WeChat client.
            if not self.check_wechat_exe():
                self.start_wechat_exe()
                sleep(1)

            # Inject.
            self.inject_hook()
            print('Inject WeChat hook successfully.')

            # Login.
            if not self._logined:
                print('Waiting to log in to WeChat...')
            wait(
                lambda : self._logined,
                _interval=0.1
            )
            print('Login WeChat client successfully.')

            # Initialize.
            self.init_hook()
            wait(
                lambda : self._initialized,
                _interval=0.1,
                _timeout=10
            )
            print('WeChat client is ready.')

    def inject_hook(self) -> None:
        """
        Inject WeChat client hook.
        """

        # Callback.
        def callback(_, request_type: int, request_data: dict[str, str | int]) -> None:
            """
            Callback function.

            Parameters
            ----------
            request_type : Hook request type.
            request_data : Hook request data.
            """

            # Handle.
            if request_type == 11024:
                self.hook_pid = request_data['pid']
                self._injected = True
            elif request_type == 11025:
                {
                    "account": "reyhelper",
                    "avatar": "http://wx.qlogo.cn/mmhead/ver_1/54EF5gBQsGTnj2CbibckfZDViauBT2iaCN6ibiayM34BSIib883tj7n24dZV5BibickTPuWZGyB9uB3D7t8OGR8sVPTsBWFw6Epapo28RNibVJtYYvd4rIQfIaUM16l3v0QnAibYgr/0",
                    "device_id": "W449f2f0f2e24ca9c93f0b4413a0d5d59",
                    "is_fake_device_id": 0,
                    "nickname": "小助手",
                    "phone": "19916794650",
                    "pid": 3564,
                    "unread_msg_count": 0,
                    "wx_user_dir": "C:\\Users\\Administrator\\xwechat_files\\wxid_6w5hv65m6l6622_393f",
                    "wxid": "wxid_6w5hv65m6l6622",
                }
                self.login_info = {
                    'id': request_data['wxid'],
                    'account': request_data['account'],
                    'name': request_data['nickname'],
                    'phone': request_data.get('phone') or None,
                    'head_image': request_data.get('avatar') or None,
                    'file_dir': request_data['wx_user_dir']
                }
                self._logined = True
            elif request_type == 11228:
                self._initialized = True

            # Queue.
            self.queue.put({'type': request_type, 'data': request_data})

        # Inject.
        self.hook.register_callback(callback)
        self.hook.start()
        wait(
            lambda : self._injected,
            _interval=0.1,
            _timeout=10
        )

    def init_hook(self) -> None:
        """
        Initialize hook.
        """

        # CDN.
        self.send(11228)

    def popup_select_wechat_exe(self) -> str:
        """
        Pop up WeChat execute file select box.

        Returns
        -------
        WeChat execute file path.
        """

        # Pop up.
        wechat_exe_path = popup_select(
            'file',
            '请选择微信客户端',
            filter_file=[('微信客户端', '*.exe')]
        )

        # Judge.
        if wechat_exe_path is None:
            throw(WeChatClientErorr, text='WeChat execute file not selected')

        return wechat_exe_path

    def start_wechat_exe(self) -> None:
        """
        Start WeChat execute file.
        """

        # Default.
        wechat_exe_path = r'C:\Program Files\Tencent\Weixin\Weixin.exe'
        file = File(wechat_exe_path)
        if not file:
            wechat_exe_path = self.popup_select_wechat_exe()

        # Start.
        run_cmd(wechat_exe_path, True)

    def check_wechat_exe(self) -> bool:
        """
        Check if the WeChat client is started.

        Returns
        -------
        Result.
        """

        # Search.
        wechat_process_name = 'Weixin.exe'
        processes = search_process(name=wechat_process_name)

        # Check.
        if processes == []:
            return False
        else:
            return True

    def send(
        self,
        send_type: int,
        send_data: dict[str, str | int] | None = None
    ) -> None:
        """
        Send hook command.

        Parameters
        ----------
        send_type: command type.
        send_data: command data.
        """

        # Send.
        result = self.hook.send_payload(
            {
                'type': send_type,
                'data': send_data or {}
            }
        )
        if not result:
            throw(WeChatClientErorr, text='sending command hook command failed')

    def send_text(
        self,
        receive_id: str,
        text: str,
        at_id: str | list[str] | Literal['all'] | None = None
    ) -> None:
        """
        Send text message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        text : Message text.
        at_id : `@` user ID.
            - `str`: User ID.
            - `list[str]`: Multiple user IDs.
            - `Literal['all']`: `@` all room users.
        """

        # Check.
        if text == '':
            throw(ValueError, text)

        # Send.

        ## Chat room with "@".
        if (
            at_id is not None 
            and receive_id.endswith('@chatroom')
        ):
            if at_id == 'all':
                at_list = ['notify@all']
                text = '@所有人 ' + text
            elif type(at_id) is str:
                at_list = [at_id]
                text = '{$@} ' + text
            else:
                at_list = list(at_id)
                text = '{$@} ' * len(at_list) + text
            send_type = 11037
            send_data = {
                'to_wxid': receive_id,
                'content': text,
                'at_list': at_list
            }

        else:
            send_type = 11036
            send_data = {
                'to_wxid': receive_id,
                'content': text
            }
        self.send(send_type, send_data)

    def send_file(
        self,
        receive_id: str,
        file_path: str
    ) -> None:
        """
        Send file or video message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        file_path : Message file path.
        """

        # Send.

        ## Video.
        if file_path.lower().endswith(
            (
                '.mp4',
                '.mov',
                '.m4v',
                '.3gp'
            )
        ):
            send_type = 11042

        else:
            send_type = 11041
        send_data = {
            'to_wxid': receive_id,
            'file': file_path
        }
        self.send(send_type, send_data)

    def send_image(
        self,
        receive_id: str,
        file_path: str
    ) -> None:
        """
        Send image message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        file_path : Message image file path.
        """

        # Send.
        send_type = 11040
        send_data = {
            'to_wxid': receive_id,
            'file': file_path
        }
        self.send(send_type, send_data)

    def send_emotion(
        self,
        receive_id: str,
        file_path: str
    ) -> None:
        """
        Send emotion message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        file_path : Message emotion file path.
        """

        # Send.
        send_type = 11043
        send_data = {
            'to_wxid': receive_id,
            'file': file_path
        }
        self.send(send_type, send_data)

    def send_share(
        self,
        receive_id: str,
        page_url: str,
        title: str,
        text: str | None = None,
        image_url: str | None = None
    ) -> None:
        """
        Send share link message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        page_url : Control click open page URL.
        title : Control title.
        text : Control text.
        image_url : Control image URL.
        """

        # Send.
        send_type = 11039
        send_data = {
            'to_wxid': receive_id,
            'title': title,
            'desc': text or '',
            'url': page_url
        }
        if image_url is not None:
            send_data['image_url'] = image_url
        self.send(send_type, send_data)

    def send_card(
        self,
        receive_id: str,
        contact_id: str
    ) -> None:
        """
        Send contact name card message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        contact_id : Contact ID.
        """

        # Send.
        send_type = 11038
        send_data = {
            'to_wxid': receive_id,
            'card_wxid': contact_id
        }
        self.send(send_type, send_data)

    def send_forward(
        self,
        receive_id: str,
        message_id: str
    ) -> None:
        """
        Send forward message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        message_id : Message ID.
        """

        # Send.
        send_type = 11245
        send_data = {
            'to_wxid': receive_id,
            'msgid': message_id
        }
        self.send(send_type, send_data)

    def send_xml(
        self,
        receive_id: str,
        xml: str
    ) -> None:
        """
        Send `xml` format content message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        xml : `xml` format content.
        """

        # Send.
        send_type = 11113
        send_data = {
            'to_wxid': receive_id,
            'xml': xml
        }
        self.send(send_type, send_data)

    def get_contact_info(
        self,
        contact_id: str
    ) -> CallbackData:
        """
        Get contact information.
        
        Parameters
        ----------
        contact_id : Contact ID.
        
        Returns
        -------
        Contact information.
        """

        # Parameter.
        send_type = 11034
        send_data = {'wxid': contact_id}

        # Event.
        event = Event()
        key = f'{send_type}:{contact_id}'
        self._pending_callbacks[key] = {
            'event': event,
            'data': None
        }

        # Send.
        self.send(send_type, send_data)

        # Wait.
        is_set_event = event.wait(10)
        if not is_set_event:
            throw(WeChatClientErorr, text='after sending hook commmand, wait callback timeout')

        # Result.
        data: CallbackData = self._pending_callbacks[key]['data']

        return data

    def get_contact_name(
        self,
        contact_id: str
    ) -> str:
        """
        Get contact nickname, can be friend or chat room or chat room member.

        Parameters
        ----------
        contact_id : Friend or chat room ID or chat room member ID.
        
        Returns
        -------
        Contact nickname.
        """

        # Get.
        data = self.get_contact_info(contact_id)
        name: str = data['nickname']

        return name

    def get_room_info(
        self,
        room_id: str
    ) -> CallbackData:
        """
        Get chat room information.

        Parameters
        ----------
        room_id : Room ID.

        Returns
        -------
        Chat room information.
        """

        # Parameter.
        send_type = 11174
        send_data = {'wxid': room_id}

        # Event.
        event = Event()
        key = f'{send_type}:{room_id}'
        self._pending_callbacks[key] = {
            'event': event,
            'data': None
        }

        # Send.
        self.send(send_type, send_data)

        # Wait.
        is_set_event = event.wait(10)
        if not is_set_event:
            throw(WeChatClientErorr, text='after sending hook commmand, wait callback timeout')

        # Result.
        data: CallbackData = self._pending_callbacks[key]['data']

        return data

    def get_room_user_dict(
        self,
        room_id: str   
    ) -> dict[str, str]:
        """
        Get dictionary of chat room member user ID and user name.

        Parameters
        ----------
        room_id : Chat room ID.

        Returns
        -------
        Dictionary.
        """

        # Get.
        data = self.get_room_info(room_id)
        room_users: list[dict] = data['contactList'][0]['newChatroomData']['chatRoomMemberList']
        room_user_dict = {
            item['userName']: item['nickName']
            for item in room_users
        }
        
        return room_user_dict

    def download_media(
        self,
        media_type: Literal['image', 'video'],
        cdn_id: str,
        aes_key: str,
        save_path: str
    ) -> CallbackData:
        """
        Download media file.

        Parameters
        ----------
        media_type : media type.
        cdn_id : File CDN ID.
        aes_key : AES key.
        save_path : Download save path.

        Returns
        -------
        Download file information
        """

        # Parameter.
        send_type = 11230
        file_type = {
            'image': 1,
            'video': 4
        }[media_type]
        send_data = {
            'file_id': cdn_id,
            'file_type': file_type,
            'aes_key': aes_key,
            'save_path': save_path
        }

        # Event.
        event = Event()
        key = f'{send_type}:{cdn_id}'
        self._pending_callbacks[key] = {
            'event': event,
            'data': None
        }

        # Send.
        self.send(send_type, send_data)

        # Wait.
        is_set_event = event.wait(100)
        if not is_set_event:
            throw(WeChatClientErorr, text='after sending hook commmand, wait callback timeout')

        # Result.
        data: CallbackData = self._pending_callbacks[key]['data']

        return data
