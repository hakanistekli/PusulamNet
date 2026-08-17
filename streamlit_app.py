import os
import sys
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Path configuration
project_root = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(project_root, "app")
for p in [project_root, app_dir, os.getcwd()]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.database import engine, Base, SessionLocal
    from app.models import User, ExamType, Course, PracticeExam, CourseResult, StudyNote, StudyTask
    from app.services.analysis_service import AnalysisService
    from app.services.explanation_service import ExplanationService
    from app.services.demo_data_service import DemoDataService
    from app.services.net_calculator import NetCalculatorService
except ModuleNotFoundError:
    from database import engine, Base, SessionLocal
    from models import User, ExamType, Course, PracticeExam, CourseResult, StudyNote, StudyTask
    from analysis_service import AnalysisService
    from explanation_service import ExplanationService
    from demo_data_service import DemoDataService
    from net_calculator import NetCalculatorService

# Page Setup
st.set_page_config(
    page_title="PusulamNet 🧭 | Öğrenci Deneme Takip & Analiz",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Ultra-Modern Styling
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }

    /* Main Container Background */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
    }

    /* Top Glass Navbar Header */
    .hero-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
    }

    .hero-title {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-top: 0.2rem;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }

    .metric-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.2;
    }

    .metric-sub {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }

    /* Explanation & Advice Card */
    .advice-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-left: 4px solid #6366f1;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    .advice-title {
        color: #818cf8;
        font-size: 1rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.6rem;
    }

    .advice-item {
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-bottom: 0.4rem;
        padding-left: 1.2rem;
        position: relative;
    }
    .advice-item::before {
        content: "✦";
        position: absolute;
        left: 0;
        color: #818cf8;
        font-size: 0.75rem;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-danger { background: rgba(244, 63, 94, 0.2); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.4); }
    .badge-info { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }

    /* Button Styling */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 0.5rem 1.25rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 0.4rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: #ffffff !important;
        font-weight: 700;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .hero-title { font-size: 1.25rem; }
        .metric-value { font-size: 1.4rem; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Database Initialization Helper
def get_db():
    return SessionLocal()

def init_app_state():
    Base.metadata.create_all(bind=engine)
    with get_db() as db:
        user = db.query(User).filter_by(id=1).first()
        if not user:
            user = User(id=1, name="Demo Öğrenci", email="demo@pusulamnet.com")
            db.add(user)
            db.commit()
            db.refresh(user)

        exam_types = db.query(ExamType).filter_by(user_id=1).all()
        if not exam_types:
            DemoDataService.init_predefined_types_only(db)

init_app_state()

# Session State Setup
if "user_id" not in st.session_state:
    st.session_state.user_id = 1

# Database Queries
def load_exam_types(user_id: int):
    with get_db() as db:
        return db.query(ExamType).filter_by(user_id=user_id).all()

def load_courses(exam_type_id: int):
    with get_db() as db:
        return db.query(Course).filter_by(exam_type_id=exam_type_id).order_by(Course.display_order).all()

def load_exams(user_id: int, exam_type_id: int):
    with get_db() as db:
        exams = db.query(PracticeExam).filter_by(
            user_id=user_id,
            exam_type_id=exam_type_id
        ).order_by(PracticeExam.exam_date.asc(), PracticeExam.id.asc()).all()

        exam_list = []
        for e in exams:
            results = []
            for r in e.course_results:
                results.append({
                    "course_id": r.course_id,
                    "course_name": r.course.name if r.course else "Bilinmeyen",
                    "correct_count": r.correct_count,
                    "wrong_count": r.wrong_count,
                    "blank_count": r.blank_count,
                    "net": r.net,
                    "question_count": r.course.question_count if r.course else 0
                })
            exam_list.append({
                "id": e.id,
                "name": e.name,
                "publisher": e.publisher or "-",
                "exam_date": e.exam_date,
                "duration_minutes": e.duration_minutes or 0,
                "difficulty": e.difficulty or "Orta",
                "total_correct": e.total_correct,
                "total_wrong": e.total_wrong,
                "total_blank": e.total_blank,
                "total_net": e.total_net,
                "course_results": results
            })
        return exam_list

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1rem;">
        <div style="background:linear-gradient(135deg, #3b82f6, #8b5cf6); padding:0.6rem; border-radius:12px; font-size:1.4rem;">🧭</div>
        <div>
            <div style="font-weight:800; font-size:1.2rem; color:#f8fafc;">PusulamNet</div>
            <div style="font-size:0.75rem; color:#94a3b8;">Deneme Takip & Analiz</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    exam_types = load_exam_types(st.session_state.user_id)
    if not exam_types:
        st.warning("Henüz sınav türü bulunamadı.")
        st.stop()

    exam_type_names = [et.name for et in exam_types]
    selected_type_name = st.selectbox("🎯 Aktif Sınav Türü", exam_type_names, index=0)
    selected_exam_type = next(et for et in exam_types if et.name == selected_type_name)

    # Sınav Tarihi Sayacı (Countdown)
    if selected_exam_type.exam_date:
        today = date.today()
        days_left = (selected_exam_type.exam_date - today).days
        if days_left > 0:
            st.markdown(f"""
            <div style="background:rgba(59, 130, 246, 0.15); border:1px solid rgba(59, 130, 246, 0.3); border-radius:12px; padding:0.75rem; margin:0.75rem 0; text-align:center;">
                <div style="font-size:0.75rem; color:#93c5fd; font-weight:600;">SINAVA KALAN SÜRE</div>
                <div style="font-size:1.5rem; font-weight:800; color:#ffffff;">{days_left} Gün</div>
                <div style="font-size:0.7rem; color:#94a3b8;">{selected_exam_type.exam_date.strftime('%d.%m.%Y')}</div>
            </div>
            """, unsafe_allow_html=True)
        elif days_left == 0:
            st.info("🎯 Sınav Günü Geldi! Başarılar!")

    st.markdown("---")
    
    menu = st.radio(
        "📌 Menü",
        [
            "📊 Panel (Dashboard)",
            "📝 Denemelerim",
            "➕ Yeni Deneme Girişi",
            "📈 Ders Analizleri",
            "🎯 Hedef Takibi",
            "⏱️ Odaklanma & Notlar",
            "⚙️ Ayarlar & Demo Veri"
        ]
    )

    st.markdown("---")
    st.caption("PusulamNet v4.0.0 • Modern Mobil Arayüz")

# Load current data
courses = load_courses(selected_exam_type.id)
exams_data = load_exams(st.session_state.user_id, selected_exam_type.id)
overall_stats = AnalysisService.calculate_overall_statistics(exams_data, target_net=selected_exam_type.target_net)

# Course analysis calculations
courses_analysis = []
for c in courses:
    c_results = []
    for e in exams_data:
        for cr in e["course_results"]:
            if cr["course_id"] == c.id:
                c_results.append({
                    "exam_date": e["exam_date"],
                    "net": cr["net"],
                    "correct_count": cr["correct_count"],
                    "wrong_count": cr["wrong_count"],
                    "blank_count": cr["blank_count"]
                })
    c_stat = AnalysisService.calculate_course_performance(c.id, c.name, c_results, target_net=c.target_net)
    courses_analysis.append(c_stat)

most_improved, most_declined = AnalysisService.identify_course_growth_and_decline(courses_analysis)
declined_val = None
if most_declined:
    for ca in courses_analysis:
        if ca["course_name"] == most_declined:
            declined_val = abs(ca["period_change"]) if ca.get("period_change") else None

# Header Banner
st.markdown(f"""
<div class="hero-header">
    <div>
        <h1 class="hero-title">🧭 PusulamNet • {selected_exam_type.name}</h1>
        <div class="hero-subtitle">Net takibi, yapay zeka destekli akıllı gelişim ve ders analizleri</div>
    </div>
    <div style="text-align:right;">
        <span class="badge badge-info">{len(exams_data)} Deneme Kayıtlı</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: 📊 PANEL (DASHBOARD)
# ==============================================================================
if menu == "📊 Panel (Dashboard)":
    # 4 Metric Cards
    col1, col2, col3, col4 = st.columns(4)

    latest_net = overall_stats.get("latest_exam_total_net")
    overall_avg = overall_stats.get("overall_net_average")
    last_5_avg = overall_stats.get("last_5_net_average")
    target_net = overall_stats.get("target_net", 0.0)
    target_diff = overall_stats.get("target_net_diff")
    stability = overall_stats.get("stability_status") or "Yetersiz Veri"

    # Stability Badge Style
    stability_badge_class = "badge-info"
    if stability == "İstikrarlı":
        stability_badge_class = "badge-success"
    elif stability == "Dalgalı":
        stability_badge_class = "badge-danger"
    elif stability == "Orta düzeyde dalgalı":
        stability_badge_class = "badge-warning"

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Son Deneme Neti</div>
            <div class="metric-value">{f"{latest_net:.2f}" if latest_net is not None else "-"}</div>
            <div class="metric-sub">{f"En yüksek: {overall_stats['highest_total_net']:.2f}" if overall_stats.get('highest_total_net') is not None else "Kayıt yok"}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Genel Net Ortalaması</div>
            <div class="metric-value">{f"{overall_avg:.2f}" if overall_avg is not None else "-"}</div>
            <div class="metric-sub">{f"En düşük: {overall_stats['lowest_total_net']:.2f}" if overall_stats.get('lowest_total_net') is not None else "Kayıt yok"}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Son 5 Deneme & İstikrar</div>
            <div class="metric-value">{f"{last_5_avg:.2f}" if last_5_avg is not None else "-"}</div>
            <div class="metric-sub"><span class="badge {stability_badge_class}">{stability}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        diff_str = ""
        if target_diff is not None:
            if target_diff > 0:
                diff_str = f"Hedefe <span style='color:#fb7185;'>{target_diff:.1f}</span> net kaldı"
            else:
                diff_str = f"Hedef <span style='color:#34d399;'>+{abs(target_diff):.1f}</span> aşıldı 🎉"
        else:
            diff_str = "Hedef belirlenmedi"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Hedef Net</div>
            <div class="metric-value">{f"{target_net:.1f}" if target_net > 0 else "-"}</div>
            <div class="metric-sub">{diff_str}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Akıllı Rehberlik ve Yorum Kutusu
    explanations = ExplanationService.generate_dashboard_explanations(
        overall_stats, most_improved, most_declined, declined_val
    )
    if explanations:
        items_html = "".join([f'<div class="advice-item">{exp}</div>' for exp in explanations])
        st.markdown(f"""
        <div class="advice-card">
            <div class="advice-title">💡 Akıllı Pusula Rehberliği & Değerlendirme</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    if exams_data:
        # Charts Row
        c_left, c_right = st.columns([3, 2])

        with c_left:
            st.markdown("### 📈 Net Gelişim Trendi")
            df_plot = pd.DataFrame([
                {
                    "Deneme": f"{e['name']} ({e['exam_date'].strftime('%d.%m')})",
                    "Net": e["total_net"],
                    "Tarih": e["exam_date"]
                }
                for e in exams_data
            ])

            fig_trend = go.Figure()

            # Net Çizgisi & Dolgu
            fig_trend.add_trace(go.Scatter(
                x=df_plot["Deneme"],
                y=df_plot["Net"],
                mode="lines+markers",
                name="Toplam Net",
                line=dict(color="#3b82f6", width=3, shape="spline"),
                marker=dict(size=8, color="#60a5fa", line=dict(width=2, color="#ffffff")),
                fill="tozeroy",
                fillcolor="rgba(59, 130, 246, 0.12)"
            ))

            # Hareketli Ortalama (Son 3)
            if len(df_plot) >= 3:
                df_plot["MA3"] = df_plot["Net"].rolling(window=3, min_periods=1).mean()
                fig_trend.add_trace(go.Scatter(
                    x=df_plot["Deneme"],
                    y=df_plot["MA3"],
                    mode="lines",
                    name="3'lü Hareketli Ort.",
                    line=dict(color="#a78bfa", width=2, dash="dot")
                ))

            # Hedef Çizgisi
            if target_net > 0:
                fig_trend.add_trace(go.Scatter(
                    x=df_plot["Deneme"],
                    y=[target_net] * len(df_plot),
                    mode="lines",
                    name=f"Hedef ({target_net:.1f})",
                    line=dict(color="#f43f5e", width=2, dash="dash")
                ))

            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=30),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with c_right:
            st.markdown("### 📊 Derslerin Son Netleri & Hedefler")
            if courses_analysis:
                df_courses = pd.DataFrame([
                    {
                        "Ders": ca["course_name"],
                        "Son Net": ca["latest_net"],
                        "Ortalama": ca["overall_avg_net"],
                        "Hedef": ca["target_net"]
                    }
                    for ca in courses_analysis
                ])

                fig_courses = go.Figure()
                fig_courses.add_trace(go.Bar(
                    x=df_courses["Ders"],
                    y=df_courses["Son Net"],
                    name="Son Net",
                    marker_color="#6366f1"
                ))
                fig_courses.add_trace(go.Bar(
                    x=df_courses["Ders"],
                    y=df_courses["Ortalama"],
                    name="Ortalama",
                    marker_color="#38bdf8"
                ))

                fig_courses.update_layout(
                    barmode="group",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=30, b=30),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_courses, use_container_width=True)
    else:
        st.info("Henüz deneme kaydı yok. Sol menüden **'➕ Yeni Deneme Girişi'** veya **'⚙️ Ayarlar'** bölümünden demo verileri yükleyebilirsiniz.")


