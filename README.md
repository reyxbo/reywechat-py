[中文](README_zh.md)

# reywechat

**reywechat** is a WeChat client control framework based on a WeChat client Hook program.

This package depends on the Hook program provided by **reywechat-hook**. The two programs need to run simultaneously and communicate with each other to control and interact with the WeChat client.

It provides common capabilities such as WeChat client control, message receiving, message sending, message triggers, database records, file caching, and message logging. Through a unified WeChat object and modular design, it simplifies the development of applications based on the WeChat client.

## Features

* WeChat client control based on a Hook program
* Provides a unified WeChat client object
* Supports WeChat client integration and startup
* Provides asynchronous WeChat message receiving
* Supports batch message receiving based on a thread pool
* Provides a WeChat message sending queue
* Supports queue-based message sending
* Supports human-like message sending operations
* Provides message receiving triggers
* Supports registering message handlers
* Provides unified WeChat message object processing
* Supports processing various message data such as text and files
* Supports file caching and file indexing
* Provides database records for WeChat messages and contacts
* Provides WeChat message receiving and sending logs
* Supports console logging and file logging
* Provides WeChat user and group information retrieval
* Supports WeChat file downloading
* Provides convenient message reply methods
* Provides common WeChat client control methods

---

## Installation

Requires **Python 3.12 or higher**.

```bash
pip install reywechat
```

---

## Quick Start

The basic usage is as follows:

```python
from reywechat import WeChat

wechat = WeChat(**args)

wechat.start()

wechat.keep()
```

Where:

* `WeChat`: The top-level WeChat client object provided by reywechat
* `args`: Initialization arguments for the WeChat object
* `start()`: Starts the WeChat client components, including the message receiving queue and message sending queue daemon threads
* `keep()`: Blocks the current main thread to keep the program running

The `WeChat` object provides a top-level interface for WeChat client functionality. Other module objects and methods can be used to handle message receiving, message sending, user information retrieval, file processing, and other operations.

> **Note:** reywechat depends on the Hook program provided by `reywechat-hook`. When using reywechat, the reywechat program and the Hook program must run simultaneously.

---

# Modules

reywechat is divided into multiple modules by functionality. Each module provides different capabilities for WeChat client control and message processing.

## `rall` — All import methods

**Unified import module.**

Provides convenient exports for all methods and objects in reywechat. This module allows framework functionality to be imported from a single location, reducing the need to import from multiple modules separately.

---

## `rbase` — Base methods

**Base module.**

Provides dependency methods and basic functionality shared by other modules.

It is mainly used to provide common dependencies and basic processing capabilities for other modules.

---

## `rcache` — Cache methods

**Cache module.**

Provides data caching capabilities for the WeChat client.

Main features include:

* WeChat received message file caching
* File index management
* File storage management
* Preventing duplicate file storage

The file cache object provides unified indexing and storage for files received from WeChat, reducing duplicate file storage.

---

## `rclient` — Client methods

**WeChat client module.**

Provides integrated methods for controlling and interacting with the WeChat client.

This module implements WeChat client control and interaction through communication with the Hook program and serves as the primary module for interacting with the WeChat client.

Main features include:

* WeChat client control
* Hook injection
* Message callbacks
* Various WeChat message sending methods
* User information retrieval
* Group information retrieval
* WeChat file downloading
* Other WeChat client operations

---

## `rdb` — Database methods

**Database module.**

Provides database record objects for WeChat-related data.

It is used to uniformly record and manage WeChat messages, contacts, and other related data in the database.

Main features include:

* WeChat message records
* Contact records
* Automatic data insertion
* Automatic data updates
* Automatic data deletion
* Database record objects

---

## `rlog` — Log methods

**Logging module.**

Provides logging capabilities for WeChat messages.

It is mainly used to record received and sent WeChat messages.

Main features include:

* WeChat received message logs
* WeChat sent message logs
* Console logging
* Log file recording

---

## `rreceive` — Receive methods

**Message receiving module.**

Provides WeChat message receiving and message object processing capabilities.

It uses a thread pool to asynchronously receive messages in batches and encapsulates received messages into unified WeChat message objects.

The WeChat message object provides integrated processing capabilities for various message data and operations.

Main features include:

* Asynchronous WeChat message receiving
* Batch message processing based on a thread pool
* WeChat message objects
* Message text data
* File data
* File transfer status
* XML data
* Chat window information
* Message sender information
* Other user reference information
* Message content descriptions
* Message reply methods

---

## `rsend` — Send methods

**Message sending module.**

Provides the WeChat message sending queue and message sending objects.

Messages are managed through a queue and sent using human-like operations to reduce risks associated with continuous and rapid operations.

Main features include:

* WeChat message sending queue
* Message sending parameter objects
* Various message sending methods
* Message sending status
* Queue task management
* Human-like message sending

---

## `rtrigger` — Trigger methods

**Message trigger module.**

Provides WeChat message receiving trigger objects for invoking corresponding handlers based on received WeChat messages.

Main features include:

* Message handler registration
* Received message triggering
* Message processing framework
* Asynchronous message processing coordination

The unified trigger processing framework helps reduce problems caused by directly handling asynchronous messages.

---

## `rwechat` — WeChat methods

**Top-level WeChat module.**

Provides the top-level `WeChat` object of reywechat and serves as the primary entry point for using the framework.

Main features include:

* Creating a WeChat client object
* Integrating other module functionality
* Starting the WeChat client components
* Starting the message receiving queue
* Starting the message sending queue
* Keeping the program running

Basic usage:

```python
from reywechat import WeChat

wechat = WeChat(**args)

wechat.start()

wechat.keep()
```

Here, `start()` starts the daemon threads for the message receiving queue and message sending queue, while `keep()` blocks the current main thread to keep the WeChat client program running.

---

# Module Overview

| Module     | Function                                                  |
| ---------- | --------------------------------------------------------- |
| `rwechat`  | Top-level WeChat object and component integration startup |
| `rall`     | Unified export of all methods                             |
| `rbase`    | Base methods and common dependencies                      |
| `rcache`   | WeChat file caching and file indexing                     |
| `rclient`  | WeChat client control and Hook communication              |
| `rdb`      | WeChat message and contact database records               |
| `rlog`     | WeChat message receiving and sending logs                 |
| `rreceive` | WeChat message receiving and message object processing    |
| `rsend`    | WeChat message sending queue and sending objects          |
| `rtrigger` | WeChat message receiving triggers                         |

---

# Dependencies

Main dependencies:

* `reydb`
* `reykit`
* `reyserver`

In addition, reywechat depends on the **reywechat-hook** Hook program at runtime, which needs to run simultaneously with reywechat.

---

# Project Information

| Project    | Information                                                |
| ---------- | ---------------------------------------------------------- |
| Name       | `reywechat`                                                |
| Version    | `1.1.41`                                                   |
| Python     | `>=3.12`                                                   |
| Author     | `Rey`                                                      |
| Email      | `reyxbo@163.com`                                           |
| Homepage   | [reyxbo.com](https://www.reyxbo.com/release/python/reywechat)                       |
| Repository | [reywechat-py](https://github.com/reyxbo/reywechat-py.git) |

## Keywords

`rey` · `reyxbo` · `wechat` · `robot` · `helper` · `file` · `recevie` · `send` · `client`
