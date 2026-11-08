# Relatório Experimental de Validação: Busca Semântica vs. Busca Lexical
**Trabalho de Conclusão de Curso (TCC 2) - Engenharia de Software / UTFPR**  
**Autor:** Matheus de Aquino da Silva  
**Orientador:** Prof. Dr. Bruno Honorato  
**Data de Atualização:** 08/11/2026 16:32:20

---

## 1. Desenho Metodológico e Construção do Padrão-Ouro (*Ground Truth*)

O experimento submeteu uma amostra controlada e estratificada de **60 consultas analíticas** (30 do Cenário A — suporte corporativo Microsoft e 30 do Cenário B — administração e logs Ubuntu Linux) sobre uma coleção canônica de **200 documentos técnicos** segmentados em **455 fragmentos (*chunks*)** com sobreposição (`max_chars=260, overlap=50`).

### 1.1 Justificativa das 60 Consultas e de 1 Documento Relevante por Consulta ($|Rel_q| = 1$)
* **Paradigma de Busca por Item Conhecido (*Known-Item Search*):** Em bases de conhecimento de *Help Desk* estruturadas segundo boas práticas de documentação (*Knowledge-Centered Service* — KCS), cada incidente ou causa-raiz possui um único artigo canônico de resolução para evitar duplicidade e inconsistência operacional (Voorhees, 1999; Manning et al., 2008).
* **Protocolo de Determinação de Relevância:** Cada documento da base ($N_{docs} = 200$) foi estruturado em *Sintoma*, *Causa* e *Solução técnica*. As 60 consultas foram formuladas de modo reverso a partir do **sintoma observado pelo usuário ou técnico de 1º nível**, aplicando paráfrases coloquiais, supressão de acentuação ortográfica e omissão deliberada dos comandos da solução técnica. Um documento recebe rótulo relevante ($R = 1$) se, e somente se, seu procedimento técnico soluciona diretamente a causa-raiz do chamado. Realizou-se auditoria cruzada contra os demais 199 documentos para garantir exclusividade temática ($|Rel_q| = 1$).
* **Implicação nas Métricas de Corte Top-5:** Como há exatamente 1 documento relevante por consulta ($|Rel_q| = 1$), o teto matemático da métrica **Precisão@5** é $1/5 = 0,2000$ ($20,00\%$), enquanto **Revocação@5**, **Hits@1** e **MRR** possuem limite máximo igual a $1,0000$ ($100,00\%$).

### 1.2 Diferenciação Conceitual: Pré-filtragem Relacional vs. Busca Híbrida Lexical-Vetorial
Neste estudo, distingue-se rigorosamente:
1. **Busca Semântica com Pré-filtragem Relacional (*Filtered Vector Search* — RF07):** Restringe o espaço de busca no PostgreSQL por meio de predicados relacionais exatos (`WHERE c.categoria = :filtro` via índice B-Tree ou `JSONB` via GIN) e ordena os candidatos **exclusivamente pela distância angular de cosseno (`<=>`) no grafo HNSW**.
2. **Busca Híbrida Lexical-Vetorial (*Sparse-Dense Hybrid Search*):** Combina matematicamente os escores ou posições da busca lexical (BM25 / FTS `ts_rank_cd`) com a similaridade vetorial densa (por exemplo, via *Reciprocal Rank Fusion* — RRF). O escopo experimental deste trabalho avalia especificamente a **Busca Semântica Pura** e a **Busca Semântica com Pré-filtragem Relacional**, confrontando-as contra dois baselines lexicais.

---

## 2. Métricas Globais de Recuperação da Informação e Latência

