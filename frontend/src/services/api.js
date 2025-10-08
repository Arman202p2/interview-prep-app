import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instances
export const authAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Services
export const quizAPI = {
  // Get daily quiz
  getDailyQuiz: () => api.get('/quizzes/daily'),
  
  // Start quiz
  startQuiz: (quizData) => api.post('/quizzes/start', quizData),
  
  // Submit quiz answer
  submitAnswer: (quizId, questionId, answer) => 
    api.post(`/quizzes/${quizId}/questions/${questionId}/answer`, { answer }),
  
  // Complete quiz
  completeQuiz: (quizId) => api.post(`/quizzes/${quizId}/complete`),
  
  // Get quiz history
  getQuizHistory: (page = 1, limit = 10) => 
    api.get(`/quizzes/history?page=${page}&limit=${limit}`),
  
  // Get quiz results
  getQuizResults: (quizId) => api.get(`/quizzes/${quizId}/results`),
};

export const topicsAPI = {
  // Get all topics
  getTopics: () => api.get('/topics'),
  
  // Get user topics
  getUserTopics: () => api.get('/topics/user'),
  
  // Add user topic
  addUserTopic: (topicId, priority = 1) => 
    api.post('/topics/user', { topic_id: topicId, priority }),
  
  // Remove user topic
  removeUserTopic: (topicId) => api.delete(`/topics/user/${topicId}`),
  
  // Create custom topic
  createTopic: (topicData) => api.post('/topics', topicData),
  
  // Update topic priority
  updateTopicPriority: (topicId, priority) => 
    api.put(`/topics/user/${topicId}`, { priority }),
};

export const analyticsAPI = {
  // Get user analytics
  getUserAnalytics: (period = '30d') => api.get(`/analytics/user?period=${period}`),
  
  // Get topic performance
  getTopicPerformance: () => api.get('/analytics/topics'),
  
  // Get quiz statistics
  getQuizStats: () => api.get('/analytics/quiz-stats'),
  
  // Get progress trends
  getProgressTrends: (period = '30d') => api.get(`/analytics/trends?period=${period}`),
  
  // Get recommendations
  getRecommendations: () => api.get('/analytics/recommendations'),
};

export const notificationsAPI = {
  // Get user notifications
  getNotifications: (page = 1, limit = 20) => 
    api.get(`/notifications?page=${page}&limit=${limit}`),
  
  // Mark notification as read
  markAsRead: (notificationId) => api.put(`/notifications/${notificationId}/read`),
  
  // Update notification settings
  updateSettings: (settings) => api.put('/notifications/settings', settings),
  
  // Register FCM token
  registerFCMToken: (token) => api.post('/notifications/fcm-token', { token }),
};

export const questionsAPI = {
  // Get questions by topic
  getQuestionsByTopic: (topicId, page = 1, limit = 10) => 
    api.get(`/questions/topic/${topicId}?page=${page}&limit=${limit}`),
  
  // Search questions
  searchQuestions: (query, filters = {}) => 
    api.get('/questions/search', { params: { query, ...filters } }),
  
  // Get question details
  getQuestion: (questionId) => api.get(`/questions/${questionId}`),
  
  // Report question issue
  reportQuestion: (questionId, issue) => 
    api.post(`/questions/${questionId}/report`, { issue }),
};

export const userAPI = {
  // Get user profile
  getProfile: () => api.get('/users/profile'),
  
  // Update user profile
  updateProfile: (profileData) => api.put('/users/profile', profileData),
  
  // Update notification preferences
  updateNotificationPreferences: (preferences) => 
    api.put('/users/notification-preferences', preferences),
  
  // Get user statistics
  getUserStats: () => api.get('/users/stats'),
  
  // Delete account
  deleteAccount: () => api.delete('/users/account'),
};