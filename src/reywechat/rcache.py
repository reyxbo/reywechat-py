#!/usr/bin/env python3

"""
@Time    : 2025-08-13
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Cache module.
    Provides data caching capabilities for the WeChat client.
"""

from reykit.ros import FileStore

from .rbase import WeChatBase
from .rwechat import WeChat

__all__ = (
    'WeChatFileCache',
)

class WeChatFileCache(WeChatBase, FileStore):
    """
    WeChat file cache type.
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
        dir_path : Cache directory.
        """

        # Set attribute.
        self.wechat = wechat
        self.file_store = FileStore(dir_path)
        self.folder = self.file_store.folder
        self.index = self.file_store.index
        self.store = self.file_store.store
