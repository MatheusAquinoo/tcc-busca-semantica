# Relatório Experimental de Validação: Busca Semântica vs. Busca Lexical
**Trabalho de Conclusão de Curso (TCC 2) - Engenharia de Software / UTFPR**  
**Autor:** Matheus de Aquino da Silva  
**Orientador:** Prof. Dr. Bruno Honorato  
**Data de Execução:** 02/11/2026 22:28:43

---

## 1. Resumo Executivo do Experimento

Este documento consolida os resultados quantitativos e estatísticos obtidos na execução do protocolo experimental especificado na Seção 2.6 do TCC. O experimento submeteu uma amostra controlada de **60 consultas analíticas** (30 simulando chamados de suporte técnico Microsoft e 30 simulando problemas no sistema operacional Ubuntu) sobre a base de **200 documentos técnicos** segmentados em **455 fragmentos (chunks)** com sobreposição:

1. **Grupo de Controle I — Busca Lexical Estrita (`plainto_tsquery` - Operador AND):** Exige a coocorrência exata de todos os radicais da consulta em linguagem natural no mesmo fragmento.
2. **Grupo de Controle II — Busca Lexical Flexível (`ts_rank_cd` Disjuntivo - Operador OR + Índice GIN):** Recupera e ranqueia fragmentos pela densidade de cobertura de qualquer radical coincidente nos dicionários Português e Inglês do PostgreSQL.
3. **Abordagem Proposta — Busca Semântica Vetorial (`pgvector` + HNSW 768d):** Mapeia consultas e fragmentos no espaço vetorial denso de 768 dimensões (`paraphrase-multilingual-mpnet-base-v2`) e executa busca por vizinhos mais próximos aproximados (ANN) via distância de cosseno (`<=>`).
4. **Abordagem Semântica Híbrida (`pgvector` HNSW + Pre-Filtering Relacional RF07):** Combina a varredura geométrica no grafo HNSW com filtragem relacional prévia de categoria técnica (`WHERE c.categoria = :filtro`).

---

## 2. Métricas Globais de Recuperação da Informação e Latência

| Abordagem | Hits@1 | Precisão@5 | Revocação@5 | MRR | T_emb Médio (ms) | T_sql Médio (ms) | T_total Médio (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Busca Lexical Estrita (FTS Conjuntivo AND) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.00 | 17.31 | 17.31 |
| Busca Lexical Flexível (FTS Disjuntivo OR / GIN) | 0.4833 | 0.1500 | 0.7500 | 0.5919 | 0.00 | 32.92 | 32.92 |
| Busca Semântica Vetorial (pgvector HNSW) | 0.8333 | 0.1933 | 0.9667 | 0.8944 | 14.31 | 2.56 | 16.87 |
| Busca Semântica Híbrida (HNSW + Pre-filtering RF07) | 0.8500 | 0.2000 | 1.0000 | 0.9139 | 13.13 | 1.69 | 14.81 |

---

## 3. Testes de Hipóteses Estatísticas (Significância Experimental)

Para comprovar que a superioridade da arquitetura vetorial proposta não decorre de flutuação amostral (Seção 2.6.3), aplicaram-se o **Teste *t* de Student Pareado** e o **Teste Não-Paramétrico dos Postos Sinalizados de Wilcoxon** sobre os vetores de Posto Recíproco (*Reciprocal Rank*, $N = 60$):

* **Busca Semântica HNSW vs. Busca Lexical Flexível (FTS Disjuntivo):**
  * Estatística $t = 4.7757$ ($p = 1.2247e-05$)
  * Estatística de Wilcoxon $W = 66.5$ ($p = 6.2236e-05$)
  * **Conclusão:** Rejeita-se a hipótese nula ($H_0$) com nível de confiança superior a $99,99\%$ ($p < 0,0001$).
* **Busca Semântica Híbrida (Pre-filtering) vs. Busca Lexical Flexível (FTS Disjuntivo):**
  * Estatística $t = 5.2027$ ($p = 2.5930e-06$)
  * Estatística de Wilcoxon $W = 49.0$ ($p = 1.6522e-05$)
  * **Conclusão:** Ganho estatisticamente significativo ($p < 0,0001$), demonstrando a eficácia combinada da representação densa com a filtragem relacional unificada no PostgreSQL.
* **Busca Semântica Híbrida vs. Busca Semântica Pura:**
  * Estatística $t = 1.8765$ ($p = 0.0655$)

---

## 4. Telemetria Computacional e Custo de Indexação ($T_{idx}$)

* **Custo Temporal Total de Indexação ($T_{idx}$):** `9.3116 s` para processar 200 documentos (455 chunks), sendo `8.6468 s` na inferência vetorial em lote e `0.6614 s` na persistência transacional e construção dos índices HNSW e GIN.
* **Consumo de Recursos do Container PostgreSQL (`tcc_postgres_vector`):**
  * **Memória RAM Alocada:** `44.96MiB / 15.34GiB` (`0.29%`)
  * **Utilização de CPU em Repouso/Consulta:** `0.08%`

---

## 5. Análise Detalhada por Cenário de Suporte Técnico

| Cenário | Abordagem | Hits@1 | Precisão@5 | Revocação@5 | MRR | T_sql (ms) | T_total (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Cenário Microsoft | lexical_estrito | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 17.11 | 17.11 |
| Cenário Microsoft | lexical_disjuntivo | 0.4333 | 0.1467 | 0.7333 | 0.5522 | 33.27 | 33.27 |
| Cenário Microsoft | semantica | 0.8333 | 0.1867 | 0.9333 | 0.8833 | 2.58 | 16.70 |
| Cenário Microsoft | semantica_prefilter | 0.8333 | 0.2000 | 1.0000 | 0.9000 | 1.71 | 14.58 |
| Cenário Ubuntu | lexical_estrito | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 17.52 | 17.52 |
| Cenário Ubuntu | lexical_disjuntivo | 0.5333 | 0.1533 | 0.7667 | 0.6317 | 32.57 | 32.57 |
| Cenário Ubuntu | semantica | 0.8333 | 0.2000 | 1.0000 | 0.9056 | 2.54 | 17.05 |
| Cenário Ubuntu | semantica_prefilter | 0.8667 | 0.2000 | 1.0000 | 0.9278 | 1.66 | 15.05 |
