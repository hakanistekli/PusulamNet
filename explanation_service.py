from typing import List, Dict, Any, Optional
try:
    from app.config import settings
except ModuleNotFoundError:
    try:
        from config import settings
    except ModuleNotFoundError:
        from config import settings

class ExplanationService:
    @staticmethod
    def generate_dashboard_explanations(
        overall_stats: Dict[str, Any],
        most_improved: Optional[str] = None,
        most_declined: Optional[str] = None,
        declined_amount: Optional[float] = None
    ) -> List[str]:
        """
        Ana panel ve genel özet ekranları için kural tabanlı Türkçe açıklama metinleri üretir.
        """
        explanations = []
        total_exams = overall_stats.get("total_exams_count", 0)

        # 1. Veri yetersizliği kontrolü (En az 3 deneme)
        if total_exams < settings.MIN_EXAMS_FOR_TREND:
            explanations.append("Henüz yeterli deneme kaydı bulunmuyor. Sağlıklı ve güçlü yorumlar üretebilmek için en az 3 deneme eklemelisin.")
            return explanations

        # 2. Dönemsel değişim yorumları (Son 3 vs Önceki 3)
        period_change = overall_stats.get("period_change")
        if period_change is not None:
            if period_change >= settings.PERIOD_CHANGE_SIGNIFICANT:
                explanations.append(
                    f"Son dönem net ortalaman önceki döneme göre {period_change:.1f} net arttı. Genel performansında olumlu bir gelişim bulunuyor."
                )
            elif period_change <= -settings.PERIOD_CHANGE_SIGNIFICANT:
                explanations.append(
                    f"Son dönem net ortalaman önceki döneme göre {abs(period_change):.1f} net düştü."
                )
            else:
                explanations.append("Son dönem net ortalaman büyük ölçüde sabit kaldı.")
        elif total_exams < settings.MIN_EXAMS_FOR_PERIOD_ANALYSIS:
            explanations.append("Dönemsel gelişim analizi oluşturulabilmesi için en az 6 deneme sonucu eklemelisin.")

        # 3. İstikrar (Standart Sapma) yorumları
        stability = overall_stats.get("stability_status")
        std_dev = overall_stats.get("std_dev")
        if stability == "İstikrarlı":
            explanations.append("Son 5 denemedeki sonuçların birbirine yakın. Performansın istikrarlı görünüyor.")
        elif stability == "Dalgalı":
            explanations.append("Son 5 denemedeki netlerin arasında belirgin fark bulunuyor. Sonuçların dalgalı bir görünüm sergiliyor.")
        elif stability == "Orta düzeyde dalgalı":
            explanations.append("Son 5 denemedeki netlerin orta düzeyde bir dalgalanma gösteriyor.")

        # 4. Ders bazlı gelişim ve düşüş yorumları
        if most_improved:
            explanations.append(f"Son dönemde en yüksek net artışını {most_improved} dersinde gösterdin.")
        
        if most_declined:
            if declined_amount and declined_amount > 0:
                explanations.append(f"{most_declined} net ortalaman önceki döneme göre {declined_amount:.1f} net düştü.")
            else:
                explanations.append(f"{most_declined} dersinde son dönemde düşüş eğilimi gözlemleniyor.")

        # 5. Hedef net yorumları
        target_diff = overall_stats.get("target_net_diff")
        target_net = overall_stats.get("target_net", 0.0)
        if target_net > 0 and target_diff is not None:
            if target_diff > 0:
                explanations.append(
                    f"Hedefine ulaşmak için son 5 deneme ortalamana göre {target_diff:.1f} netlik gelişime ihtiyacın bulunuyor."
                )
            else:
                explanations.append(
                    f"Son 5 deneme ortalaman belirlediğin hedefin {abs(target_diff):.1f} net üzerinde."
                )

        return explanations

    @staticmethod
    def generate_course_explanations(course_stats: Dict[str, Any]) -> List[str]:
        """
        Tek bir ders için özelleştirilmiş kural tabanlı Türkçe açıklama metinleri üretir.
        """
        explanations = []
        course_name = course_stats.get("course_name", "Ders")
        period_change = course_stats.get("period_change")
        wrong_avg = course_stats.get("wrong_avg", 0.0)
        blank_avg = course_stats.get("blank_avg", 0.0)
        target_diff = course_stats.get("target_diff", 0.0)
        target_net = course_stats.get("target_net", 0.0)

        # Dönemsel Değişim
        if period_change is not None:
            if period_change > 1.0:
                explanations.append(f"{course_name} dersinde son dönem ortalaman önceki döneme göre {period_change:.1f} net yükseldi.")
            elif period_change < -1.0:
                explanations.append(f"{course_name} dersinde son dönem ortalaman önceki döneme göre {abs(period_change):.1f} net geriledi.")
            else:
                explanations.append(f"{course_name} netlerin dönemsel olarak dengeli bir seyir izliyor.")

        # Yanlış ve Boş Sayısı Tavsiyeleri (İhtimalli ve Yapıcı Dil)
        if wrong_avg > 4.0:
            explanations.append(
                f"{course_name} dersindeki ortalama {wrong_avg:.1f} yanlış sayısı sonuçlarını olumsuz etkilemiş olabilir. Soruları daha dikkatli okumak faydalı olabilir."
            )
        elif blank_avg > 4.0:
            explanations.append(
                f"{course_name} dersinde ortalama {blank_avg:.1f} sorunun boş bırakıldığı görülüyor. Konu eksiklerini gözden geçirmek net artışı sağlayabilir."
            )

        # Ders Hedefi
        if target_net > 0:
            if target_diff > 0:
                explanations.append(f"{course_name} ders hedefinden {target_diff:.1f} net geridesin.")
            else:
                explanations.append(f"Tebrikler! {course_name} dersinde hedefini {abs(target_diff):.1f} net aştın.")

        return explanations