# ==============================================================================
# VIEW 2: 📝 DENEMELERİM (EXAMS LIST)
# ==============================================================================
elif menu == "📝 Denemelerim":
    st.markdown("### 📝 Kayıtlı Denemeler")
    if not exams_data:
        st.info("Kayıtlı deneme bulunamadı.")
    else:
        # Table summary
        table_rows = []
        for e in reversed(exams_data):
            table_rows.append({
                "ID": e["id"],
                "Tarih": e["exam_date"].strftime("%d.%m.%Y"),
                "Deneme Adı": e["name"],
                "Yayıncı": e["publisher"],
                "Zorluk": e["difficulty"],
                "Doğru": e["total_correct"],
                "Yanlış": e["total_wrong"],
                "Boş": e["total_blank"],
                "Toplam Net": f"{e['total_net']:.2f}"
            })

        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### 🔍 Deneme Detay Karnesi")
        exam_names_dict = {f"#{e['id']} - {e['name']} ({e['exam_date'].strftime('%d.%m.%Y')})": e for e in reversed(exams_data)}
        selected_exam_label = st.selectbox("İncelemek istediğiniz denemeyi seçin:", list(exam_names_dict.keys()))

        selected_exam = exam_names_dict[selected_exam_label]

        # Detailed breakdown
        c_detail_rows = []
        for cr in selected_exam["course_results"]:
            c_detail_rows.append({
                "Ders": cr["course_name"],
                "Soru Sayısı": cr["question_count"],
                "Doğru": cr["correct_count"],
                "Yanlış": cr["wrong_count"],
                "Boş": cr["blank_count"],
                "Net": f"{cr['net']:.2f}"
            })

        st.table(pd.DataFrame(c_detail_rows))

        # Delete Action
        col_del, _ = st.columns([1, 4])
        with col_del:
            if st.button("🗑️ Bu Denemeyi Sil", type="secondary"):
                with get_db() as db:
                    pe = db.query(PracticeExam).filter_by(id=selected_exam["id"]).first()
                    if pe:
                        db.delete(pe)
                        db.commit()
                        st.success("Deneme başarıyla silindi!")
                        st.rerun()


