# -*- coding: utf-8 -*-
"""
消息服务实现

一比一复刻参考项目 MessageServiceImpl.java
@author: continew-admin
@since: 2023/11/2 23:00
"""

from typing import Optional, List

from ..message_service import MessageService
from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp
from apps.system.core.model.resp.message_type_unread_resp import MessageTypeUnreadResp
from apps.system.core.enums.message_type_enum import MessageTypeEnum
from apps.common.websocket.websocket_manager import WebSocketUtils
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class MessageServiceImpl(MessageService):
    """
    消息服务实现

    一比一复刻参考项目 MessageServiceImpl.java
    """

    async def count_unread_by_user_id(self, user_id: int, is_detail: Optional[bool] = False) -> MessageUnreadResp:
        """
        查询用户未读消息数量

        一比一复刻: countUnreadByUserId(Long userId, Boolean isDetail)

        Args:
            user_id: 用户ID
            is_detail: 是否查询详情

        Returns:
            MessageUnreadResp: 未读消息响应
        """
        # TODO: 实现实际的数据库查询逻辑
        # 参考实现：baseMapper.selectUnreadCountByUserIdAndType(userId, messageType.getValue())
        result = MessageUnreadResp()

        if is_detail:
            # 查询各类型未读消息数量
            detail_list = []
            total = 0

            for message_type in MessageTypeEnum:
                # TODO: 从数据库查询该类型的未读数量
                # count = baseMapper.selectUnreadCountByUserIdAndType(userId, messageType.getValue())
                count = 0  # 临时模拟数据

                # 创建响应对象（使用枚举的value值）
                resp = MessageTypeUnreadResp(
                    type=message_type.value,  # 使用枚举的整数值
                    count=count
                )
                detail_list.append(resp)
                total += count

            result.details = detail_list
            result.total = total
        else:
            # 只返回总数
            # TODO: 从数据库查询总未读数量
            # total = baseMapper.selectUnreadCountByUserIdAndType(userId, null)
            result.total = 0  # 临时模拟数据

        return result

    async def read_message(self, ids: Optional[List[int]], user_id: int):
        """
        标记消息已读

        一比一复刻: readMessage(List<Long> ids, Long userId)

        参考实现：
        public void readMessage(List<Long> ids, Long userId) {
            // 查询当前用户的未读消息
            List<MessageDO> list = baseMapper.selectUnreadListByUserId(userId);
            List<Long> unreadIds = CollUtils.mapToList(list, MessageDO::getId);
            messageLogService.addWithUserId(CollUtil.isNotEmpty(ids)
                ? CollUtil.intersection(unreadIds, ids).stream().toList()
                : unreadIds, userId);
            WebSocketUtils.sendMessage(StpUtil.getTokenValueByLoginId(userId), String.valueOf(baseMapper
                .selectUnreadListByUserId(userId)
                .size()));
        }

        Args:
            ids: 消息ID列表（可选，为None时标记全部未读消息）
            user_id: 用户ID
        """
        try:
            # TODO: 实现数据库操作
            # 1. 查询当前用户的未读消息
            # unread_list = baseMapper.selectUnreadListByUserId(userId)
            # unread_ids = [msg.id for msg in unread_list]

            # 2. 标记消息为已读
            # if ids:
            #     # 取交集，只标记未读消息中的指定ID
            #     ids_to_mark = set(ids) & set(unread_ids)
            # else:
            #     # 标记全部未读消息
            #     ids_to_mark = unread_ids
            # messageLogService.addWithUserId(list(ids_to_mark), userId)

            # 3. 查询更新后的未读数量
            # TODO: 实际查询数据库
            # unread_count = baseMapper.selectUnreadListByUserId(userId).size()
            unread_count = 0  # 临时模拟数据

            # 4. 通过WebSocket推送未读数量更新 - 一比一复刻参考项目
            # WebSocketUtils.sendMessage(StpUtil.getTokenValueByLoginId(userId), String.valueOf(unread_count))
            # Python实现：通过user_id获取token，然后推送
            # TODO: 需要实现 get_token_by_user_id 方法
            # token = get_token_by_user_id(user_id)
            # WebSocketUtils.send_message(token, str(unread_count))

            logger.info(f"Message marked as read for user {user_id}, new unread count: {unread_count}")

        except Exception as e:
            logger.error(f"Failed to mark message as read for user {user_id}: {e}")
            raise

    async def add(self, title: str, content: str, message_type: str, user_id_list: Optional[List[str]] = None):
        """
        创建消息

        一比一复刻: add(MessageReq req, List<String> userIdList)

        参考实现：
        public void add(MessageReq req, List<String> userIdList) {
            MessageDO message = BeanUtil.copyProperties(req, MessageDO.class);
            message.setScope(CollUtil.isEmpty(userIdList) ? NoticeScopeEnum.ALL : NoticeScopeEnum.USER);
            message.setUsers(userIdList);
            baseMapper.insert(message);
            // 发送消息给指定在线用户
            if (CollUtil.isNotEmpty(userIdList)) {
                userIdList.parallelStream().forEach(userId -> {
                    List<String> tokenList = StpUtil.getTokenValueListByLoginId(userId);
                    tokenList.parallelStream().forEach(token -> WebSocketUtils.sendMessage(token, "1"));
                });
                return;
            }
            // 发送消息给所有在线用户
            WebSocketUtils.sendMessage("1");
        }

        Args:
            title: 消息标题
            content: 消息内容
            message_type: 消息类型
            user_id_list: 目标用户ID列表（可选，为None时发送给所有用户）
        """
        try:
            # TODO: 实现数据库操作
            # 1. 创建消息记录
            # message = MessageDO()
            # message.title = title
            # message.content = content
            # message.type = message_type
            # message.scope = NoticeScopeEnum.USER if user_id_list else NoticeScopeEnum.ALL
            # message.users = user_id_list
            # baseMapper.insert(message)

            # 2. 通过WebSocket推送通知 - 一比一复刻参考项目
            if user_id_list:
                # 发送给指定用户
                for user_id in user_id_list:
                    # TODO: 获取该用户的所有在线token
                    # token_list = StpUtil.getTokenValueListByLoginId(user_id)
                    # for token in token_list:
                    #     WebSocketUtils.send_message(token, "1")
                    pass
            else:
                # 广播给所有在线用户 - 一比一复刻参考项目
                WebSocketUtils.send_message("1")

            logger.info(f"Message created: {title}, target users: {user_id_list or 'ALL'}")

        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise

    async def page(self, query, page: int, size: int):
        """
        分页查询消息列表

        一比一复刻参考项目 MessageServiceImpl.page()
        SQL: selectMessagePage

        Args:
            query: MessageQuery查询条件
            page: 页码
            size: 页大小

        Returns:
            PageResp[MessageResp]: 分页结果
        """
        from apps.common.config.database.database_session import DatabaseSession
        from apps.common.models.page_resp import PageResp
        from apps.system.core.model.resp.message_resp import MessageResp
        from apps.system.core.model.entity.message_entity import MessageEntity
        from apps.system.core.model.entity.message_log_entity import MessageLogEntity
        from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum
        from sqlalchemy import select, func, or_, and_, desc
        from sqlalchemy.orm import aliased
        
        async with DatabaseSession.get_session_context() as session:
            # 创建别名
            t1 = aliased(MessageEntity)
            t2 = aliased(MessageLogEntity)
            
            # 基础查询
            base_query = select(
                t1.id,
                t1.title,
                t1.type,
                t1.path,
                t1.scope,
                t1.users,
                t1.create_time,
                (t2.read_time.isnot(None)).label('is_read'),
                t2.read_time.label('read_time')
            ).outerjoin(
                t2,
                and_(
                    t2.message_id == t1.id,
                    t2.user_id == query.user_id if query.user_id else None
                )
            )
            
            # 添加过滤条件
            conditions = []
            
            # 用户ID过滤（通知范围）
            if query.user_id is not None:
                conditions.append(
                    or_(
                        t1.scope == NoticeScopeEnum.ALL.value,
                        and_(
                            t1.scope == NoticeScopeEnum.USER.value,
                            func.json_extract(t1.users, '$[0]') == str(query.user_id)
                        )
                    )
                )
            
            # 标题过滤
            if query.title:
                conditions.append(t1.title.like(f'%{query.title}%'))
            
            # 类型过滤
            if query.type is not None:
                conditions.append(t1.type == query.type)
            
            # 是否已读过滤
            if query.is_read is not None:
                if query.is_read:
                    conditions.append(t2.read_time.isnot(None))
                else:
                    conditions.append(t2.read_time.is_(None))
            
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            # 排序
            base_query = base_query.order_by(desc(t1.create_time))
            
            # 查询总数
            count_query = select(func.count()).select_from(base_query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # 分页
            offset = (page - 1) * size
            base_query = base_query.offset(offset).limit(size)
            
            # 执行查询
            result = await session.execute(base_query)
            rows = result.all()
            
            # 转换为响应对象
            records = [
                MessageResp(
                    id=row.id,
                    title=row.title,
                    type=row.type,
                    path=row.path,
                    is_read=bool(row.is_read),
                    read_time=row.read_time,
                    create_time=row.create_time
                )
                for row in rows
            ]

            return PageResp(
                list=records,
                total=total,
                current=page,
                size=size,
                pages=(total + size - 1) // size if total > 0 else 0
            )
    
    async def get(self, message_id: int):
        """
        查询消息详情

        一比一复刻参考项目 MessageServiceImpl.get()
        SQL: selectMessageById

        Args:
            message_id: 消息ID

        Returns:
            MessageDetailResp: 消息详情
        """
        from apps.common.config.database.database_session import DatabaseSession
        from apps.system.core.model.resp.message_resp import MessageDetailResp
        from apps.system.core.model.entity.message_entity import MessageEntity
        from apps.system.core.model.entity.message_log_entity import MessageLogEntity
        from sqlalchemy import select, and_
        from sqlalchemy.orm import aliased
        
        async with DatabaseSession.get_session_context() as session:
            # 创建别名
            t1 = aliased(MessageEntity)
            t2 = aliased(MessageLogEntity)
            
            # 查询
            query = select(
                t1.id,
                t1.title,
                t1.content,
                t1.type,
                t1.path,
                t1.scope,
                t1.users,
                t1.create_time,
                (t2.read_time.isnot(None)).label('is_read'),
                t2.read_time.label('read_time')
            ).outerjoin(
                t2,
                t2.message_id == t1.id
            ).where(
                t1.id == message_id
            )
            
            result = await session.execute(query)
            row = result.first()
            
            if row is None:
                return None
            
            return MessageDetailResp(
                id=row.id,
                title=row.title,
                content=row.content,
                type=row.type,
                path=row.path,
                scope=row.scope,
                users=row.users.split(',') if row.users else None,
                is_read=bool(row.is_read),
                read_time=row.read_time,
                create_time=row.create_time
            )
