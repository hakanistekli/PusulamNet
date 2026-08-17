import pytest
try:
    from app.services.analysis_service import AnalysisService
except ModuleNotFoundError:
    try:
        from services.analysis_service import AnalysisService
    except ModuleNotFoundError:
        from analysis_service import AnalysisService

def test_period_comparison_and_averages():
    # 6 denemelik veri seti
    exams = [
        {"exam_date": "01.01.2026", "total_net": 60.0},
        {"exam_date": "08.01.2026", "total_net": 62.0},
        {"exam_date": "15.01.2026", "total_net": 64.0}, # İlk 3 ortalama = 62.0
        {"exam_date": "22.01.2026", "total_net": 68.0},
        {"exam_date": "29.01.2026", "total_net": 70.0},
        {"exam_date": "05.02.2026", "total_net": 72.0}, # Son 3 ortalama = 70.0
    ]
    
    stats = AnalysisService.calculate_overall_statistics(exams, target_net=80.0)
    assert stats["overall_net_average"] == 66.0
    assert stats["last_3_net_average"] == 70.0
    assert stats["period_change"] == 8.0 # 70.0 - 62.0 = 8.0 net artış
    assert stats["highest_total_net"] == 72.0
    assert stats["lowest_total_net"] == 60.0

def test_stability_classification():
    # Son 5 denemesi birbirine çok yakın (std <= 2.0 -> İstikrarlı)
    stable_exams = [{"exam_date": f"0{i}.01.2026", "total_net": net} for i, net in enumerate([80.0, 81.0, 80.5, 79.5, 80.0], 1)]
    stats_stable = AnalysisService.calculate_overall_statistics(stable_exams)
    assert stats_stable["stability_status"] == "İstikrarlı"

    # Son 5 denemesi dalgalı (std > 5.0 -> Dalgalı)
    volatile_exams = [{"exam_date": f"0{i}.01.2026", "total_net": net} for i, net in enumerate([50.0, 75.0, 60.0, 85.0, 55.0], 1)]
    stats_volatile = AnalysisService.calculate_overall_statistics(volatile_exams)
    assert stats_volatile["stability_status"] == "Dalgalı"

def test_target_difference_calculation():
    exams = [{"exam_date": f"0{i}.01.2026", "total_net": net} for i, net in enumerate([70.0, 72.0, 74.0, 76.0, 78.0], 1)]
    stats = AnalysisService.calculate_overall_statistics(exams, target_net=85.0)
    # Son 5 ortalama: 74.0. Hedef: 85.0 -> Fark: 85 - 74 = 11.0
    assert stats["target_net_diff"] == 11.0

def test_most_improved_course_identification():
    courses_stats = [
        {"course_name": "Türkçe", "period_change": 4.5, "last_3_avg_net": 32.0, "overall_avg_net": 28.0},
        {"course_name": "Matematik", "period_change": 1.2, "last_3_avg_net": 25.0, "overall_avg_net": 24.0},
        {"course_name": "Fen", "period_change": -2.5, "last_3_avg_net": 10.0, "overall_avg_net": 12.5}
    ]
    improved, declined = AnalysisService.identify_course_growth_and_decline(courses_stats)
    assert improved == "Türkçe"
    assert declined == "Fen"
