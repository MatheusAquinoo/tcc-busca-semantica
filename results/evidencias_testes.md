# Evidências de Execução da Suíte de 23 Testes Automatizados (`pytest`)

**Trabalho de Conclusão de Curso (TCC 2) - Engenharia de Software / UTFPR**  
**Autor:** Matheus de Aquino da Silva  
**Orientador:** Prof. Dr. Bruno Honorato  

Este documento registra as evidências formais de verificação automatizada do software (23 casos de teste divididos em nível Unitário, de Persistência/Integração com SGBD e de Sistema/API REST). Os artefatos brutos de execução encontram-se em [`results/pytest_evidencias.txt`](./pytest_evidencias.txt) e [`results/pytest_junit.xml`](./pytest_junit.xml).

---

## 1. Comando de Reprodução

Com o container `tcc_postgres_vector` ativo (`docker compose up -d`), execute na raiz do repositório:

```powershell
.\.venv\Scripts\pytest.exe -v -rA --junitxml=results/pytest_junit.xml
```

---

## 2. Sumário de Execução

* **Framework de Testes:** `pytest 9.1.1` (Python `3.11.9`)
* **Total de Casos de Teste Executados:** `23`
* **Aprovados (`PASSED`):** `23 (100,00%)`
* **Falhas (`FAILED` / `ERROR`):** `0`
* **Tempo Total de Execução:** `~10,90 s`

---

## 3. Matriz Rastreável dos 23 Casos de Teste Automatizados

### 3.1 Módulo de Testes Unitários (`tests/test_unit.py` — 8 Testes)
| # | Função de Teste | Requisito | O que é Verificado (Asserção) | Status |
| :---: | :--- | :---: | :--- | :---: |
| 1 | `test_clean_text_removes_control_chars_and_multiple_spaces` | RF02 | Remoção de `\r`, `\n`, `\t` e colapso de múltiplos espaços consecutivos em `clean_text()`. | `PASSED` |
| 2 | `test_chunk_text_short_document_single_chunk` | RF02 | Preservação integral de textos curtos ($\le 260$ caracteres) em um único fragmento. | `PASSED` |
| 3 | `test_chunk_text_long_document_creates_overlapping_chunks` | RF02 | Segmentação com janela deslizante (`overlap`) respeitando `max_chars` e fronteiras de palavras. | `PASSED` |
| 4 | `test_load_dataset_json_and_csv_equivalence` | RF01 | Equivalência estrita de leitura e estrutura entre `microsoft_faq.json` e `microsoft_faq.csv` (100 registros). | `PASSED` |
| 5 | `test_embedding_dimension_and_l2_normalization` | RF03 | Geração de vetor denso com dimensionalidade exata $D = 768$ e norma unitária $L_2$ ($\|\vec{v}\|_2 = 1,0 \pm 10^{-4}$). | `PASSED` |
| 6 | `test_semantic_similarity_synonyms_vs_unrelated` | RF03 | Produto interno entre consulta coloquial e manual sinônimo ($> 0,45$) superior a texto de domínio disjunto. | `PASSED` |
| 7 | `test_pydantic_search_request_validation` | API | Rejeição via `ValidationError` de consultas em branco e valores de `top_n` fora de $[1, 50]$. | `PASSED` |
| 8 | `test_pydantic_document_ingest_request_validation` | RF01 | Validação de comprimentos mínimos de `titulo`, `fonte`, `categoria` e `conteudo` no schema de ingestão. | `PASSED` |

### 3.2 Módulo de Testes de Persistência e Integração SGBD (`tests/test_persistence.py` — 5 Testes)
| # | Função de Teste | Requisito | O que é Verificado (Asserção) | Status |
| :---: | :--- | :---: | :--- | :---: |
| 9 | `test_pgvector_extension_installed` | RF04 | Presença e ativação da extensão `vector` (`pgvector`) no catálogo `pg_extension` do PostgreSQL 16. | `PASSED` |
| 10 | `test_tables_and_columns_schema` | DDL | Existência e tipagem física das colunas de `documentos` e `documento_chunks` (`vector(768)` e `jsonb`). | `PASSED` |
| 11 | `test_hnsw_and_gin_indexes_exist` | RF04 / RF05 / RF07 | Presença de `idx_chunks_embedding_hnsw` (`USING hnsw`, `vector_cosine_ops`), B-Trees e índices GIN em `pg_indexes`. | `PASSED` |
| 12 | `test_referential_integrity_cascade_delete` | ACID / DDL | Remoção automática em cascata (`ON DELETE CASCADE`) de `documento_chunks` ao excluir o registro pai em `documentos` (com `ROLLBACK`). | `PASSED` |
| 13 | `test_cosine_distance_operator_and_ordering` | RF04 / RF06 | Monotonicidade ascendente estrita das distâncias retornadas pelo operador `<=>` no intervalo $[0, 1]$. | `PASSED` |

### 3.3 Módulo de Testes de Sistema e API REST (`tests/test_api.py` — 10 Testes)
| # | Função de Teste | Requisito | O que é Verificado (Asserção) | Status |
| :---: | :--- | :---: | :--- | :---: |
| 14 | `test_root_endpoint` | Web UI | Renderização HTTP 200 da interface web interativa (`GET /`). | `PASSED` |
| 15 | `test_api_info_endpoint` | API | Retorno HTTP 200 de metadados institucionais, modelo ativo e `dimensao_vetorial == 768` (`GET /api/info`). | `PASSED` |
| 16 | `test_health_check_endpoint` | SGBD | Verificação de saúde (`GET /health`), confirmando 200 documentos, 455 *chunks* e índice HNSW ativo. | `PASSED` |
| 17 | `test_categories_and_stats_endpoints` | RF07 | Listagem de categorias (`GET /categories`) e estatísticas físicas do banco (`GET /stats`). | `PASSED` |
| 18 | `test_documents_listing_and_detail_endpoints` | RF01 / RF02 | Paginação filtrada (`GET /documents`), detalhamento de *chunks* (`GET /documents/1`) e tratamento HTTP 404. | `PASSED` |
| 19 | `test_semantic_search_endpoint_and_deduplication` | RF04 / RF06 | Busca semântica (`POST /search/semantic`), telemetria ($T_{emb}, T_{sql}, T_{total}$) e ausência de `documento_id` duplicado no Top-5. | `PASSED` |
| 20 | `test_semantic_search_with_category_and_tag_prefiltering` | RF07 | Pré-filtragem relacional combinada por `categoria`, `fonte`, `tag` JSONB e `ef_search`. | `PASSED` |
| 21 | `test_lexical_search_modes` | RF05 | Execução do motor lexical FTS (`POST /search/lexical`) nos modos `disjuntivo` e `estrito`. | `PASSED` |
| 22 | `test_compare_search_endpoint` | RF04 / RF05 | Execução comparativa simultânea (`POST /search/compare`) retornando rankings e telemetrias de ambos os motores. | `PASSED` |
| 23 | `test_document_ingest_endpoint_lifecycle` | RF01–RF03 | Ciclo completo de ingestão em tempo real (`POST /documents/ingest`, HTTP 201) seguido de limpeza transacional. | `PASSED` |
