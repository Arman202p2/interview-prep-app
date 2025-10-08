import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import re
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ScrapedQuestion:
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    company_name: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None

class WebScraper:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            limits=httpx.Limits(max_connections=settings.MAX_CONCURRENT_REQUESTS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def scrape_page(self, url: str) -> Optional[str]:
        """Scrape a single page and return HTML content"""
        try:
            await asyncio.sleep(settings.SCRAPING_DELAY)  # Rate limiting
            response = await self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    async def scrape_tcyonline(self, topic: str) -> List[ScrapedQuestion]:
        """Scrape questions from TCYOnline"""
        questions = []
        try:
            # TCYOnline specific scraping logic
            search_url = f"https://www.tcyonline.com/search?q={topic}"
            html = await self.scrape_page(search_url)
            
            if not html:
                return questions
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find question containers (adjust selectors based on actual site structure)
            question_containers = soup.find_all('div', class_='question-container')
            
            for container in question_containers:
                try:
                    question_text = container.find('div', class_='question-text')
                    if not question_text:
                        continue
                    
                    options = []
                    option_elements = container.find_all('div', class_='option')
                    for opt in option_elements:
                        options.append(opt.get_text(strip=True))
                    
                    correct_answer = None
                    correct_element = container.find('div', class_='correct-answer')
                    if correct_element:
                        correct_answer = correct_element.get_text(strip=True)
                    
                    questions.append(ScrapedQuestion(
                        question_text=question_text.get_text(strip=True),
                        options=options if options else None,
                        correct_answer=correct_answer,
                        source_url=search_url,
                        source_name="TCYOnline",
                        topic=topic,
                        difficulty="medium"
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing question from TCYOnline: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping TCYOnline for topic {topic}: {str(e)}")
        
        return questions
    
    async def scrape_prepinsta(self, topic: str) -> List[ScrapedQuestion]:
        """Scrape questions from PrepInsta"""
        questions = []
        try:
            # PrepInsta specific scraping logic
            topic_slug = topic.lower().replace(' ', '-')
            search_url = f"https://prepinsta.com/{topic_slug}-questions"
            html = await self.scrape_page(search_url)
            
            if not html:
                return questions
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find question containers
            question_containers = soup.find_all('div', class_='mcq-question')
            
            for container in question_containers:
                try:
                    question_text = container.find('p', class_='question')
                    if not question_text:
                        continue
                    
                    options = []
                    option_elements = container.find_all('li', class_='option')
                    for opt in option_elements:
                        options.append(opt.get_text(strip=True))
                    
                    # Look for answer explanation
                    answer_element = container.find('div', class_='answer')
                    correct_answer = None
                    if answer_element:
                        correct_answer = answer_element.get_text(strip=True)
                    
                    questions.append(ScrapedQuestion(
                        question_text=question_text.get_text(strip=True),
                        options=options if options else None,
                        correct_answer=correct_answer,
                        source_url=search_url,
                        source_name="PrepInsta",
                        topic=topic,
                        difficulty="medium"
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing question from PrepInsta: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping PrepInsta for topic {topic}: {str(e)}")
        
        return questions
    
    async def scrape_indiabix(self, topic: str) -> List[ScrapedQuestion]:
        """Scrape questions from IndiaBIX"""
        questions = []
        try:
            # IndiaBIX specific scraping logic
            topic_slug = topic.lower().replace(' ', '-')
            search_url = f"https://www.indiabix.com/{topic_slug}/questions-and-answers"
            html = await self.scrape_page(search_url)
            
            if not html:
                return questions
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find question containers
            question_containers = soup.find_all('div', class_='bix-div-container')
            
            for container in question_containers:
                try:
                    question_text = container.find('td', class_='bix-td-qtxt')
                    if not question_text:
                        continue
                    
                    options = []
                    option_table = container.find('table', class_='bix-tbl-options')
                    if option_table:
                        option_elements = option_table.find_all('td')
                        for opt in option_elements:
                            option_text = opt.get_text(strip=True)
                            if option_text and len(option_text) > 2:  # Filter out empty options
                                options.append(option_text)
                    
                    # Look for correct answer
                    answer_element = container.find('div', class_='bix-ans-description')
                    correct_answer = None
                    if answer_element:
                        answer_text = answer_element.get_text(strip=True)
                        # Extract answer from explanation
                        answer_match = re.search(r'Answer:\s*([A-D])', answer_text)
                        if answer_match:
                            correct_answer = answer_match.group(1)
                    
                    questions.append(ScrapedQuestion(
                        question_text=question_text.get_text(strip=True),
                        options=options if options else None,
                        correct_answer=correct_answer,
                        source_url=search_url,
                        source_name="IndiaBIX",
                        topic=topic,
                        difficulty="medium"
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing question from IndiaBIX: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping IndiaBIX for topic {topic}: {str(e)}")
        
        return questions
    
    async def scrape_reddit_interviews(self, company: str = None) -> List[ScrapedQuestion]:
        """Scrape interview questions from Reddit"""
        questions = []
        try:
            # Reddit API or web scraping for interview experiences
            subreddits = ['cscareerquestions', 'interviews', 'programming']
            
            for subreddit in subreddits:
                search_query = f"interview questions {company}" if company else "interview questions"
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q={search_query}&sort=relevance&limit=25"
                
                html = await self.scrape_page(search_url)
                if not html:
                    continue
                
                # Parse Reddit JSON response
                import json
                try:
                    data = json.loads(html)
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        url = f"https://www.reddit.com{post_data.get('permalink', '')}"
                        
                        # Extract questions from post content
                        content = f"{title} {selftext}"
                        extracted_questions = self._extract_questions_from_text(content)
                        
                        for q_text in extracted_questions:
                            questions.append(ScrapedQuestion(
                                question_text=q_text,
                                source_url=url,
                                source_name="Reddit",
                                company_name=company,
                                topic="Interview Experience",
                                difficulty="medium"
                            ))
                
                except json.JSONDecodeError:
                    logger.error(f"Error parsing Reddit JSON for subreddit {subreddit}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping Reddit interviews: {str(e)}")
        
        return questions
    
    def _extract_questions_from_text(self, text: str) -> List[str]:
        """Extract potential interview questions from text"""
        questions = []
        
        # Common question patterns
        question_patterns = [
            r'Q\d*[:\.]?\s*(.+?\?)',
            r'Question\s*\d*[:\.]?\s*(.+?\?)',
            r'They asked[:\s]*(.+?\?)',
            r'The interviewer asked[:\s]*(.+?\?)',
            r'["\'](.+?\?)["\']',
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                question = match.strip()
                if len(question) > 10 and question not in questions:  # Avoid duplicates and too short questions
                    questions.append(question)
        
        return questions[:5]  # Limit to 5 questions per post
    
    async def scrape_all_sources(self, topic: str, company: str = None) -> List[ScrapedQuestion]:
        """Scrape questions from all sources"""
        all_questions = []
        
        # Scrape from different sources concurrently
        tasks = [
            self.scrape_tcyonline(topic),
            self.scrape_prepinsta(topic),
            self.scrape_indiabix(topic),
        ]
        
        if company:
            tasks.append(self.scrape_reddit_interviews(company))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_questions.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping task failed: {str(result)}")
        
        return all_questions