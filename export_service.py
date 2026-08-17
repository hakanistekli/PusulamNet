import io
import pandas as pd
from typing import List, Dict, Any

class ExportService:
    @staticmethod
    def export_exams_to_csv(exams_data: List[Dict[str, Any]]) -> str:
        """
        Deneme sınavları listesini CSV formatına dönüştürür.
        """
        df = pd.DataFrame(exams_data)
        if df.empty:
            return "Tarih,Deneme Adı,Sınav Türü,Toplam Doğru,Toplam Yanlış,Toplam Boş,Toplam Net\n"
        
        # Sadece gerekli sütunları Türkçe başlıklarla sırala
        columns_map = {
            "exam_date": "Tarih",
            "name": "Deneme Adı",
            "exam_type_name": "Sınav Türü",
            "total_correct": "Toplam Doğru",
            "total_wrong": "Toplam Yanlış",
            "total_blank": "Toplam Boş",
            "total_net": "Toplam Net"
        }
        
        selected_cols = [c for c in columns_map.keys() if c in df.columns]
        df = df[selected_cols].rename(columns=columns_map)
        return df.to_csv(index=False, encoding="utf-8-sig")

    @staticmethod
    def export_exams_to_excel(exams_data: List[Dict[str, Any]]) -> bytes:
        """
        Deneme sınavları listesini Excel (.xlsx) formatında binary olarak döndürür.
        """
        df = pd.DataFrame(exams_data)
        columns_map = {
            "exam_date": "Tarih",
            "name": "Deneme Adı",
            "exam_type_name": "Sınav Türü",
            "total_correct": "Toplam Doğru",
            "total_wrong": "Toplam Yanlış",
            "total_blank": "Toplam Boş",
            "total_net": "Toplam Net"
        }
        
        if not df.empty:
            selected_cols = [c for c in columns_map.keys() if c in df.columns]
            df = df[selected_cols].rename(columns=columns_map)
        else:
            df = pd.DataFrame(columns=list(columns_map.values()))

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Deneme Geçmişi")
        return output.getvalue()

    @staticmethod
    def export_report_to_csv(report_data: Dict[str, Any]) -> str:
        """
        Genel performans raporunu CSV formatına dönüştürür.
        """
        lines = []
        lines.append("PUSULAMNET - GENEL PERFORMANS RAPORU")
        lines.append(f"Tarih Aralığı,{report_data.get('start_date', 'Tümü')} - {report_data.get('end_date', 'Tümü')}")
        lines.append(f"Toplam Deneme Sayısı,{report_data.get('exam_count', 0)}")
        lines.append(f"İlk Deneme Neti,{report_data.get('first_exam_net', '-')}")
        lines.append(f"Son Deneme Neti,{report_data.get('last_exam_net', '-')}")
        lines.append(f"Net Değişimi,{report_data.get('net_change', '-')}")
        lines.append(f"Ortalama Net,{report_data.get('average_net', '-')}")
        lines.append(f"En Yüksek Net,{report_data.get('highest_net', '-')}")
        lines.append(f"En Düşük Net,{report_data.get('lowest_net', '-')}")
        lines.append(f"Performans İstikrarı,{report_data.get('stability_status', '-')}")
        lines.append(f"En Çok Gelişen Ders,{report_data.get('most_improved_course', '-')}")
        lines.append(f"En Çok Düşen Ders,{report_data.get('most_declined_course', '-')}")
        lines.append("")
        lines.append("DERS BAZLI ÖZET")
        lines.append("Ders Adı,Ortalama Net,Ortalama Doğru,Ortalama Yanlış,Ortalama Boş,Dönemsel Değişim")
        
        for c in report_data.get("course_summaries", []):
            lines.append(
                f"{c.get('course_name')},{c.get('overall_avg_net')},{c.get('correct_avg')},"
                f"{c.get('wrong_avg')},{c.get('blank_avg')},{c.get('period_change', '-')}"
            )
        
        lines.append("")
        lines.append("OTOMATİK ANALİZ AÇIKLAMALARI")
        for exp in report_data.get("explanations", []):
            lines.append(f'"{exp}"')

        return "\n".join(lines)

    @staticmethod
    def export_report_to_excel(report_data: Dict[str, Any]) -> bytes:
        """
        Genel performans raporunu Excel (.xlsx) formatında binary olarak döndürür.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Genel özet sayfası
            summary_items = [
                {"Metrik": "Toplam Deneme Sayısı", "Değer": report_data.get("exam_count", 0)},
                {"Metrik": "İlk Deneme Neti", "Değer": report_data.get("first_exam_net", "-")},
                {"Metrik": "Son Deneme Neti", "Değer": report_data.get("last_exam_net", "-")},
                {"Metrik": "Net Değişimi", "Değer": report_data.get("net_change", "-")},
                {"Metrik": "Ortalama Net", "Değer": report_data.get("average_net", "-")},
                {"Metrik": "En Yüksek Net", "Değer": report_data.get("highest_net", "-")},
                {"Metrik": "En Düşük Net", "Değer": report_data.get("lowest_net", "-")},
                {"Metrik": "Performans İstikrarı", "Değer": report_data.get("stability_status", "-")},
                {"Metrik": "En Çok Gelişen Ders", "Değer": report_data.get("most_improved_course", "-")},
                {"Metrik": "En Çok Düşen Ders", "Değer": report_data.get("most_declined_course", "-")}
            ]
            pd.DataFrame(summary_items).to_excel(writer, index=False, sheet_name="Genel Özet")

            # Ders Bazlı İstatistikler Sayfası
            courses = report_data.get("course_summaries", [])
            if courses:
                courses_df = pd.DataFrame(courses).rename(columns={
                    "course_name": "Ders Adı",
                    "overall_avg_net": "Ortalama Net",
                    "correct_avg": "Ortalama Doğru",
                    "wrong_avg": "Ortalama Yanlış",
                    "blank_avg": "Ortalama Boş",
                    "period_change": "Dönemsel Değişim"
                })
                courses_df.to_excel(writer, index=False, sheet_name="Ders Detayları")

        return output.getvalue()