# ==============================================================================
# VIEW 3: ➕ YENİ DENEME GİRİŞİ (ADD EXAM)
# ==============================================================================
elif menu == "➕ Yeni Deneme Girişi":
    st.markdown(f"### ➕ {selected_exam_type.name} Deneme Sonucu Girişi")
    st.caption("Derslerin doğru ve yanlış sayılarını girin, netler anında otomatik hesaplanır.")

    with st.form("form_add_exam"):
        c1, c2, c3 = st.columns(3)
        with c1:
            exam_name = st.text_input("Deneme Adı / Başlığı *", placeholder="Örn: 3D Türkiye Geneli 1")
            publisher = st.text_input("Yayıncı / Kurum", placeholder="Örn: 3D Yayınları, Özdebir")
        with c2:
            exam_date_val = st.date_input("Sınav Tarihi", value=date.today())
            difficulty = st.selectbox("Zorluk Derecesi", ["Kolay", "Orta", "Zor", "Çok Zor"], index=1)
        with c3:
            duration = st.number_input("Süre (Dakika)", min_value=0, max_value=300, value=165)

        st.markdown("#### 📚 Ders Sonuçları")
        divisor = selected_exam_type.wrong_penalty_divisor or 4.0

        course_inputs = {}
        for c in courses:
            st.markdown(f"**{c.name}** *(Toplam {c.question_count} Soru)*")
            col_d, col_y, col_b = st.columns(3)
            with col_d:
                correct = st.number_input(f"Doğru", min_value=0, max_value=c.question_count, value=0, key=f"c_{c.id}_d")
            with col_y:
                wrong = st.number_input(f"Yanlış", min_value=0, max_value=c.question_count, value=0, key=f"c_{c.id}_y")
            with col_b:
                blank = max(0, c.question_count - (correct + wrong))
                st.number_input(f"Boş", min_value=0, max_value=c.question_count, value=blank, disabled=True, key=f"c_{c.id}_b")

            calc_net = NetCalculatorService.calculate_net(correct, wrong, divisor)
            course_inputs[c.id] = {
                "course_id": c.id,
                "correct": correct,
                "wrong": wrong,
                "blank": blank,
                "net": calc_net,
                "max": c.question_count
            }
            st.markdown("---")

        submit_btn = st.form_submit_button("💾 Denemeyi Kaydet", type="primary", use_container_width=True)

        if submit_btn:
            if not exam_name.strip():
                st.error("Lütfen bir deneme adı girin.")
            else:
                # Total net calculation
                tot_c = sum(ci["correct"] for ci in course_inputs.values())
                tot_w = sum(ci["wrong"] for ci in course_inputs.values())
                tot_b = sum(ci["blank"] for ci in course_inputs.values())
                tot_net = sum(ci["net"] for ci in course_inputs.values())

                with get_db() as db:
                    new_exam = PracticeExam(
                        user_id=st.session_state.user_id,
                        exam_type_id=selected_exam_type.id,
                        name=exam_name.strip(),
                        publisher=publisher.strip() if publisher else None,
                        exam_date=exam_date_val,
                        duration_minutes=int(duration),
                        difficulty=difficulty,
                        total_correct=tot_c,
                        total_wrong=tot_w,
                        total_blank=tot_b,
                        total_net=round(tot_net, 2)
                    )
                    db.add(new_exam)
                    db.flush()

                    for c_id, c_data in course_inputs.items():
                        c_res = CourseResult(
                            practice_exam_id=new_exam.id,
                            course_id=c_id,
                            correct_count=c_data["correct"],
                            wrong_count=c_data["wrong"],
                            blank_count=c_data["blank"],
                            net=round(c_data["net"], 2)
                        )
                        db.add(c_res)

                    db.commit()

                st.balloons()
                st.success(f"🎉 Deneme başarıyla kaydedildi! Toplam Net: **{tot_net:.2f}**")


