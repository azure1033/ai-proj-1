## MODIFIED Requirements

### Requirement: Weather Keyword Classification
The system SHALL use tiered keyword matching to classify weather intent, preventing false matches from over-broad single keywords.

#### Scenario: Primary weather keyword triggers weather intent
- **WHEN** user query contains a primary weather keyword (e.g., "天气", "下雨", "温度", "热", "冷")
- **THEN** the system SHALL classify as "天气查询"

#### Scenario: Secondary keyword alone does NOT trigger weather
- **WHEN** user query contains only secondary keywords (e.g., "今天", "明天", "这里", "穿")
- **AND** no primary weather keyword is present
- **THEN** the system SHALL NOT classify as weather
- **AND** SHALL delegate to LLM classification instead

#### Scenario: Secondary keyword with primary triggers weather normally
- **WHEN** user query contains both a primary keyword (e.g., "天气") and a secondary keyword (e.g., "今天")
- **THEN** the system SHALL classify as "天气查询" normally
