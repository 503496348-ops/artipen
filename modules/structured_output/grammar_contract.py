"""Small structured-output contract engine."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json, re
from typing import Any, Dict, Iterable, List
@dataclass(frozen=True)
class FieldSpec:
    name: str; type: str; required: bool = True; min_length: int = 0
@dataclass(frozen=True)
class ValidationIssue:
    field: str; message: str
@dataclass(frozen=True)
class ContractResult:
    ok: bool; data: Dict[str, Any]; issues: List[ValidationIssue]
    def to_dict(self) -> dict: return {"ok": self.ok, "data": self.data, "issues": [asdict(i) for i in self.issues]}
def strip_json_wrappers(text: str) -> str:
    value=(text or '').strip(); fence=re.search(r'```(?:json)?\s*(.*?)```', value, re.S | re.I)
    if fence: value=fence.group(1).strip()
    start=value.find('{'); end=value.rfind('}')
    if start >= 0 and end > start: value=value[start:end+1]
    return value
def parse_object(text: str) -> Dict[str, Any]: return json.loads(strip_json_wrappers(text))
def _type_ok(value: Any, typ: str) -> bool:
    return {'str': isinstance(value,str), 'list': isinstance(value,list), 'dict': isinstance(value,dict), 'int': isinstance(value,int) and not isinstance(value,bool), 'float': isinstance(value,(int,float)) and not isinstance(value,bool), 'bool': isinstance(value,bool)}.get(typ, True)
def validate_contract(text: str, fields: Iterable[FieldSpec]) -> ContractResult:
    issues=[]
    try: data=parse_object(text)
    except Exception as exc: return ContractResult(False, {}, [ValidationIssue('$', f'invalid json: {exc}')])
    for spec in fields:
        if spec.required and spec.name not in data: issues.append(ValidationIssue(spec.name, 'missing required field')); continue
        if spec.name in data:
            value=data[spec.name]
            if not _type_ok(value, spec.type): issues.append(ValidationIssue(spec.name, f'expected {spec.type}'))
            if isinstance(value, str) and len(value.strip()) < spec.min_length: issues.append(ValidationIssue(spec.name, f'min length {spec.min_length}'))
    return ContractResult(not issues, data, issues)
def article_plan_contract() -> List[FieldSpec]:
    return [FieldSpec('title','str',True,4), FieldSpec('hook','str',True,12), FieldSpec('outline','list',True), FieldSpec('evidence','list',False), FieldSpec('risk_notes','list',False)]
