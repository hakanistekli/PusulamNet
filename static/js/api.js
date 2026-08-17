// PusulamNet - Backend API Communication Layer
const API_BASE = "";

class ApiService {
    static getAuthToken() {
        return localStorage.getItem("pusulamnet_token");
    }

    static async request(endpoint, options = {}) {
        try {
            const token = this.getAuthToken();
            const headers = {
                "Content-Type": "application/json",
                ...options.headers
            };
            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers: headers
            });

            if (!response.ok) {
                let errDetail = "Bir hata oluştu.";
                try {
                    const errData = await response.json();
                    errDetail = errData.detail || JSON.stringify(errData);
                } catch (e) {}
                if (response.status === 401) {
                    // Token invalid or expired
                    localStorage.removeItem("pusulamnet_token");
                    localStorage.removeItem("pusulamnet_user");
                }
                const requestError = new Error(errDetail);
                requestError.status = response.status;
                throw requestError;
            }

            if (response.status === 204) return null;
            return await response.json();
        } catch (error) {
            // A logged-out visitor intentionally receives 401 and is shown guest mode.
            if (error.status !== 401) {
                console.error(`API Error on ${endpoint}:`, error);
            }
            throw error;
        }
    }

    // Auth
    static register(name, email, password) {
        return this.request("/api/auth/register", { method: "POST", body: JSON.stringify({ name, email, password }) });
    }
    static login(email, password) {
        return this.request("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    }
    static getMe() {
        return this.request("/api/auth/me");
    }


    // Exam Types
    static getExamTypes() {
        return this.request("/api/exam-types");
    }
    static getPublicExamCatalog() {
        return this.request("/api/exam-types/catalog");
    }
    static getExamType(id) {
        return this.request(`/api/exam-types/${id}`);
    }
    static createExamType(data) {
        return this.request("/api/exam-types", { method: "POST", body: JSON.stringify(data) });
    }
    static updateExamType(id, data) {
        return this.request(`/api/exam-types/${id}`, { method: "PUT", body: JSON.stringify(data) });
    }
    static deleteExamType(id) {
        return this.request(`/api/exam-types/${id}`, { method: "DELETE" });
    }

    // Practice Exams
    static getExams(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/exams${query ? '?' + query : ''}`);
    }
    static getExam(id) {
        return this.request(`/api/exams/${id}`);
    }
    static createExam(data) {
        return this.request("/api/exams", { method: "POST", body: JSON.stringify(data) });
    }
    static updateExam(id, data) {
        return this.request(`/api/exams/${id}`, { method: "PUT", body: JSON.stringify(data) });
    }
    static deleteExam(id) {
        return this.request(`/api/exams/${id}`, { method: "DELETE" });
    }

    // Dashboard
    static getDashboard(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/dashboard${query ? '?' + query : ''}`);
    }

    // Course Analysis
    static getCourses(examTypeId) {
        const query = examTypeId ? `?exam_type_id=${examTypeId}` : '';
        return this.request(`/api/course-analysis/courses${query}`);
    }
    static getCourseAnalysis(courseId) {
        return this.request(`/api/course-analysis/${courseId}`);
    }

    // Goals
    static getGoals(examTypeId) {
        const query = examTypeId ? `?exam_type_id=${examTypeId}` : '';
        return this.request(`/api/goals${query}`);
    }

    // Report
    static getReport(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/report${query ? '?' + query : ''}`);
    }

    // Data Reset
    static clearAllExams() {
        return this.request("/api/demo/clear", { method: "POST" });
    }

    // Planner API (Notes & Tasks)
    static getNotes(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/planner/notes${query ? '?' + query : ''}`);
    }
    static createNote(data) {
        return this.request("/api/planner/notes", { method: "POST", body: JSON.stringify(data) });
    }
    static updateNote(id, data) {
        return this.request(`/api/planner/notes/${id}`, { method: "PUT", body: JSON.stringify(data) });
    }
    static deleteNote(id) {
        return this.request(`/api/planner/notes/${id}`, { method: "DELETE" });
    }

    static getTasks() {
        return this.request("/api/planner/tasks");
    }
    static createTask(data) {
        return this.request("/api/planner/tasks", { method: "POST", body: JSON.stringify(data) });
    }
    static updateTask(id, data) {
        return this.request(`/api/planner/tasks/${id}`, { method: "PUT", body: JSON.stringify(data) });
    }
    static deleteTask(id) {
        return this.request(`/api/planner/tasks/${id}`, { method: "DELETE" });
    }
}

