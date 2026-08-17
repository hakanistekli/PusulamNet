from typing import Dict, List, Tuple

class NetCalculatorService:
    @staticmethod
    def calculate_course_net(correct: int, wrong: int, penalty_divisor: float = 4.0) -> float:
        """
        Ders netini hesaplar.
        Formül: Net = Doğru - (Yanlış / penalty_divisor)
        """
        if penalty_divisor <= 0:
            raise ValueError("Götürme oranı (yanlış ceza katsayısı) 0'dan büyük olmalıdır.")
        if correct < 0 or wrong < 0:
            raise ValueError("Doğru ve yanlış sayıları negatif olamaz.")
        
        net = correct - (wrong / penalty_divisor)
        return round(net, 2)

    @staticmethod
    def validate_and_calculate_course_result(
        correct: int,
        wrong: int,
        blank: int,
        question_count: int,
        penalty_divisor: float = 4.0,
        course_name: str = "Ders"
    ) -> float:
        """
        Ders sonuçlarını doğrular ve neti hesaplar.
        Kurallar:
        - Doğru, yanlış ve boş negatif olamaz.
        - Doğru + Yanlış + Boş toplamı ilgili dersin soru sayısını aşamaz.
        """
        if correct < 0 or wrong < 0 or blank < 0:
            raise ValueError(f"{course_name} için doğru, yanlış ve boş sayıları negatif olamaz.")
        
        total_answers = correct + wrong + blank
        if total_answers > question_count:
            raise ValueError(
                f"{course_name} dersinde girilen toplam soru sayısı ({total_answers}), "
                f"dersin tanımlı soru sayısını ({question_count}) aşıyor!"
            )
        
        return NetCalculatorService.calculate_course_net(correct, wrong, penalty_divisor)

    @staticmethod
    def calculate_exam_totals(
        course_data_list: List[Dict[str, int]], 
        question_count_map: Dict[int, int],
        penalty_divisor: float = 4.0,
        course_name_map: Dict[int, str] = None
    ) -> Tuple[int, int, int, float, List[Dict]]:
        """
        Tüm deneme için toplam doğru, yanlış, boş ve toplam neti hesaplar.
        Her dersin doğrulanmış sonuçlarını döndürür.
        """
        if course_name_map is None:
            course_name_map = {}

        total_correct = 0
        total_wrong = 0
        total_blank = 0
        total_net = 0.0
        validated_course_results = []

        for item in course_data_list:
            course_id = item["course_id"]
            correct = item["correct_count"]
            wrong = item["wrong_count"]
            blank = item["blank_count"]

            question_count = question_count_map.get(course_id, 0)
            course_name = course_name_map.get(course_id, f"Ders #{course_id}")

            net = NetCalculatorService.validate_and_calculate_course_result(
                correct=correct,
                wrong=wrong,
                blank=blank,
                question_count=question_count,
                penalty_divisor=penalty_divisor,
                course_name=course_name
            )

            total_correct += correct
            total_wrong += wrong
            total_blank += blank
            total_net += net

            validated_course_results.append({
                "course_id": course_id,
                "correct_count": correct,
                "wrong_count": wrong,
                "blank_count": blank,
                "net": net
            })

        return total_correct, total_wrong, total_blank, round(total_net, 2), validated_course_results
