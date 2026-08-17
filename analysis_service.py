import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
try:
    from app.config import settings
except ModuleNotFoundError:
    try:
        from config import settings
    except ModuleNotFoundError:
        from config import settings


class AnalysisService:
    @staticmethod
    def calculate_overall_statistics(exams: List[Dict[str, Any]], target_net: float = 0.0) -> Dict[str, Any]:
        """
        Deneme sınavları listesinden genel istatistikleri ve özet kart verilerini hesaplar.
        exams listesindeki her bir nesne exam_date göre artan (kronolojik) sıralı olmalıdır.
        """
        if not exams:
            return {
                "latest_exam_total_net": None,
                "overall_net_average": None,
                "last_3_net_average": None,
                "last_5_net_average": None,
                "highest_total_net": None,
                "lowest_total_net": None,
                "target_net": target_net,
                "target_net_diff": None,
                "most_improved_course": None,
                "most_declined_course": None,
                "total_exams_count": 0,
                "stability_status": None,
                "std_dev": None,
                "period_change": None
            }

        df = pd.DataFrame(exams)
        # Tarih sıralamasını string alfabetik değil, datetime olarak yap
        if "exam_date" in df.columns:
            df["sort_date"] = pd.to_datetime(df["exam_date"], dayfirst=True, errors="coerce")
            df = df.sort_values(by="sort_date", ascending=True).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        total_exams = len(df)

        nets = df["total_net"].values

        latest_exam_net = round(float(nets[-1]), 2)
        overall_avg = round(float(np.mean(nets)), 2)
        highest_net = round(float(np.max(nets)), 2)
        lowest_net = round(float(np.min(nets)), 2)

        last_3_avg = round(float(np.mean(nets[-3:])), 2) if total_exams >= 3 else round(float(np.mean(nets)), 2)
        last_5_avg = round(float(np.mean(nets[-5:])), 2) if total_exams >= 5 else round(float(np.mean(nets)), 2)

        # Hedefe kalan fark (Hedef Net - Son 5 Ortalama)
        ref_avg_for_target = last_5_avg if total_exams >= 5 else overall_avg
        target_diff = round(target_net - ref_avg_for_target, 2) if target_net > 0 else None

        # İstikrar Analizi (Son 5 deneme standart sapması)
        std_dev = None
        stability_status = None
        if total_exams >= settings.MIN_EXAMS_FOR_STABILITY_ANALYSIS:
            std_dev = float(np.std(nets[-5:], ddof=1)) if len(nets[-5:]) > 1 else 0.0
            std_dev = round(std_dev, 2)
            
            if std_dev <= settings.STD_STABLE_THRESHOLD:
                stability_status = "İstikrarlı"
            elif std_dev <= settings.STD_MODERATE_THRESHOLD:
                stability_status = "Orta düzeyde dalgalı"
            else:
                stability_status = "Dalgalı"
        else:
            stability_status = "Yetersiz Veri"

        # Dönemsel Değişim (Son 3 ortalaması - Önceki 3 ortalaması)
        period_change = None
        if total_exams >= settings.MIN_EXAMS_FOR_PERIOD_ANALYSIS:
            recent_3_avg = np.mean(nets[-3:])
            prev_3_avg = np.mean(nets[-6:-3])
            period_change = round(float(recent_3_avg - prev_3_avg), 2)

        return {
            "latest_exam_total_net": latest_exam_net,
            "overall_net_average": overall_avg,
            "last_3_net_average": last_3_avg,
            "last_5_net_average": last_5_avg,
            "highest_total_net": highest_net,
            "lowest_total_net": lowest_net,
            "target_net": target_net,
            "target_net_diff": target_diff,
            "total_exams_count": total_exams,
            "stability_status": stability_status,
            "std_dev": std_dev,
            "period_change": period_change
        }

    @staticmethod
    def calculate_course_performance(
        course_id: int, 
        course_name: str,
        results_list: List[Dict[str, Any]], 
        target_net: float = 0.0
    ) -> Dict[str, Any]:
        """
        Belirli bir ders için detaylı analiz istatistiklerini hesaplar.
        results_list: exam_date sıralı ders sonuçları ve tarihleri.
        """
        if not results_list:
            return {
                "course_id": course_id,
                "course_name": course_name,
                "latest_net": 0.0,
                "overall_avg_net": 0.0,
                "last_3_avg_net": 0.0,
                "highest_net": 0.0,
                "lowest_net": 0.0,
                "period_change": None,
                "correct_avg": 0.0,
                "wrong_avg": 0.0,
                "blank_avg": 0.0,
                "std_dev": 0.0,
                "target_net": target_net,
                "target_diff": target_net
            }

        df = pd.DataFrame(results_list)
        if "exam_date" in df.columns:
            df["sort_date"] = pd.to_datetime(df["exam_date"], dayfirst=True, errors="coerce")
            df = df.sort_values(by="sort_date", ascending=True).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        total_count = len(df)

        nets = df["net"].values
        corrects = df["correct_count"].values
        wrongs = df["wrong_count"].values
        blanks = df["blank_count"].values

        latest_net = round(float(nets[-1]), 2)
        overall_avg = round(float(np.mean(nets)), 2)
        last_3_avg = round(float(np.mean(nets[-3:])), 2) if total_count >= 3 else overall_avg
        highest_net = round(float(np.max(nets)), 2)
        lowest_net = round(float(np.min(nets)), 2)

        correct_avg = round(float(np.mean(corrects)), 2)
        wrong_avg = round(float(np.mean(wrongs)), 2)
        blank_avg = round(float(np.mean(blanks)), 2)

        std_dev = round(float(np.std(nets, ddof=1)), 2) if total_count > 1 else 0.0

        period_change = None
        if total_count >= settings.MIN_EXAMS_FOR_PERIOD_ANALYSIS:
            recent_3 = np.mean(nets[-3:])
            prev_3 = np.mean(nets[-6:-3])
            period_change = round(float(recent_3 - prev_3), 2)

        target_diff = round(target_net - overall_avg, 2)

        return {
            "course_id": course_id,
            "course_name": course_name,
            "latest_net": latest_net,
            "overall_avg_net": overall_avg,
            "last_3_avg_net": last_3_avg,
            "highest_net": highest_net,
            "lowest_net": lowest_net,
            "period_change": period_change,
            "correct_avg": correct_avg,
            "wrong_avg": wrong_avg,
            "blank_avg": blank_avg,
            "std_dev": std_dev,
            "target_net": target_net,
            "target_diff": target_diff
        }

    @staticmethod
    def identify_course_growth_and_decline(
        courses_analysis: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Derslerin dönemsel değişimlerini (veya son 3 vs genel ortalamalarını) karşılaştırarak
        en çok gelişen ve en çok düşüş gösteren dersi belirler.
        """
        if not courses_analysis:
            return None, None

        # Period change varsa ona göre, yoksa (last_3_avg_net - overall_avg_net) farkına göre
        valid_courses = []
        for c in courses_analysis:
            change = c.get("period_change")
            if change is None:
                change = round(c["last_3_avg_net"] - c["overall_avg_net"], 2)
            valid_courses.append((c["course_name"], change))

        if not valid_courses:
            return None, None

        # Sort by change descending
        valid_courses.sort(key=lambda x: x[1], reverse=True)

        most_improved = valid_courses[0][0] if valid_courses[0][1] > 0 else None
        most_declined = valid_courses[-1][0] if valid_courses[-1][1] < 0 else None

        return most_improved, most_declined
