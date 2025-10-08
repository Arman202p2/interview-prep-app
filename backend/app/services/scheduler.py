import asyncio
from datetime import datetime, timedelta
from typing import List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.quiz import DailyQuizSchedule
from app.models.topic import UserTopic, Topic
from app.services.notification import NotificationService
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.question_service = QuestionService()
        self.is_running = False
    
    async def start(self):
        """Start the scheduler service"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting scheduler service...")
        
        # Start background tasks
        asyncio.create_task(self._daily_quiz_scheduler())
        asyncio.create_task(self._notification_processor())
    
    async def stop(self):
        """Stop the scheduler service"""
        self.is_running = False
        logger.info("Stopping scheduler service...")
    
    async def _daily_quiz_scheduler(self):
        """Schedule daily quizzes for all active users"""
        while self.is_running:
            try:
                async with AsyncSessionLocal() as db:
                    await self._create_daily_quiz_schedules(db)
                
                # Run every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in daily quiz scheduler: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _notification_processor(self):
        """Process pending notifications"""
        while self.is_running:
            try:
                async with AsyncSessionLocal() as db:
                    await self.notification_service.process_pending_notifications(db)
                
                # Run every 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Error in notification processor: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _create_daily_quiz_schedules(self, db: AsyncSession):
        """Create daily quiz schedules for users who don't have one for today"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # Get all active users
            result = await db.execute(
                select(User).where(User.is_active == True)
            )
            users = result.scalars().all()
            
            for user in users:
                # Check if user already has a quiz scheduled for today
                existing_schedule = await db.execute(
                    select(DailyQuizSchedule).where(
                        and_(
                            DailyQuizSchedule.user_id == user.id,
                            DailyQuizSchedule.scheduled_date >= today,
                            DailyQuizSchedule.scheduled_date < tomorrow
                        )
                    )
                )
                
                if existing_schedule.scalar_one_or_none():
                    continue  # User already has a quiz for today
                
                # Get user's active topics
                user_topics_result = await db.execute(
                    select(UserTopic, Topic)
                    .join(Topic, UserTopic.topic_id == Topic.id)
                    .where(
                        and_(
                            UserTopic.user_id == user.id,
                            UserTopic.is_active == True
                        )
                    )
                    .order_by(UserTopic.priority.desc())
                )
                
                user_topics = user_topics_result.all()
                
                if not user_topics:
                    continue  # User has no active topics
                
                # Select topics for today's quiz (limit to top 5 by priority)
                selected_topics = [ut.topic_id for ut, _ in user_topics[:5]]
                
                # Create daily quiz schedule
                quiz_schedule = DailyQuizSchedule(
                    user_id=user.id,
                    scheduled_date=datetime.now(),
                    topics=selected_topics,
                    questions_per_topic=1
                )
                
                db.add(quiz_schedule)
            
            await db.commit()
            logger.info(f"Created daily quiz schedules for {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error creating daily quiz schedules: {str(e)}")
            await db.rollback()
    
    async def create_user_quiz_schedule(self, user_id: int, db: AsyncSession):
        """Create a quiz schedule for a specific user"""
        try:
            today = datetime.now().date()
            
            # Check if user already has a quiz for today
            existing_schedule = await db.execute(
                select(DailyQuizSchedule).where(
                    and_(
                        DailyQuizSchedule.user_id == user_id,
                        DailyQuizSchedule.scheduled_date >= today
                    )
                )
            )
            
            if existing_schedule.scalar_one_or_none():
                return  # User already has a quiz for today
            
            # Get user's active topics
            user_topics_result = await db.execute(
                select(UserTopic)
                .where(
                    and_(
                        UserTopic.user_id == user_id,
                        UserTopic.is_active == True
                    )
                )
                .order_by(UserTopic.priority.desc())
            )
            
            user_topics = user_topics_result.scalars().all()
            
            if not user_topics:
                return  # User has no active topics
            
            # Select topics for quiz
            selected_topics = [ut.topic_id for ut in user_topics[:5]]
            
            # Create quiz schedule
            quiz_schedule = DailyQuizSchedule(
                user_id=user_id,
                scheduled_date=datetime.now(),
                topics=selected_topics,
                questions_per_topic=1
            )
            
            db.add(quiz_schedule)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error creating user quiz schedule: {str(e)}")
            await db.rollback()

# Global scheduler instance
scheduler_service = SchedulerService()

def start_scheduler():
    """Start the scheduler service"""
    asyncio.create_task(scheduler_service.start())