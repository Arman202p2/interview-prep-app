import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import json

from app.core.config import settings
from app.models.user import User
from app.models.notification import Notification, NotificationSchedule
from app.models.quiz import DailyQuizSchedule

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.firebase_app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Create credentials from environment variables
                firebase_config = {
                    "type": "service_account",
                    "project_id": settings.FIREBASE_PROJECT_ID,
                    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                    "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
                    "client_email": settings.FIREBASE_CLIENT_EMAIL,
                    "client_id": settings.FIREBASE_CLIENT_ID,
                    "auth_uri": settings.FIREBASE_AUTH_URI,
                    "token_uri": settings.FIREBASE_TOKEN_URI,
                }
                
                cred = credentials.Certificate(firebase_config)
                self.firebase_app = firebase_admin.initialize_app(cred)
            else:
                self.firebase_app = firebase_admin.get_app()
                
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            self.firebase_app = None
    
    async def send_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        fcm_token: str = None,
        data: Dict = None,
        db: AsyncSession = None
    ) -> bool:
        """Send a push notification to a user"""
        try:
            if not self.firebase_app:
                logger.error("Firebase not initialized")
                return False
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                fcm_token=fcm_token,
                data=data
            )
            
            if db:
                db.add(notification)
                await db.commit()
                await db.refresh(notification)
            
            # Send FCM notification if token is provided
            if fcm_token:
                fcm_message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message
                    ),
                    data=data or {},
                    token=fcm_token,
                    android=messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            icon="ic_notification",
                            color="#FF6B35"
                        )
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                badge=1,
                                sound="default"
                            )
                        )
                    )
                )
                
                try:
                    response = messaging.send(fcm_message)
                    logger.info(f"Successfully sent message: {response}")
                    
                    # Update notification record
                    if db:
                        notification.is_sent = True
                        notification.sent_at = datetime.utcnow()
                        notification.fcm_message_id = response
                        await db.commit()
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to send FCM message: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    async def send_quiz_reminder(
        self,
        user: User,
        fcm_token: str = None,
        db: AsyncSession = None
    ) -> bool:
        """Send a quiz reminder notification"""
        title = "📚 Time for your daily quiz!"
        message = f"Complete your quiz to stay on track with your {user.quiz_completion_goal} daily goal."
        
        data = {
            "type": "quiz_reminder",
            "action": "open_quiz",
            "user_id": str(user.id)
        }
        
        return await self.send_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type="quiz_reminder",
            fcm_token=fcm_token,
            data=data,
            db=db
        )
    
    async def send_achievement_notification(
        self,
        user: User,
        achievement: str,
        fcm_token: str = None,
        db: AsyncSession = None
    ) -> bool:
        """Send an achievement notification"""
        title = "🎉 Achievement Unlocked!"
        message = f"Congratulations! You've {achievement}"
        
        data = {
            "type": "achievement",
            "achievement": achievement,
            "user_id": str(user.id)
        }
        
        return await self.send_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type="achievement",
            fcm_token=fcm_token,
            data=data,
            db=db
        )
    
    async def setup_daily_notifications(self, user_id: int, db: AsyncSession):
        """Set up daily notification schedule for a user"""
        try:
            # Create notification schedule
            schedule = NotificationSchedule(
                user_id=user_id,
                notification_type="quiz_reminder",
                scheduled_time=datetime.now().replace(
                    hour=int(settings.DEFAULT_NOTIFICATION_TIME.split(':')[0]),
                    minute=int(settings.DEFAULT_NOTIFICATION_TIME.split(':')[1]),
                    second=0,
                    microsecond=0
                ),
                frequency="daily",
                title_template="📚 Daily Quiz Reminder",
                message_template="Time to complete your daily quiz! Stay consistent with your learning goals."
            )
            
            db.add(schedule)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error setting up daily notifications: {str(e)}")
    
    async def get_pending_notifications(self, db: AsyncSession) -> List[Dict]:
        """Get all pending notifications that need to be sent"""
        try:
            now = datetime.utcnow()
            
            # Get active notification schedules that are due
            result = await db.execute(
                select(NotificationSchedule, User)
                .join(User, NotificationSchedule.user_id == User.id)
                .where(
                    and_(
                        NotificationSchedule.is_active == True,
                        NotificationSchedule.next_send <= now,
                        User.notification_enabled == True,
                        User.is_active == True
                    )
                )
            )
            
            pending = []
            for schedule, user in result.all():
                # Check if user has completed today's quiz
                today = datetime.now().date()
                quiz_result = await db.execute(
                    select(DailyQuizSchedule)
                    .where(
                        and_(
                            DailyQuizSchedule.user_id == user.id,
                            DailyQuizSchedule.scheduled_date >= today,
                            DailyQuizSchedule.is_completed == True
                        )
                    )
                )
                
                completed_today = quiz_result.scalar_one_or_none()
                
                # Only send notification if quiz not completed
                if not completed_today:
                    pending.append({
                        "schedule": schedule,
                        "user": user,
                        "title": schedule.title_template,
                        "message": schedule.message_template
                    })
            
            return pending
            
        except Exception as e:
            logger.error(f"Error getting pending notifications: {str(e)}")
            return []
    
    async def process_pending_notifications(self, db: AsyncSession):
        """Process all pending notifications"""
        try:
            pending = await self.get_pending_notifications(db)
            
            for notification_data in pending:
                schedule = notification_data["schedule"]
                user = notification_data["user"]
                
                # Send notification (FCM token would be stored in user profile)
                success = await self.send_quiz_reminder(
                    user=user,
                    fcm_token=None,  # Would get from user profile
                    db=db
                )
                
                if success:
                    # Update schedule
                    schedule.last_sent = datetime.utcnow()
                    
                    # Calculate next send time based on frequency
                    if schedule.frequency == "daily":
                        schedule.next_send = schedule.scheduled_time + timedelta(days=1)
                    elif schedule.frequency == "weekly":
                        schedule.next_send = schedule.scheduled_time + timedelta(weeks=1)
                    elif schedule.frequency == "monthly":
                        schedule.next_send = schedule.scheduled_time + timedelta(days=30)
                    
                    await db.commit()
                    
        except Exception as e:
            logger.error(f"Error processing pending notifications: {str(e)}")
    
    async def mark_notification_read(self, notification_id: int, db: AsyncSession):
        """Mark a notification as read"""
        try:
            result = await db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
    
    async def get_user_notifications(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        db: AsyncSession = None
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            result = await db.execute(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []