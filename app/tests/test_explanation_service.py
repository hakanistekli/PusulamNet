import pytest
try:
    from app.services.explanation_service import ExplanationService
except ModuleNotFoundError:
    try:
        from services.explanation_service import ExplanationService
    except ModuleNotFoundError:
        from explanation_service import ExplanationService

def test_insufficient_data_warning():
    stats = {"total_exams_count": 2}
    explanations = ExplanationService.generate_dashboard_explanations(stats)
    assert any("en az 3 deneme" in exp for exp in explanations)

def test_explanation_rules_for_growth_and_declines():
    stats = {
        "total_exams_count": 6,
        "period_change": 4.2,
        "stability_status": "İstikrarlı",
        "target_net": 90.0,
        "target_net_diff": 5.0
    }
    explanations = ExplanationService.generate_dashboard_explanations(
        overall_stats=stats,
        most_improved="Türkçe",
        most_declined="Fen Bilimleri",
        declined_amount=1.7
    )
    
    # Check that rule-based text matches requirements
    assert any("4.2 net arttı" in exp for exp in explanations)
    assert any("İstikrarlı" in stats["stability_status"] and "istikrarlı" in exp for exp in explanations)
    assert any("Türkçe" in exp and "en yüksek net artışını" in exp for exp in explanations)
    assert any("Fen Bilimleri net ortalaman önceki döneme göre 1.7 net düştü" in exp for exp in explanations)
    assert any("5.0 netlik gelişime ihtiyacın bulunuyor" in exp for exp in explanations)