# ==============================================================================
# VIEW 4: 📈 DERS ANALİZLERİ (COURSE ANALYSIS)
# ==============================================================================
elif menu == "📈 Ders Analizleri":
    st.markdown("### 📈 Ders Bazlı İstatistik ve Performans Analizi")

    if not courses:
        st.warning("Bu sınav türünde tanımlı ders bulunamadı.")
    else:
        selected_course_name = st.selectbox("İncelemek istediğiniz dersi seçin:", [c.name for c in courses])
        selected_course = next(c for c in courses if c.name == selected_course_name)

        c_stat = next((ca for ca in courses_analysis if ca["course_id"] == selected_course.id), None)

        if c_stat:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{selected_course.name} Son Net</div>
                    <div class="metric-value">{c_stat['latest_net']:.2f}</div>
                    <div class="metric-sub">Soru: {selected_course.question_count}</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Ortalama Net</div>
                    <div class="metric-value">{c_stat['overall_avg_net']:.2f}</div>
                    <div class="metric-sub">En yüksek: {c_stat['highest_net']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Ortalama Yanlış / Boş</div>
                    <div class="metric-value">{c_stat['wrong_avg']:.1f} <span style="font-size:1rem; color:#94a3b8;">Y</span> / {c_stat['blank_avg']:.1f} <span style="font-size:1rem; color:#94a3b8;">B</span></div>
                    <div class="metric-sub">Doğru Ort: {c_stat['correct_avg']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Ders Hedefi</div>
                    <div class="metric-value">{c_stat['target_net']:.1f}</div>
                    <div class="metric-sub">Fark: {c_stat['target_diff']:.1f} net</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Smart Advice for Course
            c_explanations = ExplanationService.generate_course_explanations(c_stat)
            if c_explanations:
                items_html = "".join([f'<div class="advice-item">{exp}</div>' for exp in c_explanations])
                st.markdown(f"""
                <div class="advice-card">
                    <div class="advice-title">💡 {selected_course.name} Dersi Tavsiyesi</div>
                    {items_html}
                </div>
                """, unsafe_allow_html=True)

            # Course Trend Plot
            c_timeline = []
            for e in exams_data:
                for cr in e["course_results"]:
                    if cr["course_id"] == selected_course.id:
                        c_timeline.append({
                            "Deneme": f"{e['name']} ({e['exam_date'].strftime('%d.%m')})",
                            "Net": cr["net"],
                            "Doğru": cr["correct_count"],
                            "Yanlış": cr["wrong_count"],
                            "Boş": cr["blank_count"]
                        })

            if c_timeline:
                col_chart1, col_chart2 = st.columns([3, 2])
                with col_chart1:
                    df_c_time = pd.DataFrame(c_timeline)
                    fig_c = go.Figure()
                    fig_c.add_trace(go.Scatter(
                        x=df_c_time["Deneme"],
                        y=df_c_time["Net"],
                        mode="lines+markers",
                        name="Net",
                        line=dict(color="#10b981", width=3, shape="spline"),
                        marker=dict(size=8, color="#34d399")
                    ))
                    if selected_course.target_net > 0:
                        fig_c.add_trace(go.Scatter(
                            x=df_c_time["Deneme"],
                            y=[selected_course.target_net] * len(df_c_time),
                            mode="lines",
                            name="Hedef",
                            line=dict(color="#f43f5e", width=2, dash="dash")
                        ))
                    fig_c.update_layout(
                        title=f"{selected_course.name} Net Değişimi",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=30, b=30)
                    )
                    st.plotly_chart(fig_c, use_container_width=True)

                with col_chart2:
                    # Donut chart for average correct, wrong, blank
                    fig_donut = go.Figure(data=[go.Pie(
                        labels=["Doğru", "Yanlış", "Boş"],
                        values=[c_stat["correct_avg"], c_stat["wrong_avg"], c_stat["blank_avg"]],
                        hole=.6,
                        marker_colors=["#10b981", "#f43f5e", "#64748b"]
                    )])
                    fig_donut.update_layout(
                        title="Ortalama Dağılım",
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=30, b=30)
                    )
                    st.plotly_chart(fig_donut, use_container_width=True)


