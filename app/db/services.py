from sqlmodel import Session, select
from app.db.models import Conversation, Message
from typing import List, Optional, Dict, Any
import logging
import datetime
import json
import uuid
from app.db.database import get_session

logger = logging.getLogger(__name__)


class ConversationService:
    """Service to handle conversations and messages."""

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    async def create_conversation(user_id: str, title: Optional[str] = None, meta_data: Dict = None) -> str:
        """
        Tạo cuộc trò chuyện mới
        
        Args:
            user_id: ID người dùng
            title: Tiêu đề cuộc trò chuyện
            meta_data: Thông tin metadata
            
        Returns:
            str: ID của cuộc trò chuyện mới
        """
        conversation_id = str(uuid.uuid4())
        
        meta_data_str = "{}"
        if meta_data:
            try:
                meta_data_str = json.dumps(meta_data)
            except:
                meta_data_str = "{}"
        
        db_generator = get_session()
        db = next(db_generator)
        try:
            new_conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title,
                meta_data=meta_data_str
            )
            db.add(new_conversation)
            db.commit()
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
        finally:
            db.close()

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        return self.session.exec(query).first()

    def get_conversation_by_user(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        query = select(Conversation).where(Conversation.user_id == user_id)
        return self.session.exec(query).all()

    @staticmethod
    async def add_message(conversation_id: str, role: str, content: str, meta_data: Dict = None) -> str:
        """
        Thêm tin nhắn vào cuộc trò chuyện
        
        Args:
            conversation_id: ID cuộc trò chuyện
            role: Vai trò của người gửi (user/assistant)
            content: Nội dung tin nhắn
            meta_data: Thông tin metadata
            
        Returns:
            str: ID của tin nhắn mới
        """
        message_id = str(uuid.uuid4())
        
        # Hạn chế độ dài của nội dung nếu quá lớn
        if content and len(content) > 10000:
            logger.warning(f"Message content too long ({len(content)} chars), truncating...")
            content = content[:10000] + "... (truncated)"
        
        meta_data_str = "{}"
        if meta_data:
            try:
                meta_data_str = json.dumps(meta_data)
                # Hạn chế độ dài của metadata nếu quá lớn
                if len(meta_data_str) > 10000:
                    logger.warning(f"Message meta_data too long ({len(meta_data_str)} chars), truncating...")
                    meta_data_str = meta_data_str[:10000] + "... (truncated)"
            except:
                meta_data_str = "{}"
        
        db_generator = get_session()
        db = next(db_generator)
        try:
            new_message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                meta_data=meta_data_str
            )
            db.add(new_message)
            db.commit()
            logger.info(f"Added message {message_id} to conversation {conversation_id}")
            return message_id
        finally:
            db.close()

    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a conversation, ordered by created_at."""
        query = select(Message) \
            .where(Message.conversation_id == conversation_id) \
            .order_by(Message.created_at.asc()) \
            .limit(limit)
        return self.session.exec(query).all()

    @staticmethod
    async def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử cuộc trò chuyện
        
        Args:
            conversation_id: ID cuộc trò chuyện
            
        Returns:
            List[Dict]: Danh sách tin nhắn trong cuộc trò chuyện
        """
        db_generator = get_session()
        db = next(db_generator)
        try:
            messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
            
            history = []
            for message in messages:
                meta_data = {}
                try:
                    if message.meta_data:
                        meta_data = json.loads(message.meta_data)
                except:
                    pass
                    
                history.append({
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                    "meta_data": meta_data
                })
            
            return history
        finally:
            db.close() 