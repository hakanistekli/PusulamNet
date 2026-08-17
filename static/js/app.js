// PusulamNet - Main Frontend Single Page Application (SPA) Controller
document.addEventListener("DOMContentLoaded", () => {
    App.init();
});

class App {
    static state = {
        currentPage: "dashboard",
        examTypes: [],
        selectedExamTypeId: isNaN(parseInt(localStorage.getItem("pusulamnet_selected_exam_type"))) ? null : parseInt(localStorage.getItem("pusulamnet_selected_exam_type")),
        coursesForCurrentExamType: [],
        currentEditingExamId: null,
        theme: localStorage.getItem("pusulamnet_theme") || "dark"
    };


    static async init() {
        this.applyTheme(this.state.theme);

        // Masaüstü menü durum tercihini uygula
        const isCollapsed = localStorage.getItem("pusulamnet_sidebar_collapsed") === "true";
        if (isCollapsed && window.innerWidth > 992) {
            document.body.classList.add("sidebar-collapsed");
        }

        this.bindEvents();
        this.bindAuthEvents();
        await this.checkAuthStatus();
        lucide.createIcons();
    }

    static async checkAuthStatus() {
        const token = ApiService.getAuthToken();
        if (!token) {
            // Misafir modu: uygulamayı göster ama veri yükleme
            this.state.isGuest = true;
            this.updateUserUI(null);
            await this.loadExamTypesForGuest();
            this.showGuestDashboard();
            return;
        }

        try {
            const user = await ApiService.getMe();
            this.state.currentUser = user;
            this.state.isGuest = false;
            this.updateUserUI(user);
            this.hideAuthModal();
            await this.loadInitialData();
        } catch (e) {
            console.warn("Auth check failed:", e);
            // Token geçersiz: misafir moduna geç
            localStorage.removeItem("pusulamnet_token");
            localStorage.removeItem("pusulamnet_user");
            this.state.isGuest = true;
            this.updateUserUI(null);
            await this.loadExamTypesForGuest();
            this.showGuestDashboard();
        }
    }

    static async loadExamTypesForGuest() {
        try {
            this.state.examTypes = await ApiService.getPublicExamCatalog();
            if (!this.state.examTypes || this.state.examTypes.length === 0) {
                throw new Error("No exam types");
            }
            this.populateExamTypeDropdowns();
        } catch (e) {
            this.state.examTypes = [
                { id: 1, name: "YKS - TYT", exam_date: "2026-06-20", wrong_penalty_divisor: 4.0, target_net: 95.0 },
                { id: 2, name: "YKS - AYT", exam_date: "2026-06-21", wrong_penalty_divisor: 4.0, target_net: 65.0 },
                { id: 3, name: "LGS (8. Sınıf)", exam_date: "2026-06-14", wrong_penalty_divisor: 3.0, target_net: 80.0 },
                { id: 4, name: "KPSS (Genel Yetenek - Genel Kültür)", exam_date: "2026-09-06", wrong_penalty_divisor: 4.0, target_net: 90.0 },
                { id: 5, name: "TUS (Tıpta Uzmanlık Eğitimi)", exam_date: "2026-08-23", wrong_penalty_divisor: 4.0, target_net: 150.0 },
                { id: 6, name: "DUS (Diş Hekimliğinde Uzmanlık)", exam_date: "2026-11-01", wrong_penalty_divisor: 4.0, target_net: 90.0 }
            ];
            this.populateExamTypeDropdowns();
        }
    }

    // Auth guard: giriş gerektiren işlemler için
    static requireAuth() {
        if (this.state.isGuest) {
            this.showAuthModal();
            return false;
        }
        return true;
    }