# ==============================================================================
# VIEW 5: 🎯 HEDEFLER (GOALS)
# ==============================================================================
elif menu == "🎯 Hedef Takibi":
    st.markdown("### 🎯 Hedef Belirleme & İlerleme Takibi")
    st.caption("Genel ve ders bazlı net hedeflerinizi güncelleyin.")

    with st.form("form_goals"):
        current_target = selected_exam_type.target_net or 0.0
        new_target = st.number_input(
            f"{selected_exam_type.name} Genel Net Hedefi",
            min_value=0.0,
            max_value=300.0,
            value=float(current_target),
            step=0.5
        )

        st.markdown("#### 📚 Ders Bazlı Net Hedefleri")
        course_target_inputs = {}
        for c in courses:
            val = st.number_input(
                f"{c.name} Hedef Neti (Maks: {c.question_count})",
                min_value=0.0,
                max_value=float(c.question_count),
                value=float(c.target_net or 0.0),
                step=0.5,
                key=f"target_c_{c.id}"
            )
            course_target_inputs[c.id] = val

        save_goals_btn = st.form_submit_button("🎯 Hedefleri Güncelle", type="primary", use_container_width=True)
        if save_goals_btn:
            with get_db() as db:
                et = db.query(ExamType).filter_by(id=selected_exam_type.id).first()
                if et:
                    et.target_net = new_target
                for cid, t_val in course_target_inputs.items():
                    c_rec = db.query(Course).filter_by(id=cid).first()
                    if c_rec:
                        c_rec.target_net = t_val
                db.commit()
            st.success("Hedefler başarıyla güncellendi!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Hedefe Ulaşma Durumu")
    for ca in courses_analysis:
        t_net = ca["target_net"]
        avg_net = ca["overall_avg_net"]
        pct = min(100, int((avg_net / t_net * 100))) if t_net > 0 else 0
        st.markdown(f"**{ca['course_name']}**: {avg_net:.2f} / {t_net:.1f} Net (%{pct})")
        st.progress(pct / 100.0)


