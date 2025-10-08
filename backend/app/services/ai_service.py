import httpx
import json
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AIAnswer:
    answer: str
    explanation: str
    confidence_score: float
    reasoning: str

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://interview-prep-app.com",
            "X-Title": "Interview Prep App"
        }
    
    async def generate_answer(self, question: str, options: List[str] = None) -> AIAnswer:
        """Generate AI answer for a given question"""
        try:
            # Prepare the prompt
            if options:
                options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                prompt = f"""
                Question: {question}
                
                Options:
                {options_text}
                
                Please provide:
                1. The correct answer (A, B, C, or D)
                2. A detailed explanation of why this answer is correct
                3. Your confidence level (0.0 to 1.0)
                4. Step-by-step reasoning
                
                Format your response as JSON:
                {{
                    "answer": "A",
                    "explanation": "Detailed explanation here...",
                    "confidence_score": 0.95,
                    "reasoning": "Step by step reasoning..."
                }}
                """
            else:
                prompt = f"""
                Question: {question}
                
                Please provide:
                1. A comprehensive answer to this question
                2. A detailed explanation
                3. Your confidence level (0.0 to 1.0)
                4. Step-by-step reasoning
                
                Format your response as JSON:
                {{
                    "answer": "Your answer here...",
                    "explanation": "Detailed explanation here...",
                    "confidence_score": 0.95,
                    "reasoning": "Step by step reasoning..."
                }}
                """
            
            # Make API call to OpenRouter
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3.5-sonnet",  # Using Claude for better reasoning
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert interview preparation assistant. Provide accurate, well-reasoned answers to interview questions with detailed explanations."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        ai_response = json.loads(content)
                        return AIAnswer(
                            answer=ai_response.get("answer", ""),
                            explanation=ai_response.get("explanation", ""),
                            confidence_score=float(ai_response.get("confidence_score", 0.5)),
                            reasoning=ai_response.get("reasoning", "")
                        )
                    except json.JSONDecodeError:
                        # Fallback if JSON parsing fails
                        return AIAnswer(
                            answer=content[:200],
                            explanation=content,
                            confidence_score=0.5,
                            reasoning="AI response parsing failed"
                        )
                else:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return self._fallback_answer(question, options)
        
        except Exception as e:
            logger.error(f"Error generating AI answer: {str(e)}")
            return self._fallback_answer(question, options)
    
    async def validate_answer(self, question: str, scraped_answer: str, options: List[str] = None) -> Tuple[bool, float, str]:
        """Validate a scraped answer using AI"""
        try:
            if options:
                options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
                prompt = f"""
                Question: {question}
                
                Options:
                {options_text}
                
                Scraped Answer: {scraped_answer}
                
                Please validate if the scraped answer is correct. Provide:
                1. Is the answer correct? (true/false)
                2. Confidence score (0.0 to 1.0)
                3. Explanation of your validation
                
                Format as JSON:
                {{
                    "is_correct": true,
                    "confidence_score": 0.95,
                    "explanation": "Validation explanation..."
                }}
                """
            else:
                prompt = f"""
                Question: {question}
                Scraped Answer: {scraped_answer}
                
                Please validate if this answer is reasonable and correct. Provide:
                1. Is the answer correct? (true/false)
                2. Confidence score (0.0 to 1.0)
                3. Explanation of your validation
                
                Format as JSON:
                {{
                    "is_correct": true,
                    "confidence_score": 0.95,
                    "explanation": "Validation explanation..."
                }}
                """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert validator for interview questions and answers. Carefully analyze the correctness of provided answers."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    try:
                        validation = json.loads(content)
                        return (
                            validation.get("is_correct", False),
                            float(validation.get("confidence_score", 0.5)),
                            validation.get("explanation", "")
                        )
                    except json.JSONDecodeError:
                        return False, 0.5, "Validation parsing failed"
                else:
                    return False, 0.5, f"API error: {response.status_code}"
        
        except Exception as e:
            logger.error(f"Error validating answer: {str(e)}")
            return False, 0.5, f"Validation error: {str(e)}"
    
    async def improve_question(self, question: str, context: str = None) -> str:
        """Improve question quality and clarity"""
        try:
            prompt = f"""
            Original Question: {question}
            Context: {context or "General interview question"}
            
            Please improve this question to make it:
            1. More clear and specific
            2. Grammatically correct
            3. Professional and interview-appropriate
            4. Maintain the original intent
            
            Return only the improved question text.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert at improving interview questions for clarity and professionalism."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    improved_question = result["choices"][0]["message"]["content"].strip()
                    return improved_question
                else:
                    return question  # Return original if improvement fails
        
        except Exception as e:
            logger.error(f"Error improving question: {str(e)}")
            return question
    
    def _fallback_answer(self, question: str, options: List[str] = None) -> AIAnswer:
        """Provide a fallback answer when AI service fails"""
        if options:
            return AIAnswer(
                answer="Unable to determine",
                explanation="AI service temporarily unavailable. Please refer to the source material.",
                confidence_score=0.0,
                reasoning="Fallback response due to service unavailability"
            )
        else:
            return AIAnswer(
                answer="Please research this topic further",
                explanation="AI service temporarily unavailable. Consult relevant documentation or experts.",
                confidence_score=0.0,
                reasoning="Fallback response due to service unavailability"
            )