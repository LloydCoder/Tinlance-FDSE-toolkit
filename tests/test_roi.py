from fdse_toolkit.roi import ROIInput, calculate_roi


def test_roi_is_assumption_driven_and_has_sensitivity():
    result = calculate_roi(ROIInput("ROI-ACME-001", 6000, 100000, 0.25))
    assert result["expected_loss_avoided_usd"] == 25000.0
    assert result["roi_multiple"] == 3.1667
    assert len(result["sensitivity"]) == 3
    assert "detection latency" in " ".join(result["assumptions"])
