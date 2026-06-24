# 妙笔生花 × Outlines 融合增强

## 融合来源
- **竞品**: dottxt-ai/outlines (10K⭐)
- **核心能力**: 结构化输出约束 + JSON/Pydantic/正则/选择 + 类型系统映射

## 新增模块

### structured_generator.py
结构化输出生成器——在生成时约束LLM输出：
- `generate_json()`: JSON Schema 强制输出
- `generate_pydantic()`: Pydantic 模型生成
- `generate_choice()`: 选项约束（二选一/多选一）
- `generate_regex()`: 正则表达式匹配
- `SchemaBuilder`: 从类型提示/Pydantic模型自动构建JSON Schema
- 重试+错误反馈机制

### schema_prompts.py
Schema→Prompt 转换器——从类型定义自动生成提示词：
- `SchemaToPrompt.from_json_schema()`: JSON Schema → 自然语言描述
- `SchemaToPrompt.from_dict_example()`: 示例字典 → 提示词
- `SchemaToPrompt.from_field_descriptions()`: 字段描述 → 提示词
- `PromptTemplates`: 预置模板（文章/邮件/报告/评论）

### output_validator.py
输出验证器——验证、重试、回退：
- 4种策略：strict / lenient / coerce / fallback
- JSON自动修复（单引号→双引号、尾逗号、未引号键）
- 模糊匹配选择
- 类型强制转换
- `retry()`: 带反馈的重试机制

### format_templates.py
内容格式模板——5种预置结构化模板：
- `article`: 文章（标题+章节+关键点+结论）
- `email`: 邮件（主题+正文+行动号召）
- `report`: 报告（摘要+发现+建议+下一步）
- `summary`: 摘要（一句话+关键点+详情）
- `review`: 评论（评分+方面+优缺点+结论）

## 用法

```python
from structured_generator import StructuredGenerator
from output_validator import OutputValidator
from format_templates import get_template, generate_from_template, list_templates

# 1. 结构化JSON生成
gen = StructuredGenerator(llm_fn=your_llm)
result = gen.generate_json(
    "Write about AI agents",
    schema={"type": "object", "properties": {"title": {"type": "string"}, "body": {"type": "string"}}}
)

# 2. 选项约束
result = gen.generate_choice("Is this product good?", choices=["yes", "no", "maybe"])

# 3. 使用模板
article = generate_from_template(
    "article",
    llm_fn=your_llm,
    topic="AI Agent Architecture",
    word_count=1000,
    tone="professional",
    audience="developers",
)

# 4. 带验证的重试
validator = OutputValidator(strategy="lenient")
result = validator.retry(
    generate_fn=lambda: gen.generate_json(prompt, schema).raw_text,
    validate_fn=lambda raw: validator.validate_json(raw, schema),
    max_attempts=3,
)
```
