# Pré-processamento de entrevistas KYRA

Run ID: `20260520_111127`

## Decisão metodológica

A segmentação final foi reconstruída a partir da tabela de entrevistas completas, não da tabela antiga de chunks.
A tabela antiga é usada apenas para comparação/auditoria.

## Base principal

Por enquanto, a base principal contém somente chunks classificados como português:

- `data/processed/interviews_chunks_modeling.parquet`
- `data/processed/interviews_chunks_modeling_pt.parquet`

## Volumes

- Entrevistas: 155
- Turnos extraídos: 63,647
- Novos chunks totais: 6,228
- Novos chunks PT para modelagem: 4,976
- Docs com chunks PT para modelagem: 131
- Percentual mantido na base PT: 79.9%
- Mediana de palavras por novo chunk: 265.0
- Média de tokens explicativos por chunk PT: 91.7

## Checklist

| check                                                | ok   | valor        |
|:-----------------------------------------------------|:-----|:-------------|
| doc_id unico em docs_pre                             | True | 155          |
| chunk_id unico em chunks_pre                         | True | 6228         |
| chunk_id unico em chunks_modeling_pt                 | True | 4976         |
| tokens_long_modeling alinhado com chunks_modeling_pt | True | 4976 vs 4976 |
| sem page counters na base principal                  | True | 0            |
| sem filenames/metadados na base principal            | True | 0            |
| sem timestamps na base principal                     | True | 0            |
| base principal somente pt                            | True | pt           |

## Ruído residual na base principal PT

| flag                      |   n_chunks |
|:--------------------------|-----------:|
| has_page_counter_residual |          0 |
| has_filename_residual     |          0 |
| has_meeting_meta_residual |          0 |
| has_timestamp_residual    |          0 |

## Uso recomendado

Para embeddings/clusterização, use:

- ID: `chunk_id`
- Texto: `text_for_embedding`
- Keywords explicativas: `text_for_keywords`
- Metadados: `doc_id`, `projeto`, `marca_foco`, `publico`, `tipo_sessao`, se existirem.

Não use stemming como entrada principal de embeddings.
