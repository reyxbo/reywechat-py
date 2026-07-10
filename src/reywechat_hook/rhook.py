# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2026-07-02
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Hook methods.
"""

from typing import Any, Dict, Literal, Callable, Final
from os.path import exists as os_exists, abspath as os_abspath, split as os_split, join as os_join
from json import dumps as json_dumps, loads as json_loads
import ctypes
from reykit.rbase import throw
from reykit.rnet import listen_socket, send_socket
from reykit.rsys import get_sys_bits

__all__ = (
    'SEND_PORT',
    'RECEIVE_PORT',
    'WeChatHookLoader',
    'WeChatHook',
    'WeChatHookSocket'
)

SEND_PORT = 49152
'Listen socket port to send message.'
RECEIVE_PORT = 49153
'Send socket port to receive message.'

_path_dir: Final[str] = os_split(os_abspath(__file__))[0]
_path_helper_dll: Final[str] = os_join(_path_dir, 'Helper_4.1.2.17.dll')
_path_loader_dll: Final[str] = os_join(_path_dir, 'Loader_4.1.2.17.dll')
_socket_id: int | None = None
_recv_callback: Callable[[int, int, dict], None] | None = None
def _c_str(text: str | bytes) -> ctypes.c_char_p:
    return ctypes.c_char_p(text.encode('utf-8'))

@ctypes.WINFUNCTYPE(None, ctypes.c_void_p)
def _on_connect(client_id: int) -> None:
    """
    Called when a new WeChat socket client is connected.

    Parameters
    ----------
    client_id : Socket client ID.
    """

    # Handle.
    global _socket_id
    _socket_id = int(client_id)

@ctypes.WINFUNCTYPE(None, ctypes.c_long, ctypes.c_char_p, ctypes.c_ulong)
def _on_recv(client_id: int, data: bytes, length: int) -> None:
    """
    Called when WeChat sends a message.

    Parameters
    ----------
    client_id : Socket client ID.
    data : Raw JSON data pointer.
    length : Data length.
    """

    # Handle.
    global _recv_callback
    if not data or not _recv_callback:
        return
    try:
        raw = ctypes.string_at(data, length)
        text = raw.decode('utf-8', errors='ignore').rstrip('\x00')
        if not text:
            return
        try:
            packet = json_loads(text)
        except Exception:
            end = text.rfind('}')
            if end == -1:
                return
            packet = json_loads(text[:end + 1])
        _recv_callback(
            int(client_id),
            packet.get('type'),
            packet.get('data'),
        )
    except Exception:
        pass

@ctypes.WINFUNCTYPE(None, ctypes.c_ulong)
def _on_close(client_id: int) -> None:
    """
    Called when a socket client disconnects.

    Parameters
    ----------
    client_id : Socket client ID.
    """

    # Handle.
    global _socket_id
    if _socket_id == int(client_id):
        _socket_id = None

class WeChatHookLoader(object):
    """
    WeChat client hook loader.
    """

    OFFSET_SOCKET = 0xB080
    OFFSET_SEND = 0xAF90
    OFFSET_INJECT = 0xCC10
    OFFSET_DESTROY = 0xC540
    OFFSET_UTF8 = 0xC680

    def __init__(self) -> None:
        """
        Build instance attributes.
        """

        # Build.
        if not os_exists(_path_loader_dll):
            raise FileNotFoundError(_path_loader_dll)
        dll = ctypes.WinDLL(_path_loader_dll)
        self.base = dll._handle
        self._init_shared_memory()
        self._enable_utf8()
        self._init_socket()

    def _call(self, offset: int, argtypes: list, restype) -> ctypes._CFuncPtr:
        """
        Call function by offset.

        Parameters
        ----------
        offset : Function offset relative to the Loader.dll base address.
        argtypes : List of ctypes parameter types.
        restype : ctypes return type.

        Returns
        -------
        Callable ctypes function object.
        """

        # Function.
        func = ctypes.WINFUNCTYPE(restype, *argtypes)
        result = func(self.base + offset)

        return result

    @staticmethod
    def _init_shared_memory() -> None:
        """
        Initialize create shared memory required by Loader/Helper.
        """

        # Initialize.
        k32 = ctypes.windll.kernel32
        mapping = k32.CreateFileMappingA(
            -1, None, 0x04, 0, 33, b'windows_shell_global__'
        )
        if not mapping:
            return
        addr = k32.MapViewOfFile(mapping, 0x000F001F, 0, 0, 0)
        if not addr:
            return
        key = b'3101b223dca7715b0154924f0eeeee20'
        ctypes.memmove(addr, ctypes.create_string_buffer(key), len(key))

    def _enable_utf8(self) -> None:
        """
        Enable UTF-8 communication mode.
        """

        # Enable.
        self._call(self.OFFSET_UTF8, [], ctypes.c_bool)()

    def _init_socket(self) -> None:
        """
        Initialize socket callbacks.
        """

        # Initialize.
        self._call(
            self.OFFSET_SOCKET,
            [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p],
            ctypes.c_bool,
        )(_on_connect, _on_recv, _on_close)

    def inject(self) -> int:
        """
        Inject `DLL` file into WeChat.

        Returns
        -------
        Process ID of the injected WeChat process.
        """

        # Inject.
        process_id = self._call(
            self.OFFSET_INJECT,
            [ctypes.c_char_p],
            ctypes.c_uint32,
        )(_c_str(_path_helper_dll))

        return process_id

    def send(self, client_id: int, text: str) -> bool:
        """
        Send raw JSON message to WeChat.

        Args:
            client_id (int): socket client id
            text (str): JSON string

        Returns:
            bool: success
        """
        return self._call(
            self.OFFSET_SEND,
            [ctypes.c_uint32, ctypes.c_char_p],
            ctypes.c_bool,
        )(client_id, _c_str(text))

    def destroy(self) -> bool:
        """
        Release Loader resources.

        Returns:
            bool
        """
        return self._call(self.OFFSET_DESTROY, [], ctypes.c_bool)()

class WeChatHook(object):
    """
    WeChat hook.
    """

    def __init__(self):
        """
        Build instance attributes.
        """

        # Check System bits.
        sys_bits = get_sys_bits()
        if sys_bits != 32:
            throw(AssertionError, text='python must be 32-bit')

        # Build.
        self.loader: WeChatHookLoader | None = None

    def inject(self) -> bool:
        """
        Inject WeChat hook.

        Returns
        -------
        Whether it is successful.
        """

        # Start.
        self.loader = WeChatHookLoader()
        result = bool(self.loader.inject())

        return result

    def register_callback(
        self,
        callback: Callable[[int, int, Dict[str, Any]], None],
    ) -> None:
        """
        Register message callback.

        Parameters
        ----------
        callback : Callback function.
        """

        # Register.
        global _recv_callback
        _recv_callback = callback

    def send_payload(self, payload: Dict[str, Any]) -> bool:
        """
        Send raw protocol payload.

        Parameters
        ----------
        payload : WeChat protocol JSON.

        Returns
        -------
        Whether it is successful.
        """

        # Check.
        if not self.loader or not _socket_id:
            return False

        # Send.
        result = self.loader.send(
            _socket_id,
            json_dumps(payload, ensure_ascii=False),
        )

        return result

class WeChatHookSocket(object):
    """
    WeChat hook socket communication.
    """

    def __init__(self):
        """
        Build instance attributes.
        """

        # Build.
        self.hook = WeChatHook()

    def start(self) -> None:
        """
        Start socket, will block.
        """

        # Receive.
        self.hook.register_callback(
            lambda _, request_type, request_data: send_socket(
                '127.0.0.1',
                RECEIVE_PORT,
                {
                    'type': request_type,
                    'data': request_data
                }
            )
        )

        # Send.
        def handler(data: Literal['inject'] | Dict[str, Any]) -> None:
            if data == 'inject':
                self.hook.inject()
            else:
                self.hook.send_payload(data)
        listen_socket(
            '127.0.0.1',
            SEND_PORT,
            handler
        )
