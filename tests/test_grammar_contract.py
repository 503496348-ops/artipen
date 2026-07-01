from modules.structured_output.grammar_contract import validate_contract, article_plan_contract

def test_validate_contract_accepts_json():
    text='{"title":"好标题内容","hook":"这是一个足够长的开头钩子","outline":["a"]}'
    result=validate_contract(text, article_plan_contract())
    assert result.ok

def test_validate_contract_reports_missing_field():
    result=validate_contract('{"title":"短"}', article_plan_contract())
    assert not result.ok
    assert any(i.field == 'hook' for i in result.issues)
