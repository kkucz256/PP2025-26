/**
 * API Client - Komunikacja z REST API
 * Provides helper methods for common API operations
 */

class QuizAPI {
    constructor(baseUrl = '/api/quiz', csrfToken = null) {
        this.baseUrl = baseUrl;
        this.csrfToken = csrfToken || this.getCsrfToken();
    }

    /**
     * Get CSRF token from meta tag or cookies
     */
    getCsrfToken() {
        // Try meta tag first
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');

        // Try cookie
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return value;
        }
        return null;
    }

    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.csrfToken) {
            headers['X-CSRFToken'] = this.csrfToken;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error at ${endpoint}:`, error);
            throw error;
        }
    }

    // ============ QUIZ OPERATIONS ============

    /**
     * Create a new quiz
     */
    async createQuiz(quizData) {
        return this.request('/quizzes/', {
            method: 'POST',
            body: JSON.stringify(quizData)
        });
    }

    /**
     * Get all quizzes
     */
    async getQuizzes(userId = null) {
        const params = userId ? `?user_id=${userId}` : '';
        return this.request(`/quizzes/${params}`);
    }

    /**
     * Get single quiz
     */
    async getQuiz(quizId) {
        return this.request(`/quizzes/${quizId}/`);
    }

    /**
     * Delete a quiz
     */
    async deleteQuiz(quizId) {
        return this.request(`/quizzes/${quizId}/`, {
            method: 'DELETE'
        });
    }

    /**
     * Share quiz with another user
     */
    async shareQuiz(quizId, userId) {
        return this.request(`/quizzes/${quizId}/share/`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });
    }

    // ============ QUESTION OPERATIONS ============

    /**
     * Create a question
     */
    async createQuestion(questionData) {
        return this.request('/questions/', {
            method: 'POST',
            body: JSON.stringify(questionData)
        });
    }

    /**
     * Get all questions
     */
    async getQuestions(quizId = null) {
        const params = quizId ? `?quiz_id=${quizId}` : '';
        return this.request(`/questions/${params}`);
    }

    /**
     * Get single question
     */
    async getQuestion(questionId) {
        return this.request(`/questions/${questionId}/`);
    }

    /**
     * Delete a question
     */
    async deleteQuestion(questionId) {
        return this.request(`/questions/${questionId}/`, {
            method: 'DELETE'
        });
    }

    /**
     * Add answer to question
     */
    async createAnswer(questionId, answerData) {
        return this.request(`/questions/${questionId}/answers/`, {
            method: 'POST',
            body: JSON.stringify(answerData)
        });
    }

    // ============ QUIZ SESSION OPERATIONS ============

    /**
     * Create a quiz session
     */
    async createSession(sessionData) {
        return this.request('/sessions/', {
            method: 'POST',
            body: JSON.stringify(sessionData)
        });
    }

    /**
     * Get quiz sessions
     */
    async getSessions(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/sessions/?${params}`);
    }

    // ============ QUIZ ATTEMPT OPERATIONS ============

    /**
     * Create a quiz attempt
     */
    async createAttempt(attemptData) {
        return this.request('/attempts/', {
            method: 'POST',
            body: JSON.stringify(attemptData)
        });
    }

    /**
     * Get quiz attempts
     */
    async getAttempts(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/attempts/?${params}`);
    }

    /**
     * Submit quiz attempt (check answers)
     */
    async submitAttempt(attemptId, answers) {
        return this.request(`/attempts/${attemptId}/submit/`, {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    }

    // ============ STATISTICS OPERATIONS ============

    /**
     * Get quiz statistics
     */
    async getQuizStats(quizId) {
        return this.request(`/quizzes/${quizId}/stats/`);
    }

    /**
     * Get question statistics
     */
    async getQuestionStats(questionId) {
        return this.request(`/questions/${questionId}/stats/`);
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuizAPI;
}