# ==============================================================================
# VIEW 6: ⏱️ ODAKLANMA & NOTLAR (PLANNER)
# ==============================================================================
elif menu == "⏱️ Odaklanma & Notlar":
    st.markdown("### ⏱️ Çalışma Planlayıcısı & Pomodoro")

    tab_tasks, tab_notes, tab_timer = st.tabs(["📋 Yapılacaklar (To-Do)", "📝 Çalışma Notları", "⏱️ Pomodoro / Kronometre"])

    with tab_tasks:
        with st.form("form_add_task"):
            col_t1, col_t2, col_t3 = st.columns([3, 2, 1])
            with col_t1:
                task_title = st.text_input("Yeni Görev / Konu", placeholder="Örn: Paragraf 40 soru çözülecek")
            with col_t2:
                task_course = st.selectbox("Ders", ["Genel"] + [c.name for c in courses])
            with col_t3:
                task_priority = st.selectbox("Öncelik", ["Yüksek", "Orta", "Düşük"], index=1)
            add_task_btn = st.form_submit_button("➕ Görevi Ekle")

            if add_task_btn and task_title.strip():
                with get_db() as db:
                    new_task = StudyTask(
                        user_id=st.session_state.user_id,
                        title=task_title.strip(),
                        course_name=task_course,
                        priority=task_priority.lower(),
                        is_completed=False
                    )
                    db.add(new_task)
                    db.commit()
                st.success("Görev eklendi!")
                st.rerun()

        # Task List
        with get_db() as db:
            tasks = db.query(StudyTask).filter_by(user_id=st.session_state.user_id).order_by(StudyTask.is_completed.asc(), StudyTask.id.desc()).all()
            if not tasks:
                st.info("Henüz eklenmiş bir çalışma görevi yok.")
            else:
                for t in tasks:
                    col_chk, col_info, col_del = st.columns([1, 8, 1])
                    with col_chk:
                        done = st.checkbox("", value=t.is_completed, key=f"chk_t_{t.id}")
                        if done != t.is_completed:
                            t.is_completed = done
                            db.commit()
                            st.rerun()
                    with col_info:
                        strike = "line-through" if t.is_completed else "none"
                        color = "#94a3b8" if t.is_completed else "#f8fafc"
                        st.markdown(f"<span style='text-decoration:{strike}; color:{color}; font-weight:600;'>{t.title}</span> <span class='badge badge-info'>{t.course_name}</span>", unsafe_allow_html=True)
                    with col_del:
                        if st.button("❌", key=f"del_t_{t.id}"):
                            db.delete(t)
                            db.commit()
                            st.rerun()

    with tab_notes:
        with st.form("form_add_note"):
            n_title = st.text_input("Not Başlığı", placeholder="Örn: Trigonometri Yarım Açı Formülleri")
            n_content = st.text_area("Not İçeriği / Hata Defteri", placeholder="Önemli formüller veya denemede kaçan soru tipi notları...")
            add_note_btn = st.form_submit_button("📌 Notu Kaydet")
            if add_note_btn and n_title.strip() and n_content.strip():
                with get_db() as db:
                    new_note = StudyNote(
                        user_id=st.session_state.user_id,
                        exam_type_id=selected_exam_type.id,
                        title=n_title.strip(),
                        content=n_content.strip()
                    )
                    db.add(new_note)
                    db.commit()
                st.success("Not kaydedildi!")
                st.rerun()

        # Display Notes
        with get_db() as db:
            notes = db.query(StudyNote).filter_by(user_id=st.session_state.user_id).order_by(StudyNote.id.desc()).all()
            for n in notes:
                with st.expander(f"📌 {n.title} ({n.created_at.strftime('%d.%m.%Y') if n.created_at else ''})"):
                    st.write(n.content)
                    if st.button("🗑️ Notu Sil", key=f"del_n_{n.id}"):
                        db.delete(n)
                        db.commit()
                        st.rerun()

    with tab_timer:
        st.markdown("#### ⏳ Pomodoro Odaklanma Zamanlayıcısı")
        st.markdown("""
        <div style="background:rgba(30, 41, 59, 0.8); border-radius:16px; padding:1.5rem; text-align:center; border:1px solid rgba(99, 102, 241, 0.3); max-width:400px; margin:auto;">
            <div style="font-size:3rem; font-weight:800; color:#38bdf8; letter-spacing:2px;">25:00</div>
            <div style="color:#94a3b8; font-size:0.9rem; margin-bottom:1rem;">Odaklanma Seansı</div>
            <p style="font-size:0.85rem; color:#cbd5e1;">Odaklanma seanslarınızı mobil tarayıcınızda veya telefonunuzda açarak verimli çalışabilirsiniz.</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# VIEW 7: ⚙️ AYARLAR & DEMO VERİ (SETTINGS & DEMO)
# ==============================================================================
elif menu == "⚙️ Ayarlar & Demo Veri":
    st.markdown("### ⚙️ Ayarlar ve Demo Veri Yönetimi")

    col_demo, col_reset = st.columns(2)

    with col_demo:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">⚡ Hızlı Demo Verisi Yükle</div>
            <p style="font-size:0.85rem; color:#cbd5e1;">Uygulamayı tüm grafikler, karne detayları ve istatistiklerle anında test etmek için 10 adet gerçekçi deneme sonucu oluşturur.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Demo Denemeleri Yükle", type="primary", use_container_width=True):
            with get_db() as db:
                DemoDataService.seed_full_demo_data(db)
            st.balloons()
            st.success("10 adet gerçekçi deneme sınavı başarıyla yüklendi!")
            st.rerun()

    with col_reset:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">🗑️ Denemeleri Sıfırla</div>
            <p style="font-size:0.85rem; color:#cbd5e1;">Bu sınav türüne ait tüm deneme kayıtlarını siler ve temiz bir başlangıç yapmanızı sağlar.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚠️ Bu Sınav Türünün Denemelerini Sil", type="secondary", use_container_width=True):
            with get_db() as db:
                db.query(PracticeExam).filter_by(
                    user_id=st.session_state.user_id,
                    exam_type_id=selected_exam_type.id
                ).delete()
                db.commit()
            st.warning("Tüm denemeler silindi.")
            st.rerun()
