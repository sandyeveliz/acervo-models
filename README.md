# Acervo Graph Model

Fine-tuning de **Qwen3-8B** para reemplazar las llamadas LLM del pipeline de Acervo con un modelo especializado en extracción de grafos semánticos.

## Qué hace este modelo

Acervo es un índice semántico comprimido que reemplaza el retrieval de chunks (RAG clásico) con nodos estructurados de grafo. Este modelo maneja dos tareas:

- **S1 Unified** — Extrae entidades, relaciones, hechos, eventos y gestiona el topic activo (same/subtopic/changed)
- **S1.5 Graph Update** — Curación post-respuesta: merges de duplicados, correcciones de tipo, descarte de ruido

## Hardware requerido

- GPU: NVIDIA RTX 5070 Ti (16GB VRAM, Blackwell sm_120)
- CUDA: 12.8+ (driver compatible con Blackwell)
- PyTorch: nightly con backend cu128 (stable no soporta sm_120)
- OS: Windows 11

## Stack

- **Base model:** Qwen3-8B (non-thinking mode, `/no_think`)
- **Fine-tuning:** unsloth + LoRA (r=16, alpha=32)
- **Training:** trl SFT (DPO opcional en fase 2)
- **Dataset:** generado con Claude Sonnet via Anthropic API
- **Inferencia:** Ollama o LM Studio (GGUF cuantizado)

## Estructura

```
00_setup/          GPU check + instalación de dependencias
01_dataset/        Schemas, generación y validación de dataset
02_training/       SFT y DPO
03_eval/           Evaluación de métricas
04_export/         Export a GGUF para inferencia local
```

## Orden de ejecución

1. `00_setup/check_gpu.ipynb` — verificar GPU y compatibilidad Blackwell
2. `00_setup/install_deps.ipynb` — instalar dependencias (orden crítico)
3. `01_dataset/schema.py` — schemas Pydantic de S1 y S1.5
4. `01_dataset/generate_s1.ipynb` — generar 50 ejemplos, revisar a mano
5. Escalar a 2000 ejemplos S1 si pasan la revisión
6. `01_dataset/generate_s1_5.ipynb` — 1000 ejemplos S1.5
7. `01_dataset/validate_dataset.ipynb` — distribución, json_parse_rate, outliers
8. `02_training/train_sft.ipynb` — solo con ≥500 ejemplos validados y json_parse_rate > 98%

## Métricas clave

- **JSON parse rate** > 98% (gate #1 — antes que calidad de contenido)
- **Latencia S1** < 400ms (sync, bloquea respuesta)
- **Latencia S1.5** < 800ms (async, best-effort)

## Dataset target

- 2000 ejemplos S1 + 1000 ejemplos S1.5
- Distribución por tipo: 40% conversacional, 30% documento, 30% código
- Distribución topic_action: 50% same, 30% changed, 20% subtopic
- Idioma: 60% español, 40% inglés
