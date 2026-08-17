import pytest
try:
    from app.services.net_calculator import NetCalculatorService
except ModuleNotFoundError:
    try:
        from services.net_calculator import NetCalculatorService
    except ModuleNotFoundError:
        from net_calculator import NetCalculatorService

def test_net_calculator_default_divisor():
    # 4 yanlış 1 doğruyu götürür (30 doğru, 8 yanlış = 30 - 2 = 28 net)
    net = NetCalculatorService.calculate_course_net(30, 8, penalty_divisor=4.0)
    assert net == 28.0

def test_net_calculator_custom_divisor():
    # 3 yanlış 1 doğruyu götürür (30 doğru, 6 yanlış = 30 - 2 = 28 net)
    net = NetCalculatorService.calculate_course_net(30, 6, penalty_divisor=3.0)
    assert net == 28.0

    # 4 yanlış 1 doğruyu götürür (25 doğru, 5 yanlış = 25 - 1.25 = 23.75 net)
    net2 = NetCalculatorService.calculate_course_net(25, 5, penalty_divisor=4.0)
    assert net2 == 23.75

def test_net_calculator_negative_values():
    with pytest.raises(ValueError):
        NetCalculatorService.calculate_course_net(-5, 4)
    with pytest.raises(ValueError):
        NetCalculatorService.calculate_course_net(10, -2)

def test_total_exceeds_question_count_validation():
    # Toplam 40 soru olan derste 30 doğru + 10 yanlış + 5 boş = 45 soru (HATA vermeli)
    with pytest.raises(ValueError) as exc_info:
        NetCalculatorService.validate_and_calculate_course_result(
            correct=30, wrong=10, blank=5, question_count=40, penalty_divisor=4.0, course_name="Matematik"
        )
    assert "dersin tanımlı soru sayısını (40) aşıyor" in str(exc_info.value)

def test_exam_totals_calculation():
    courses_data = [
        {"course_id": 1, "correct_count": 30, "wrong_count": 4, "blank_count": 6},
        {"course_id": 2, "correct_count": 15, "wrong_count": 4, "blank_count": 1}
    ]
    q_map = {1: 40, 2: 20}
    
    tot_c, tot_w, tot_b, tot_net, results = NetCalculatorService.calculate_exam_totals(
        course_data_list=courses_data,
        question_count_map=q_map,
        penalty_divisor=4.0
    )
    assert tot_c == 45
    assert tot_w == 8
    assert tot_b == 7
    # Course 1 net: 30 - 1 = 29.0, Course 2 net: 15 - 1 = 14.0, Total = 43.0
    assert tot_net == 43.0
