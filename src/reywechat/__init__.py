#!/usr/bin/env python3

"""
@Time    : 2023-10-17
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : WeChat client control framework based on a WeChat client Hook program.

Modules
-------
rall : Unified export module.
    Provides convenient exports for all reyserver modules, methods, and objects.
    It allows framework functionality to be imported from a centralized module, reducing the need to import components separately from multiple modules.
rbase : Base utility module.
    Provides common methods and shared functionality used by other modules.
rcache : Cache module.
    Provides data caching capabilities for the WeChat client.
rclient : WeChat client module.
    Provides integrated methods for controlling and interacting with the WeChat client.
    This module implements WeChat client control and interaction through communication
    with the Hook program and serves as the primary module for interacting with the WeChat client.
rdb : Database module.
    Provides database record objects for WeChat-related data.
    It is used to uniformly record and manage WeChat messages, contacts, and other related data in the database.
rlog : Logging module.
    Provides logging capabilities for WeChat messages.
    It is mainly used to record received and sent WeChat messages.
rreceive : Message receiving module.
    Provides WeChat message receiving and message object processing capabilities.
    It uses a thread pool to asynchronously receive messages in batches and encapsulates received messages into unified WeChat message objects.
    The WeChat message object provides integrated processing capabilities for various message data and operations.
rsend : Message sending module.
    Provides the WeChat message sending queue and message sending objects.
    Messages are managed through a queue and sent using human-like operations to reduce risks associated with continuous and rapid operations.
rtrigger : Message trigger module.
    Provides WeChat message receiving trigger objects for invoking corresponding handlers based on received WeChat messages.
rwechat : Top-level WeChat module.
    Provides the top-level `WeChat` object of reywechat and serves as the primary entry point for using the framework.
"""

from .rwechat import WeChat as WeChat
