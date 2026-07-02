from __future__ import annotations
from dataclasses import dataclass, asdict
import json, re
@dataclass
class SlideOutline:
    title:str; lead:str; modules:list[dict]; footer:str
    def information_points(self)->int: return 1 + sum(1+len(m.get('points',[]))+(1 if m.get('metric') else 0) for m in self.modules) + 1
    def validate(self)->list[str]:
        errors=[]
        if len(self.modules)<3: errors.append('at least 3 modules are required')
        if self.information_points()<12: errors.append('slide outline too thin')
        if re.search(r'lorem|placeholder|占位|待填写', json.dumps(asdict(self), ensure_ascii=False), re.I): errors.append('placeholder detected')
        return errors
def thicken_for_slide(title:str, claims:list[str], footer:str='')->SlideOutline:
    claims=[c.strip() for c in claims if c.strip()]; modules=[]
    for i in range(0,len(claims),3):
        chunk=claims[i:i+3]
        if chunk: modules.append({'title':f'模块 {len(modules)+1}','points':chunk,'metric':f'{len(chunk)} 个要点'})
    while len(modules)<3: modules.append({'title':f'补充维度 {len(modules)+1}','points':['补充真实案例或证据','补充执行动作'],'metric':'2 个动作'})
    return SlideOutline(title, f'围绕「{title}」建立可展示的结构化叙事。', modules[:4], footer or '先锁定观点，再扩展视觉表达。')
