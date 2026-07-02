import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from artipen.presentation_outline import thicken_for_slide

def test_thicken_for_slide_creates_enough_modules():
    s=thicken_for_slide('AI内容运营', ['统一入口','沉淀模板','复盘指标','渠道分发','线索回收','案例复用'])
    assert len(s.modules) >= 3
    assert not s.validate(), s.validate()
