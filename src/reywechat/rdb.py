# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-23
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Database methods.
"""

from enum import StrEnum
from reydb import rorm, Database
from reykit.rbase import throw, catch_exc
from reykit.ros import File
from reykit.rtime import now, to_time, time_to, sleep
from reykit.rwrap import wrap_thread
from reyserver.rclient import ServerClient

from .rbase import WeChatBase
from .rreceive import WeChatMessage
from .rsend import WeChatSendTypeEnum, WeChatSenderStatusEnum, WeChatSendParameters
from .rwechat import WeChat

__all__ = (
    'WeChatDatabaseSendStatusEnum',
    'DatabaseORMTableContactUser',
    'DatabaseORMTableContactRoom',
    'DatabaseORMTableContactRoomUser',
    'DatabaseORMTableMessageReceive',
    'DatabaseORMTableMessageSend',
    'WeChatDatabase'
)

class WeChatDatabaseSendStatusEnum(StrEnum):
    """
    WeChat database send status enumeration type.
    """

    WAIT = 'wait'
    'Wait send.'
    START = 'start'
    'Send stated.'
    SUCCESS = 'success'
    'Send successded.'
    FAIL = 'fail'
    'Send failed.'
    CANCEL = 'cancel'
    'Send cancelled.'

class DatabaseORMTableContactUser(rorm.Table):
    """
    Database "contact_user" table ORM model.
    """

    __name__ = 'contact_user'
    __comment__ = 'User contact table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', arg_default=now, index_n=True, comment='Record update time.')
    user_id: str = rorm.Field(rorm.types.VARCHAR(24), key=True, comment='User ID.')
    name: str = rorm.Field(rorm.types.TEXT, comment='User name.')
    is_contact: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the contact.')
    is_valid: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the valid.')

class DatabaseORMTableContactRoom(rorm.Table):
    """
    Database "contact_room" table ORM model.
    """

    __name__ = 'contact_room'
    __comment__ = 'Chat room contact table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', arg_default=now, index_n=True, comment='Record update time.')
    room_id: str = rorm.Field(rorm.types.VARCHAR(31), key=True, comment='Chat room ID.')
    name: str = rorm.Field(rorm.types.TEXT, comment='Chat room name.')
    is_contact: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the contact.')
    is_valid: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the valid.')

class DatabaseORMTableContactRoomUser(rorm.Table):
    """
    Database "contact_room_user" table ORM model.
    """

    __name__ = 'contact_room_user'
    __comment__ = 'Chat room user contact table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', arg_default=now, index_n=True, comment='Record update time.')
    room_id: str = rorm.Field(rorm.types.VARCHAR(31), key=True, comment='Chat room ID.')
    user_id: str = rorm.Field(rorm.types.VARCHAR(24), key=True, comment='Chat room user ID.')
    name: str = rorm.Field(rorm.types.TEXT, comment='Chat room user name.')
    is_contact: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the contact.')
    is_valid: bool = rorm.Field(field_default='TRUE', not_null=True, comment='Is the valid.')

class DatabaseORMTableMessageReceive(rorm.Table):
    """
    Database "message_receive" table ORM model.
    """

    __name__ = 'message_receive'
    __comment__ = 'Message receive table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    message_time: rorm.Datetime = rorm.Field(not_null=True, index_n=True, comment='Message time.')
    message_id: int = rorm.Field(rorm.types.BIGINT, key=True, comment='Message ID.')
    room_id: str = rorm.Field(rorm.types.VARCHAR(31), index_n=True, comment='Message chat room ID, null for private chat.')
    user_id: str = rorm.Field(rorm.types.VARCHAR(24), index_n=True, comment='Message sender user ID, null for system message.')
    type: int = rorm.Field(
        rorm.types.SMALLINT,
        not_null=True,
        comment=(
            'Message type, '
            '1 is text message, '
            '3 is image message, '
            '34 is voice message, '
            '37 is new friend invitation message, '
            '42 is business card message, '
            '43 is video message, '
            '47 is emoticon message, '
            '48 is position message, '
            '49 is share message ('
                'data type, '
                '1 is pure link text, '
                '6 is other side upload file completed, '
                '17 is initiate real time location, '
                '19 or 40 is forward, '
                '33 is mini program, '
                '51 is video channel, '
                '57 is quote, '
                '74 is other side start uploading file, '
                '2000 is transfer money, '
                'include "<appname>[^<>]+</appname>" is app, '
                'other omit'
            '), '
            '50 is voice call or video call invitation message, '
            '51 is system synchronize data message, '
            '56 is real time position data message, '
            '10000 is text system message, '
            '10002 is system message ('
                'date type, '
                '"pat" is pat, '
                '"revokemsg" is recall, '
                '"paymsg" is transfer money tip, '
                'other omit'
            '), '
            'other omit.'
        )
    )
    data: str = rorm.Field(rorm.types.TEXT, not_null=True, comment='Message data.')
    file_id: int = rorm.Field(comment='Message file ID, from the file API.')

class DatabaseORMTableMessageSend(rorm.Table):
    """
    Database "message_send" table ORM model.
    """

    __name__ = 'message_send'
    __comment__ = 'Message send table.'
    create_time: rorm.Datetime = rorm.Field(field_default=':time', not_null=True, index_n=True, comment='Record create time.')
    update_time: rorm.Datetime = rorm.Field(field_default=':time', arg_default=now, index_n=True, comment='Record update time.')
    send_id: int = rorm.Field(key_auto=True, comment='Send ID.')
    hook_id: int = rorm.Field(rorm.types.ARRAY(rorm.types.CHAR(32)), comment='Multiple hook UUID (multiple messages may be sent).')
    message_id: int = rorm.Field(rorm.types.BIGINT, comment='Message UUID.')
    status: int = rorm.Field(rorm.ENUM(WeChatDatabaseSendStatusEnum), field_default=WeChatDatabaseSendStatusEnum.WAIT, not_null=True, comment='Send status.')
    type: int = rorm.Field(rorm.ENUM(WeChatSendTypeEnum), not_null=True, comment='Message type.')
    receive_id: str = rorm.Field(rorm.types.VARCHAR(31), not_null=True, index_n=True, comment='Receive to user ID or chat room ID.')
    parameter: str = rorm.Field(rorm.JSONB, not_null=True, comment='Send parameters.')
    file_id: int = rorm.Field(comment='Message file ID, from the file API.')

class WeChatDatabase(WeChatBase):
    """
    WeChat database type.
    Can create database used "self.build_db" method.
    """

    def __init__(
        self,
        wechat: WeChat,
        db: Database,
        sclient: ServerClient
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        wechat : "WeChatClient" instance.
        db : Database. Note: must include database engine of "wechat" name.
        sclient : Server client.
        """

        # Build attribute.
        self.wechat = wechat
        self.db = db
        self.sclient = sclient

        # Build Database.
        self.build_db()

        # Add handler.
        self.__add_receiver_handler_to_contact_user()
        self.__add_receiver_handler_to_contact_room()
        self.__add_receiver_handler_to_contact_room_user()
        self.__add_receiver_handler_to_message_receive()
        self.__add_sender_handler_update_send_status()

        # Loop.
        self.__start_from_message_send()

    def build_db(self) -> None:
        """
        Check and build database tables.
        """

        # Check.
        if 'wechat' not in self.db:
            throw(ValueError, self.db)

        # Parameter.

        ## Table.
        tables = [
            DatabaseORMTableContactUser,
            DatabaseORMTableContactRoom,
            DatabaseORMTableContactRoomUser,
            DatabaseORMTableMessageReceive,
            DatabaseORMTableMessageSend
        ]

        ## View stats.
        views_stats = [
            {
                'table': 'stats',
                'items': [
                    {
                        'name': 'receive_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_receive"'
                        ),
                        'comment': 'Message receive count.'
                    },
                    {
                        'name': 'send_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_send"\n'
                            f'WHERE "status" = \'{WeChatDatabaseSendStatusEnum.SUCCESS}\''
                        ),
                        'comment': 'Message send count.'
                    },
                    {
                        'name': 'user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_user"'
                        ),
                        'comment': 'Contact user count.'
                    },
                    {
                        'name': 'room_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room"'
                        ),
                        'comment': 'Contact room count.'
                    },
                    {
                        'name': 'room_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room_user"'
                        ),
                        'comment': 'Contact room user count.'
                    },
                    {
                        'name': 'past_day_receive_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_receive"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Message receive count in the past day.'
                    },
                    {
                        'name': 'past_day_send_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_send"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Message send count in the past day.'
                    },
                    {
                        'name': 'past_day_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Contact user count in the past day.'
                    },
                    {
                        'name': 'past_day_room_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Contact room count in the past day.'
                    },
                    {
                        'name': 'past_day_room_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") = 0'
                        ),
                        'comment': 'Contact room user count in the past day.'
                    },
                    {
                        'name': 'past_week_receive_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_receive"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Message receive count in the past week.'
                    },
                    {
                        'name': 'past_week_send_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_send"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Message send count in the past week.'
                    },
                    {
                        'name': 'past_week_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Contact user count in the past week.'
                    },
                    {
                        'name': 'past_week_room_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Contact room count in the past week.'
                    },
                    {
                        'name': 'past_week_room_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 6'
                        ),
                        'comment': 'Contact room user count in the past week.'
                    },
                    {
                        'name': 'past_month_receive_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_receive"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Message receive count in the past month.'
                    },
                    {
                        'name': 'past_month_send_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "message_send"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Message send count in the past month.'
                    },
                    {
                        'name': 'past_month_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Contact user count in the past month.'
                    },
                    {
                        'name': 'past_month_room_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Contact room count in the past month.'
                    },
                    {
                        'name': 'past_month_room_user_count',
                        'select': (
                            'SELECT COUNT(1)\n'
                            'FROM "contact_room_user"'
                            'WHERE DATE_PART(\'day\', NOW() - "create_time") <= 29'
                        ),
                        'comment': 'Contact room user count in the past month.'
                    },
                    {
                        'name': 'receive_last_time',
                        'select': (
                            'SELECT MAX("message_time")\n'
                            'FROM "message_receive"'
                        ),
                        'comment': 'Message last receive time.'
                    },
                    {
                        'name': 'send_last_time',
                        'select': (
                            'SELECT MAX("update_time")\n'
                            'FROM "message_send"\n'
                            f'WHERE "status" = \'{WeChatDatabaseSendStatusEnum.SUCCESS}\''
                        ),
                        'comment': 'Message last send time.'
                    }
                ]
            }
        ]

        # Build.

        ## WeChat.
        self.db.wechat.build.build(tables=tables, views_stats=views_stats, skip=True)

        # Update.
        self.update_contact_user()
        self.update_contact_room()
        self.update_contact_room_user()

    def update_contact_user(self) -> None:
        """
        Update table "contact_user".
        """

        # Get data.
        contact_table = self.wechat.client.get_contact_table_user()
        user_data = [
            {
                'user_id': row['id'],
                'name': row['name']
            }
            for row in contact_table
        ]
        user_ids = [
            row['id']
            for row in contact_table
        ]

        # Insert and update.
        conn = self.db.wechat.connect()

        ## Insert.
        if contact_table != []:
            conn.execute.insert(
                'contact_user',
                user_data,
                'user_id',
                'update',
                update_time=':NOW()'
            )

        ## Update.
        if user_ids == []:
            sql = (
                'UPDATE "contact_user"\n'
                'SET "is_contact" = FALSE'
            )
        else:
            sql = (
                'UPDATE "contact_user"\n'
                'SET "is_contact" = FALSE\n'
                'WHERE "user_id" NOT IN :user_ids'
            )
        conn.execute(
            sql,
            user_ids=user_ids
        )

        ## Commit.
        conn.commit()

        ## Close.
        conn.close()

    def update_contact_room(self) -> None:
        """
        Update table "contact_room".
        """

        # Get data.
        contact_table = self.wechat.client.get_contact_table_room()
        room_data = [
            {
                'room_id': row['id'],
                'name': row['name']
            }
            for row in contact_table
        ]
        room_ids = [
            row['id']
            for row in contact_table
        ]

        # Insert and update.
        conn = self.db.wechat.connect()

        ## Insert.
        if contact_table != []:
            conn.execute.insert(
                'contact_room',
                room_data,
                'room_id',
                'update',
                update_time=':NOW()'
            )

        ## Update.
        if room_ids == []:
            sql = (
                'UPDATE "contact_room"\n'
                'SET "is_contact" = FALSE'
            )
        else:
            sql = (
                'UPDATE "contact_room"\n'
                'SET "is_contact" = FALSE\n'
                'WHERE "room_id" NOT IN :room_ids'
            )
        conn.execute(
            sql,
            room_ids=room_ids
        )

        ## Commit.
        conn.commit()

        ## Close.
        conn.close()

    def update_contact_room_user(
        self,
        room_id: str | None = None
    ) -> None:
        """
        Update table "contact_room_user".

        Parameters
        ----------
        room_id : Chat room ID.
            - "None": Update all chat room.
            - "str": Update this chat room.
        """

        # Get data.

        ## All.
        if room_id is None:
            contact_table = self.wechat.client.get_contact_table_room()

        ## Given.
        else:
            contact_table = [{'id': room_id}]

        room_user_data = [
            {
                'room_id': row['id'],
                'user_id': user_id,
                'name': name
            }
            for row in contact_table
            for user_id, name
            in self.wechat.client.get_room_user_dict(row['id']).items()
        ]
        room_user_ids = [
            '%s,%s' % (
                row['room_id'],
                row['user_id']
            )
            for row in room_user_data
        ]

        # Insert and update.
        conn = self.db.wechat.connect()

        ## Insert.
        if room_user_data != []:
            conn.execute.insert(
                'contact_room_user',
                room_user_data,
                ('room_id', 'user_id'),
                'update',
                update_time=':NOW()'
            )

        ## Update.
        if room_user_ids == []:
            sql = (
                'UPDATE "contact_room_user"\n'
                'SET "is_contact" = FALSE'
            )
        elif room_id is None:
            sql = (
                'UPDATE "contact_room_user"\n'
                'SET "is_contact" = FALSE\n'
                'WHERE CONCAT("room_id", \',\', "user_id") NOT IN :room_user_ids'
            )
        else:
            sql = (
                'UPDATE "contact_room_user"\n'
                'SET "is_contact" = FALSE\n'
                'WHERE (\n'
                '    "room_id" = :room_id\n'
                '    AND CONCAT("room_id", \',\', "user_id") NOT IN :room_user_ids\n'
                ')'
            )
        conn.execute(
            sql,
            room_user_ids=room_user_ids,
            room_id=room_id
        )

        ## Commit.
        conn.commit()

        ## Close.
        conn.close()

    def update_message_send(
        self,
        hook_id: list[str],
        message_id: int
    ) -> None:
        """
        Update table "message_send" by hook ID.

        Parameters
        ----------
        hook_id : Hook ID.
        message_id : Message ID.
        """

        # Check.
        if not hook_id:
            throw(ValueError, hook_id)

        # Update.
        sql = (
            'UPDATE "message_send"\n'
            'SET "message_id" = :message_id\n'
            'WHERE :hook_id = ANY("hook_id")'
        )
        self.db.wechat.execute(
            sql,
            message_id=message_id,
            hook_id=hook_id
        )

    def __add_receiver_handler_to_contact_user(self) -> None:
        """
        Add receiver handler, write record to table "contact_user".
        """

        def receiver_handler_to_contact_user(message: WeChatMessage) -> None:
            """
            Write record to table "contact_user".

            Parameters
            ----------
            message : "WeChatMessage" instance.
            """

            # Add friend.
            if message.is_new_user:

                ## Generate data.
                name = self.wechat.client.get_contact_name(message.user)
                data = {
                    'user_id': message.user,
                    'name': name
                }

                ## Insert.
                self.db.wechat.execute.insert(
                    'contact_user',
                    data,
                    'user_id',
                    'update',
                    update_time=':NOW()'
                )

        # Add handler.
        self.wechat.receiver.add_handler(receiver_handler_to_contact_user)

    def __add_receiver_handler_to_contact_room(self) -> None:
        """
        Add receiver handler, write record to table "contact_room".
        """

        def receiver_handler_to_contact_room(message: WeChatMessage) -> None:
            """
            Write record to table "contact_room".

            Parameters
            ----------
            message : "WeChatMessage" instance.
            """

            # Invite.
            if message.is_new_room:

                ## Generate data.
                name = self.wechat.client.get_contact_name(message.room)
                data = {
                    'room_id': message.room,
                    'name': name
                }

                ## Insert.

                ### 'contact_room'.
                self.db.wechat.execute.insert(
                    'contact_room',
                    data,
                    'room_id',
                    'update',
                    update_time=':NOW()'
                )

                ### 'contact_room_user'.
                self.update_contact_room_user(message.room)

            # Modify room name.
            elif message.is_change_room_name:

                ## Generate data.
                _, name = message.data.rsplit('“', 1)
                name = name[:-1]
                data = {
                    'room_id': message.room,
                    'update_time': ':NOW()',
                    'name': name
                }

                ## Update.
                self.db.wechat.execute.update(
                    'contact_room',
                    data
                )

            elif (

                # Kick out.
                message.is_kick_out_room

                # Dissolve.
                or message.is_dissolve_room
            ):

                ## Generate data.
                data = {
                    'room_id': message.room,
                    'update_time': ':NOW()',
                    'is_contact': False
                }

                ## Update.
                self.db.wechat.execute.update(
                    'contact_room',
                    data
                )

        # Add handler.
        self.wechat.receiver.add_handler(receiver_handler_to_contact_room)

    def __add_receiver_handler_to_contact_room_user(self) -> None:
        """
        Add receiver handler, write record to table "contact_room_user".
        """

        def receiver_handler_to_contact_room_user(message: WeChatMessage) -> None:
            """
            Write record to table "contact_room_user".

            Parameters
            ----------
            message : "WeChatMessage" instance.
            """

            # Add memeber.
            if message.is_new_room_user:

                ## Sleep.
                sleep(1)

                ## Insert.
                self.update_contact_room_user(message.room)

        # Add handler.
        self.wechat.receiver.add_handler(receiver_handler_to_contact_room_user)

    def __add_receiver_handler_to_message_receive(self) -> None:
        """
        Add receiver handler, write record to table "message_receive".
        """

        def receiver_handler_to_message_receive(message: WeChatMessage) -> None:
            """
            Write record to table "message_receive".

            Parameters
            ----------
            message : "WeChatMessage" instance.
            """

            # Upload file.
            if message.file is None:
                file_id = None
            else:
                file_id = self.sclient.upload_file(
                    message.file['path'],
                    message.file['name'],
                    'WeChat'
                )

            # Generate data.
            message_time_obj = to_time(message.time)
            message_time_str = time_to(message_time_obj)
            data = {
                'message_time': message_time_str,
                'message_id': message.id,
                'room_id': message.room,
                'user_id': message.user,
                'type': message.type,
                'data': message.data,
                'file_id': file_id
            }

            # Insert.
            self.db.wechat.execute.insert(
                'message_receive',
                data,
                'message_id'
            )

        # Add handler.
        self.wechat.receiver.add_handler(receiver_handler_to_message_receive)

    def __add_sender_handler_update_send_status(self) -> None:
        """
        Add sender handler, update field "status" of table "message_send".
        """

        def sender_handler_update_send_status(send_params: WeChatSendParameters) -> None:
            """
            Update field "status" of table "message_send".

            Parameters
            ----------
            send_params : "WeChatSendParameters" instance.
            """

            # Check.
            if send_params.status != WeChatSenderStatusEnum.SENT:
                return

            # Parameter.
            if send_params.exc_reports == []:
                status = WeChatDatabaseSendStatusEnum.SUCCESS
            else:
                status = WeChatDatabaseSendStatusEnum.FAIL
            hook_id = send_params.hook_id and tuple(send_params.hook_id)
            data = {
                'send_id': send_params.send_id,
                'update_time': ':NOW()',
                'hook_id': hook_id,
                'status': status
            }

            # Update.
            self.db.wechat.execute.update(
                'message_send',
                data
            )

        # Add handler.
        self.wechat.sender.add_handler(sender_handler_update_send_status)

    def __download_file(
        self,
        file_id: int
    ) -> tuple[str, str]:
        """
        Download file by ID.

        Parameters
        ----------
        file_id : File ID.

        Returns
        -------
        File save path and file name.
        """

        # Information.
        file_info = self.sclient.get_file_info(file_id)
        file_md5 = file_info['md5']
        file_name = file_info['name']

        # Cache.
        cache_path = self.wechat.cache.index(file_md5, file_name, True)

        ## Download.
        if cache_path is None:
            file_bytes = self.sclient.download_file(file_id)
            cache_path = self.wechat.cache.store(file_bytes, file_name)

        return cache_path, file_name

    @wrap_thread
    def __start_from_message_send(self) -> None:
        """
        Start loop read record from table "message_send", put send queue.
        """

        def __from_message_send() -> None:
            """
            Read record from table "message_send", put send queue.
            """

            # Parameter.
            conn = self.db.wechat.connect()

            # Read.
            where = f'"status" = \'{WeChatDatabaseSendStatusEnum.WAIT}\''
            result = conn.execute.select(
                'message_send',
                ['send_id', 'type', 'receive_id', 'parameter', 'file_id'],
                where,
                order='"send_id"'
            )

            # Convert.
            if result.empty:
                conn.close()
                return
            table = result.to_table()

            # Update.
            send_ids = [
                row['send_id']
                for row in table
            ]
            sql = (
                'UPDATE "message_send"\n'
                f'SET "status" = \'{WeChatDatabaseSendStatusEnum.START}\'\n'
                'WHERE "send_id" IN :send_ids'
            )
            conn.execute(
                sql,
                send_ids=send_ids
            )

            # Send.
            for row in table:
                send_id, type_, receive_id, parameter, file_id = row.values()
                send_type = WeChatSendTypeEnum(type_)

                ## File.
                if file_id is not None:
                    try:
                        file_path, file_name = self.__download_file(file_id)
                    except:
                        exc_text, *_ = catch_exc()
                        print(exc_text)
                        continue
                    parameter['file_path'] = file_path
                    parameter['file_name'] = file_name

                send_params = WeChatSendParameters(
                    self.wechat.sender,
                    send_type,
                    receive_id,
                    send_id,
                    **parameter
                )
                send_params.status = WeChatSenderStatusEnum.WAIT
                self.wechat.sender.queue.put(send_params)

            # Commit.
            conn.commit()

        # Loop.
        while True:

            # Put.
            __from_message_send()

            # Wait.
            sleep(1)

    def is_valid(
        self,
        message: WeChatMessage
    ) -> bool:
        """
        Judge if is valid user or chat room from database.

        Parameters
        ----------
        message : "WeChatMessage" instance.

        Returns
        -------
        Judgment result.
            - "True": Valid.
            - "False": Invalid or no record.
        """

        # Judge.

        ## User.
        if message.room is None:
            result = message.receiver.wechat.db.db.wechat.execute.select(
                'contact_user',
                ['is_valid'],
                '"user_id" = :user_id',
                limit=1,
                user_id=message.user
            )

        ## Room.
        elif message.user is None:
            result = message.receiver.wechat.db.db.wechat.execute.select(
                'contact_room',
                ['is_valid'],
                '"room_id" = :room_id',
                limit=1,
                room_id=message.room
            )

        ## Room user.
        else:
            sql = (
            'SELECT (\n'
            '    SELECT "is_valid"\n'
            '    FROM "contact_room_user"\n'
            '    WHERE "room_id" = :room_id AND "user_id" = :user_id\n'
            '    LIMIT 1\n'
            ') AS "is_valid"\n'
            'FROM (\n'
            '    SELECT "is_valid"\n'
            '    FROM "contact_room"\n'
            '    WHERE "room_id" = :room_id\n'
            '    LIMIT 1\n'
            ') AS "a"\n'
            'WHERE "is_valid" = TRUE'
            )
            result = message.receiver.wechat.db.db.wechat.execute(
                sql,
                room_id=message.room,
                user_id=message.user
            )

        judge = result.scalar()

        return judge

    def _insert_send(self, send_params: WeChatSendParameters) -> None:
        """
        Insert into "wechat.message_send" table of database, wait send.

        Parameters
        ----------
        send_params : "WeChatSendParameters" instance.
        """

        # Parameter.
        params = send_params.params.copy()
        data = {
            'type': send_params.send_type,
            'receive_id': send_params.receive_id,
            'parameter': params
        }

        # Upload file.
        if 'file_path' in params:
            file_path: str = params.pop('file_path')
            if 'file_name' in params:
                file_name: str = params.pop('file_name')
            else:
                file = File(file_path)
                file_name = file.name_suffix

            ## Cache.
            cache_path = self.wechat.cache.store(file_path, file_name)

            file_id = self.sclient.upload_file(
                cache_path,
                file_name,
                'WeChat'
            )
        elif 'file_id' in params:
            file_id = params['file_id']
        else:
            file_id = None
        data['file_id'] = file_id

        # Insert.
        self.db.wechat.execute.insert(
            'message_send',
            data
        )
