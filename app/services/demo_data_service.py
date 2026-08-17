from datetime import date, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
try:
    from app.models import User, ExamType, Course, PracticeExam, CourseResult
except ModuleNotFoundError:
    try:
        from models import User, ExamType, Course, PracticeExam, CourseResult
    except ModuleNotFoundError:
        from models import User, ExamType, Course, PracticeExam, CourseResult
try:
    from app.services.net_calculator import NetCalculatorService
except ModuleNotFoundError:
    try:
        from services.net_calculator import NetCalculatorService
    except ModuleNotFoundError:
        from net_calculator import NetCalculatorService

class DemoDataService:
    PREDEFINED_EXAM_TYPES = [
        {
            "name": "YKS - TYT",
            "wrong_penalty_divisor": 4.0,
            "target_net": 95.0,
            "exam_date": date(2026, 6, 20),
            "courses": [
                {"name": "Türkçe", "question_count": 40, "target_net": 35.0, "order": 1},
                {"name": "Sosyal Bilimler", "question_count": 20, "target_net": 16.0, "order": 2},
                {"name": "Temel Matematik", "question_count": 40, "target_net": 32.0, "order": 3},
                {"name": "Fen Bilimleri", "question_count": 20, "target_net": 14.0, "order": 4},
            ]
        },
        {
            "name": "YKS - AYT",
            "wrong_penalty_divisor": 4.0,
            "target_net": 65.0,
            "exam_date": date(2026, 6, 21),
            "courses": [
                {"name": "Matematik", "question_count": 40, "target_net": 30.0, "order": 1},
                {"name": "Fen Bilimleri", "question_count": 40, "target_net": 25.0, "order": 2},
                {"name": "Türk Dili ve Ed. - Sosyal 1", "question_count": 40, "target_net": 30.0, "order": 3},
                {"name": "Sosyal Bilimler 2", "question_count": 40, "target_net": 28.0, "order": 4},
            ]
        },
        {
            "name": "LGS (8. Sınıf)",
            "wrong_penalty_divisor": 3.0, # LGS'de 3 yanlış 1 doğruyu götürür
            "target_net": 80.0,
            "exam_date": date(2026, 6, 14),
            "courses": [
                {"name": "Türkçe", "question_count": 20, "target_net": 18.0, "order": 1},
                {"name": "Matematik", "question_count": 20, "target_net": 16.0, "order": 2},
                {"name": "Fen Bilimleri", "question_count": 20, "target_net": 18.0, "order": 3},
                {"name": "T.C. İnkılap Tarihi", "question_count": 10, "target_net": 9.5, "order": 4},
                {"name": "Din Kültürü ve A.B.", "question_count": 10, "target_net": 9.5, "order": 5},
                {"name": "Yabancı Dil (İngilizce)", "question_count": 10, "target_net": 9.0, "order": 6},
            ]
        },
        {
            "name": "KPSS (Genel Yetenek - Genel Kültür)",
            "wrong_penalty_divisor": 4.0,
            "target_net": 90.0,
            "exam_date": date(2026, 9, 6),
            "courses": [
                {"name": "Türkçe", "question_count": 30, "target_net": 26.0, "order": 1},
                {"name": "Matematik", "question_count": 30, "target_net": 22.0, "order": 2},
                {"name": "Tarih", "question_count": 27, "target_net": 21.0, "order": 3},
                {"name": "Coğrafya", "question_count": 18, "target_net": 15.0, "order": 4},
                {"name": "Vatandaşlık & Güncel", "question_count": 15, "target_net": 12.0, "order": 5},
            ]
        },
        {
            "name": "TUS (Tıpta Uzmanlık Eğitimi)",
            "wrong_penalty_divisor": 4.0,
            "target_net": 150.0,
            "exam_date": date(2026, 8, 23),
            "courses": [
                # Temel Tıp Bilimleri (100 Soru)
                {"name": "Anatomi", "question_count": 14, "target_net": 11.0, "order": 1, "group": "Temel Tıp Bilimleri"},
                {"name": "Histoloji ve Embriyoloji", "question_count": 8, "target_net": 6.0, "order": 2, "group": "Temel Tıp Bilimleri"},
                {"name": "Fizyoloji", "question_count": 10, "target_net": 8.0, "order": 3, "group": "Temel Tıp Bilimleri"},
                {"name": "Tıbbi Biyokimya", "question_count": 18, "target_net": 14.0, "order": 4, "group": "Temel Tıp Bilimleri"},
                {"name": "Tıbbi Mikrobiyoloji", "question_count": 18, "target_net": 14.0, "order": 5, "group": "Temel Tıp Bilimleri"},
                {"name": "Tıbbi Patoloji", "question_count": 22, "target_net": 17.0, "order": 6, "group": "Temel Tıp Bilimleri"},
                {"name": "Tıbbi Farmakoloji", "question_count": 10, "target_net": 8.0, "order": 7, "group": "Temel Tıp Bilimleri"},
                # Klinik Tıp Bilimleri (100 Soru)
                {"name": "Dahiliye Grubu", "question_count": 42, "target_net": 33.0, "order": 8, "group": "Klinik Tıp Bilimleri"},
                {"name": "Pediatri", "question_count": 30, "target_net": 24.0, "order": 9, "group": "Klinik Tıp Bilimleri"},
                {"name": "Cerrahi Grubu & Kadın Doğum", "question_count": 28, "target_net": 22.0, "order": 10, "group": "Klinik Tıp Bilimleri"},
            ]
        },
        {
            "name": "DUS (Diş Hekimliğinde Uzmanlık)",
            "wrong_penalty_divisor": 4.0,
            "target_net": 90.0,
            "exam_date": date(2026, 11, 1),
            "courses": [


                # Temel Bilimler (40 Soru)
                {"name": "Anatomi", "question_count": 6, "target_net": 5.0, "order": 1, "group": "Temel Bilimler"},
                {"name": "Histoloji ve Embriyoloji", "question_count": 4, "target_net": 3.0, "order": 2, "group": "Temel Bilimler"},
                {"name": "Fizyoloji", "question_count": 6, "target_net": 5.0, "order": 3, "group": "Temel Bilimler"},
                {"name": "Tıbbi Biyokimya", "question_count": 6, "target_net": 5.0, "order": 4, "group": "Temel Bilimler"},
                {"name": "Tıbbi Mikrobiyoloji", "question_count": 6, "target_net": 5.0, "order": 5, "group": "Temel Bilimler"},
                {"name": "Tıbbi Patoloji", "question_count": 4, "target_net": 3.0, "order": 6, "group": "Temel Bilimler"},
                {"name": "Tıbbi Farmakoloji", "question_count": 4, "target_net": 3.0, "order": 7, "group": "Temel Bilimler"},
                {"name": "Tıbbi Biyoloji ve Genetik", "question_count": 4, "target_net": 3.0, "order": 8, "group": "Temel Bilimler"},
                # Klinik Bilimler (80 Soru)
                {"name": "Protetik Diş Tedavisi", "question_count": 10, "target_net": 8.0, "order": 9, "group": "Klinik Bilimler"},
                {"name": "Restoratif Diş Tedavisi", "question_count": 10, "target_net": 8.0, "order": 10, "group": "Klinik Bilimler"},
                {"name": "Ağız, Diş ve Çene Cerrahisi", "question_count": 10, "target_net": 8.0, "order": 11, "group": "Klinik Bilimler"},
                {"name": "Ağız, Diş ve Çene Radyolojisi", "question_count": 10, "target_net": 8.0, "order": 12, "group": "Klinik Bilimler"},
                {"name": "Periodontoloji", "question_count": 10, "target_net": 8.0, "order": 13, "group": "Klinik Bilimler"},
                {"name": "Endodonti", "question_count": 10, "target_net": 8.0, "order": 14, "group": "Klinik Bilimler"},
                {"name": "Ortodonti", "question_count": 10, "target_net": 8.0, "order": 15, "group": "Klinik Bilimler"},
                {"name": "Çocuk Diş Hekimliği", "question_count": 10, "target_net": 8.0, "order": 16, "group": "Klinik Bilimler"},
            ]
        }

    ]

    @classmethod
    def get_public_exam_catalog(cls) -> list[dict[str, Any]]:
        """Return a read-only copy of all built-in exams and their courses."""
        catalog = []
        for index, exam_spec in enumerate(cls.PREDEFINED_EXAM_TYPES, start=1):
            courses = [
                {
                    "name": course["name"],
                    "question_count": course["question_count"],
                    "target_net": course["target_net"],
                    "display_order": course["order"],
                    "group_name": course.get("group"),
                }
                for course in exam_spec["courses"]
            ]
            catalog.append(
                {
                    "id": index,
                    "name": exam_spec["name"],
                    "wrong_penalty_divisor": exam_spec["wrong_penalty_divisor"],
                    "target_net": exam_spec["target_net"],
                    "exam_date": exam_spec["exam_date"],
                    "courses": courses,
                }
            )
        return catalog


    @classmethod
    def init_predefined_types_only(cls, db: Session) -> None:
        """
        Sadece kullanıcıyı ve hazır sınav türlerini (YKS-TYT, YKS-AYT, LGS, KPSS, TUS, DUS) ilklendirir; deneme sınavı eklemez.
        """
        user = db.query(User).first()
        if not user:
            user = User(name="Öğrenci", email="ogrenci@pusulam.net")
            db.add(user)
            db.commit()
            db.refresh(user)

        cls.create_predefined_exam_types(db, user)

    @staticmethod
    def clear_all_practice_exams(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Veritabanındaki tüm deneme sınavı kayıtlarını siler ve temizler.
        """
        deleted_count = (
            db.query(PracticeExam)
            .filter(PracticeExam.user_id == user_id)
            .delete(synchronize_session=False)
        )
        db.commit()
        return {
            "status": "success",
            "message": f"Tüm deneme sınavı kayıtları temizlendi. ({deleted_count} deneme silindi).",
            "deleted_count": deleted_count
        }

    @classmethod
    def create_predefined_exam_types(cls, db: Session, user: User) -> Dict[str, ExamType]:

        """
        Hazır sınav türlerini (YKS-TYT, YKS-AYT, LGS, KPSS, TUS, DUS) ve ders yapılarını oluşturur.
        """
        created_exam_types = {}
        for et_spec in cls.PREDEFINED_EXAM_TYPES:
            exam_type = db.query(ExamType).filter_by(user_id=user.id, name=et_spec["name"]).first()
            if not exam_type:
                exam_type = ExamType(
                    user_id=user.id,
                    name=et_spec["name"],
                    wrong_penalty_divisor=et_spec["wrong_penalty_divisor"],
                    target_net=et_spec["target_net"],
                    exam_date=et_spec.get("exam_date")
                )

                db.add(exam_type)
                db.commit()
                db.refresh(exam_type)

                for c_data in et_spec["courses"]:
                    course = Course(
                        exam_type_id=exam_type.id,
                        name=c_data["name"],
                        question_count=c_data["question_count"],
                        target_net=c_data["target_net"],
                        display_order=c_data["order"],
                        group_name=c_data.get("group")
                    )
                    db.add(course)
                db.commit()
                db.refresh(exam_type)

            created_exam_types[et_spec["name"]] = exam_type


            created_exam_types[et_spec["name"]] = exam_type

        return created_exam_types


    @classmethod
    def load_demo_data(cls, db: Session) -> Dict[str, Any]:
        """
        Hazır sınav türlerini oluşturur ve YKS - TYT için 12 adet gerçekçi deneme sınavı yükler.
        """
        # 1. Varsayılan Kullanıcı Oluştur veya Al
        user = db.query(User).first()
        if not user:
            user = User(name="Örnek Öğrenci", email="ogrenci@pusulam.net")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Hazır Sınav Türlerini Oluştur (YKS-TYT, YKS-AYT, LGS, KPSS, TUS, DUS)
        exam_types_map = cls.create_predefined_exam_types(db, user)
        tyt_exam_type = exam_types_map.get("YKS - TYT")

        # Ders nesneleri eşleşmesi
        course_objects = {}
        for course in tyt_exam_type.courses:
            course_objects[course.name] = course

        # 3. TYT için 12 adet örnek deneme sınavı verisi
        start_date = date.today() - timedelta(days=90)
        demo_exams_spec = [
            {"name": "3D Yayınları Türkiye Geneli - 1", "pub": "3D Yayınları", "diff": "Kolay", "days": 0, 
             "scores": {"Türkçe": (28, 6, 6), "Sosyal Bilimler": (14, 4, 2), "Temel Matematik": (20, 8, 12), "Fen Bilimleri": (14, 4, 2)}},
            {"name": "Özdebir TYT Pro-1", "pub": "Özdebir", "diff": "Orta", "days": 7, 
             "scores": {"Türkçe": (29, 5, 6), "Sosyal Bilimler": (15, 3, 2), "Temel Matematik": (22, 6, 12), "Fen Bilimleri": (13, 5, 2)}},
            {"name": "Bilgi Sarmal TYT 1", "pub": "Bilgi Sarmal", "diff": "Orta", "days": 14, 
             "scores": {"Türkçe": (30, 4, 6), "Sosyal Bilimler": (14, 5, 1), "Temel Matematik": (24, 7, 9), "Fen Bilimleri": (12, 5, 3)}},
            {"name": "Toprak Yayınları Kurumsal 1", "pub": "Toprak", "diff": "Kolay", "days": 21, 
             "scores": {"Türkçe": (31, 5, 4), "Sosyal Bilimler": (16, 2, 2), "Temel Matematik": (26, 4, 10), "Fen Bilimleri": (12, 4, 4)}},
            {"name": "Aydın Yayınları TYT 2", "pub": "Aydın", "diff": "Zor", "days": 28, 
             "scores": {"Türkçe": (30, 7, 3), "Sosyal Bilimler": (13, 6, 1), "Temel Matematik": (19, 10, 11), "Fen Bilimleri": (11, 6, 3)}},
            {"name": "Endemik TYT Deneme 3", "pub": "Endemik", "diff": "Orta", "days": 35, 
             "scores": {"Türkçe": (32, 4, 4), "Sosyal Bilimler": (15, 4, 1), "Temel Matematik": (25, 6, 9), "Fen Bilimleri": (11, 5, 4)}},
            {"name": "Limit Yayınları Kurumsal 2", "pub": "Limit", "diff": "Zor", "days": 42, 
             "scores": {"Türkçe": (33, 5, 2), "Sosyal Bilimler": (14, 5, 1), "Temel Matematik": (27, 8, 5), "Fen Bilimleri": (10, 7, 3)}},
            {"name": "345 TYT Genel Prova 1", "pub": "ÜçDörtBeş", "diff": "Orta", "days": 49, 
             "scores": {"Türkçe": (34, 4, 2), "Sosyal Bilimler": (16, 3, 1), "Temel Matematik": (29, 5, 6), "Fen Bilimleri": (10, 6, 4)}},
            {"name": "Hız ve Renk TYT 4", "pub": "Hız ve Renk", "diff": "Kolay", "days": 56, 
             "scores": {"Türkçe": (35, 3, 2), "Sosyal Bilimler": (17, 2, 1), "Temel Matematik": (31, 4, 5), "Fen Bilimleri": (10, 5, 5)}},
            {"name": "Özdebir TYT Pro-2", "pub": "Özdebir", "diff": "Zor", "days": 63, 
             "scores": {"Türkçe": (34, 5, 1), "Sosyal Bilimler": (15, 4, 1), "Temel Matematik": (26, 9, 5), "Fen Bilimleri": (9, 8, 3)}},
            {"name": "Kafa Dengi Ekstra TYT", "pub": "Kafa Dengi", "diff": "Orta", "days": 70, 
             "scores": {"Türkçe": (36, 3, 1), "Sosyal Bilimler": (16, 3, 1), "Temel Matematik": (30, 6, 4), "Fen Bilimleri": (9, 7, 4)}},
            {"name": "3D Türkiye Geneli - 2", "pub": "3D Yayınları", "diff": "Orta", "days": 77, 
             "scores": {"Türkçe": (37, 2, 1), "Sosyal Bilimler": (17, 2, 1), "Temel Matematik": (32, 5, 3), "Fen Bilimleri": (10, 6, 4)}}
        ]

        added_count = 0
        for spec in demo_exams_spec:
            exam_date_val = start_date + timedelta(days=spec["days"])
            
            existing = db.query(PracticeExam).filter_by(
                user_id=user.id,
                exam_type_id=tyt_exam_type.id,
                name=spec["name"]
            ).first()

            if existing:
                continue

            tot_c, tot_w, tot_b = 0, 0, 0
            tot_net = 0.0

            results_to_create = []
            for course_name, (c, w, b) in spec["scores"].items():
                course_obj = course_objects[course_name]
                net = NetCalculatorService.calculate_course_net(c, w, tyt_exam_type.wrong_penalty_divisor)
                tot_c += c
                tot_w += w
                tot_b += b
                tot_net += net
                results_to_create.append({
                    "course_id": course_obj.id,
                    "correct_count": c,
                    "wrong_count": w,
                    "blank_count": b,
                    "net": net
                })

            exam = PracticeExam(
                user_id=user.id,
                exam_type_id=tyt_exam_type.id,
                name=spec["name"],
                publisher=spec["pub"],
                exam_date=exam_date_val,
                duration_minutes=165,
                difficulty=spec["diff"],
                total_correct=tot_c,
                total_wrong=tot_w,
                total_blank=tot_b,
                total_net=round(tot_net, 2)
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)

            for r in results_to_create:
                cr = CourseResult(
                    practice_exam_id=exam.id,
                    course_id=r["course_id"],
                    correct_count=r["correct_count"],
                    wrong_count=r["wrong_count"],
                    blank_count=r["blank_count"],
                    net=r["net"]
                )
                db.add(cr)

            db.commit()
            added_count += 1

        return {
            "status": "success",
            "message": f"Hazır sınav türleri ve demo verileri yüklendi. ({added_count} yeni deneme eklendi).",
            "added_exams_count": added_count
        }
