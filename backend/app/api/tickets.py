"""工单路由"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.core.database import get_db
from app.models import User, Ticket, TicketStatus, TicketPriority, TicketStatusHistory
from app.schemas import (
    CreateTicketRequest,
    UpdateTicketRequest,
    AssignTicketRequest,
    ChangeStatusRequest,
    TicketResponse,
    TicketDetailResponse,
    TicketListResponse,
    UserBriefResponse,
    StatusHistoryItem,
    STATUS_TRANSITIONS
)
from app.api.deps import get_current_user
from app.services import AuditService

router = APIRouter(prefix="/tickets", tags=["工单"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    data: CreateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None
):
    """创建工单"""
    ticket_id = uuid.uuid4()
    ticket = Ticket(
        id=ticket_id.bytes,
        title=data.title,
        description=data.description,
        priority=TicketPriority(data.priority),
        status=TicketStatus.PENDING,
        creator_id=current_user.id
    )
    db.add(ticket)

    # 记录初始状态
    history = TicketStatusHistory(
        id=uuid.uuid4().bytes,
        ticket_id=ticket_id.bytes,
        from_status=None,
        to_status=TicketStatus.PENDING,
        changed_by_id=current_user.id
    )
    db.add(history)

    await db.commit()
    await db.refresh(ticket)

    # 审计日志
    client_ip = None
    user_agent = None
    if request:
        from app.api.deps import get_client_ip
        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")[:500] if request else None

    await AuditService.log(
        db=db,
        user_id=bytes(current_user.id).hex(),
        action="ticket.create",
        resource_type="ticket",
        resource_id=ticket_id.hex,
        new_value={"title": ticket.title, "status": ticket.status.value},
        ip_address=client_ip,
        user_agent=user_agent
    )

    return TicketResponse(
        id=bytes(ticket.id).hex(),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBriefResponse(id=bytes(current_user.id).hex(), username=current_user.username),
        assignee=None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取工单列表"""
    # 构建查询
    query = select(Ticket).where(Ticket.deleted_at.is_(None))
    count_query = select(func.count(Ticket.id)).where(Ticket.deleted_at.is_(None))

    # 非管理员只能看自己创建的和自己被指派的
    if current_user.role.value != "admin":
        query = query.where(
            or_(
                Ticket.creator_id == current_user.id,
                Ticket.assignee_id == current_user.id
            )
        )
        count_query = count_query.where(
            or_(
                Ticket.creator_id == current_user.id,
                Ticket.assignee_id == current_user.id
            )
        )

    # 筛选
    if status_filter:
        query = query.where(Ticket.status == TicketStatus(status_filter))
        count_query = count_query.where(Ticket.status == TicketStatus(status_filter))
    if priority:
        query = query.where(Ticket.priority == TicketPriority(priority))
        count_query = count_query.where(Ticket.priority == TicketPriority(priority))
    if assignee_id:
        assignee_id_bin = uuid.UUID(assignee_id).bytes
        query = query.where(Ticket.assignee_id == assignee_id_bin)
        count_query = count_query.where(Ticket.assignee_id == assignee_id_bin)

    # 总数
    total = (await db.execute(count_query)).scalar()

    # 分页
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Ticket.created_at.desc())
    result = await db.execute(query)
    tickets = result.scalars().all()

    # 构建响应
    items = []
    for ticket in tickets:
        creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
        creator = creator_result.scalar_one()

        assignee = None
        if ticket.assignee_id:
            assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
            assignee_user = assignee_result.scalar_one_or_none()
            if assignee_user:
                assignee = UserBriefResponse(id=bytes(assignee_user.id).hex(), username=assignee_user.username)

        items.append(TicketResponse(
            id=bytes(ticket.id).hex(),
            title=ticket.title,
            description=ticket.description,
            priority=ticket.priority.value,
            status=ticket.status.value,
            creator=UserBriefResponse(id=bytes(creator.id).hex(), username=creator.username),
            assignee=assignee,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        ))

    return TicketListResponse(items=items, total=total, page=page, limit=limit)


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取工单详情"""
    result = await db.execute(select(Ticket).where(Ticket.id == uuid.UUID(ticket_id).bytes))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role.value != "admin" and \
       ticket.creator_id != current_user.id and \
       ticket.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此工单")

    # 获取创建者
    creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
    creator = creator_result.scalar_one()

    # 获取指派人
    assignee = None
    if ticket.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
        assignee_user = assignee_result.scalar_one_or_none()
        if assignee_user:
            assignee = UserBriefResponse(id=bytes(assignee_user.id).hex(), username=assignee_user.username)

    # 获取状态历史
    history_result = await db.execute(
        select(TicketStatusHistory)
        .where(TicketStatusHistory.ticket_id == ticket.id)
        .order_by(TicketStatusHistory.created_at)
    )
    history_items = []
    for history in history_result.scalars():
        changed_by_result = await db.execute(select(User).where(User.id == history.changed_by_id))
        changed_by = changed_by_result.scalar_one()
        history_items.append(StatusHistoryItem(
            id=bytes(history.id).hex(),
            from_status=history.from_status.value if history.from_status else None,
            to_status=history.to_status.value,
            changed_by=UserBriefResponse(id=bytes(changed_by.id).hex(), username=changed_by.username),
            created_at=history.created_at
        ))

    return TicketDetailResponse(
        id=bytes(ticket.id).hex(),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBriefResponse(id=bytes(creator.id).hex(), username=creator.username),
        assignee=assignee,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        status_history=history_items
    )


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: str,
    data: UpdateTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None
):
    """更新工单"""
    result = await db.execute(select(Ticket).where(Ticket.id == uuid.UUID(ticket_id).bytes))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role.value != "admin" and \
       ticket.creator_id != current_user.id and \
       ticket.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此工单")

    # 更新字段
    old_value = {"title": ticket.title, "description": ticket.description, "priority": ticket.priority.value}
    if data.title is not None:
        ticket.title = data.title
    if data.description is not None:
        ticket.description = data.description
    if data.priority is not None:
        ticket.priority = TicketPriority(data.priority)

    await db.commit()
    await db.refresh(ticket)

    # 审计日志
    new_value = {"title": ticket.title, "description": ticket.description, "priority": ticket.priority.value}
    client_ip = None
    if request:
        from app.api.deps import get_client_ip
        client_ip = get_client_ip(request)

    await AuditService.log(
        db=db,
        user_id=bytes(current_user.id).hex(),
        action="ticket.update",
        resource_type="ticket",
        resource_id=ticket_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=client_ip
    )

    # 构建响应
    creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
    creator = creator_result.scalar_one()
    assignee = None
    if ticket.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
        assignee_user = assignee_result.scalar_one_or_none()
        if assignee_user:
            assignee = UserBriefResponse(id=bytes(assignee_user.id).hex(), username=assignee_user.username)

    return TicketResponse(
        id=bytes(ticket.id).hex(),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBriefResponse(id=bytes(creator.id).hex(), username=creator.username),
        assignee=assignee,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None
):
    """删除工单（软删除）"""
    result = await db.execute(select(Ticket).where(Ticket.id == uuid.UUID(ticket_id).bytes))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 只有创建者和管理员可以删除
    if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此工单")

    # 软删除
    ticket.deleted_at = datetime.utcnow()
    await db.commit()

    # 审计日志
    client_ip = None
    if request:
        from app.api.deps import get_client_ip
        client_ip = get_client_ip(request)

    await AuditService.log(
        db=db,
        user_id=bytes(current_user.id).hex(),
        action="ticket.delete",
        resource_type="ticket",
        resource_id=ticket_id,
        ip_address=client_ip
    )


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: str,
    data: AssignTicketRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None
):
    """指派工单"""
    result = await db.execute(select(Ticket).where(Ticket.id == uuid.UUID(ticket_id).bytes))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权指派此工单")

    # 验证指派人
    old_assignee_id = bytes(ticket.assignee_id).hex() if ticket.assignee_id else None
    if data.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == uuid.UUID(data.assignee_id).bytes))
        assignee = assignee_result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=404, detail="指派用户不存在")
        ticket.assignee_id = uuid.UUID(data.assignee_id).bytes
    else:
        ticket.assignee_id = None

    await db.commit()
    await db.refresh(ticket)

    # 审计日志
    client_ip = None
    if request:
        from app.api.deps import get_client_ip
        client_ip = get_client_ip(request)

    await AuditService.log(
        db=db,
        user_id=bytes(current_user.id).hex(),
        action="ticket.assign" if data.assignee_id else "ticket.unassign",
        resource_type="ticket",
        resource_id=ticket_id,
        old_value={"assignee_id": old_assignee_id},
        new_value={"assignee_id": data.assignee_id},
        ip_address=client_ip
    )

    # 构建响应
    creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
    creator = creator_result.scalar_one()
    assignee = None
    if ticket.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
        assignee_user = assignee_result.scalar_one_or_none()
        if assignee_user:
            assignee = UserBriefResponse(id=bytes(assignee_user.id).hex(), username=assignee_user.username)

    return TicketResponse(
        id=bytes(ticket.id).hex(),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBriefResponse(id=bytes(creator.id).hex(), username=creator.username),
        assignee=assignee,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def change_ticket_status(
    ticket_id: str,
    data: ChangeStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request=None
):
    """变更工单状态"""
    result = await db.execute(select(Ticket).where(Ticket.id == uuid.UUID(ticket_id).bytes))
    ticket = result.scalar_one_or_none()

    if not ticket or ticket.deleted_at:
        raise HTTPException(status_code=404, detail="工单不存在")

    new_status = TicketStatus(data.status)
    old_status = ticket.status

    # 状态转换验证
    allowed_transitions = STATUS_TRANSITIONS.get(old_status.value, [])
    if new_status.value not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不允许的状态转换：从 {old_status.value} 到 {new_status.value}"
        )

    # 指派人检查
    if new_status.value in ["in_progress", "pending", "resolved"]:
        if current_user.role.value != "admin" and ticket.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="只有指派人可以变更此状态")

    # closed 状态需要是创建者或管理员
    if new_status.value == "closed":
        if current_user.role.value != "admin" and ticket.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="只有创建者或管理员可以关闭工单")

    # 更新状态
    ticket.status = new_status
    if new_status == TicketStatus.CLOSED:
        ticket.closed_at = datetime.utcnow()

    await db.commit()

    # 记录状态历史
    history = TicketStatusHistory(
        id=uuid.uuid4().bytes,
        ticket_id=ticket.id,
        from_status=old_status,
        to_status=new_status,
        changed_by_id=current_user.id
    )
    db.add(history)
    await db.commit()

    # 审计日志
    client_ip = None
    if request:
        from app.api.deps import get_client_ip
        client_ip = get_client_ip(request)

    await AuditService.log(
        db=db,
        user_id=bytes(current_user.id).hex(),
        action="ticket.status_change",
        resource_type="ticket",
        resource_id=ticket_id,
        old_value={"status": old_status.value},
        new_value={"status": new_status.value},
        ip_address=client_ip
    )

    # 构建响应
    creator_result = await db.execute(select(User).where(User.id == ticket.creator_id))
    creator = creator_result.scalar_one()
    assignee = None
    if ticket.assignee_id:
        assignee_result = await db.execute(select(User).where(User.id == ticket.assignee_id))
        assignee_user = assignee_result.scalar_one_or_none()
        if assignee_user:
            assignee = UserBriefResponse(id=bytes(assignee_user.id).hex(), username=assignee_user.username)

    return TicketResponse(
        id=bytes(ticket.id).hex(),
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority.value,
        status=ticket.status.value,
        creator=UserBriefResponse(id=bytes(creator.id).hex(), username=creator.username),
        assignee=assignee,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )
