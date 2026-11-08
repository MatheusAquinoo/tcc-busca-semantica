# Documentação dos Conjuntos de Dados e do Padrão-Ouro (*Ground Truth*)

Este diretório armazena os conjuntos de dados brutos (`raw/`), os fragmentos processados pela pipeline de *chunking* (`processed/`) e a matriz de Padrão-Ouro (`ground_truth.json` e `ground_truth.csv`) utilizados na validação experimental do TCC 2.

---

## 1. Estrutura dos Arquivos de Dados

| Arquivo | Formato | Registros | Descrição Técnica |
| :--- | :---: | :---: | :--- |
| `raw/microsoft_faq.json` / `.csv` | JSON e CSV | 100 docs (IDs 1–100) | Manuais e FAQs de suporte corporativo Microsoft (Windows 10/11, Windows Server, Active Directory, Microsoft 365). |
| `raw/ubuntu_logs.json` / `.csv` | JSON e CSV | 100 docs (IDs 101–200) | Registros de diagnóstico e procedimentos de administração de sistemas Ubuntu Linux (22.04/24.04 LTS). |
| `processed/chunks_indexados.json` / `.csv` | JSON e CSV | 455 *chunks* | Fragmentos sanitizados e segmentados com sobreposição (`max_chars=260, overlap=50`) e prefixo contextual de título. |
| `ground_truth.json` / `.csv` | JSON e CSV | 60 consultas | Matriz de Padrão-Ouro (*Ground Truth*) mapeando cada consulta em linguagem natural ao seu documento relevante canônico. |

---

## 2. Metodologia de Construção do Padrão-Ouro (60 Consultas e $|Rel_q| = 1$)

A construção da matriz de avaliação (`ground_truth.json` / `ground_truth.csv`) seguiu o paradigma de **Busca por Item Conhecido (*Known-Item Search* / *Question Answering Retrieval*)** (Voorhees, 1999; Manning et al., 2008), estruturado em quatro etapas auditáveis:

1. **Curadoria de Exclusividade Temática do Corpus ($N_{docs} = 200$):**
   Os 200 documentos técnicos foram construídos segundo a metodologia *Knowledge-Centered Service* (KCS), na qual cada artigo documenta um único problema técnico distinto, estruturado explicitamente em **Sintoma**, **Causa** e **Solução técnica**. Não existem dois documentos na coleção que tratem da mesma causa-raiz ou do mesmo procedimento corretivo.
2. **Amostragem Estratificada por Cenário e Categoria ($|Q| = 60$):**
   Foram selecionados 60 incidentes-alvo (30 no Cenário A — Microsoft, cobrindo 10 de *Conectividade*, 10 de *Autenticação* e 10 de *Sistema Operacional*; e 30 no Cenário B — Ubuntu, distribuídos entre *Gerenciamento de Pacotes*, *Conectividade*, *Sistema Operacional*, *Armazenamento*, *Segurança* e *Serviços & Daemons*). O tamanho amostral $N = 60$ ($N = 30$ por subdomínio) garante poder estatístico adequado para a aplicação dos testes pareados $t$ de Student e dos postos sinalizados de Wilcoxon.
3. **Formulação Reversa Baseada em Sintomas (*Symptom-Driven Query Formulation*):**
   Para cada documento-alvo, a consulta foi redigida descrevendo o **sintoma observado pelo usuário ou técnico de 1º nível**, aplicando-se:
   - Substituição de jargões formais por paráfrases e termos coloquiais (ex.: *"computador ta muito lento com disco em 100 porcento"* para o Documento ID 22);
   - Omissão deliberada dos comandos e ferramentas da seção de solução (ex.: omitir `SysMain`, `chkdsk`, `dsa.msc`, `Start-ADSyncSyncCycle`, `iotop`), que são desconhecidos pelo usuário antes da busca;
   - Ausência de acentuação ortográfica estrita (`nao`, `conexao`, `usuario`, `particao`), reproduzindo o padrão real de digitação em sistemas de *Help Desk*.
4. **Determinação da Relevância Binária ($R \in \{0, 1\}$) e Justificativa de Documento Único ($|Rel_q| = 1$):**
   - **Critério de Relevância:** Um documento $d$ recebe rótulo relevante ($R = 1$) para a consulta $q$ se, e somente se, seu procedimento técnico resolve integralmente a causa-raiz do incidente relatado em $q$. Documentos que pertencem à mesma categoria geral (ex.: *Conectividade*), mas solucionam falhas distintas (ex.: falha de VPN vs. falha de DNS), recebem rótulo não relevante ($R = 0$).
   - **Auditoria Cruzada:** Cada uma das 60 consultas foi verificada contra todos os 200 documentos do corpus para confirmar a inexistência de artigos concorrentes com a mesma solução técnica.
   - **Implicação nas Métricas Top-5:** Como há exatamente $|\{\text{relevantes na base}\}| = 1$ documento gabarito por consulta, o limite superior teórico da métrica $\text{Precisão@5}$ é $1/5 = 0,2000$ ($20,00\%$), enquanto $\text{Revocação@5}$, $\text{Hits@1}$ e $\text{MRR}$ possuem limite superior igual a $1,0000$ ($100,00\%$).
