# Documentación — índice

> Docs internos en **español**; README raíz y UI del dashboard en **inglés** (jurado internacional).

| Carpeta | Qué contiene | Dueño |
|---|---|---|
| [00_executive/](00_executive/) | [EXECUTIVE_PLAN.md](00_executive/EXECUTIVE_PLAN.md): visión, alcance, fases, tareas, gates, cronograma, contingencia | Todos |
| [01_management/](01_management/) | [MILESTONES.md](01_management/MILESTONES.md) (checklist) · [PROGRESS.md](01_management/PROGRESS.md) (tablero + bitácora) · [TEAM_AND_ROLES.md](01_management/TEAM_AND_ROLES.md) · [RISK_REGISTER.md](01_management/RISK_REGISTER.md) · [decisions/](01_management/decisions/) (ADRs) | PM |
| [02_data_engineering/](02_data_engineering/) | [DATA_SOURCES.md](02_data_engineering/DATA_SOURCES.md) · [TRIAGE_METHODOLOGY.md](02_data_engineering/TRIAGE_METHODOLOGY.md) · [PIPELINE_MEDALLION.md](02_data_engineering/PIPELINE_MEDALLION.md) · [DATA_DICTIONARY.md](02_data_engineering/DATA_DICTIONARY.md) · [investigations/](02_data_engineering/investigations/) (perfil por PSI-ID) | DE |
| [03_data_science/](03_data_science/) | [RESEARCH_QUESTIONS.md](03_data_science/RESEARCH_QUESTIONS.md) · [EDA_PROTOCOL.md](03_data_science/EDA_PROTOCOL.md) · [MODELING_PLAN.md](03_data_science/MODELING_PLAN.md) · [RANKING_METHODOLOGY.md](03_data_science/RANKING_METHODOLOGY.md) · [RAG_DESIGN.md](03_data_science/RAG_DESIGN.md) · [findings/](03_data_science/findings/) · [model_cards/](03_data_science/model_cards/) | DS / RAG |
| [04_physics/](04_physics/) | [PHYSICS_PRIMER.md](04_physics/PHYSICS_PRIMER.md) · [HABITAT_ATMOSPHERES.md](04_physics/HABITAT_ATMOSPHERES.md) · [INTERPRETATION_FRAMEWORK.md](04_physics/INTERPRETATION_FRAMEWORK.md) · [LITERATURE_REVIEW.md](04_physics/LITERATURE_REVIEW.md) · [RECOMMENDATIONS.md](04_physics/RECOMMENDATIONS.md) | PHY |
| [05_dashboard/](05_dashboard/) | [DASHBOARD_SPEC.md](05_dashboard/DASHBOARD_SPEC.md) | APP |
| [06_submission/](06_submission/) | [SUBMISSION_CHECKLIST.md](06_submission/SUBMISSION_CHECKLIST.md) · [DEMO_SCRIPT.md](06_submission/DEMO_SCRIPT.md) | SUB |
| [REFERENCES.md](REFERENCES.md) | Bibliografía, datos y créditos | Todos |

## Flujo documental

```text
RESEARCH_QUESTIONS ─► TRIAGE ─► ADR-0002 ─► DATA_DICTIONARY ─► (pipeline) ─► findings/ + model_cards/
                                                                              │
                         PHYSICS_PRIMER + INTERPRETATION_FRAMEWORK ──revisión─┘
                                                                              ▼
                                                                    RECOMMENDATIONS ─► dashboard
```

## Plantillas
- ADR: [01_management/decisions/ADR-0000-template.md](01_management/decisions/ADR-0000-template.md)
- Perfil de investigación: [02_data_engineering/investigations/_TEMPLATE.md](02_data_engineering/investigations/_TEMPLATE.md)
- Finding: [03_data_science/findings/_TEMPLATE.md](03_data_science/findings/_TEMPLATE.md)
- Model card: [03_data_science/model_cards/_TEMPLATE.md](03_data_science/model_cards/_TEMPLATE.md)
- Ficha de literatura: dentro de [04_physics/LITERATURE_REVIEW.md](04_physics/LITERATURE_REVIEW.md)