    // Misafir modunda gösterilecek tanıtım ekranı
    static showGuestDashboard() {
        // Tüm sayfa görünümlerini gizle, dashboard'u göster
        document.querySelectorAll(".page-view").forEach(p => p.style.display = "none");
        const dash = document.getElementById("page-dashboard");
        if (dash) dash.style.display = "block";
        this.state.currentPage = "dashboard";

        // Nav item güncelle
        document.querySelectorAll(".nav-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-page") === "dashboard");
        });

        // Boş grafik grid'ini misafir modunda gizle
        const chartsGrid = document.querySelector(".charts-grid");
        if (chartsGrid) chartsGrid.style.display = "none";

        const expBox = document.getElementById("dashExplanationBox");
        if (expBox) expBox.style.display = "none";

        // Misafir dashboard içeriği
        const cardsContainer = document.getElementById("dashMetricCards");
        if (cardsContainer) {
            cardsContainer.innerHTML = `
                <!-- Karşılama Kartı -->
                <div class="metric-card" style="grid-column:1/-1; text-align:center; padding:2.5rem 1.5rem; display:flex; flex-direction:column; align-items:center;">
                    <h2 style="font-size:1.5rem; font-weight:800; margin-bottom:0.75rem; color:var(--accent-blue);">PusulamNet'e Hoş Geldiniz</h2>
                    <p style="color:var(--text-secondary); max-width:520px; margin:0 auto 1.5rem; line-height:1.6;">
                        Deneme takip sisteminizi görüntülemek için lütfen giriş yapın veya ücretsiz hesap oluşturun.
                        Şu an misafir modundasınız — menüyü ve uygulamayı serbestçe gezebilirsiniz.
                    </p>
                    <div style="display:flex; justify-content:center; align-items:center; gap:1rem; flex-wrap:wrap; width:100%;">
                        <button id="guestLoginBtn" class="btn btn-primary" style="padding:0.75rem 2rem; font-size:1rem; font-weight:700; width:auto;" onclick="App.showAuthModal()">
                            Giriş Yap / Kayıt Ol
                        </button>
                        <button id="guestGuideBtn" class="btn btn-secondary" style="padding:0.75rem 2rem; font-size:1rem; font-weight:700; width:auto;" onclick="App.navigateTo('guide')">
                            Kullanım Kılavuzu
                        </button>
                    </div>
                </div>

                <!-- 1. Temsilî Kart: Deneme Takibi & Net Gelişimi -->
                <div class="metric-card" style="padding:1.5rem; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:var(--accent-blue); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.4rem;">Performans Analizi</div>
                        <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">Deneme Takibi & Net Analizi</h3>
                        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.5; margin-bottom:1rem;">
                            Çözdüğünüz her denemenin net artış hızını, son dönem ortalamanızı ve başarı eğrinizi görün.
                        </p>
                    </div>
                    <div style="background:var(--bg-secondary); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Son Deneme:</span>
                            <span style="font-weight:700; color:var(--accent-blue); font-size:0.95rem;">92.50 Net</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Son 5 Deneme Ort.:</span>
                            <span style="font-weight:700; color:var(--text-primary); font-size:0.95rem;">87.20 Net</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Gelişim Durumu:</span>
                            <span class="badge badge-success">+11.25 Net Artış</span>
                        </div>
                    </div>
                </div>

                <!-- 2. Temsilî Kart: Ders Bazlı Hedef Takibi -->
                <div class="metric-card" style="padding:1.5rem; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:var(--accent-emerald); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.4rem;">Hedef Sistemi</div>
                        <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">Ders Bazlı Hedef Takibi</h3>
                        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.5; margin-bottom:1rem;">
                            Derslerinize özel hedef netler belirleyin; mevcut ortalamanızla hedefinize olan farkı anlık izleyin.
                        </p>
                    </div>
                    <div style="background:var(--bg-secondary); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border-color); display:flex; flex-direction:column; gap:0.5rem;">
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; margin-bottom:0.2rem;">
                                <span>Türkçe (Hedef: 35 Net)</span>
                                <span style="font-weight:700; color:var(--accent-emerald);">%92</span>
                            </div>
                            <div style="width:100%; height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                                <div style="width:92%; height:100%; background:var(--accent-emerald);"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; margin-bottom:0.2rem;">
                                <span>Matematik (Hedef: 32 Net)</span>
                                <span style="font-weight:700; color:var(--accent-blue);">%84</span>
                            </div>
                            <div style="width:100%; height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                                <div style="width:84%; height:100%; background:var(--accent-blue);"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; margin-bottom:0.2rem;">
                                <span>Fen Bilimleri (Hedef: 16 Net)</span>
                                <span style="font-weight:700; color:var(--accent-indigo);">%78</span>
                            </div>
                            <div style="width:100%; height:6px; background:rgba(255,255,255,0.08); border-radius:3px; overflow:hidden;">
                                <div style="width:78%; height:100%; background:var(--accent-indigo);"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3. Temsilî Kart: Akıllı Yorumlar -->
                <div class="metric-card" style="padding:1.5rem; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:var(--accent-purple); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.4rem;">Otomatik Analiz</div>
                        <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">Kural Tabanlı Öneriler</h3>
                        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.5; margin-bottom:1rem;">
                            Netlerinizi sürekli tarayarak hangi derste geliştiğinizi ve nerede eksik kaldığınızı söyler.
                        </p>
                    </div>
                    <div style="background:var(--bg-secondary); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border-color); display:flex; flex-direction:column; gap:0.45rem;">
                        <div style="font-size:0.78rem; color:var(--text-primary); padding-left:0.5rem; border-left:3px solid var(--accent-emerald);">
                            Matematik netlerinizde son 3 denemedir düzenli artış var.
                        </div>
                        <div style="font-size:0.78rem; color:var(--text-primary); padding-left:0.5rem; border-left:3px solid var(--accent-rose);">
                            Sosyal dersinde yanlış oranı yüksek, soru çözümüne odaklanın.
                        </div>
                        <div style="font-size:0.78rem; color:var(--text-primary); padding-left:0.5rem; border-left:3px solid var(--accent-blue);">
                            Genel hedef netinize 7.5 net kaldı.
                        </div>
                    </div>
                </div>

                <!-- 4. Temsilî Kart: Sınav Sayacı & Notlar -->
                <div class="metric-card" style="padding:1.5rem; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:var(--accent-rose); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.4rem;">Çalışma Araçları</div>
                        <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">Sınav Sayacı & Not Defteri</h3>
                        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.5; margin-bottom:1rem;">
                            Resmi sürelerle gerçek sınav simülasyonu, Pomodoro odaklanma ve kategori bazlı ders notları tutun.
                        </p>
                    </div>
                    <div style="background:var(--bg-secondary); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">TYT Sayacı:</span>
                            <span style="font-family:monospace; font-weight:700; color:var(--accent-blue); font-size:0.95rem;">02:45:00</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Pomodoro Modu:</span>
                            <span style="font-weight:600; color:var(--accent-emerald); font-size:0.8rem;">25 Dk Çalış / 5 Dk Mola</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Ders Notları:</span>
                            <span class="badge badge-neutral">Hazır</span>
                        </div>
                    </div>
                </div>

                <!-- 5. Temsilî Kart: Sınav Türleri Bilgisi -->
                <div class="metric-card" style="padding:1.5rem; justify-content:space-between;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:var(--accent-amber, #f59e0b); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:0.4rem;">Sınav Sistemi</div>
                        <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:0.5rem;">Sınav Türleri & Şablonlar</h3>
                        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.5; margin-bottom:1rem;">
                            Tüm ulusal sınavların ders, soru sayıları ve ceza katsayıları hazır; dilerseniz kendinize özel sınav ekleyin.
                        </p>
                    </div>
                    <div style="background:var(--bg-secondary); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border-color); display:flex; flex-direction:column; gap:0.45rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Hazır Sınavlar:</span>
                            <span style="font-size:0.75rem; font-weight:700; color:var(--text-primary);">YKS, KPSS, DUS, TUS, LGS</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Ceza Sistemi:</span>
                            <span style="font-size:0.75rem; font-weight:600; color:var(--accent-blue);">4 Yanlış 1 Doğru / 3Y1D</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:var(--text-secondary);">Özel Sınav:</span>
                            <span class="badge badge-success">Sınırsız Ekleme</span>
                        </div>
                    </div>
                </div>
            `;
        }

        lucide.createIcons();
    }

    static updateUserUI(user) {
        const nameEl = document.getElementById("userNameDisplay");
        const emailEl = document.getElementById("userEmailDisplay");
        const profileCard = document.getElementById("userProfileCard");
        const logoutBtn = document.getElementById("btnLogout");

        if (!user) {
            // Misafir modu: sidebar'da giriş yap butonu göster
            if (nameEl) nameEl.textContent = "Misafir";
            if (emailEl) emailEl.textContent = "Giriş yapmadınız";
            if (logoutBtn) logoutBtn.style.display = "none";
            if (profileCard) {
                // Giriş yap butonunu ekle (yoksa)
                if (!document.getElementById("guestSidebarLoginBtn")) {
                    const btn = document.createElement("button");
                    btn.id = "guestSidebarLoginBtn";
                    btn.className = "btn btn-primary";
                    btn.style.cssText = "width:100%; margin-top:0.5rem; justify-content:center; font-size:0.8rem; padding:0.45rem 0.75rem;";
                    btn.innerHTML = 'Giriş Yap / Kayıt Ol';
                    btn.onclick = () => App.showAuthModal();
                    profileCard.parentNode.insertBefore(btn, profileCard.nextSibling);
                }
            }
        } else {
            if (nameEl) nameEl.textContent = user.name;
            if (emailEl) emailEl.textContent = user.email;
            if (logoutBtn) logoutBtn.style.display = "";
            // Misafir butonunu kaldır
            document.getElementById("guestSidebarLoginBtn")?.remove();
        }
    }

    static showAuthModal() {
        document.getElementById("authModal")?.classList.add("active");
    }

    static hideAuthModal() {
        document.getElementById("authModal")?.classList.remove("active");
    }

    static bindAuthEvents() {
        const tabLogin = document.getElementById("tabLogin");
        const tabRegister = document.getElementById("tabRegister");
        const loginForm = document.getElementById("loginForm");
        const registerForm = document.getElementById("registerForm");

        tabLogin?.addEventListener("click", () => {
            tabLogin.style.borderBottom = "2px solid var(--accent-blue)";
            tabLogin.style.opacity = "1";
            tabRegister.style.borderBottom = "none";
            tabRegister.style.opacity = "0.7";
            loginForm.style.display = "block";
            registerForm.style.display = "none";
        });

        tabRegister?.addEventListener("click", () => {
            tabRegister.style.borderBottom = "2px solid var(--accent-emerald)";
            tabRegister.style.opacity = "1";
            tabLogin.style.borderBottom = "none";
            tabLogin.style.opacity = "0.7";
            registerForm.style.display = "block";
            loginForm.style.display = "none";
        });

        loginForm?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("loginEmail").value;
            const password = document.getElementById("loginPassword").value;
            try {
                const res = await ApiService.login(email, password);
                localStorage.setItem("pusulamnet_token", res.access_token);
                localStorage.setItem("pusulamnet_user", JSON.stringify(res.user));
                this.state.currentUser = res.user;
                this.state.isGuest = false;
                this.updateUserUI(res.user);
                this.hideAuthModal();
                await this.loadInitialData();
            } catch (err) {
                alert(`Giriş Hatası: ${err.message}`);
            }
        });

        registerForm?.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("registerName").value;
            const email = document.getElementById("registerEmail").value;
            const password = document.getElementById("registerPassword").value;
            try {
                const res = await ApiService.register(name, email, password);
                localStorage.setItem("pusulamnet_token", res.access_token);
                localStorage.setItem("pusulamnet_user", JSON.stringify(res.user));
                this.state.currentUser = res.user;
                this.state.isGuest = false;
                this.updateUserUI(res.user);
                this.hideAuthModal();
                await this.loadInitialData();
            } catch (err) {
                alert(`Kayıt Hatası: ${err.message}`);
            }
        });

        document.getElementById("btnLogout")?.addEventListener("click", () => {
            this.showModal({
                title: "Oturumu Kapat",
                content: "<p style='color:var(--text-secondary); margin-bottom:1rem;'>Hesabınızdan çıkış yapmak istediğinizden emin misiniz?</p>",
                confirmText: "Çıkış Yap",
                cancelText: "İptal",
                confirmClass: "btn-danger",
                onConfirm: () => {
                    localStorage.removeItem("pusulamnet_token");
                    localStorage.removeItem("pusulamnet_user");
                    location.reload();
                }
            });
        });

    }

    static setSelectedExamType(examTypeId) {
        if (!examTypeId) return;
        const idNum = parseInt(examTypeId);
        if (isNaN(idNum)) return;

        this.state.selectedExamTypeId = idNum;
        localStorage.setItem("pusulamnet_selected_exam_type", idNum);

        const selects = [
            "globalHeaderExamTypeSelect",
            "dashExamTypeSelect",
            "formExamTypeSelect",
            "histExamTypeSelect",
            "goalsExamTypeSelect",
            "reportExamTypeSelect"
        ];

        selects.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = idNum;
        });

        this.updateExamCountdownCard(idNum);

        // Refresh active page with selected exam type
        this.navigateTo(this.state.currentPage);
    }


    // --- THEME CONTROL ---
    static applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("pusulamnet_theme", theme);
        this.state.theme = theme;

        const iconEl = document.getElementById("themeIcon");
        const labelEl = document.getElementById("themeLabel");
        if (iconEl) {
            iconEl.setAttribute("data-lucide", theme === "light" ? "sun" : "moon");
        }
        if (labelEl) {
            labelEl.textContent = theme === "light" ? "Açık Tema" : "Koyu Tema";
        }
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    static toggleTheme() {
        const current = this.state.theme || "dark";
        const nextTheme = current === "dark" ? "light" : "dark";
        this.applyTheme(nextTheme);
        this.navigateTo(this.state.currentPage);
    }




    // --- NAVIGATION ROUTER ---
    static bindEvents() {
        // Nav items click
        document.querySelectorAll(".nav-item").forEach(item => {
            item.addEventListener("click", (e) => {
                const targetPage = item.getAttribute("data-page");
                this.navigateTo(targetPage);
            });
        });

        // Brand logo click -> Navigate to Dashboard
        document.getElementById("brandLogo")?.addEventListener("click", () => {
            this.navigateTo("dashboard");
        });

        // Theme Toggle Button
        document.getElementById("themeToggleBtn")?.addEventListener("click", () => {
            this.toggleTheme();
        });




        // Global & Header Exam Type Change
        document.getElementById("globalHeaderExamTypeSelect")?.addEventListener("change", (e) => {
            this.setSelectedExamType(e.target.value);
        });

        // Dashboard Filters
        document.getElementById("dashExamTypeSelect")?.addEventListener("change", (e) => {
            this.setSelectedExamType(e.target.value);
        });
        document.getElementById("btnFilterDashboard")?.addEventListener("click", () => this.renderDashboard());

        // Add Exam Form Change & Live Net Calculation
        document.getElementById("formExamTypeSelect")?.addEventListener("change", (e) => {
            this.setSelectedExamType(e.target.value);
            this.handleExamTypeChangeForForm(parseInt(e.target.value));
        });


        document.getElementById("btnPreviewExam")?.addEventListener("click", () => this.handleExamFormSubmit());

        // History Filters & Export Links
        document.getElementById("btnFilterHistory")?.addEventListener("click", () => this.renderExamHistory());

        // Course Analysis Dropdown Change
        document.getElementById("analysisCourseSelect")?.addEventListener("change", (e) => {
            this.renderCourseAnalysis(parseInt(e.target.value));
        });

        // Goals Filter
        document.getElementById("goalsExamTypeSelect")?.addEventListener("change", (e) => {
            this.setSelectedExamType(e.target.value);
            this.renderGoals(parseInt(e.target.value));
        });

        // Report Filter & Export
        document.getElementById("btnGenerateReport")?.addEventListener("click", () => this.renderReport());
        document.getElementById("reportExamTypeSelect")?.addEventListener("change", (e) => {
            this.setSelectedExamType(e.target.value);
            this.renderReport();
        });

        // Settings Clear Button
        document.getElementById("btnClearAllExams")?.addEventListener("click", () => this.handleClearAllExams());



        // Settings Exam Type Form
        document.getElementById("examTypeSettingsForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.handleSaveExamTypeSettings();
        });

        document.getElementById("btnNewExamType")?.addEventListener("click", () => this.handleCreateNewExamType());
        document.getElementById("btnDeleteExamType")?.addEventListener("click", () => this.handleDeleteExamType());
        document.getElementById("btnAddCourseRow")?.addEventListener("click", () => this.addCourseRowToSettingsTable());

        // Modal Close & ESC Key
        document.querySelectorAll(".close-btn").forEach(btn => {
            btn.addEventListener("click", () => this.closeModal());
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                this.closeModal();
                this.hideAuthModal();
            }
        });
    }



    // Misafir modunda içerik gerektiren sayfalarda g\u00f6sterilecek mesaj
    static showGuestPageMessage(pageId, title, message) {
        document.querySelectorAll(".page-view").forEach(p => p.style.display = "none");
        const targetEl = document.getElementById(`page-${pageId}`);
        if (targetEl) {
            targetEl.style.display = "block";
            // Sayfanın içine misafir mesajını ekle (varsa eskisini temizle)
            let guestMsg = targetEl.querySelector(".guest-placeholder");
            if (!guestMsg) {
                guestMsg = document.createElement("div");
                guestMsg.className = "guest-placeholder";
                guestMsg.style.cssText = "text-align:center; padding:4rem 2rem;";
                targetEl.appendChild(guestMsg);
            }
            guestMsg.innerHTML = `
                <h2 style="font-size:1.4rem; font-weight:800; margin-bottom:0.75rem;">${title}</h2>
                <p style="color:var(--text-secondary); max-width:400px; margin:0 auto 1.5rem; line-height:1.6;">${message}</p>
                <div style="display:flex; justify-content:center; width:100%;">
                    <button class="btn btn-primary" style="padding:0.75rem 2rem; font-weight:700; width:auto; margin:0 auto;" onclick="App.showAuthModal()">
                        Giriş Yap / Kayıt Ol
                    </button>
                </div>
            `;
            lucide.createIcons();
        }
        // Nav state g\u00fcncelle
        document.querySelectorAll(".nav-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-page") === pageId);
        });
        this.state.currentPage = pageId;
    }

    static async loadInitialData() {
        try {
            this.state.isGuest = false;
            this.state.examTypes = await ApiService.getExamTypes();
            this.populateExamTypeDropdowns();
            this.navigateTo("dashboard");
        } catch (e) {
            console.error("Data load failed:", e);
        }
    }


    static populateExamTypeDropdowns() {
        const selects = [
            "globalHeaderExamTypeSelect",
            "dashExamTypeSelect",
            "formExamTypeSelect",
            "histExamTypeSelect",
            "goalsExamTypeSelect",
            "reportExamTypeSelect"
        ];

        let activeId = this.state.selectedExamTypeId;
        if (isNaN(activeId)) activeId = null;

        const validActive = this.state.examTypes.find(et => et.id === activeId);
        if (!validActive && this.state.examTypes.length > 0) {
            activeId = this.state.examTypes[0].id;
            this.state.selectedExamTypeId = activeId;
            localStorage.setItem("pusulamnet_selected_exam_type", activeId);
        } else if (validActive) {
            activeId = validActive.id;
            this.state.selectedExamTypeId = activeId;
            localStorage.setItem("pusulamnet_selected_exam_type", activeId);
        }



        selects.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            el.innerHTML = "";
            this.state.examTypes.forEach((et) => {
                const opt = document.createElement("option");
                opt.value = et.id;
                opt.textContent = et.name;
                if (et.id === activeId) opt.selected = true;
                el.appendChild(opt);
            });
            if (activeId) {
                el.value = activeId;
            }
        });
        this.updateExamCountdownCard(activeId);
    }



    static updateExamCountdownCard(examTypeId) {
        const textEl = document.getElementById("examCountdownText");
        const dateEl = document.getElementById("examDateText");
        if (!textEl || !dateEl) return;

        let activeId = examTypeId || this.state.selectedExamTypeId;
        const examType = this.state.examTypes.find(et => et.id == activeId);

        if (!examType || !examType.exam_date) {
            textEl.textContent = "Tarih Belirtilmedi";
            dateEl.textContent = "Sınav Tarihi: Girilmedi";
            return;
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const targetDate = new Date(examType.exam_date);
        targetDate.setHours(0, 0, 0, 0);

        const diffTime = targetDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        const formattedDate = targetDate.toLocaleDateString("tr-TR", {
            day: "numeric",
            month: "long",
            year: "numeric"
        });

        dateEl.textContent = `Sınav Tarihi: ${formattedDate}`;

        if (diffDays > 0) {
            if (diffDays >= 30) {
                const months = Math.floor(diffDays / 30);
                const remainingDays = diffDays % 30;
                if (remainingDays > 0) {
                    textEl.textContent = `${diffDays} Gün (${months} Ay ${remainingDays} Gün)`;
                } else {
                    textEl.textContent = `${diffDays} Gün (${months} Ay)`;
                }
            } else {
                textEl.textContent = `${diffDays} Gün Kaldı`;
            }
        } else if (diffDays === 0) {
            textEl.textContent = "Sınav Günü!";
        } else {
            textEl.textContent = "Sınav Tamamlandı";
        }
    }

    // --- MENÜ (SIDEBAR) AÇMA / KAPAMA YÖNETİMİ ---
    static toggleSidebar() {
        const sidebar = document.querySelector(".sidebar");
        const overlay = document.getElementById("sidebarOverlay");
        if (!sidebar) return;

        const isMobile = window.innerWidth <= 992;
        if (isMobile) {
            const isOpen = sidebar.classList.toggle("mobile-open");
            if (overlay) overlay.classList.toggle("active", isOpen);
        } else {
            const isCollapsed = document.body.classList.toggle("sidebar-collapsed");
            localStorage.setItem("pusulamnet_sidebar_collapsed", isCollapsed ? "true" : "false");
        }
        if (window.lucide) lucide.createIcons();
    }

    static closeSidebar() {
        const sidebar = document.querySelector(".sidebar");
        const overlay = document.getElementById("sidebarOverlay");
        if (!sidebar) return;

        const isMobile = window.innerWidth <= 992;
        if (isMobile) {
            sidebar.classList.remove("mobile-open");
            if (overlay) overlay.classList.remove("active");
        }
    }

    static async navigateTo(pageId) {
        this.state.currentPage = pageId;

        // Mobilde menü açıksa sekmeye tıklandığında menüyü kapat
        this.closeSidebar();

        // Misafir modunda: veri girişi gerektiren sayfalarda auth modal aç
        const authRequiredPages = ["add_exam", "planner", "settings"];
        if (this.state.isGuest && authRequiredPages.includes(pageId)) {
            this.showAuthModal();
            return;
        }

        // Update nav item active state
        document.querySelectorAll(".nav-item").forEach(item => {
            if (item.getAttribute("data-page") === pageId) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        // Hide all page views and show target
        document.querySelectorAll(".page-view").forEach(page => {
            page.style.display = "none";
        });

        const targetEl = document.getElementById(`page-${pageId}`);
        if (targetEl) {
            targetEl.style.display = "block";
        }

        // Render page content
        switch (pageId) {
            case "dashboard":
                if (this.state.isGuest) { this.showGuestDashboard(); return; }
                this.renderDashboard();
                break;
            case "add_exam":
                this.renderAddExamForm();
                break;
            case "exam_history":
                if (this.state.isGuest) { this.showGuestPageMessage("exam_history", "Deneme Geçmişi", "Kayıtlı denemelerinizi görüntülemek için giriş yapın."); return; }
                this.renderExamHistory();
                break;
            case "course_analysis":
                if (this.state.isGuest) { this.showGuestPageMessage("course_analysis", "Ders Analizi", "Ders bazlı analizlerinizi görmek için giriş yapın."); return; }
                this.initCourseAnalysisPage();
                break;
            case "goals":
                if (this.state.isGuest) { this.showGuestPageMessage("goals", "Hedef Takibi", "Hedef takip sisteminizi kullanmak için giriş yapın."); return; }
                this.renderGoals();
                break;
            case "report":
                if (this.state.isGuest) { this.showGuestPageMessage("report", "Genel Rapor", "Performans raporunuzu görmek için giriş yapın."); return; }
                this.renderReport();
                break;
            case "timer":
                this.initTimerPage();
                break;
            case "planner":
                this.initPlannerPage();
                break;
            case "settings":
                await this.renderSettings();
                break;
            case "guide":
                this.showGuidePage();
                break;


        }
        lucide.createIcons();
    }

    static showGuidePage() {
        this.closeSidebar();
        document.querySelectorAll(".page-view").forEach(p => p.style.display = "none");
        const guideEl = document.getElementById("page-guide");
        if (guideEl) {
            guideEl.style.display = "block";
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        document.querySelectorAll(".nav-item").forEach(item => {
            item.classList.toggle("active", item.getAttribute("data-page") === "guide");
        });
        this.state.currentPage = "guide";
        lucide.createIcons();
    }


    // --- 1. DASHBOARD RENDERER ---
    static async renderDashboard() {
        const chartsGrid = document.querySelector(".charts-grid");
        if (chartsGrid) chartsGrid.style.display = "";
        const expBox = document.getElementById("dashExplanationBox");
        if (expBox) expBox.style.display = "";

        const examTypeId = document.getElementById("dashExamTypeSelect")?.value || this.state.selectedExamTypeId;
        this.updateExamCountdownCard(examTypeId);
        const startDate = document.getElementById("dashStartDate")?.value;

        const endDate = document.getElementById("dashEndDate")?.value;

        const params = {};
        if (examTypeId) params.exam_type_id = examTypeId;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        try {
            const data = await ApiService.getDashboard(params);
            const metrics = data.metrics;

            // Render Metric Cards
            const cardsContainer = document.getElementById("dashMetricCards");
            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Son Deneme Neti</span>
                            <div class="metric-icon" style="background:rgba(59,130,246,0.15); color:#60a5fa;"><i data-lucide="award"></i></div>
                        </div>
                        <div class="metric-value">${metrics.latest_exam_total_net !== null ? metrics.latest_exam_total_net.toFixed(2) : '-'}</div>
                        <div class="metric-sub">Son denemeden elde edilen toplam net</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Genel Net Ortalaması</span>
                            <div class="metric-icon" style="background:rgba(99,102,241,0.15); color:#818cf8;"><i data-lucide="calculator"></i></div>
                        </div>
                        <div class="metric-value">${metrics.overall_net_average !== null ? metrics.overall_net_average.toFixed(2) : '-'}</div>
                        <div class="metric-sub">Tüm denemelerin ortalaması (${metrics.total_exams_count} deneme)</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Son 3 Deneme Ortalaması</span>
                            <div class="metric-icon" style="background:rgba(139,92,246,0.15); color:#c084fc;"><i data-lucide="trending-up"></i></div>
                        </div>
                        <div class="metric-value">${metrics.last_3_net_average !== null ? metrics.last_3_net_average.toFixed(2) : '-'}</div>
                        <div class="metric-sub">Son dönem kısa vadeli ortalama</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Son 5 Deneme Ortalaması</span>
                            <div class="metric-icon" style="background:rgba(16,185,129,0.15); color:#34d399;"><i data-lucide="activity"></i></div>
                        </div>
                        <div class="metric-value">${metrics.last_5_net_average !== null ? metrics.last_5_net_average.toFixed(2) : '-'}</div>
                        <div class="metric-sub">Performans istikrar ölçütü</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">En Yüksek / En Düşük Net</span>
                            <div class="metric-icon" style="background:rgba(245,158,11,0.15); color:#fbbf24;"><i data-lucide="bar-chart-3"></i></div>
                        </div>
                        <div class="metric-value" style="font-size:1.4rem;">
                            <span style="color:var(--success-text)">${metrics.highest_total_net !== null ? metrics.highest_total_net.toFixed(2) : '-'}</span> / 
                            <span style="color:var(--danger-text)">${metrics.lowest_total_net !== null ? metrics.lowest_total_net.toFixed(2) : '-'}</span>
                        </div>
                        <div class="metric-sub">Zirve ve taban netler</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">Hedef Net / Kalan Fark</span>
                            <div class="metric-icon" style="background:rgba(244,63,94,0.15); color:#fb7185;"><i data-lucide="target"></i></div>
                        </div>
                        <div class="metric-value" style="font-size:1.4rem;">
                            ${metrics.target_net > 0 ? metrics.target_net.toFixed(2) : 'Tanımsız'} 
                            ${metrics.target_net_diff !== null ? `<span class="badge ${metrics.target_net_diff <= 0 ? 'badge-success' : 'badge-danger'}">${metrics.target_net_diff <= 0 ? 'Aşıldı' : metrics.target_net_diff.toFixed(2) + ' net'}</span>` : ''}
                        </div>
                        <div class="metric-sub">Belirlenen genel hedef net</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">En Çok Gelişen Ders</span>
                            <div class="metric-icon" style="background:rgba(16,185,129,0.15); color:#34d399;"><i data-lucide="arrow-up-right"></i></div>
                        </div>
                        <div class="metric-value" style="font-size:1.3rem; color:var(--success-text)">${metrics.most_improved_course || 'Veri Yetersiz'}</div>
                        <div class="metric-sub">Son dönemde en yüksek net artışı</div>
                    </div>

                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-title">En Çok Düşen Ders</span>
                            <div class="metric-icon" style="background:rgba(244,63,94,0.15); color:#fb7185;"><i data-lucide="arrow-down-right"></i></div>
                        </div>
                        <div class="metric-value" style="font-size:1.3rem; color:var(--danger-text)">${metrics.most_declined_course || 'Yok'}</div>
                        <div class="metric-sub">Son dönemde net gerilemesi</div>
                    </div>
                `;
            }

            // Render Explanations Box
            const expList = document.getElementById("dashExplanationList");
            if (expList) {
                expList.innerHTML = metrics.explanations.map(exp => `
                    <li class="explanation-item">
                        <div class="explanation-bullet"></div>
                        <div>${exp}</div>
                    </li>
                `).join('');
            }

            // Render Charts
            ChartManager.renderTrendChart("chartTrend", data.charts.trend_chart);
            ChartManager.renderLatestCoursesChart("chartLatestCourses", data.charts.latest_exam_courses);
            ChartManager.renderAnswersBreakdownChart("chartAnswersBreakdown", data.charts.answers_breakdown);
            ChartManager.renderTargetVsLast5Chart("chartTargetVsLast5", data.charts.target_vs_last5);

            lucide.createIcons();
        } catch (e) {
            console.error("Dashboard error:", e);
        }
    }

    // --- 2. ADD EXAM FORM & LIVE NET CALCULATOR ---
    static async renderAddExamForm() {
        const selectEl = document.getElementById("formExamTypeSelect");
        if (!selectEl) return;

        if (!this.state.examTypes || this.state.examTypes.length === 0) {
            this.state.examTypes = await ApiService.getExamTypes();
            this.populateExamTypeDropdowns();
        }

        if (this.state.examTypes.length === 0) return;

        // Set default date to today
        const dateInput = document.getElementById("formExamDate");
        if (dateInput && !dateInput.value) {
            dateInput.valueAsDate = new Date();
        }

        let selectedTypeId = parseInt(selectEl.value);
        if (isNaN(selectedTypeId) && this.state.examTypes.length > 0) {
            selectedTypeId = this.state.examTypes[0].id;
            selectEl.value = selectedTypeId;
        }

        if (!isNaN(selectedTypeId)) {
            await this.handleExamTypeChangeForForm(selectedTypeId);
        }
    }


    static async handleExamTypeChangeForForm(examTypeId) {
        try {
            let examType = this.state.examTypes.find(et => et.id == examTypeId);
            if (!examType) {
                examType = await ApiService.getExamType(examTypeId);
            }
            if (!examType) return;

            this.state.coursesForCurrentExamType = examType.courses || [];
            this.state.currentPenaltyDivisor = examType.wrong_penalty_divisor || 4.0;

            const container = document.getElementById("courseInputsContainer");
            if (!container) return;

            const courses = examType.courses || [];
            const hasGroups = courses.some(c => c.group_name);

            if (hasGroups) {
                // Group courses
                const groups = {};
                courses.forEach(c => {
                    const g = c.group_name || "Diğer";
                    if (!groups[g]) groups[g] = [];
                    groups[g].push(c);
                });

                container.innerHTML = Object.entries(groups).map(([groupName, groupCourses]) => `
                    <div style="margin-bottom: 1.25rem;">
                        <div style="font-size:0.7rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; color:var(--accent-blue); padding:0.4rem 0.75rem; background:rgba(59,130,246,0.08); border-radius:var(--radius-sm); margin-bottom:0.5rem; border-left:3px solid var(--accent-blue);">
                            ${groupName}
                        </div>
                        ${groupCourses.map(course => `
                        <div class="course-input-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap:1rem; align-items:center; background:var(--bg-secondary); padding:0.85rem 1.25rem; border-radius:var(--radius-md); margin-bottom:0.5rem; border:1px solid var(--border-color);" data-course-id="${course.id}" data-qcount="${course.question_count}">
                            <div>
                                <strong style="font-size:0.95rem;">${course.name}</strong>
                                <span style="font-size:0.75rem; color:var(--text-secondary); display:block;">(Toplam ${course.question_count} Soru)</span>
                            </div>
                            <div>
                                <label style="font-size:0.75rem; color:var(--text-secondary);">Doğru</label>
                                <input type="number" class="text-input course-correct" style="width:100%;" min="0" max="${course.question_count}" value="0">
                            </div>
                            <div>
                                <label style="font-size:0.75rem; color:var(--text-secondary);">Yanlış</label>
                                <input type="number" class="text-input course-wrong" style="width:100%;" min="0" max="${course.question_count}" value="0">
                            </div>
                            <div>
                                <label style="font-size:0.75rem; color:var(--text-secondary);">Boş</label>
                                <input type="number" class="text-input course-blank" style="width:100%;" min="0" max="${course.question_count}" value="${course.question_count}">
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:0.75rem; color:var(--text-secondary); display:block;">Net</span>
                                <strong class="course-net-display" style="font-size:1.1rem; color:var(--accent-blue);">0.00</strong>
                            </div>
                        </div>
                        `).join('')}
                    </div>
                `).join('');
            } else {
                container.innerHTML = courses.map(course => `
                <div class="course-input-row" style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap:1rem; align-items:center; background:var(--bg-secondary); padding:0.85rem 1.25rem; border-radius:var(--radius-md); margin-bottom:0.75rem; border:1px solid var(--border-color);" data-course-id="${course.id}" data-qcount="${course.question_count}">
                    <div>
                        <strong style="font-size:0.95rem;">${course.name}</strong>
                        <span style="font-size:0.75rem; color:var(--text-secondary); display:block;">(Toplam ${course.question_count} Soru)</span>
                    </div>
                    <div>
                        <label style="font-size:0.75rem; color:var(--text-secondary);">Doğru</label>
                        <input type="number" class="text-input course-correct" style="width:100%;" min="0" max="${course.question_count}" value="0">
                    </div>
                    <div>
                        <label style="font-size:0.75rem; color:var(--text-secondary);">Yanlış</label>
                        <input type="number" class="text-input course-wrong" style="width:100%;" min="0" max="${course.question_count}" value="0">
                    </div>
                    <div>
                        <label style="font-size:0.75rem; color:var(--text-secondary);">Boş</label>
                        <input type="number" class="text-input course-blank" style="width:100%;" min="0" max="${course.question_count}" value="${course.question_count}">
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.75rem; color:var(--text-secondary); display:block;">Net</span>
                        <strong class="course-net-display" style="font-size:1.1rem; color:var(--accent-blue);">0.00</strong>
                    </div>
                </div>
                `).join('');
            }


            // Attach input event listeners for live net calculation
            container.querySelectorAll("input").forEach(input => {
                input.addEventListener("input", (e) => {
                    this.recalculateLiveNets();
                });
            });

            this.recalculateLiveNets();
        } catch (e) {
            console.error("Exam type load failed:", e);
        }
    }


    static recalculateLiveNets() {
        let totalCorrect = 0;
        let totalWrong = 0;
        let totalBlank = 0;
        let totalNet = 0.0;
        const penaltyDivisor = this.state.currentPenaltyDivisor || 4.0;

        document.querySelectorAll(".course-input-row").forEach(row => {
            const qCount = parseInt(row.getAttribute("data-qcount"));
            const correctInput = row.querySelector(".course-correct");
            const wrongInput = row.querySelector(".course-wrong");
            const blankInput = row.querySelector(".course-blank");
            const netDisplay = row.querySelector(".course-net-display");

            let c = parseInt(correctInput.value) || 0;
            let w = parseInt(wrongInput.value) || 0;
            let b = parseInt(blankInput.value) || 0;

            // Auto balance blank count if total != qCount
            if (c + w + b !== qCount) {
                b = Math.max(0, qCount - (c + w));
                blankInput.value = b;
            }

            const net = Math.max(-qCount, c - (w / penaltyDivisor));
            netDisplay.textContent = net.toFixed(2);

            totalCorrect += c;
            totalWrong += w;
            totalBlank += b;
            totalNet += net;
        });

        document.getElementById("liveTotalNet").textContent = totalNet.toFixed(2);
        document.getElementById("liveTotalCorrect").textContent = totalCorrect;
        document.getElementById("liveTotalWrong").textContent = totalWrong;
        document.getElementById("liveTotalBlank").textContent = totalBlank;
    }

    static async handleExamFormSubmit() {
        if (!this.requireAuth()) return;
        const examTypeId = parseInt(document.getElementById("formExamTypeSelect").value);

        const name = document.getElementById("formExamName").value.trim();
        const dateVal = document.getElementById("formExamDate").value;
        const publisher = document.getElementById("formPublisher").value.trim() || null;
        const duration = parseInt(document.getElementById("formDuration").value) || null;
        const difficulty = document.getElementById("formDifficulty").value || "Orta";

        if (!name || !dateVal) {
            alert("Lütfen deneme adını ve tarihini girin.");
            return;
        }

        const courseResults = [];
        let hasValidationError = false;

        document.querySelectorAll(".course-input-row").forEach(row => {
            const courseId = parseInt(row.getAttribute("data-course-id"));
            const qCount = parseInt(row.getAttribute("data-qcount"));
            const c = parseInt(row.querySelector(".course-correct").value) || 0;
            const w = parseInt(row.querySelector(".course-wrong").value) || 0;
            const b = parseInt(row.querySelector(".course-blank").value) || 0;

            if (c + w + b > qCount) {
                alert(`Ders için girilen doğru+yanlış+boş toplamı soru sayısını (${qCount}) aşıyor!`);
                hasValidationError = true;
                return;
            }

            courseResults.push({
                course_id: courseId,
                correct_count: c,
                wrong_count: w,
                blank_count: b
            });
        });

        if (hasValidationError) return;

        const payload = {
            exam_type_id: examTypeId,
            name: name,
            publisher: publisher,
            exam_date: dateVal,
            duration_minutes: duration,
            difficulty: difficulty,
            course_results: courseResults
        };

        // Show confirmation modal before saving
        const totalNetStr = document.getElementById("liveTotalNet").textContent;
        this.showModal({
            title: "Deneme Kaydı Onayı",
            body: `
                <p style="margin-bottom:1rem;">Aşağıdaki deneme sınavı veritabanına kaydedilecek:</p>
                <ul>
                    <li><b>Deneme Adı:</b> ${name}</li>
                    <li><b>Tarih:</b> ${dateVal}</li>
                    <li><b>Hesaplanan Toplam Net:</b> <span style="color:var(--accent-blue); font-weight:700;">${totalNetStr}</span></li>
                </ul>
            `,
            confirmText: "Kaydet",
            onConfirm: async () => {
                try {
                    await ApiService.createExam(payload);
                    this.closeModal();
                    alert("Deneme sınavı başarıyla kaydedildi!");
                    this.navigateTo("exam_history");
                } catch (err) {
                    alert(`Hata: ${err.message}`);
                }
            }
        });
    }

    // --- 3. EXAM HISTORY RENDERER ---
    static async renderExamHistory() {
        const activeExamTypeId = this.state.selectedExamTypeId;
        const params = {};
        if (activeExamTypeId) params.exam_type_id = activeExamTypeId;

        // Update export links
        const queryStr = new URLSearchParams(params).toString();
        document.getElementById("btnExportCSV").href = `/api/exams/export/csv${queryStr ? '?' + queryStr : ''}`;
        document.getElementById("btnExportExcel").href = `/api/exams/export/excel${queryStr ? '?' + queryStr : ''}`;


        try {
            const exams = await ApiService.getExams(params);
            const tbody = document.getElementById("historyTableBody");
            if (!tbody) return;

            if (exams.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">Henüz kayıtlı deneme bulunamadı.</td></tr>`;
                return;
            }

            tbody.innerHTML = exams.map(exam => `
                <tr>
                    <td>${new Date(exam.exam_date).toLocaleDateString('tr-TR')}</td>
                    <td><strong>${exam.name}</strong> ${exam.publisher ? `<span style="font-size:0.8rem; color:var(--text-secondary);">(${exam.publisher})</span>` : ''}</td>
                    <td><span class="badge badge-neutral">${exam.exam_type_name}</span></td>
                    <td style="color:var(--success-text); font-weight:600;">${exam.total_correct}</td>
                    <td style="color:var(--danger-text); font-weight:600;">${exam.total_wrong}</td>
                    <td style="color:var(--text-muted); font-weight:600;">${exam.total_blank}</td>
                    <td style="font-size:1.1rem; font-weight:700; color:var(--accent-blue);">${exam.total_net.toFixed(2)}</td>
                    <td>
                        <button type="button" class="btn btn-secondary btn-view-details" data-exam-id="${exam.id}" onclick="window.viewExamDetails(${exam.id}); return false;" style="padding:0.3rem 0.6rem; font-size:0.8rem;"><i data-lucide="eye"></i> Detay</button>
                        <button type="button" class="btn btn-danger btn-delete-exam" data-exam-id="${exam.id}" onclick="window.confirmDeleteExam(${exam.id}); return false;" style="padding:0.3rem 0.6rem; font-size:0.8rem;"><i data-lucide="trash-2"></i> Sil</button>
                    </td>
                </tr>
            `).join('');

            tbody.querySelectorAll(".btn-view-details").forEach(btn => {
                btn.onclick = (e) => {
                    e.preventDefault();
                    const examId = parseInt(btn.getAttribute("data-exam-id"));
                    this.viewExamDetails(examId);
                };
            });

            tbody.querySelectorAll(".btn-delete-exam").forEach(btn => {
                btn.onclick = (e) => {
                    e.preventDefault();
                    const examId = parseInt(btn.getAttribute("data-exam-id"));
                    this.confirmDeleteExam(examId);
                };
            });

            if (window.lucide) {
                lucide.createIcons();
            }
        } catch (e) {
            console.error("Exam history error:", e);
        }
    }

    static async viewExamDetails(examId) {
        if (!examId) return;
        try {
            const exam = await ApiService.getExam(examId);
            if (!exam) return;

            const courseRows = (exam.course_results || []).map(cr => `
                <tr>
                    <td><strong>${cr.course_name}</strong></td>
                    <td style="color:var(--success-text); font-weight:600;">${cr.correct_count}</td>
                    <td style="color:var(--danger-text); font-weight:600;">${cr.wrong_count}</td>
                    <td style="color:var(--text-muted); font-weight:600;">${cr.blank_count}</td>
                    <td style="font-size:1rem; font-weight:700; color:var(--accent-blue);">${cr.net.toFixed(2)}</td>
                </tr>
            `).join('');

            const detailsHtml = `
                <div style="margin-bottom:1.25rem; font-size:0.9rem; line-height:1.6; background:var(--bg-card); padding:1rem; border-radius:var(--radius-md); border:1px solid var(--border-color);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <strong>Sınav Türü:</strong>
                        <span class="badge badge-neutral">${exam.exam_type_name}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <strong>Tarih:</strong>
                        <span>${new Date(exam.exam_date).toLocaleDateString('tr-TR')}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <strong>Yayın / Açıklama:</strong>
                        <span>${exam.publisher || '-'}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed var(--border-color); pt-2; margin-top:0.5rem; padding-top:0.5rem;">
                        <strong>Toplam Net:</strong>
                        <strong style="color:var(--accent-blue); font-size:1.3rem;">${exam.total_net.toFixed(2)}</strong>
                    </div>
                </div>
                <h4 style="font-size:0.95rem; margin-bottom:0.5rem;">Ders Bazlı Sonuçlar:</h4>
                <table class="custom-table" style="font-size:0.85rem;">
                    <thead>
                        <tr><th>Ders Adı</th><th>Doğru</th><th>Yanlış</th><th>Boş</th><th>Net</th></tr>
                    </thead>
                    <tbody>
                        ${courseRows}
                    </tbody>
                </table>
            `;

            this.showModal({
                title: `Deneme Detayı: ${exam.name}`,
                body: detailsHtml,
                confirmText: "Kapat",
                onConfirm: () => this.closeModal()
            });
        } catch (e) {
            alert(`Hata: ${e.message}`);
        }
    }

    static confirmDeleteExam(examId) {
        if (!examId) return;

        this.showModal({
            title: "Deneme Sınavını Sil",
            body: `
                <div style="text-align:center; padding: 1.25rem 0.5rem 0.5rem 0.5rem;">
                    <div style="width:60px; height:60px; border-radius:50%; background:rgba(239,68,68,0.15); color:var(--danger-text); display:flex; align-items:center; justify-content:center; margin:0 auto 1.25rem auto; font-size:1.6rem; border:1px solid rgba(239,68,68,0.3);">
                        <i data-lucide="alert-triangle"></i>
                    </div>
                    <h4 style="font-size:1.15rem; margin-bottom:0.6rem; color:var(--text-primary); font-weight:700;">Bu deneme sınavını silmek istediğinizden emin misiniz?</h4>
                    <p style="color:var(--text-secondary); font-size:0.9rem; line-height:1.5; max-width:380px; margin:0 auto;">
                        Bu deneme kaydı veritabanınızdan kalıcı olarak silinecektir. Tüm istatistikleriniz ve net ortalamalarınız güncellenecektir. Bu işlem geri alınamaz.
                    </p>
                </div>
            `,
            confirmText: "Evet, Denemeyi Sil",
            isDanger: true,
            onConfirm: async () => {
                try {
                    await ApiService.deleteExam(examId);
                    this.closeModal();
                    await this.renderExamHistory();
                    this.state.examTypes = await ApiService.getExamTypes();
                    this.populateExamTypeDropdowns();
                } catch (e) {
                    alert(`Silme hatası: ${e.message}`);
                }
            }

        });

        if (window.lucide) {
            lucide.createIcons();
        }
    }



    // --- 4. COURSE ANALYSIS RENDERER ---
    static async initCourseAnalysisPage() {
        const select = document.getElementById("analysisCourseSelect");
        if (!select) return;

        try {
            const courses = await ApiService.getCourses(this.state.selectedExamTypeId);

            // Check if any course has group_name → use optgroup
            const hasGroups = courses.some(c => c.group_name);
            if (hasGroups) {
                const groups = {};
                courses.forEach(c => {
                    const g = c.group_name || "Diğer";
                    if (!groups[g]) groups[g] = [];
                    groups[g].push(c);
                });
                select.innerHTML = Object.entries(groups).map(([groupName, groupCourses]) => `
                    <optgroup label="${groupName}">
                        ${groupCourses.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                    </optgroup>
                `).join('');
            } else {
                select.innerHTML = courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }

            if (courses.length > 0) {
                this.renderCourseAnalysis(courses[0].id);
            }
        } catch (e) {
            console.error("Course list error:", e);
        }
    }


    static async renderCourseAnalysis(courseId) {
        if (!courseId) return;

        try {
            const data = await ApiService.getCourseAnalysis(courseId);
            const m = data.metrics;

            // Render Cards
            const cardsContainer = document.getElementById("courseMetricCards");
            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="metric-card">
                        <span class="metric-title">Son Denemedeki Net</span>
                        <div class="metric-value">${m.latest_net.toFixed(2)}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Genel Net Ortalaması</span>
                        <div class="metric-value">${m.overall_avg_net.toFixed(2)}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Son 3 Ortalaması</span>
                        <div class="metric-value">${m.last_3_avg_net.toFixed(2)}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Doğru / Yanlış / Boş Ort.</span>
                        <div class="metric-value" style="font-size:1.3rem;">
                            <span style="color:var(--success-text)">${m.correct_avg}</span> / 
                            <span style="color:var(--danger-text)">${m.wrong_avg}</span> / 
                            <span style="color:var(--text-muted)">${m.blank_avg}</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Standart Sapma (İstikrar)</span>
                        <div class="metric-value">${m.std_dev.toFixed(2)}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Ders Hedefi / Fark</span>
                        <div class="metric-value" style="font-size:1.3rem;">
                            ${m.target_net > 0 ? m.target_net.toFixed(2) : 'Tanımsız'}
                            ${m.target_net > 0 ? `<span class="badge ${m.target_diff <= 0 ? 'badge-success' : 'badge-danger'}">${m.target_diff <= 0 ? 'Aşıldı' : m.target_diff.toFixed(2) + ' eksi'}</span>` : ''}
                        </div>
                    </div>
                `;
            }

            // Render Explanations
            const expList = document.getElementById("courseExplanationList");
            if (expList) {
                expList.innerHTML = m.explanations.map(e => `
                    <li class="explanation-item">
                        <div class="explanation-bullet"></div>
                        <div>${e}</div>
                    </li>
                `).join('');
            }

            // Render Chart
            ChartManager.renderCourseTrendChart("chartCourseTrend", data.chart_data);

            // Render Table
            const tbody = document.getElementById("courseComparisonTableBody");
            if (tbody) {
                tbody.innerHTML = data.comparison_table.map(row => `
                    <tr>
                        <td>${row.exam_date_str}</td>
                        <td>${row.exam_name}</td>
                        <td style="color:var(--success-text)">${row.correct_count}</td>
                        <td style="color:var(--danger-text)">${row.wrong_count}</td>
                        <td style="color:var(--text-muted)">${row.blank_count}</td>
                        <td style="font-weight:700; color:var(--accent-blue);">${row.net.toFixed(2)}</td>
                    </tr>
                `).join('');
            }
        } catch (e) {
            console.error("Course analysis error:", e);
        }
    }

    // --- 5. GOALS RENDERER ---
    static async renderGoals(examTypeId = null) {
        const selectedId = examTypeId || document.getElementById("goalsExamTypeSelect")?.value || this.state.selectedExamTypeId;
        try {
            const data = await ApiService.getGoals(selectedId);

            const cardsContainer = document.getElementById("goalsMetricCards");
            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="metric-card">
                        <span class="metric-title">Hedef Toplam Net</span>
                        <div class="metric-value">${data.target_total_net > 0 ? data.target_total_net.toFixed(2) : 'Tanımsız'}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Son Deneme vs Hedef</span>
                        <div class="metric-value" style="font-size:1.4rem;">
                            ${data.latest_exam_net !== null ? data.latest_exam_net.toFixed(2) : '-'} 
                            ${data.latest_vs_target_diff !== null ? `<span class="badge ${data.latest_vs_target_diff <= 0 ? 'badge-success' : 'badge-danger'}">${data.latest_vs_target_diff <= 0 ? 'Aşıldı' : data.latest_vs_target_diff.toFixed(2) + ' eksi'}</span>` : ''}
                        </div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Son 5 Ort. vs Hedef</span>
                        <div class="metric-value" style="font-size:1.4rem;">
                            ${data.last_5_avg_net !== null ? data.last_5_avg_net.toFixed(2) : '-'} 
                            ${data.last_5_vs_target_diff !== null ? `<span class="badge ${data.last_5_vs_target_diff <= 0 ? 'badge-success' : 'badge-danger'}">${data.last_5_vs_target_diff <= 0 ? 'Aşıldı' : data.last_5_vs_target_diff.toFixed(2) + ' eksi'}</span>` : ''}
                        </div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Hedefe En Yakın Ders</span>
                        <div class="metric-value" style="font-size:1.3rem; color:var(--success-text)">
                            ${data.closest_course_to_target ? data.closest_course_to_target.course_name : 'Yok'}
                        </div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Hedefe En Uzak Ders</span>
                        <div class="metric-value" style="font-size:1.3rem; color:var(--danger-text)">
                            ${data.furthest_course_to_target ? data.furthest_course_to_target.course_name : 'Yok'}
                        </div>
                    </div>
                `;
            }

            const expList = document.getElementById("goalsExplanationList");
            if (expList) {
                expList.innerHTML = data.explanations.map(e => `
                    <li class="explanation-item">
                        <div class="explanation-bullet"></div>
                        <div>${e}</div>
                    </li>
                `).join('');
            }

            const tbody = document.getElementById("courseGoalsTableBody");
            if (tbody) {
                tbody.innerHTML = data.course_goals.map(cg => `
                    <tr>
                        <td><strong>${cg.course_name}</strong></td>
                        <td>${cg.question_count}</td>
                        <td>${cg.target_net > 0 ? cg.target_net.toFixed(2) : '-'}</td>
                        <td>${cg.current_avg_net.toFixed(2)}</td>
                        <td>${cg.target_net > 0 ? cg.difference.toFixed(2) : '-'}</td>
                        <td>
                            ${cg.target_net > 0 ? 
                                `<span class="badge ${cg.is_reached ? 'badge-success' : 'badge-danger'}">${cg.is_reached ? 'Hedef Ulaşıldı' : 'Gelişim Gerekiyor'}</span>` 
                                : '<span class="badge badge-neutral">Hedef Yok</span>'}
                        </td>
                    </tr>
                `).join('');
            }
        } catch (e) {
            console.error("Goals error:", e);
        }
    }

    // --- 6. REPORT RENDERER ---
    static async renderReport() {
        const activeExamTypeId = this.state.selectedExamTypeId;
        const params = {};
        if (activeExamTypeId) params.exam_type_id = activeExamTypeId;

        const queryStr = new URLSearchParams(params).toString();
        document.getElementById("btnReportCSV").href = `/api/report/export/csv${queryStr ? '?' + queryStr : ''}`;
        document.getElementById("btnReportExcel").href = `/api/report/export/excel${queryStr ? '?' + queryStr : ''}`;


        try {
            const data = await ApiService.getReport(params);

            const cardsContainer = document.getElementById("reportMetricCards");
            if (cardsContainer) {
                cardsContainer.innerHTML = `
                    <div class="metric-card">
                        <span class="metric-title">Tarih Aralığı / Deneme Sayısı</span>
                        <div class="metric-value">${data.exam_count} Deneme</div>
                        <div class="metric-sub">${data.start_date} - ${data.end_date}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">İlk vs Son Deneme Neti</span>
                        <div class="metric-value" style="font-size:1.4rem;">
                            ${data.first_exam_net !== null ? data.first_exam_net.toFixed(2) : '-'} ➔ ${data.last_exam_net !== null ? data.last_exam_net.toFixed(2) : '-'}
                        </div>
                        <div class="metric-sub">Net Değişimi: <strong style="color:${data.net_change >= 0 ? 'var(--success-text)' : 'var(--danger-text)'}">${data.net_change !== null ? (data.net_change >= 0 ? '+' : '') + data.net_change.toFixed(2) : '-'}</strong></div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Ortalama Net</span>
                        <div class="metric-value">${data.average_net !== null ? data.average_net.toFixed(2) : '-'}</div>
                    </div>
                    <div class="metric-card">
                        <span class="metric-title">Performans İstikrarı</span>
                        <div class="metric-value" style="font-size:1.3rem;">
                            <span class="badge badge-neutral">${data.stability_status || 'Yetersiz Veri'}</span>
                        </div>
                    </div>
                `;
            }

            const expList = document.getElementById("reportExplanationList");
            if (expList) {
                expList.innerHTML = data.explanations.map(e => `
                    <li class="explanation-item">
                        <div class="explanation-bullet"></div>
                        <div>${e}</div>
                    </li>
                `).join('');
            }

            const tbody = document.getElementById("reportCourseTableBody");
            if (tbody) {
                tbody.innerHTML = data.course_summaries.map(c => `
                    <tr>
                        <td><strong>${c.course_name}</strong></td>
                        <td>${c.overall_avg_net.toFixed(2)}</td>
                        <td style="color:var(--success-text)">${c.correct_avg}</td>
                        <td style="color:var(--danger-text)">${c.wrong_avg}</td>
                        <td style="color:var(--text-muted)">${c.blank_avg}</td>
                        <td>${c.period_change !== null ? (c.period_change >= 0 ? '+' : '') + c.period_change.toFixed(2) : '-'}</td>
                    </tr>
                `).join('');
            }
        } catch (e) {
            console.error("Report error:", e);
        }
    }


    // --- 6.5. TIMERS & STOPWATCH CONTROLLER ---

    static timerState = {
        activeTab: "exam",
        exam: {
            minutes: 165,
            remainingSeconds: 165 * 60,
            totalSeconds: 165 * 60,
            isRunning: false,
            interval: null
        },
        pomodoro: {
            workMinutes: 25,
            breakMinutes: 5,
            phase: "work",
            remainingSeconds: 25 * 60,
            totalSeconds: 25 * 60,
            isRunning: false,
            interval: null,
            completedCount: 0
        },
        stopwatch: {
            elapsedSeconds: 0,
            isRunning: false,
            interval: null,
            laps: []
        }
    };

    static initTimerPage() {
        this.bindTimerEventsOnce();
        this.syncExamTimerWithActiveExam();
        this.updateExamClockUI();
        this.updatePomoClockUI();
        this.updateSwClockUI();
    }

    static timerEventsBound = false;
    static bindTimerEventsOnce() {
        if (this.timerEventsBound) return;
        this.timerEventsBound = true;

        // Timer Main Mode Dropdown Selector
        const timerMainModeSelect = document.getElementById("timerMainModeSelect");
        if (timerMainModeSelect) {
            timerMainModeSelect.addEventListener("change", (e) => {
                const mode = e.target.value;
                document.querySelectorAll(".timer-mode-content").forEach(c => c.style.display = "none");
                if (mode === "exam") document.getElementById("timerModeExam").style.display = "block";
                if (mode === "pomodoro") document.getElementById("timerModePomodoro").style.display = "block";
                if (mode === "stopwatch") document.getElementById("timerModeStopwatch").style.display = "block";
            });
        }

        // Exam Mode Preset Dropdown
        const examPresetSelect = document.getElementById("timerExamPresetSelect");
        if (examPresetSelect) {
            examPresetSelect.addEventListener("change", (e) => {
                const mins = parseInt(e.target.value);
                const selectedText = e.target.options[e.target.selectedIndex].text;
                this.setExamTimerMinutes(mins, false);
                const titleEl = document.getElementById("timerExamTitle");
                if (titleEl) titleEl.textContent = selectedText;
            });
        }

        // Exam Mode Controls
        document.getElementById("btnExamStart")?.addEventListener("click", () => this.startExamTimer());
        document.getElementById("btnExamPause")?.addEventListener("click", () => this.pauseExamTimer());
        document.getElementById("btnExamReset")?.addEventListener("click", () => this.resetExamTimer());
        document.getElementById("btnExamFinish")?.addEventListener("click", () => this.finishExamTimerAndSave());

        // Pomodoro Preset Dropdown
        const pomoPresetSelect = document.getElementById("timerPomoPresetSelect");
        if (pomoPresetSelect) {
            pomoPresetSelect.addEventListener("change", (e) => {
                const [workStr, breakStr] = e.target.value.split('-');
                const work = parseInt(workStr);
                const brk = parseInt(breakStr);
                this.setPomoTimes(work, brk);
            });
        }

        // Pomodoro Controls
        document.getElementById("btnPomoStart")?.addEventListener("click", () => this.startPomoTimer());
        document.getElementById("btnPomoPause")?.addEventListener("click", () => this.pausePomoTimer());
        document.getElementById("btnPomoReset")?.addEventListener("click", () => this.resetPomoTimer());

        // Stopwatch Controls
        document.getElementById("btnSwStart")?.addEventListener("click", () => this.startSwTimer());
        document.getElementById("btnSwPause")?.addEventListener("click", () => this.pauseSwTimer());
        document.getElementById("btnSwLap")?.addEventListener("click", () => this.addSwLap());
        document.getElementById("btnSwReset")?.addEventListener("click", () => this.resetSwTimer());
    }

    static syncExamTimerWithActiveExam() {
        const activeId = this.state.selectedExamTypeId;
        const examType = this.state.examTypes.find(et => et.id == activeId);
        let mins = 165;
        let title = "YKS - TYT (165 Dk)";

        if (examType) {
            const name = examType.name.toLowerCase();
            if (name.includes("ayt")) { mins = 180; title = "YKS - AYT (180 Dk)"; }
            else if (name.includes("dus")) { mins = 150; title = `${examType.name} (150 Dk)`; }
            else if (name.includes("tus")) { mins = 135; title = `${examType.name} (135 Dk)`; }
            else if (name.includes("kpss")) { mins = 130; title = "KPSS (130 Dk)"; }
            else if (name.includes("lgs")) { mins = 75; title = "LGS (75 Dk)"; }
            else { mins = 165; title = `${examType.name} (165 Dk)`; }
        }

        const selectEl = document.getElementById("timerExamPresetSelect");
        if (selectEl) {
            let found = false;
            for (let opt of selectEl.options) {
                if (opt.value == mins) {
                    selectEl.value = mins;
                    found = true;
                    break;
                }
            }
            if (!found) {
                const newOpt = new Option(title, mins, true, true);
                selectEl.add(newOpt, 0);
            }
        }

        const titleEl = document.getElementById("timerExamTitle");
        if (titleEl) titleEl.textContent = title;

        if (!this.timerState.exam.isRunning) {
            this.setExamTimerMinutes(mins, false);
        }
    }

    static setExamTimerMinutes(mins, updateTitle = true) {
        this.pauseExamTimer();
        this.timerState.exam.minutes = mins;
        this.timerState.exam.totalSeconds = mins * 60;
        this.timerState.exam.remainingSeconds = mins * 60;
        if (updateTitle) {
            const titleEl = document.getElementById("timerExamTitle");
            if (titleEl) titleEl.textContent = `${mins} Dakika`;
        }
        this.updateExamClockUI();
    }

    static startExamTimer() {
        if (this.timerState.exam.isRunning) return;
        this.timerState.exam.isRunning = true;
        document.getElementById("btnExamStart").style.display = "none";
        document.getElementById("btnExamPause").style.display = "inline-flex";

        this.timerState.exam.interval = setInterval(() => {
            if (this.timerState.exam.remainingSeconds > 0) {
                this.timerState.exam.remainingSeconds--;
                this.updateExamClockUI();
            } else {
                this.pauseExamTimer();
                this.playBeepSound();
                alert("Süre Doldu! Deneme sınavı süreniz bitti.");
            }
        }, 1000);
    }

    static pauseExamTimer() {
        this.timerState.exam.isRunning = false;
        if (this.timerState.exam.interval) {
            clearInterval(this.timerState.exam.interval);
            this.timerState.exam.interval = null;
        }
        const startBtn = document.getElementById("btnExamStart");
        const pauseBtn = document.getElementById("btnExamPause");
        if (startBtn) startBtn.style.display = "inline-flex";
        if (pauseBtn) pauseBtn.style.display = "none";
    }

    static resetExamTimer() {
        this.pauseExamTimer();
        this.timerState.exam.remainingSeconds = this.timerState.exam.totalSeconds;
        this.updateExamClockUI();
    }

    static async finishExamTimerAndSave() {
        const elapsedSecs = this.timerState.exam.totalSeconds - this.timerState.exam.remainingSeconds;
        const elapsedMins = Math.max(1, Math.round(elapsedSecs / 60));
        this.pauseExamTimer();

        // Navigate to add_exam page
        this.navigateTo("add_exam");
        const durationInput = document.getElementById("formDurationMinutes");
        if (durationInput) {
            durationInput.value = elapsedMins;
        }
    }

    static updateExamClockUI() {
        const secs = this.timerState.exam.remainingSeconds;
        const hrs = Math.floor(secs / 3600);
        const mins = Math.floor((secs % 3600) / 60);
        const s = secs % 60;

        const formatted = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        const clockEl = document.getElementById("examClockDisplay");
        if (clockEl) clockEl.textContent = formatted;

        const barEl = document.getElementById("examProgressBar");
        if (barEl && this.timerState.exam.totalSeconds > 0) {
            const pct = (secs / this.timerState.exam.totalSeconds) * 100;
            barEl.style.width = `${pct}%`;
        }
    }

    // --- POMODORO METODLARI ---
    static setPomoTimes(work, brk) {
        this.pausePomoTimer();
        this.timerState.pomodoro.workMinutes = work;
        this.timerState.pomodoro.breakMinutes = brk;
        this.timerState.pomodoro.phase = "work";
        this.timerState.pomodoro.totalSeconds = work * 60;
        this.timerState.pomodoro.remainingSeconds = work * 60;
        this.updatePomoClockUI();
    }

    static startPomoTimer() {
        if (this.timerState.pomodoro.isRunning) return;
        this.timerState.pomodoro.isRunning = true;
        document.getElementById("btnPomoStart").style.display = "none";
        document.getElementById("btnPomoPause").style.display = "inline-flex";

        this.timerState.pomodoro.interval = setInterval(() => {
            if (this.timerState.pomodoro.remainingSeconds > 0) {
                this.timerState.pomodoro.remainingSeconds--;
                this.updatePomoClockUI();
            } else {
                this.pausePomoTimer();
                this.playBeepSound();
                if (this.timerState.pomodoro.phase === "work") {
                    this.timerState.pomodoro.completedCount++;
                    this.timerState.pomodoro.phase = "break";
                    this.timerState.pomodoro.totalSeconds = this.timerState.pomodoro.breakMinutes * 60;
                    this.timerState.pomodoro.remainingSeconds = this.timerState.pomodoro.breakMinutes * 60;
                    alert("Tebrikler! Odaklanma süreniz bitti. Şimdi Mola Zamanı");

                } else {
                    this.timerState.pomodoro.phase = "work";
                    this.timerState.pomodoro.totalSeconds = this.timerState.pomodoro.workMinutes * 60;
                    this.timerState.pomodoro.remainingSeconds = this.timerState.pomodoro.workMinutes * 60;
                    alert("Mola Bitti! Yeni çalışma seansına hazır mısınız?");
                }
                this.updatePomoClockUI();
            }
        }, 1000);
    }

    static pausePomoTimer() {
        this.timerState.pomodoro.isRunning = false;
        if (this.timerState.pomodoro.interval) {
            clearInterval(this.timerState.pomodoro.interval);
            this.timerState.pomodoro.interval = null;
        }
        const startBtn = document.getElementById("btnPomoStart");
        const pauseBtn = document.getElementById("btnPomoPause");
        if (startBtn) startBtn.style.display = "inline-flex";
        if (pauseBtn) pauseBtn.style.display = "none";
    }

    static resetPomoTimer() {
        this.pausePomoTimer();
        this.timerState.pomodoro.phase = "work";
        this.timerState.pomodoro.totalSeconds = this.timerState.pomodoro.workMinutes * 60;
        this.timerState.pomodoro.remainingSeconds = this.timerState.pomodoro.workMinutes * 60;
        this.updatePomoClockUI();
    }

    static updatePomoClockUI() {
        const secs = this.timerState.pomodoro.remainingSeconds;
        const mins = Math.floor(secs / 60);
        const s = secs % 60;

        const formatted = `${String(mins).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        const clockEl = document.getElementById("pomoClockDisplay");
        if (clockEl) clockEl.textContent = formatted;

        const titleEl = document.getElementById("pomodoroPhaseTitle");
        if (titleEl) {
            if (this.timerState.pomodoro.phase === "work") {
                titleEl.textContent = "Odaklanma Süresi (Çalışma)";
                titleEl.style.color = "var(--accent-emerald)";
            } else {
                titleEl.textContent = "Mola Süresi (Dinlenme)";
                titleEl.style.color = "var(--accent-blue)";
            }
        }


        const countEl = document.getElementById("pomoCountDisplay");
        if (countEl) {
            countEl.innerHTML = `Bugün Tamamlanan Pomodoro: <strong>${this.timerState.pomodoro.completedCount} Session</strong>`;
        }

    }

    // --- STOPWATCH METODLARI ---
    static startSwTimer() {
        if (this.timerState.stopwatch.isRunning) return;
        this.timerState.stopwatch.isRunning = true;
        document.getElementById("btnSwStart").style.display = "none";
        document.getElementById("btnSwPause").style.display = "inline-flex";

        this.timerState.stopwatch.interval = setInterval(() => {
            this.timerState.stopwatch.elapsedSeconds++;
            this.updateSwClockUI();
        }, 1000);
    }

    static pauseSwTimer() {
        this.timerState.stopwatch.isRunning = false;
        if (this.timerState.stopwatch.interval) {
            clearInterval(this.timerState.stopwatch.interval);
            this.timerState.stopwatch.interval = null;
        }
        const startBtn = document.getElementById("btnSwStart");
        const pauseBtn = document.getElementById("btnSwPause");
        if (startBtn) startBtn.style.display = "inline-flex";
        if (pauseBtn) pauseBtn.style.display = "none";
    }

    static resetSwTimer() {
        this.pauseSwTimer();
        this.timerState.stopwatch.elapsedSeconds = 0;
        this.timerState.stopwatch.laps = [];
        this.updateSwClockUI();
        this.renderSwLaps();
    }

    static addSwLap() {
        const secs = this.timerState.stopwatch.elapsedSeconds;
        if (secs === 0) return;
        const lapNum = this.timerState.stopwatch.laps.length + 1;
        
        const hrs = Math.floor(secs / 3600);
        const mins = Math.floor((secs % 3600) / 60);
        const s = secs % 60;
        const formatted = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(s).padStart(2, '0')}`;

        this.timerState.stopwatch.laps.unshift({ num: lapNum, time: formatted });
        this.renderSwLaps();
    }

    static renderSwLaps() {
        const listEl = document.getElementById("swLapList");
        if (!listEl) return;
        if (this.timerState.stopwatch.laps.length === 0) {
            listEl.innerHTML = `<li style="padding:0.75rem; text-align:center; color:var(--text-muted); font-size:0.85rem;">Henüz tur kaydedilmedi.</li>`;
            return;
        }
        listEl.innerHTML = this.timerState.stopwatch.laps.map(l => `
            <li style="padding:0.6rem 0.85rem; background:var(--bg-secondary); border-radius:var(--radius-sm); display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border-color); font-size:0.9rem;">
                <strong>Tur ${l.num}</strong>
                <span style="font-family:monospace; font-weight:700; color:var(--accent-blue);">${l.time}</span>
            </li>
        `).join('');
    }

    static updateSwClockUI() {
        const secs = this.timerState.stopwatch.elapsedSeconds;
        const hrs = Math.floor(secs / 3600);
        const mins = Math.floor((secs % 3600) / 60);
        const s = secs % 60;

        const formatted = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        const clockEl = document.getElementById("swClockDisplay");
        if (clockEl) clockEl.textContent = formatted;
    }

    static playBeepSound() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            osc.type = "sine";
            osc.frequency.setValueAtTime(587.33, ctx.currentTime);
            osc.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.6);
        } catch (e) {}
    }


    // --- 6.8. NOTES & PLANNER CONTROLLER ---
    static plannerEventsBound = false;

    static async initPlannerPage() {
        this.bindPlannerEventsOnce();
        this.populatePlannerCourseDropdowns();
        await this.loadNotes();
        await this.loadTasks();
    }

    static bindPlannerEventsOnce() {
        if (this.plannerEventsBound) return;
        this.plannerEventsBound = true;

        // Planner Tab Dropdown Selector (Sade ve Dikey Format)
        const plannerMainTabSelect = document.getElementById("plannerMainTabSelect");
        if (plannerMainTabSelect) {
            plannerMainTabSelect.addEventListener("change", (e) => {
                const tab = e.target.value;
                document.querySelectorAll(".planner-tab-content").forEach(c => c.style.display = "none");
                if (tab === "notes") document.getElementById("plannerTabNotes").style.display = "block";
                if (tab === "tasks") document.getElementById("plannerTabTasks").style.display = "block";
            });
        }



        // Filter Selects
        document.getElementById("noteFilterCourseSelect")?.addEventListener("change", () => this.loadNotes());
        document.getElementById("noteFilterTypeSelect")?.addEventListener("change", () => this.loadNotes());

        // Modal Open
        document.getElementById("btnOpenCreateNoteModal")?.addEventListener("click", () => this.openNoteEditorModal());

        // Note Editor Form Submit
        document.getElementById("noteEditorForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.saveNoteForm();
        });

        // Task Form Submit
        document.getElementById("createTaskForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.createTaskSubmit();
        });
    }

    static populatePlannerCourseDropdowns() {
        const activeId = this.state.selectedExamTypeId;
        const examType = this.state.examTypes.find(et => et.id == activeId);
        const courses = examType ? examType.courses : [];

        const optionsHtml = courses.map(c => `<option value="${c.name}">${c.name}</option>`).join('');

        const filterSelect = document.getElementById("noteFilterCourseSelect");
        if (filterSelect) {
            filterSelect.innerHTML = `<option value="">Tüm Dersler</option>` + optionsHtml;
        }

        const modalCourseSelect = document.getElementById("noteCourseSelect");
        if (modalCourseSelect) {
            modalCourseSelect.innerHTML = `<option value="">Genel Not</option>` + optionsHtml;
        }

        const taskCourseSelect = document.getElementById("taskCourseSelect");
        if (taskCourseSelect) {
            taskCourseSelect.innerHTML = `<option value="">Genel / Ders Yok</option>` + optionsHtml;
        }
    }

    // --- NOTES METHODS ---
    static async loadNotes() {
        const grid = document.getElementById("notesGrid");
        if (!grid) return;

        try {
            const courseName = document.getElementById("noteFilterCourseSelect")?.value;
            const noteType = document.getElementById("noteFilterTypeSelect")?.value;

            const params = {};
            if (this.state.selectedExamTypeId) params.exam_type_id = this.state.selectedExamTypeId;
            if (courseName) params.course_name = courseName;

            let notes = await ApiService.getNotes(params);

            if (noteType) {
                notes = notes.filter(n => n.note_type === noteType);
            }

            if (notes.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align:center; padding:3rem; color:var(--text-muted);">
                        <i data-lucide="notebook" style="width:48px; height:48px; opacity:0.3; margin-bottom:1rem;"></i>
                        <p>Henüz kaydedilmiş not bulunmuyor. Yeni bir ders notu ekleyebilirsiniz!</p>
                    </div>
                `;
                lucide.createIcons();
                return;
            }

            const typeBadges = {
                general: { label: 'Ders Notu', class: 'badge-neutral' },
                formula: { label: 'Formül & Püf Noktası', class: 'badge-primary' },
                mistake: { label: 'Yanlış Sorular', class: 'badge-danger' },
                reminder: { label: 'Önemli Hatırlatma', class: 'badge-warning' }
            };


            grid.innerHTML = notes.map(n => {
                const badge = typeBadges[n.note_type] || typeBadges.general;
                const formattedDate = new Date(n.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });

                return `
                    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; position:relative;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem; gap:0.5rem;">
                                <span class="badge ${badge.class}">${badge.label}</span>
                                ${n.course_name ? `<span style="font-size:0.75rem; font-weight:700; color:var(--accent-blue); background:rgba(59,130,246,0.1); padding:0.2rem 0.5rem; border-radius:4px;">${n.course_name}</span>` : ''}
                            </div>
                            <h4 style="font-size:1.05rem; font-weight:700; margin-bottom:0.5rem; color:var(--text-primary);">${n.title}</h4>
                            <p style="font-size:0.9rem; color:var(--text-secondary); line-height:1.5; white-space:pre-wrap; margin-bottom:1rem;">${n.content}</p>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); pt:0.75rem; margin-top:0.75rem; padding-top:0.75rem;">
                            <span style="font-size:0.75rem; color:var(--text-muted);">${formattedDate}</span>
                            <div style="display:flex; gap:0.4rem;">
                                <button type="button" class="btn btn-sm btn-secondary" onclick="App.openNoteEditorModal(${n.id})" title="Düzenle">
                                    <i data-lucide="edit-2" style="width:14px; height:14px;"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-danger" onclick="App.deleteNote(${n.id})" title="Sil">
                                    <i data-lucide="trash-2" style="width:14px; height:14px;"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            lucide.createIcons();
        } catch (e) {
            console.error("Notes error:", e);
        }
    }

    static async openNoteEditorModal(noteId = null) {
        const modal = document.getElementById("modalNoteEditor");
        const titleEl = document.getElementById("noteEditorModalTitle");
        const editIdInput = document.getElementById("noteEditId");
        const titleInput = document.getElementById("noteTitleInput");
        const courseSelect = document.getElementById("noteCourseSelect");
        const typeSelect = document.getElementById("noteTypeSelect");
        const contentInput = document.getElementById("noteContentInput");

        if (!modal) return;

        if (noteId) {
            titleEl.textContent = "Notu Düzenle";
            editIdInput.value = noteId;

            const notes = await ApiService.getNotes();
            const note = notes.find(n => n.id == noteId);
            if (note) {
                titleInput.value = note.title;
                courseSelect.value = note.course_name || "";
                typeSelect.value = note.note_type || "general";
                contentInput.value = note.content;
            }
        } else {
            titleEl.textContent = "Yeni Ders Notu Ekle";
            editIdInput.value = "";
            titleInput.value = "";
            courseSelect.value = "";
            typeSelect.value = "general";
            contentInput.value = "";
        }

        modal.classList.add("active");
    }

    static closeNoteEditorModal() {
        document.getElementById("modalNoteEditor")?.classList.remove("active");
    }

    static async saveNoteForm() {
        const idInput = document.getElementById("noteEditId");
        const titleInput = document.getElementById("noteTitleInput");
        const courseSelect = document.getElementById("noteCourseSelect");
        const typeSelect = document.getElementById("noteTypeSelect");
        const contentInput = document.getElementById("noteContentInput");

        const id = idInput?.value;
        const title = titleInput?.value.trim();
        const courseName = courseSelect?.value;
        const noteType = typeSelect?.value;
        const content = contentInput?.value.trim();

        if (!title || !content) return;

        const payload = {
            exam_type_id: this.state.selectedExamTypeId,
            course_name: courseName || null,
            title: title,
            note_type: noteType,
            content: content
        };

        try {
            if (id) {
                await ApiService.updateNote(id, payload);
            } else {
                await ApiService.createNote(payload);
            }

            // Reset filters to guarantee immediate visibility
            const filterCourseSelect = document.getElementById("noteFilterCourseSelect");
            const filterTypeSelect = document.getElementById("noteFilterTypeSelect");
            if (filterCourseSelect && courseName) filterCourseSelect.value = courseName;
            if (filterTypeSelect) filterTypeSelect.value = "";

            this.closeNoteEditorModal();
            await this.loadNotes();
        } catch (e) {
            console.error("Save note error:", e);
            alert("Not kaydedilirken bir hata oluştu.");
        }
    }

    static deleteNote(noteId) {
        this.showModal({
            title: "Notu Sil",
            body: "<p style='color:var(--text-secondary); margin-bottom:1rem;'>Bu ders notunu silmek istediğinize emin misiniz? Bu işlem geri alınamaz.</p>",
            confirmText: "Evet, Sil",
            isDanger: true,
            onConfirm: async () => {
                try {
                    await ApiService.deleteNote(noteId);
                    await this.loadNotes();
                } catch (e) {
                    console.error("Delete note error:", e);
                }
            }
        });
    }

    static deleteTask(taskId) {
        this.showModal({
            title: "Görevi Sil",
            body: "<p style='color:var(--text-secondary); margin-bottom:1rem;'>Bu çalışma görevini silmek istediğinize emin misiniz?</p>",
            confirmText: "Evet, Sil",
            isDanger: true,
            onConfirm: async () => {
                try {
                    await ApiService.deleteTask(taskId);
                    await this.loadTasks();
                } catch (e) {
                    console.error("Delete task error:", e);
                }
            }
        });
    }





    // --- 7. SETTINGS RENDERER & DEMO DATA ---
    static async renderSettings() {
        try {
            // Sınav türlerini al
            if (!this.state.examTypes || this.state.examTypes.length === 0) {
                this.state.examTypes = await ApiService.getExamTypes();
            }

            if (!this.state.examTypes || this.state.examTypes.length === 0) {
                // Fallback default types
                this.state.examTypes = [
                    {
                        id: 1, name: "YKS - TYT", wrong_penalty_divisor: 4.0, target_net: 95.0, exam_date: "2027-06-19",
                        courses: [
                            { name: "Türkçe", question_count: 40, target_net: 35.0, group_name: "" },
                            { name: "Sosyal Bilimler", question_count: 20, target_net: 16.0, group_name: "" },
                            { name: "Temel Matematik", question_count: 40, target_net: 32.0, group_name: "" },
                            { name: "Fen Bilimleri", question_count: 20, target_net: 14.0, group_name: "" }
                        ]
                    },
                    {
                        id: 2, name: "YKS - AYT", wrong_penalty_divisor: 4.0, target_net: 65.0, exam_date: "2027-06-20",
                        courses: [
                            { name: "Matematik", question_count: 40, target_net: 30.0, group_name: "Sayısal" },
                            { name: "Fizik", question_count: 14, target_net: 10.0, group_name: "Fen Bilimleri" },
                            { name: "Kimya", question_count: 13, target_net: 10.0, group_name: "Fen Bilimleri" },
                            { name: "Biyoloji", question_count: 13, target_net: 10.0, group_name: "Fen Bilimleri" }
                        ]
                    },
                    {
                        id: 3, name: "LGS (8. Sınıf)", wrong_penalty_divisor: 3.0, target_net: 80.0, exam_date: "2027-06-06",
                        courses: [
                            { name: "Türkçe", question_count: 20, target_net: 18.0, group_name: "Sözel" },
                            { name: "Matematik", question_count: 20, target_net: 16.0, group_name: "Sayısal" },
                            { name: "Fen Bilimleri", question_count: 20, target_net: 17.0, group_name: "Sayısal" },
                            { name: "T.C. İnkılap Tarihi", question_count: 10, target_net: 9.0, group_name: "Sözel" },
                            { name: "Din Kültürü", question_count: 10, target_net: 10.0, group_name: "Sözel" },
                            { name: "Yabancı Dil", question_count: 10, target_net: 9.0, group_name: "Sözel" }
                        ]
                    },
                    {
                        id: 4, name: "KPSS (Genel Yetenek - Genel Kültür)", wrong_penalty_divisor: 4.0, target_net: 85.0, exam_date: "2027-07-18",
                        courses: [
                            { name: "Türkçe", question_count: 30, target_net: 25.0, group_name: "Genel Yetenek" },
                            { name: "Matematik", question_count: 30, target_net: 22.0, group_name: "Genel Yetenek" },
                            { name: "Tarih", question_count: 27, target_net: 20.0, group_name: "Genel Kültür" },
                            { name: "Coğrafya", question_count: 18, target_net: 15.0, group_name: "Genel Kültür" },
                            { name: "Vatandaşlık & Güncel", question_count: 15, target_net: 10.0, group_name: "Genel Kültür" }
                        ]
                    }
                ];
            }

            const listEl = document.getElementById("settingsExamTypeList");
            if (listEl) {
                listEl.innerHTML = this.state.examTypes.map(et => `
                    <li class="settings-type-item" data-id="${et.id}" onclick="App.loadExamTypeIntoSettings(${et.id})">
                        <span>${et.name}</span>
                        <span class="settings-type-badge">${et.courses ? et.courses.length : 0} Ders</span>
                    </li>
                `).join('');
            }

            // İlk sınav türünü hemen yükle
            const firstId = this.state.selectedSettingsExamTypeId || (this.state.examTypes[0] ? this.state.examTypes[0].id : null);
            if (firstId) {
                await this.loadExamTypeIntoSettings(firstId);
            }
        } catch (e) {
            console.error("Settings load error:", e);
        }
    }

    static async loadExamTypeIntoSettings(examTypeId) {
        try {
            this.state.selectedSettingsExamTypeId = examTypeId;

            // Sol listede aktif olanı vurgula
            document.querySelectorAll("#settingsExamTypeList .settings-type-item").forEach(el => {
                const id = parseInt(el.getAttribute("data-id"));
                el.classList.toggle("active", id === examTypeId);
            });

            // Sınav türünü state'ten veya API'den bul
            let et = (this.state.examTypes || []).find(t => t.id === examTypeId);
            if (!et || !et.courses || et.courses.length === 0) {
                try {
                    et = await ApiService.getExamType(examTypeId);
                } catch (err) {
                    console.warn("Could not fetch exam type detail, using cached:", err);
                }
            }

            if (!et) return;

            document.getElementById("editExamTypeId").value = et.id || "";
            document.getElementById("editExamTypeName").value = et.name || "";
            document.getElementById("editPenaltyDivisor").value = et.wrong_penalty_divisor || 4;
            document.getElementById("editTargetNet").value = et.target_net || 0;
            document.getElementById("editExamDate").value = et.exam_date || "";
            document.getElementById("selectedExamTypeTitle").textContent = `Düzenle: ${et.name}`;

            const delBtn = document.getElementById("btnDeleteExamType");
            if (delBtn) delBtn.style.display = "inline-flex";

            const tbody = document.getElementById("editCourseRowsBody");
            if (tbody) {
                tbody.innerHTML = "";
                const courses = et.courses || [];
                courses.forEach(c => {
                    tbody.appendChild(this.createSettingCourseRow(c));
                });
                if (window.lucide) lucide.createIcons();
            }
        } catch (e) {
            console.error("Exam type settings error:", e);
        }
    }

    static createSettingCourseRow(c = {}) {
        const tr = document.createElement("tr");
        tr.className = "setting-course-row";
        tr.setAttribute("draggable", "true");
        tr.innerHTML = `
            <td style="text-align:center; cursor:grab; color:var(--text-muted); font-size:1.1rem; user-select:none;" class="drag-handle" title="Sürükleyip Sırasını Değiştir">&#8942;&#8942;</td>
            <td><input type="text" class="text-input sc-name" value="${c.name || ''}" placeholder="Ders Adı" style="width:100%;" required></td>
            <td><input type="number" class="text-input sc-qcount" value="${c.question_count !== undefined ? c.question_count : 20}" placeholder="Soru Sayısı" style="width:100%;" min="1" required></td>
            <td><input type="number" step="0.5" class="text-input sc-target" value="${c.target_net !== undefined ? c.target_net : 0}" placeholder="Hedef Net" style="width:100%;"></td>
            <td><input type="text" class="text-input sc-group" value="${c.group_name || ''}" placeholder="Grup Adı (opsiyonel)" style="width:100%;"></td>
            <td style="text-align:center;">
                <button type="button" class="btn btn-danger" style="padding:0; width:28px; height:28px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:1.1rem; font-weight:bold; line-height:1;" title="Sil" onclick="this.closest('tr').remove()">&times;</button>
            </td>
        `;
        this.makeRowDraggable(tr);
        return tr;
    }

    static makeRowDraggable(tr) {
        tr.addEventListener("dragstart", (e) => {
            tr.classList.add("dragging");
            e.dataTransfer.effectAllowed = "move";
            e.dataTransfer.setData("text/plain", "");
        });

        tr.addEventListener("dragend", () => {
            tr.classList.remove("dragging");
        });

        tr.addEventListener("dragover", (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            const draggingRow = document.querySelector(".setting-course-row.dragging");
            if (draggingRow && draggingRow !== tr) {
                const tbody = tr.parentNode;
                const bounding = tr.getBoundingClientRect();
                const offset = e.clientY - bounding.top - (bounding.height / 2);
                if (offset > 0) {
                    tbody.insertBefore(draggingRow, tr.nextSibling);
                } else {
                    tbody.insertBefore(draggingRow, tr);
                }
            }
        });
    }

    static addCourseRowToSettingsTable() {
        const tbody = document.getElementById("editCourseRowsBody");
        if (!tbody) return;
        const tr = this.createSettingCourseRow();
        tbody.appendChild(tr);
        if (window.lucide) lucide.createIcons();
    }

    static handleCreateNewExamType() {
        this.state.selectedSettingsExamTypeId = null;
        document.querySelectorAll("#settingsExamTypeList .settings-type-item").forEach(el => el.classList.remove("active"));
        document.getElementById("editExamTypeId").value = "";
        document.getElementById("editExamTypeName").value = "";
        document.getElementById("editPenaltyDivisor").value = "4";
        document.getElementById("editTargetNet").value = "0";
        document.getElementById("editExamDate").value = "";
        document.getElementById("selectedExamTypeTitle").textContent = "Yeni Sınav Türü Oluştur";

        const delBtn = document.getElementById("btnDeleteExamType");
        if (delBtn) delBtn.style.display = "none";

        const tbody = document.getElementById("editCourseRowsBody");
        if (tbody) {
            tbody.innerHTML = "";
            tbody.appendChild(this.createSettingCourseRow());
        }
    }

    static async handleDeleteExamType() {
        const id = document.getElementById("editExamTypeId").value;
        if (!id) return;
        if (!confirm("Bu sınav türünü ve bağlı tüm denemeleri silmek istediğinizden emin misiniz?")) return;

        try {
            await ApiService.deleteExamType(parseInt(id));
            this.showNotification("Sınav türü silindi.", "success");
            this.state.examTypes = await ApiService.getExamTypes();
            this.state.selectedSettingsExamTypeId = null;
            await this.renderSettings();
            this.populateExamTypeDropdowns();
        } catch (e) {
            alert("Hata: " + (e.message || "Silinemedi"));
        }
    }

    static async handleSaveExamTypeSettings() {
        const id = document.getElementById("editExamTypeId").value;
        const name = document.getElementById("editExamTypeName").value.trim();
        const divisor = parseFloat(document.getElementById("editPenaltyDivisor").value);
        const targetNet = parseFloat(document.getElementById("editTargetNet").value) || 0;
        const examDate = document.getElementById("editExamDate").value || null;

        if (!name) {
            alert("Sınav türü adı boş olamaz!");
            return;
        }

        const courses = [];
        document.querySelectorAll(".setting-course-row").forEach((row, idx) => {
            const cName = row.querySelector(".sc-name").value.trim();
            const qCount = parseInt(row.querySelector(".sc-qcount").value);
            const cTarget = parseFloat(row.querySelector(".sc-target").value) || 0.0;
            const cGroup = row.querySelector(".sc-group") ? row.querySelector(".sc-group").value.trim() || null : null;

            if (cName && qCount > 0) {
                courses.push({
                    name: cName,
                    question_count: qCount,
                    target_net: cTarget,
                    display_order: idx + 1,
                    group_name: cGroup
                });
            }
        });

        if (courses.length === 0) {
            alert("En az bir ders eklemelisiniz!");
            return;
        }

        const payload = {
            name: name,
            wrong_penalty_divisor: divisor,
            target_net: targetNet,
            exam_date: examDate,
            courses: courses
        };

        try {
            let saved;
            if (id) {
                saved = await ApiService.updateExamType(parseInt(id), payload);
            } else {
                saved = await ApiService.createExamType(payload);
            }
            alert("Değişiklikler kaydedildi!");
            this.state.examTypes = await ApiService.getExamTypes();
            this.state.selectedSettingsExamTypeId = saved.id || (id ? parseInt(id) : null);
            await this.renderSettings();
            this.populateExamTypeDropdowns();
        } catch (e) {
            alert("Hata: " + (e.message || "Kaydedilemedi"));
        }
    }




    static handleClearAllExams() {
        this.showModal({
            title: "Tüm Denemeleri Sıfırla (Temizle)",
            body: "<p>Veritabanındaki tüm deneme sınavı kayıtları silinecek ve sistem temiz bir sayfaya dönecektir. Devam etmek istiyor musunuz?</p>",
            confirmText: "Evet, Tümünü Sıfırla",
            isDanger: true,
            onConfirm: async () => {
                try {
                    const res = await ApiService.clearAllExams();
                    this.closeModal();
                    alert(`Tüm deneme sınavları temizlendi. (${res.deleted_count} deneme silindi).`);
                    await this.loadInitialData();
                    this.navigateTo("dashboard");
                } catch (e) {
                    alert(`Sıfırlama hatası: ${e.message}`);
                }
            }
        });
    }


    // --- MODAL SYSTEM ---
    static showModal({ title, body, content, confirmText = "Tamam", isDanger = false, confirmClass, onConfirm = null }) {
        const overlay = document.getElementById("genericModal");
        if (!overlay) return;

        const titleEl = document.getElementById("modalTitle");
        const bodyEl = document.getElementById("modalBody");
        const footer = document.getElementById("modalFooter");

        const modalText = body || content || "";
        const useDanger = isDanger || confirmClass === "btn-danger";

        if (titleEl) titleEl.textContent = title || "";
        if (bodyEl) bodyEl.innerHTML = modalText;

        if (footer) {
            footer.innerHTML = `
                <button type="button" class="btn btn-secondary btn-modal-close-action">İptal</button>
                <button type="button" class="btn ${useDanger ? 'btn-danger' : 'btn-primary'}" id="modalConfirmBtn">${confirmText}</button>
            `;

            footer.querySelector(".btn-modal-close-action")?.addEventListener("click", () => {
                this.closeModal();
            });

            const confirmBtn = document.getElementById("modalConfirmBtn");
            if (confirmBtn) {
                confirmBtn.onclick = async () => {
                    if (onConfirm) await onConfirm();
                    this.closeModal();
                };
            }
        }

        // Close on clicking backdrop
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                this.closeModal();
            }
        };

        overlay.classList.add("active");
    }


    static closeModal() {
        document.getElementById("genericModal")?.classList.remove("active");
    }
}

window.App = App;
window.toggleSidebar = () => App.toggleSidebar();
window.viewExamDetails = (id) => App.viewExamDetails(id);
window.confirmDeleteExam = (id) => App.confirmDeleteExam(id);
window.toggleTheme = () => App.toggleTheme();