| Abordagem Avaliada | Hits@1 | Precisão@5 | Revocação@5 | MRR | T_emb Médio (ms) | T_sql Médio (ms) | T_total Médio (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Busca Lexical Estrita (FTS Conjuntivo AND) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.00 | 17.31 | 17.31 |
| Busca Lexical Flexível (FTS Disjuntivo OR / GIN) | 0.4833 | 0.1500 | 0.7500 | 0.5919 | 0.00 | 32.92 | 32.92 |
| Busca Semântica Vetorial Pura (pgvector HNSW) | 0.8333 | 0.1933 | 0.9667 | 0.8944 | 14.31 | 2.56 | 16.87 |
| Busca Semântica com Pré-filtragem Relacional (HNSW + RF07) | 0.8500 | 0.2000 | 1.0000 | 0.9139 | 13.13 | 1.69 | 14.81 |

---

## 3. Investigação do MRR = 0 na Busca Lexical Estrita e Representatividade dos Baselines

Para investigar por que a **Busca Lexical Estrita (`plainto_tsquery` — operador conjuntivo `AND`)** obteve $\text{MRR} = 0,0000$ e comprovar a representatividade do baseline lexical adotado, conduziu-se um estudo de ablação sobre as 60 consultas do Padrão-Ouro:

* **Extensão e Cobertura de Radicais:** As 60 consultas possuem em média **8.95 palavras** e geram em média **6.42 radicais (lexemas)** não-*stopwords* conectados pelo operador booleano `&` (`AND`). Contudo, o documento gabarito contém em média apenas **4.07 desses radicais (63.38%)**. Em **52 das 60 consultas (86,67%)**, o usuário utiliza ao menos um verbo ou substantivo coloquial ausente no manual técnico, fazendo com que a interseção booleana estrita retorne falso.

| Variante de Ablação do Motor Lexical | Consultas Recuperadas | Hits@1 | Precisão@5 | Revocação@5 | MRR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1. FTS Conjuntivo Estrito (AND em c.conteudo bruto) | 0/60 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 2. FTS Conjuntivo Estrito + unaccent (AND em c.conteudo) | 2/60 | 0.0333 | 0.0067 | 0.0333 | 0.0333 |
| 3. FTS Conjuntivo Estrito + Título + unaccent (AND em titulo + conteudo) | 8/60 | 0.1333 | 0.0267 | 0.1333 | 0.1333 |
| 4. FTS Disjuntivo Flexível (OR + ts_rank_cd + GIN - Baseline Representativo) | 45/60 | 0.4833 | 0.1500 | 0.7500 | 0.5919 |

> **Conclusão da Investigação de Baselines:** A variante conjuntiva estrita (`AND`) é estruturalmente inadequada para consultas longas em linguagem natural, servindo apenas para ilustrar a falha do modelo booleano clássico. O verdadeiro grupo de controle representativo é a **Busca Lexical Flexível Disjuntiva (`OR` + `ts_rank_cd` + índice GIN)**, que recupera **75,00% das consultas no Top-5** ($\text{MRR} = 0,5919$) e é utilizada como referência em todos os testes de hipóteses estatísticas.

---

## 4. Testes de Hipóteses Estatísticas e Interpretação Rigorosa ($\alpha = 0,01$)

Aplicaram-se o **Teste *t* de Student Pareado** e o **Teste Não-Paramétrico dos Postos Sinalizados de Wilcoxon** sobre os vetores pareados de Posto Recíproco ($N = 60$), adotando-se nível de significância $\alpha = 0,01$:

1. **Busca Semântica Vetorial Pura (HNSW) vs. Busca Lexical Flexível (Baseline Representativo):**
   * Estatística $t = 4.7757$ ($p = 1.2247e-05$) | Wilcoxon $W = 66.5$ ($p = 6.2236e-05$)
   * **Interpretação:** Como $p < 0,0001 \ll \alpha = 0,01$, **rejeita-se $H_0$**, confirmando superioridade estatisticamente significativa da busca semântica pura sobre o baseline lexical.
2. **Busca Semântica com Pré-filtragem Relacional (RF07) vs. Busca Lexical Flexível (Baseline Representativo):**
   * Estatística $t = 5.2027$ ($p = 2.5930e-06$) | Wilcoxon $W = 49.0$ ($p = 1.6522e-05$)
   * **Interpretação:** Como $p < 0,0001 \ll \alpha = 0,01$, **rejeita-se $H_0$**, confirmando superioridade estatisticamente significativa sobre o baseline lexical.
3. **Busca Semântica com Pré-filtragem Relacional (RF07) vs. Busca Semântica Vetorial Pura:**
   * Estatística $t = 1.8765$ ($p = 0.0655$) | Wilcoxon $W = 0.0$ ($p = 0.0656$)
   * **Interpretação Crítica:** Como $p = 0.0655 > \alpha = 0,01$ (e também $p > 0,05$), **NÃO se rejeita a hipótese nula ($H_0$)**. Os resultados **não demonstram superioridade estatisticamente significativa** da busca com pré-filtragem relacional ($\text{MRR} = 0,9139$) sobre a busca semântica pura ($\text{MRR} = 0,8944$) em termos de qualidade de ranqueamento global. Isso ocorre porque o modelo semântico puro já atinge desempenho próximo ao teto na coleção avaliada ($96,67\%$ de Revocação@5), de modo que a contribuição primordial da pré-filtragem relacional (RF07) reside na redução do subespaço de varredura e da latência SQL ($T_{sql}$ reduzido de $2,56\text{ ms}$ para $1,69\text{ ms}$) e na desambiguação pontual de chamados categorizados.

---

## 5. Telemetria Computacional, Escopo Amostral (455 Fragmentos) e Limitações

* **Custo Temporal Total de Indexação ($T_{idx}$):** `9.3116 s` para processar 200 documentos (455 chunks), sendo `8.6468 s` na inferência vetorial em lote e `0.6614 s` na persistência transacional e construção dos índices HNSW e GIN.
* **Consumo de Recursos do Container PostgreSQL (`tcc_postgres_vector`):** Memória RAM de `44.96MiB / 15.34GiB` (`0.29%`) e CPU de `0.08%`.
* **Ressalva sobre Escalabilidade:** Os indicadores de baixa latência ($T_{sql} \approx 1,69\text{--}2,56\text{ ms}$) e reduzido consumo de memória ($44,96\text{ MiB}$) foram aferidos sobre um corpus experimental controlado de **200 documentos (455 fragmentos)**. Portanto, esses números validam a viabilidade funcional e operacional do protótipo, mas **não permitem afirmações conclusivas sobre escalabilidade** em bases massivas na ordem de milhões de vetores.

---

## 6. Análise Detalhada por Cenário de Suporte Técnico

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
