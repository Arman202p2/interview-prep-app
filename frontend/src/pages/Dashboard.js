import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  PlayArrow,
  TrendingUp,
  Assignment,
  Notifications,
  CheckCircle,
  Schedule,
  Star,
  QuestionAnswer,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { format, isToday } from 'date-fns';

import { quizAPI, analyticsAPI, notificationsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [todayQuizCompleted, setTodayQuizCompleted] = useState(false);

  // Fetch dashboard data
  const { data: dailyQuiz, isLoading: quizLoading } = useQuery(
    'dailyQuiz',
    quizAPI.getDailyQuiz,
    {
      onSuccess: (data) => {
        setTodayQuizCompleted(data?.is_completed || false);
      },
    }
  );

  const { data: analytics, isLoading: analyticsLoading } = useQuery(
    'userAnalytics',
    () => analyticsAPI.getUserAnalytics('7d')
  );

  const { data: notifications } = useQuery(
    'recentNotifications',
    () => notificationsAPI.getNotifications(1, 5)
  );

  const { data: quizHistory } = useQuery(
    'recentQuizzes',
    () => quizAPI.getQuizHistory(1, 5)
  );

  const handleStartQuiz = () => {
    navigate('/quiz');
  };

  if (quizLoading || analyticsLoading) {
    return <LoadingSpinner />;
  }

  const todayDate = format(new Date(), 'EEEE, MMMM do');
  const streak = analytics?.streak || 0;
  const totalQuizzes = analytics?.total_quizzes || 0;
  const averageScore = analytics?.average_score || 0;

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.full_name?.split(' ')[0]}! 👋
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {todayDate}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Daily Quiz Card */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <QuestionAnswer />
                </Avatar>
                <Box>
                  <Typography variant="h5" gutterBottom>
                    Daily Quiz Challenge
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {todayQuizCompleted 
                      ? "Great job! You've completed today's quiz" 
                      : "Ready to test your knowledge today?"
                    }
                  </Typography>
                </Box>
              </Box>

              {todayQuizCompleted ? (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <CheckCircle sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
                  <Typography variant="h6" color="success.main" gutterBottom>
                    Quiz Completed!
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Score: {dailyQuiz?.last_score || 0}%
                  </Typography>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/analytics')}
                    startIcon={<TrendingUp />}
                  >
                    View Results
                  </Button>
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Schedule sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                  <Typography variant="body1" sx={{ mb: 3 }}>
                    {dailyQuiz?.total_questions || 10} questions waiting for you
                  </Typography>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleStartQuiz}
                    startIcon={<PlayArrow />}
                    sx={{ px: 4, py: 1.5 }}
                  >
                    Start Daily Quiz
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Grid container spacing={2}>
            {/* Streak Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 1 }}>
                    <Star />
                  </Avatar>
                  <Typography variant="h4" color="warning.main">
                    {streak}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Day Streak
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Total Quizzes */}
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" color="primary.main">
                    {totalQuizzes}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Quizzes
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Average Score */}
            <Grid item xs={6}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" color="success.main">
                    {averageScore.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Score
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Progress Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Progress
              </Typography>
              
              {analytics?.weekly_progress?.map((day, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      {format(new Date(day.date), 'EEE')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {day.completed ? '✓' : '-'}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={day.completed ? 100 : 0}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              
              <List dense>
                {quizHistory?.results?.slice(0, 5).map((quiz, index) => (
                  <ListItem key={index} divider>
                    <ListItemIcon>
                      <Assignment color={quiz.status === 'completed' ? 'success' : 'action'} />
                    </ListItemIcon>
                    <ListItemText
                      primary={`Quiz - ${quiz.total_questions} questions`}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="caption">
                            {format(new Date(quiz.started_at), 'MMM dd, HH:mm')}
                          </Typography>
                          {quiz.status === 'completed' && (
                            <Chip
                              label={`${quiz.score_percentage}%`}
                              size="small"
                              color={quiz.score_percentage >= 70 ? 'success' : 'warning'}
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
                
                {(!quizHistory?.results || quizHistory.results.length === 0) && (
                  <ListItem>
                    <ListItemText
                      primary="No recent activity"
                      secondary="Start your first quiz to see your progress here"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                startIcon={<Assignment />}
                onClick={() => navigate('/topics')}
              >
                Manage Topics
              </Button>
              <Button
                variant="outlined"
                startIcon={<TrendingUp />}
                onClick={() => navigate('/analytics')}
              >
                View Analytics
              </Button>
              <Button
                variant="outlined"
                startIcon={<Notifications />}
                onClick={() => navigate('/profile')}
              >
                Notification Settings
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;