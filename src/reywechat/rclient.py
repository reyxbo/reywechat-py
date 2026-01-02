# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Client methods.
"""


from typing import Any, TypedDict, NotRequired, Literal
from os.path import dirname as os_dirname
from reykit.rbase import throw
from reykit.rnet import request as reykit_request
from reykit.ros import File, Folder
from reykit.rsys import run_cmd, search_process, popup_select
from reykit.rtime import now, wait

from .rbase import WeChatBase, WeChatClientErorr
from .rwechat import WeChat


__all__ = (
    'CLIENT_VERSION_MEMORY_OFFSETS',
    'WeChatClient',
    'simulate_client_version'
)


SendLogChat = TypedDict(
    'SendLogChat',
    {
        'id': str,
        'name': NotRequired[str],
        'time': NotRequired[str],
        'text': str
    }
)
"""
Key "id" is user ID or chat room ID.
Key "name" is user nickname.
Key "time" is second unit timestamp.
Key "text" is chat content.
"""


CLIENT_VERSION_MEMORY_OFFSETS = (
    61280212,
    61372636,
    61474056,
    61638128,
    61666264,
    61674264,
    61675784
)


class WeChatClient(WeChatBase):
    """
    WeChat client type.
    """


    def __init__(
        self,
        wechat: WeChat,
        client_port: int,
        callback_port: int
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        wechat : `WeChat` instance.
        client_port : Client control API port.
        callback_port : Message callback port.
        """

        # Build.
        self.wechat = wechat
        self.client_port = client_port
        self.callback_port = callback_port

        # Start.
        self.start()
        self.login_info = self.get_login_info()


    def start(self) -> None:
        """
        Start client control API.
        """

        # Not started.
        judge = self.check_api()
        if not judge:

            # Directory.
            wechat_dir = self.popup_select_wechat_dir()

            # Inject.
            self.create_inject_file(wechat_dir)

            # Start.
            self.start_wechat(wechat_dir)

            # Check API.
            judge = self.check_api()
            if not judge:
                raise WeChatClientErorr('start WeChat client API failed')

        # Check client login.
        judge = self.check_client_login()
        if not judge:
            print('Please login WeChat.')

            ## Wait.
            seconds = wait(
                self.check_client_login,
                _interval=0.5,
                _timeout=60,
                _raising=False
            )
            if seconds is None:
                raise WeChatClientErorr('WeChat not logged in')

        # Report.
        print(f'Start WeChat client API successfully, address is "127.0.0.1:{self.client_port}".')


    def popup_select_wechat_dir(self, default: str = 'C:/Program Files (x86)/Tencent/WeChat') -> str:
        """
        Pop up WeChat installation directory select box.

        Returns
        -------
        WeChat installation directory.
        """

        # Parameter.
        client_file_name = 'WeChat.exe'

        # Default.
        folder = Folder(default)
        if (
            Folder(default)
            and client_file_name in folder
        ):
            return default

        # Pop up.
        wechat_dir = popup_select(
            'folder',
            '请选择微信安装目录',
            default
        )

        # Judge.
        if wechat_dir is None:
            raise WeChatClientErorr('WeChat installation directory not selected')
        folder = Folder(wechat_dir)
        client_file_name = 'WeChat.exe'
        if client_file_name not in folder:
            raise WeChatClientErorr(f'WeChat installation directory has no client "{client_file_name}"')

        return wechat_dir


    def create_inject_file(self, wechat_dir: str) -> None:
        """
        Create injection files in the WeChat installation directory.

        Parameters
        ----------
        wechat_dir : WeChat installation directory.
        """

        # Create.

        ## DLL.
        dll_names = (
            'version.dll',
            'HPSocket4C.dll'
        )
        package_dir = os_dirname(__file__)
        for name in dll_names:
            dll_orig_path = f'{package_dir}/data/{name}'
            dll_copy_path = f'{wechat_dir}/{name}'
            if not File(dll_copy_path):
                File(dll_orig_path).copy(dll_copy_path)

        ## Config.
        config_path = f'{wechat_dir}/config.json'
        config_file = File(config_path)
        config = {
            'callBackUrl': f'http://127.0.0.1:{self.callback_port}/callback',
            'port': self.client_port,
            'timeOut': '3600000',
            'decryptImg': '1',
            'groupMemberEvent': '1',
            'revokeMsgEvent': '1',
            'hookSilk': '1',
            'httpMode': '1'
        }
        config_file(config)


    def start_wechat(self, wechat_dir: str) -> None:
        """
        Start
        """

        # Start.
        wechat_path = f'{wechat_dir}/WeChat.exe'
        run_cmd(wechat_path, True)


    def check_api(self) -> bool:
        """
        Check if the client API is started.
        """

        # Search.
        processes = search_process(port=self.client_port)

        # Check.
        if processes == []:
            return False
        process = processes[0]
        with process.oneshot():
            process_name = process.name()
        if process_name != 'WeChat.exe':
            return False

        return True


    def request(
        self,
        api: str,
        data: dict | None = None
    ) -> Any:
        """
        Request client API.

        Parameters
        ----------
        api : API name.
        data : Request data.

        Returns
        -------
        Client response content dictionary.
        """

        # Parameter.
        url = f'http://127.0.0.1:{self.client_port}/wechat/httpapi'
        data = data or {}
        json = {
            'type': api,
            'data': data
        }

        # Request.
        response = reykit_request(
            url,
            json=json,
            timeout=600,
            method='post',
            check=True
        )

        # Extract.
        response_json = response.json(strict=False)
        result = response_json['result']

        # Throw exception.
        if response_json['code'] != 200:
            raise WeChatClientErorr(f'client API "{api}" request failed', data, response_json)

        return result


    def check_client_login(self) -> bool:
        """
        Check if the client is logged in.

        Returns
        -------
        Check result.
        """

        # Parameter.
        api = 'getLoginStatus'

        # Request.
        result = self.request(api)

        # Check.
        status = result['status']
        judge = status == 3

        return judge


    def get_login_info(self, cache: bool = True) -> dict[
        Literal[
            'id',
            'account',
            'name',
            'phone',
            'signature',
            'city',
            'province',
            'country',
            'head_image',
            'email',
            'qq',
            'device'
        ],
        str | None
    ]:
        """
        Get login account information.

        Parameters
        ----------
        cache : Whether to use cache data.

        Returns
        -------
        Login user account information.
            - `Key 'id'`: User ID, cannot change.
            - `Key 'account'`: User account, can change.
            - `Key 'name'`: User nickname.
            - `Key 'phone'`: Phone number.
            - `Key 'signature'`: Personal signature.
            - `Key 'city'`: City.
            - `Key 'province'`: Province.
            - `Key 'country'`: Country.
            - `Key 'head_image'`: Head image URL.
            - `Key 'email'`: Email address.
            - `Key 'qq'`: QQ number.
            - `Key 'device'`: Login device.
        """

        # Parameter.
        api = 'getSelfInfo'
        data_type = ['1', '2'][cache]
        data = {'type': data_type}

        # Request.
        result = self.request(api, data)

        # Extract.
        info = {
            'id': result['wxid'],
            'account': result['wxNum'],
            'name': result['nick'],
            'phone': result['phone'],
            'signature': result['sign'],
            'city': result['city'],
            'province': result['province'],
            'country': result['country'],
            'head_image': result['avatarUrl'],
            'email': result['email'],
            'qq': result['qq'],
            'device': result['device']
        }
        for key, value in info.items():
            if value == '':
                info[key] = None

        return info


    def get_contact_table_user(self, cache: bool = True) -> list[dict[Literal['id', 'account', 'name', 'remark'], str | None]]:
        """
        Get contact chat user table.

        Parameters
        ----------
        cache : Whether to use cache data.

        Returns
        -------
        Contact table.
        """

        # Parameter.
        api = 'getFriendList'
        data_type = ['1', '2'][cache]
        data = {'type': data_type}

        # Request.
        result = self.request(api, data)

        # Extract.
        table = [
            {
                'id': item['wxid'],
                'account': item['wxNum'],
                'name': item['nick'],
                'remark': item['remark']
            }
            for item in result
        ]
        for item in table:
            for key, value in item.items():
                if value == '':
                    item[key] = None

        return table


    def get_contact_table_room(self, cache: bool = True) -> list[dict[Literal['id', 'name', 'remark'], str | None]]:
        """
        Get contact chat room table.

        Parameters
        ----------
        cache : Whether to use cache data.

        Returns
        -------
        Contact table.
        """

        # Parameter.
        api = 'getGroupList'
        data_type = ['1', '2'][cache]
        data = {'type': data_type}

        # Request.
        result = self.request(api, data)

        # Extract.
        table = [
            {
                'id': item['wxid'],
                'name': item['nick'],
                'remark': item['remark']
            }
            for item in result
        ]
        for item in table:
            for key, value in item.items():
                if value == '':
                    item[key] = None

        return table


    def get_contact_name(
        self,
        id_: str,
        cache: bool = True
    ) -> str:
        """
        Get contact name, can be friend and chat room and chat room member.

        Parameters
        ----------
        id\\_ : User ID or chat room ID.
        cache : Whether to use cache data.

        Returns
        -------
        User nickname or chat room name.
        """

        # Parameter.
        api = 'queryObj'
        data_type = ['1', '2'][cache]
        data = {
            'wxid': id_,
            'type': data_type
        }

        # Request.
        result = self.request(api, data)

        # Extract.
        name = result['nick']

        return name


    def get_room_users(
        self,
        room_id: str,
        cache: bool = True
    ) -> list[str]:
        """
        Get list of chat room user ID.

        Parameters
        ----------
        room_id : Chat room ID.
        cache : Whether to use cache data.

        Returns
        -------
        List ID.
        """

        # Parameter.
        api = 'getMemberList'
        data_type = ['1', '2'][cache]
        data = {
            'wxid': room_id,
            'type': data_type,
            'getNick': '1'
        }

        # Request.
        result = self.request(api, data)

        # Convert.
        ids = [
            item['wxid']
            for item in result
        ]

        return ids


    def get_room_user_dict(
        self,
        room_id: str,
        cache: bool = True
    ) -> dict[str, str]:
        """
        Get dictionary of chat room member user ID and user name.

        Parameters
        ----------
        room_id : Chat room ID.

        Returns
        -------
        Table.
        """

        # Parameter.
        api = 'getMemberList'
        data_type = ['1', '2'][cache]
        data = {
            'wxid': room_id,
            'type': data_type,
            'getNick': '2'
        }

        # Request.
        result = self.request(api, data)

        # Convert.
        user_dict = {
            item['wxid']: item['groupNick']
            for item in result
        }

        return user_dict


    def send_text(
        self,
        receive_id: str,
        text: str,
        at_id: str | list[str] | Literal['all'] | None = None
    ) -> list[str]:
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

        Returns
        -------
        Hook ID list.
        """

        # Check.
        if text == '':
            throw(ValueError, text)

        # Parameter.
        api = 'sendText2'
        if (
            at_id is not None
            and receive_id[-9:] != '@chatroom'
        ):
            at_id = None
        if type(at_id) == str:
            at_id = [at_id]
        if at_id is not None:
            at_text = ''.join(
                [
                    f'[@,wxid={id_},nick=,isAuto=true]'
                    for id_ in at_id
                ]
            )
            text = at_text + text
        data = {
            'wxid': receive_id,
            'msg': text
        }

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids


    def send_text_quote(
        self,
        receive_id: str,
        text: str,
        message_id: str,
        at_id: str | list[str] | Literal['all'] | None = None
    ) -> list[str]:
        """
        Send text message with quote.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        text : Message text.
        message_id : Quote message ID.
        at_id : `@` user ID.
            - `str`: User ID.
            - `list[str]`: Multiple user IDs.
            - `Literal['all']`: `@` all room users.

        Returns
        -------
        Hook ID list.
        """

        # Check.
        if text == '':
            throw(ValueError, text)

        # Parameter.
        api = 'sendReferText'
        if (
            at_id is not None
            and receive_id[-9:] != '@chatroom'
        ):
            at_id = None
        if type(at_id) == str:
            at_id = [at_id]
        if at_id is not None:
            at_text = ''.join(
                [
                    f'[@,wxid={id_},nick=,isAuto=true]'
                    for id_ in at_id
                ]
            )
            text = at_text + text
        data = {
            'wxid': receive_id,
            'msg': text,
            'msgId': message_id
        }

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids


    def send_file(
        self,
        receive_id: str,
        file_path: str
    ) -> list[str]:
        """
        Send file message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        file_path : Message file path.

        Returns
        -------
        Hook ID list.
        """

        # Parameter.
        api = 'sendFile'
        data = {
            'wxid': receive_id,
            'path': file_path
        }

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids


    def send_image(
        self,
        receive_id: str,
        file_path: str
    ) -> list[str]:
        """
        Send image message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        file_path : Message image file path.

        Returns
        -------
        Hook ID list.
        """

        # Parameter.
        api = 'sendImage'
        data = {
            'wxid': receive_id,
            'path': file_path
        }

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids


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

        # Parameter.
        api = 'sendGif'
        data = {
            'wxid': receive_id,
            'path': file_path
        }

        # Request.
        self.request(api, data)


    def send_share(
        self,
        receive_id: str,
        page_url: str,
        title: str,
        text: str,
        image_url: str | None = None
    ) -> list[str]:
        """
        Send share link message.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        page_url : Control click open page URL.
        title : Control title.
        text : Control text.
        image_url : Control image URL.

        Returns
        -------
        Hook ID list.
        """

        # Parameter.
        api = 'sendShareUrl'
        text = text or ''
        data = {
            'wxid': receive_id,
            'jumpUrl': page_url,
            'title': title,
            'content': text
        }
        if image_url is not None:
            data['path'] = image_url

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids


    def send_log(
        self,
        receive_id: str,
        chats: list[SendLogChat],
        title: str = '聊天记录'
    ) -> list[str]:
        """
        Send chat log.

        Parameters
        ----------
        receive_id : User ID or chat room ID of receive message.
        chats : Chat log table.
        title : Chat log title.

        Returns
        -------
        Hook ID list.
        """

        # Parameter.
        api = 'sendChatLog'
        timestamp = str(now('timestamp_s'))
        for chat in chats:
            chat.setdefault('name', chat['id'])
            chat.setdefault('time', timestamp)
        chat_table = [
            {
                'wxid': chat['id'],
                'nickName': chat['name'],
                'timestamp': chat['time'],
                'msg': chat['text']
            }
            for chat in chats
        ]
        data = {
            'wxid': receive_id,
            'title': title,
            'dataList': chat_table
        }

        # Request.
        result: dict = self.request(api, data)

        # Extract.
        hook_id: str = result['sendId']
        hook_ids = hook_id.split(',')

        return hook_ids
