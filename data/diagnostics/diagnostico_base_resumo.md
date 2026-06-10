# Diagnóstico da base de entrevistas

Run ID: `20260519_234444`  
Gerado em: `2026-05-19 23:45:32`

## Fontes BigQuery

- Base segmentada/chunks/tokens: `kyra-pml-20261.kyra_base_2026_1.entrevistas_chunks_v2`
- Base de entrevistas completas: `kyra-pml-20261.kyra_base_2026_1.entrevistas_docs_v2`

## Tamanho das bases

| base | linhas | colunas |
|---|---:|---:|
| tokens/chunks | 12,041 | 32 |
| entrevistas completas | 155 | 29 |

## Colunas detectadas

### Tokens/chunks
```json
{
  "doc_id": "doc_id",
  "chunk_id": "chunk_id",
  "chunk_index": "chunk_index",
  "language": "idioma",
  "text": "texto_analise",
  "tokens": "n_palavras",
  "date": "timestamp_inicial"
}
```

### Entrevistas completas
```json
{
  "doc_id": "doc_id",
  "chunk_id": null,
  "chunk_index": null,
  "language": "idioma",
  "text": "texto_analise",
  "tokens": "n_palavras_total",
  "date": "data_bruta_nome_arquivo"
}
```

## Cobertura e IDs

| base                  | coluna_id   |   linhas |   ids_unicos |   ids_nulos |
|:----------------------|:------------|---------:|-------------:|------------:|
| tokens_chunks         | doc_id      |    12041 |          155 |           0 |
| entrevistas_completas | doc_id      |      155 |          155 |           0 |

## Distribuição de idioma detectado

| idioma_detectado_light   |   n_chunks |
|:-------------------------|-----------:|
| pt                       |       8628 |
| mixed                    |       3138 |
| es                       |        238 |
| en                       |         37 |

## Qualidade dos chunks

| n_chunks     |   count |
|:-------------|--------:|
| atenção      |    7771 |
| problemático |    2692 |
| ok           |    1508 |
| crítico      |      70 |

## Flags de qualidade

| flag                         |   n_chunks |   pct_chunks |
|:-----------------------------|-----------:|-------------:|
| has_many_noise_flags         |       9984 |       0.8292 |
| is_mixed_or_unknown_language |       3138 |       0.2606 |
| is_too_long                  |        120 |       0.01   |
| is_high_function_word_ratio  |        108 |       0.009  |
| is_too_short                 |         11 |       0.0009 |
| is_low_lexical_diversity     |          7 |       0.0006 |

## Ruídos/PII detectados

| flag                 |   chunks_com_ocorrencia |   pct_chunks |   total_ocorrencias |
|:---------------------|------------------------:|-------------:|--------------------:|
| timestamp_hhmmss     |                   12039 |       0.9998 |               91634 |
| speaker_label_short  |                    9929 |       0.8246 |               12473 |
| audio_video_filename |                    8561 |       0.711  |               10742 |
| generic_filename     |                       0 |       0      |                   0 |
| speaker_label_long   |                       0 |       0      |                   0 |
| date_like            |                       0 |       0      |                   0 |
| email                |                       0 |       0      |                   0 |
| phone_br_like        |                       0 |       0      |                   0 |
| cpf_like             |                       0 |       0      |                   0 |
| cep_like             |                       0 |       0      |                   0 |
| url                  |                       0 |       0      |                   0 |

## Arquivos principais para olhar antes do próximo notebook

1. `01_colunas_detectadas.csv` — confirma se as colunas certas foram inferidas.
2. `04_segmentacao_por_documento.csv` — mostra gaps, duplicidade de índice e tamanho dos chunks por entrevista.
3. `04_overlap_chunks_consecutivos.csv` — mostra repetição/overlap entre chunks consecutivos.
4. `05_idioma_mismatch_amostra.csv` e `05_idioma_misto_amostra.csv` — apontam mistura de idioma.
5. `06_tokens_funcionais_top1000.csv` — identifica preposições/fillers que estavam dominando clusters.
6. `07_ruidos_pii_resumo.csv` — mostra ruídos de transcrição e PII residual.
7. `08_chunks_para_revisao_top1000.csv` — prioriza chunks problemáticos.
8. `09_reconciliacao_chunks_vs_full.csv` — compara chunks agregados contra entrevistas completas.
9. `10_tfidf_termos_globais_top1000.csv` — sanity check de vocabulário pós-limpeza diagnóstica.

## Interpretação esperada

Este notebook deve responder:

- A tabela completa realmente foi baixada e bate com a tabela de chunks?
- Os IDs estão consistentes?
- A segmentação atual tem gaps, duplicatas ou overlap excessivo?
- Há mistura de idiomas relevante?
- O vocabulário está dominado por stopwords, fillers ou ruídos técnicos?
- Quais chunks devem ser revisados antes de definir a limpeza final?