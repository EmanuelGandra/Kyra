
# Relatório de clusterização, tópicos e insights

Run ID: `20260520_113457`

## 1. Base analisada

- Chunks: **4,976**
- Entrevistas/documentos: **131**
- Texto usado para embeddings: `text_for_embedding`
- Texto usado para rótulos/tópicos: `text_for_keywords`

## 2. Modelo de clusterização selecionado

- Método selecionado: **kmeans**
- Número de clusters: **18**
- Maior cluster: **9.1%** da base
- Razão da seleção: KMeans escolhido como default por estabilidade, cobertura total e interpretabilidade.

### Comparação de modelos

| modelo             | parametro   | criterio                                          |
|:-------------------|:------------|:--------------------------------------------------|
| KMeans selecionado | k=18        | silhouette=0.113; estabilidade=0.865; score=0.346 |
| Melhor NMF         | n_topics=18 | diversidade=0.833; dominancia=0.512; score=0.763  |
| Melhor LDA         | n_topics=10 | diversidade=0.760; dominancia=0.648; score=0.778  |

## 3. Interpretação dos clusters

Os clusters devem ser lidos como agrupamentos semânticos. O rótulo automático é uma aproximação gerada por TF-IDF; ele precisa ser validado com os exemplos representativos.

### Maiores clusters

| cluster_label   | cluster_auto_label                          |   n_chunks |     share |
|:----------------|:--------------------------------------------|-----------:|----------:|
| km_013          | revista / compra / site / comprar           |        454 | 0.0912379 |
| km_017          | propaganda / pele / produto / natura        |        417 | 0.0838023 |
| km_002          | loja / boticario / presente / natura        |        404 | 0.0811897 |
| km_008          | fusao / pedido / natura / avon              |        403 | 0.0809887 |
| km_005          | natura / clientes / vende / cliente         |        385 | 0.0773714 |
| km_003          | refil / embalagem / parece / formato        |        365 | 0.0733521 |
| km_009          | produto / marca / produtos / questao        |        346 | 0.0695338 |
| km_004          | mae / casa / filho / cuidar                 |        334 | 0.0671222 |
| km_014          | boticario / natura / perfume / vende        |        253 | 0.0508441 |
| km_000          | presente / dar / gosta / comprar            |        238 | 0.0478296 |
| km_010          | transmite / tecnologia / embalagem / parece |        209 | 0.0420016 |
| km_006          | papo / nome / comecar / bate papo           |        208 | 0.0418006 |
| km_001          | pele / propagandas / mulheres / transmite   |        185 | 0.0371785 |
| km_007          | pele / corpo / uso / gosto                  |        181 | 0.0363746 |
| km_012          | tecnologia / bio / bioeficiente / produto   |        170 | 0.034164  |

### Labels automáticos

| cluster_label   |   n_chunks | auto_label_short                            | top_terms                                                                                                                                                                                                      |
|:----------------|-----------:|:--------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| km_013          |        454 | revista / compra / site / comprar           | revista; compra; site; comprar; compro; exemplo; consultora; espaco; digital; manda; pelo; loja; interativa; aplicativo; produtos; produto; revista interativa; promocao; espaco digital; acha                 |
| km_017          |        417 | propaganda / pele / produto / natura        | propaganda; pele; produto; natura; acido; amazonia; achei; questao; dessa; impressao; natural; cuidado; tempo; pode; hialuronico; acido hialuronico; natureza; traz; mostra; palavras                          |
| km_002          |        404 | loja / boticario / presente / natura        | loja; boticario; presente; natura; perfumaria; experiencia; lojas; perfume; ponto; consumidor; shopping; dentro; atencao; cara; marca; caixa; embalagem; presentes; pode; atendimento                          |
| km_008          |        403 | fusao / pedido / natura / avon              | fusao; pedido; natura; avon; lider; avo; vender; teve; ciclo; pontos; gerente; mudou; aplicativo; grupo; negocio; duas; exemplo; chegar; cliente; depois                                                       |
| km_005          |        385 | natura / clientes / vende / cliente         | natura; clientes; vende; cliente; boticario; kit; perfume; presente; kits; vender; vem; entendi; marcas; exemplo; vendo; sempre; bastante; sabonete; comprar; hidratante                                       |
| km_003          |        365 | refil / embalagem / parece / formato        | refil; embalagem; parece; formato; plastico; ecos; legal; cor; diferente; atual; design; material; ver; acham; visual; lembra; produto; natureza; ficar; bonito                                                |
| km_009          |        346 | produto / marca / produtos / questao        | produto; marca; produtos; questao; shampoo; natura; cabelo; barra; natureza; embalagem; uso; natural; propaganda; sempre; sabonete; marcas; biome; condicionador; ambiente; pode                               |
| km_004          |        334 | mae / casa / filho / cuidar                 | mae; casa; filho; cuidar; filhos; sempre; tempo; vida; momento; cabelo; trabalho; semana; seu; gosto; mulher; depois; sua; nome; maes; questao                                                                 |
| km_014          |        253 | boticario / natura / perfume / vende        | boticario; natura; perfume; vende; perfumaria; consultora; vender; perfumes; presente; venda; amostra; relacao; ponto; compra; embalagem; loja; falava; trouxe; marca; fragrancia                              |
| km_000          |        238 | presente / dar / gosta / comprar            | presente; dar; gosta; comprar; aniversario; presentear; mae; gosto; dar presente; legal; sempre; loja; exemplo; perfume; sua; costuma; presentes; entendi; dou; dei                                            |
| km_010          |        209 | transmite / tecnologia / embalagem / parece | transmite; tecnologia; embalagem; parece; inovacao; produto; atencao; imagem; avancada; tecnologia avancada; ideia; chama atencao; chama; mostra; passo; sofisticacao; cor; pele; passo passo; transmite ideia |
| km_006          |        208 | papo / nome / comecar / bate papo           | papo; nome; comecar; bate papo; bate; conversa; vontade; ouvir; pode; ideia; conversar; prazer; microfone; entrar; ver; pouquinho; mundo; ficar; camera; depois                                                |
| km_001          |        185 | pele / propagandas / mulheres / transmite   | pele; propagandas; mulheres; transmite; impressao; produto; imagens; transmitem; passa; mulher; idade; olhando; propaganda; olhar; parece; conta; rosto; mensagem; diversidade; foto                           |
| km_007          |        181 | pele / corpo / uso / gosto                  | pele; corpo; uso; gosto; hidratante; oleo; banho; creme; passo; cheiro; fica; passar; pele corpo; usa; rosto; hidratacao; depois; quero; faco; partes                                                          |
| km_012          |        170 | tecnologia / bio / bioeficiente / produto   | tecnologia; bio; bioeficiente; produto; nome; palavra; linha; eficiente; bioinovacao; cabeca; produtos; homem; dermotech; pele; biotec; otimo; bioexpert; barba; natural; nomes                                |
| km_016          |        159 | pele negra / negra / pele / linha           | pele negra; negra; pele; linha; hidratacao; marca; acha; produto; seria; hidratante; oleo; especifico; saber; produtos; acham; quero saber; negras; natura; quero; ver                                         |
| km_015          |        143 | idade / nome / trabalho / moro              | idade; nome; trabalho; moro; nome idade; filhos; mora; paulo; comecar; casada; pouquinho; prazer; vida; legal; tempo; area; natura; tarde; conhecer; otimo                                                     |
| km_011          |        122 | energia / energizante / usaria / banho      | energia; energizante; usaria; banho; corpo; compraria; gel; linha; pele; isabela; produto; usar; disposicao; escova; noite; sabonete; manha; thais; circulacao; entendi                                        |

## 4. NMF

NMF é usado como leitura auxiliar de tópicos por vocabulário. Ele tende a ser mais interpretável que LDA quando usamos TF-IDF.

- Melhor número de tópicos: **18**

| topic_id   | auto_label_short                                   | top_terms                                                                                                                                                                  |
|:-----------|:---------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| nmf_00     | boticario / natura / perfume / vende               | boticario; natura; perfume; vende; marca; marcas; vender; perfumaria; perfumes; avon; essencial; clientes; cliente; natura boticario; cheiro                               |
| nmf_01     | propaganda / impressao / propagandas / mulheres    | propaganda; impressao; propagandas; mulheres; mulher; produto; marca; tempo; expressao; pele; amiga tempo; passa; duas semanas; mostra; idade                              |
| nmf_02     | idade / trabalho / casa / filhos                   | idade; trabalho; casa; filhos; nome; mae; tempo; vida; filho; semana; mora; moro; seu; momento; faco                                                                       |
| nmf_03     | corpo / banho / uso / hidratante                   | corpo; banho; uso; hidratante; passo; creme; pele; sabonete; gosto; oleo; cheiro; rosto; usa; usar; noite                                                                  |
| nmf_04     | revista / site / compra / comprar                  | revista; site; compra; comprar; compro; digital; espaco; interativa; consultora; revista interativa; manda; espaco digital; pelo; exemplo; aplicativo                      |
| nmf_05     | presente / dar / presentear / gosta                | presente; dar; presentear; gosta; dar presente; aniversario; mae; comprar; presentes; natal; gosto; maes; legal; sempre; comprar presente                                  |
| nmf_06     | aproveite / sua camera / conversa / local          | aproveite; sua camera; conversa; local; camera; conexao; bate papo; estiver; estamos; bate; papo; sua; diferentes; tenha; seu                                              |
| nmf_07     | refil / embalagem / parece / formato               | refil; embalagem; parece; formato; plastico; diferente; ecos; legal; cor; design; material; visual; atual; acham; lembra                                                   |
| nmf_08     | transmite / atencao / parece / embalagem           | transmite; atencao; parece; embalagem; imagem; tecnologia; chama atencao; chama; inovacao; produto; sofisticacao; avancada; tecnologia avancada; chamou; ideia             |
| nmf_09     | negra / pele negra / pele / acha                   | negra; pele negra; pele; acha; linha; especifico; saber; hidratacao; marca; seria; quero saber; branca; negras; peles; produto                                             |
| nmf_10     | loja / lojas / boticario / experiencia             | loja; lojas; boticario; experiencia; shopping; perfumaria; natura; consumidor; ponto; loja natura; atendimento; atencao; varejo; dentro; vitrine                           |
| nmf_11     | tecnologia / bio / bioeficiente / linha            | tecnologia; bio; bioeficiente; linha; produtos; nome; produto; cabeca; palavra; homem; eficiente; bioinovacao; dermotech; natural; seria                                   |
| nmf_12     | pedido / fusao / lider / avon                      | pedido; fusao; lider; avon; natura; avo; teve; pontos; ciclo; vender; mudou; minimo; gerente; grupo; aconteceu                                                             |
| nmf_13     | nome / comecar / papo / vontade                    | nome; comecar; papo; vontade; bate papo; bate; ouvir; prazer; microfone; conversar; importante; papo comecar; fiquem; prontinho; acionar microfone                         |
| nmf_14     | acido / acido hialuronico / hialuronico / amazonia | acido; acido hialuronico; hialuronico; amazonia; propaganda; tucuma; producao; pele amazonia; producao acido; hidratacao; pele; corpo; natureza; sentisse; sentisse pele   |
| nmf_15     | vegano / bebe / produto / produto vegano           | vegano; bebe; produto; produto vegano; questao; frescor; natural; mar; ambiente; massagem; base; mergulho; cuidado; barra; sensacao                                        |
| nmf_16     | amanha / dormir / noite / deixasse amanha          | amanha; dormir; noite; deixasse amanha; deixasse; cuida; dormir melhor; enquanto cuida; cuida pele; melhor enquanto; enquanto; ritual; cuidar; natura noite; ritual dormir |
| nmf_17     | kit / caixa / kits / sacola                        | kit; caixa; kits; sacola; presente; vem; embalagem; cliente; sabonete; presentes; caixas; entrega; montar; preco; dentro                                                   |

## 5. LDA

LDA é usado como comparação probabilística. Se os tópicos aparecerem genéricos demais, priorize NMF e clusters semânticos.

- Melhor número de tópicos: **10**

| topic_id   | auto_label_short                        | top_terms                                                                                                                                            |
|:-----------|:----------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| lda_00     | embalagem / atencao / produto / parece  | embalagem; atencao; produto; parece; transmite; chama; sofisticacao; chama atencao; cor; imagem; chamou; tecnologia; inovacao; chamou atencao; ideia |
| lda_01     | natura / tempo / pedido / depois        | natura; tempo; pedido; depois; avon; casa; lider; sempre; fusao; seu; pode; teve; trabalho; duas; avo                                                |
| lda_02     | loja / boticario / natura / experiencia | loja; boticario; natura; experiencia; perfume; perfumaria; lojas; marca; questao; ponto; produtos; shopping; comprar; presente; consumidor           |
| lda_03     | produto / embalagem / parece / ver      | produto; embalagem; parece; ver; legal; linha; refil; produtos; diferente; natural; shampoo; pode; natureza; formato; nome                           |
| lda_04     | natura / perfume / vende / cliente      | natura; perfume; vende; cliente; boticario; vem; linha; marca; kit; vender; clientes; marcas; sabonete; avon; produtos                               |
| lda_05     | pele / corpo / uso / gosto              | pele; corpo; uso; gosto; hidratante; banho; negra; creme; oleo; pele negra; cheiro; fica; usar; sabonete; cabelo                                     |
| lda_06     | presente / mae / dar / gosto            | presente; mae; dar; gosto; legal; gosta; passo; maes; sua; sempre; comprar; presentear; aniversario; casa; natal                                     |
| lda_07     | produto / pele / propaganda / natura    | produto; pele; propaganda; natura; marca; questao; produtos; pode; cuidado; impressao; dessa; achei; tempo; mostra; mulher                           |
| lda_08     | comprar / revista / compra / site       | comprar; revista; compra; site; compro; exemplo; produto; pelo; consultora; produtos; sempre; promocao; manda; digital; aplicativo                   |
| lda_09     | nome / idade / comecar / papo           | nome; idade; comecar; papo; trabalho; vontade; pouquinho; pode; sua; conversa; prazer; ouvir; bate; bate papo; moro                                  |

## 6. Principais insights por segmento

A tabela abaixo prioriza combinações segmento-tema com maior lift e tamanho mínimo.

### Clusters por segmento

| segment_col   | segment_value              | auto_label                                  |   n_chunks_segment_label |   share_in_segment |   global_share |   lift_vs_global | insight_sentence                                                                                                                                              |
|:--------------|:---------------------------|:--------------------------------------------|-------------------------:|-------------------:|---------------:|-----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| projeto       | havana_iii                 | energia / energizante / usaria / banho      |                      122 |           0.968254 |      0.0245177 |         39.4921  | Em projeto = havana_iii, o tema 'energia / energizante / usaria / banho' aparece em 96.8% dos chunks vs. 2.5% no total (lift 39.49x; n=122).                  |
| projeto       | jack_pearson               | tecnologia / bio / bioeficiente / produto   |                      170 |           0.85     |      0.034164  |         24.88    | Em projeto = jack_pearson, o tema 'tecnologia / bio / bioeficiente / produto' aparece em 85.0% dos chunks vs. 3.4% no total (lift 24.88x; n=170).             |
| projeto       | anima                      | refil / embalagem / parece / formato        |                      358 |           0.881773 |      0.0733521 |         12.0211  | Em projeto = anima, o tema 'refil / embalagem / parece / formato' aparece em 88.2% dos chunks vs. 7.3% no total (lift 12.02x; n=358).                         |
| projeto       | compras_digitais           | revista / compra / site / comprar           |                      432 |           0.878049 |      0.0912379 |          9.62372 | Em projeto = compras_digitais, o tema 'revista / compra / site / comprar' aparece em 87.8% dos chunks vs. 9.1% no total (lift 9.62x; n=432).                  |
| projeto       | rosacea                    | propaganda / pele / produto / natura        |                      417 |           0.773655 |      0.0838023 |          9.23191 | Em projeto = rosacea, o tema 'propaganda / pele / produto / natura' aparece em 77.4% dos chunks vs. 8.4% no total (lift 9.23x; n=417).                        |
| projeto       | mercato_brasil             | fusao / pedido / natura / avon              |                      388 |           0.751938 |      0.0809887 |          9.28447 | Em projeto = mercato_brasil, o tema 'fusao / pedido / natura / avon' aparece em 75.2% dos chunks vs. 8.1% no total (lift 9.28x; n=388).                       |
| publico       | consumidoras               | presente / dar / gosta / comprar            |                      190 |           0.727969 |      0.0478296 |         15.2201  | Em publico = consumidoras, o tema 'presente / dar / gosta / comprar' aparece em 72.8% dos chunks vs. 4.8% no total (lift 15.22x; n=190).                      |
| publico       | consultoras                | natura / clientes / vende / cliente         |                      290 |           0.651685 |      0.0773714 |          8.42282 | Em publico = consultoras, o tema 'natura / clientes / vende / cliente' aparece em 65.2% dos chunks vs. 7.7% no total (lift 8.42x; n=290).                     |
| projeto       | gaia_ii                    | transmite / tecnologia / embalagem / parece |                      208 |           0.5      |      0.0420016 |         11.9043  | Em projeto = gaia_ii, o tema 'transmite / tecnologia / embalagem / parece' aparece em 50.0% dos chunks vs. 4.2% no total (lift 11.90x; n=208).                |
| projeto       | bem_maes                   | mae / casa / filho / cuidar                 |                       92 |           0.910891 |      0.0671222 |         13.5706  | Em projeto = bem_maes, o tema 'mae / casa / filho / cuidar' aparece em 91.1% dos chunks vs. 6.7% no total (lift 13.57x; n=92).                                |
| projeto       | biome                      | produto / marca / produtos / questao        |                      164 |           0.694915 |      0.0695338 |          9.99393 | Em projeto = biome, o tema 'produto / marca / produtos / questao' aparece em 69.5% dos chunks vs. 7.0% no total (lift 9.99x; n=164).                          |
| projeto       | gaia_ii                    | pele / propagandas / mulheres / transmite   |                      161 |           0.387019 |      0.0371785 |         10.4098  | Em projeto = gaia_ii, o tema 'pele / propagandas / mulheres / transmite' aparece em 38.7% dos chunks vs. 3.7% no total (lift 10.41x; n=161).                  |
| projeto       | radiosa                    | pele negra / negra / pele / linha           |                      157 |           0.331224 |      0.0319534 |         10.3658  | Em projeto = radiosa, o tema 'pele negra / negra / pele / linha' aparece em 33.1% dos chunks vs. 3.2% no total (lift 10.37x; n=157).                          |
| projeto       | radiosa                    | pele / corpo / uso / gosto                  |                      163 |           0.343882 |      0.0363746 |          9.4539  | Em projeto = radiosa, o tema 'pele / corpo / uso / gosto' aparece em 34.4% dos chunks vs. 3.6% no total (lift 9.45x; n=163).                                  |
| projeto       | 3cs_perfumes               | boticario / natura / perfume / vende        |                      180 |           0.371134 |      0.0508441 |          7.29946 | Em projeto = 3cs_perfumes, o tema 'boticario / natura / perfume / vende' aparece em 37.1% dos chunks vs. 5.1% no total (lift 7.30x; n=180).                   |
| tipo_sessao   | entrevista_em_profundidade | boticario / natura / perfume / vende        |                      180 |           0.371134 |      0.0508441 |          7.29946 | Em tipo_sessao = entrevista_em_profundidade, o tema 'boticario / natura / perfume / vende' aparece em 37.1% dos chunks vs. 5.1% no total (lift 7.30x; n=180). |
| projeto       | 3cs_perfumes               | loja / boticario / presente / natura        |                      210 |           0.43299  |      0.0811897 |          5.33306 | Em projeto = 3cs_perfumes, o tema 'loja / boticario / presente / natura' aparece em 43.3% dos chunks vs. 8.1% no total (lift 5.33x; n=210).                   |
| tipo_sessao   | entrevista_em_profundidade | loja / boticario / presente / natura        |                      210 |           0.43299  |      0.0811897 |          5.33306 | Em tipo_sessao = entrevista_em_profundidade, o tema 'loja / boticario / presente / natura' aparece em 43.3% dos chunks vs. 8.1% no total (lift 5.33x; n=210). |
| projeto       | natura_3cs                 | natura / clientes / vende / cliente         |                      296 |           0.300508 |      0.0773714 |          3.88396 | Em projeto = natura_3cs, o tema 'natura / clientes / vende / cliente' aparece em 30.1% dos chunks vs. 7.7% no total (lift 3.88x; n=296).                      |
| projeto       | natura_3cs                 | presente / dar / gosta / comprar            |                      232 |           0.235533 |      0.0478296 |          4.92442 | Em projeto = natura_3cs, o tema 'presente / dar / gosta / comprar' aparece em 23.6% dos chunks vs. 4.8% no total (lift 4.92x; n=232).                         |

### NMF por segmento

| segment_col   | segment_value              | auto_label                                      |   n_chunks_segment_label |   share_in_segment |   global_share |   lift_vs_global | insight_sentence                                                                                                                                                |
|:--------------|:---------------------------|:------------------------------------------------|-------------------------:|-------------------:|---------------:|-----------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| projeto       | jack_pearson               | tecnologia / bio / bioeficiente / linha         |                      182 |           0.91     |      0.0464228 |         19.6024  | Em projeto = jack_pearson, o tema 'tecnologia / bio / bioeficiente / linha' aparece em 91.0% dos chunks vs. 4.6% no total (lift 19.60x; n=182).                 |
| projeto       | anima                      | refil / embalagem / parece / formato            |                      367 |           0.903941 |      0.0864148 |         10.4605  | Em projeto = anima, o tema 'refil / embalagem / parece / formato' aparece em 90.4% dos chunks vs. 8.6% no total (lift 10.46x; n=367).                           |
| projeto       | compras_digitais           | revista / site / compra / comprar               |                      431 |           0.876016 |      0.106511  |          8.22464 | Em projeto = compras_digitais, o tema 'revista / site / compra / comprar' aparece em 87.6% dos chunks vs. 10.7% no total (lift 8.22x; n=431).                   |
| projeto       | mercato_brasil             | pedido / fusao / lider / avon                   |                      403 |           0.781008 |      0.0942524 |          8.28634 | Em projeto = mercato_brasil, o tema 'pedido / fusao / lider / avon' aparece em 78.1% dos chunks vs. 9.4% no total (lift 8.29x; n=403).                          |
| projeto       | gaia_ii                    | transmite / atencao / parece / embalagem        |                      253 |           0.608173 |      0.0576768 |         10.5445  | Em projeto = gaia_ii, o tema 'transmite / atencao / parece / embalagem' aparece em 60.8% dos chunks vs. 5.8% no total (lift 10.54x; n=253).                     |
| publico       | consumidoras               | presente / dar / presentear / gosta             |                      173 |           0.662835 |      0.0637058 |         10.4046  | Em publico = consumidoras, o tema 'presente / dar / presentear / gosta' aparece em 66.3% dos chunks vs. 6.4% no total (lift 10.40x; n=173).                     |
| projeto       | radiosa                    | negra / pele negra / pele / acha                |                      202 |           0.42616  |      0.0426045 |         10.0027  | Em projeto = radiosa, o tema 'negra / pele negra / pele / acha' aparece em 42.6% dos chunks vs. 4.3% no total (lift 10.00x; n=202).                             |
| projeto       | havana_iii                 | corpo / banho / uso / hidratante                |                       94 |           0.746032 |      0.0641077 |         11.6372  | Em projeto = havana_iii, o tema 'corpo / banho / uso / hidratante' aparece em 74.6% dos chunks vs. 6.4% no total (lift 11.64x; n=94).                           |
| projeto       | bem_maes                   | idade / trabalho / casa / filhos                |                       74 |           0.732673 |      0.0743569 |          9.85347 | Em projeto = bem_maes, o tema 'idade / trabalho / casa / filhos' aparece em 73.3% dos chunks vs. 7.4% no total (lift 9.85x; n=74).                              |
| projeto       | 3cs_perfumes               | loja / lojas / boticario / experiencia          |                      223 |           0.459794 |      0.0799839 |          5.74858 | Em projeto = 3cs_perfumes, o tema 'loja / lojas / boticario / experiencia' aparece em 46.0% dos chunks vs. 8.0% no total (lift 5.75x; n=223).                   |
| tipo_sessao   | entrevista_em_profundidade | loja / lojas / boticario / experiencia          |                      223 |           0.459794 |      0.0799839 |          5.74858 | Em tipo_sessao = entrevista_em_profundidade, o tema 'loja / lojas / boticario / experiencia' aparece em 46.0% dos chunks vs. 8.0% no total (lift 5.75x; n=223). |
| projeto       | natura_3cs                 | presente / dar / presentear / gosta             |                      281 |           0.285279 |      0.0637058 |          4.47807 | Em projeto = natura_3cs, o tema 'presente / dar / presentear / gosta' aparece em 28.5% dos chunks vs. 6.4% no total (lift 4.48x; n=281).                        |
| projeto       | radiosa                    | corpo / banho / uso / hidratante                |                      165 |           0.348101 |      0.0641077 |          5.42994 | Em projeto = radiosa, o tema 'corpo / banho / uso / hidratante' aparece em 34.8% dos chunks vs. 6.4% no total (lift 5.43x; n=165).                              |
| publico       | consultoras                | kit / caixa / kits / sacola                     |                      149 |           0.334831 |      0.0602894 |          5.55374 | Em publico = consultoras, o tema 'kit / caixa / kits / sacola' aparece em 33.5% dos chunks vs. 6.0% no total (lift 5.55x; n=149).                               |
| projeto       | rosacea                    | propaganda / impressao / propagandas / mulheres |                      168 |           0.311688 |      0.0590836 |          5.27538 | Em projeto = rosacea, o tema 'propaganda / impressao / propagandas / mulheres' aparece em 31.2% dos chunks vs. 5.9% no total (lift 5.28x; n=168).               |

### LDA por segmento

| segment_col   | segment_value              | auto_label                              |   n_chunks_segment_label |   share_in_segment |   global_share |   lift_vs_global | insight_sentence                                                                                                                                                  |
|:--------------|:---------------------------|:----------------------------------------|-------------------------:|-------------------:|---------------:|-----------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| projeto       | compras_digitais           | comprar / revista / compra / site       |                      423 |           0.859756 |      0.0998794 |          8.60794 | Em projeto = compras_digitais, o tema 'comprar / revista / compra / site' aparece em 86.0% dos chunks vs. 10.0% no total (lift 8.61x; n=423).                     |
| projeto       | rosacea                    | produto / pele / propaganda / natura    |                      503 |           0.93321  |      0.171423  |          5.44391 | Em projeto = rosacea, o tema 'produto / pele / propaganda / natura' aparece em 93.3% dos chunks vs. 17.1% no total (lift 5.44x; n=503).                           |
| projeto       | anima                      | produto / embalagem / parece / ver      |                      368 |           0.906404 |      0.142484  |          6.36145 | Em projeto = anima, o tema 'produto / embalagem / parece / ver' aparece em 90.6% dos chunks vs. 14.2% no total (lift 6.36x; n=368).                               |
| publico       | consumidoras               | presente / mae / dar / gosto            |                      182 |           0.697318 |      0.0653135 |         10.6765  | Em publico = consumidoras, o tema 'presente / mae / dar / gosto' aparece em 69.7% dos chunks vs. 6.5% no total (lift 10.68x; n=182).                              |
| projeto       | mercato_brasil             | natura / tempo / pedido / depois        |                      404 |           0.782946 |      0.148312  |          5.27905 | Em projeto = mercato_brasil, o tema 'natura / tempo / pedido / depois' aparece em 78.3% dos chunks vs. 14.8% no total (lift 5.28x; n=404).                        |
| projeto       | radiosa                    | pele / corpo / uso / gosto              |                      267 |           0.563291 |      0.0813907 |          6.92083 | Em projeto = radiosa, o tema 'pele / corpo / uso / gosto' aparece em 56.3% dos chunks vs. 8.1% no total (lift 6.92x; n=267).                                      |
| projeto       | jack_pearson               | produto / embalagem / parece / ver      |                      179 |           0.895    |      0.142484  |          6.28141 | Em projeto = jack_pearson, o tema 'produto / embalagem / parece / ver' aparece em 89.5% dos chunks vs. 14.2% no total (lift 6.28x; n=179).                        |
| projeto       | 3cs_perfumes               | loja / boticario / natura / experiencia |                      295 |           0.608247 |      0.110531  |          5.50298 | Em projeto = 3cs_perfumes, o tema 'loja / boticario / natura / experiencia' aparece em 60.8% dos chunks vs. 11.1% no total (lift 5.50x; n=295).                   |
| tipo_sessao   | entrevista_em_profundidade | loja / boticario / natura / experiencia |                      295 |           0.608247 |      0.110531  |          5.50298 | Em tipo_sessao = entrevista_em_profundidade, o tema 'loja / boticario / natura / experiencia' aparece em 60.8% dos chunks vs. 11.1% no total (lift 5.50x; n=295). |
| projeto       | havana_iii                 | pele / corpo / uso / gosto              |                       95 |           0.753968 |      0.0813907 |          9.26357 | Em projeto = havana_iii, o tema 'pele / corpo / uso / gosto' aparece em 75.4% dos chunks vs. 8.1% no total (lift 9.26x; n=95).                                    |
| projeto       | gaia_ii                    | embalagem / atencao / produto / parece  |                      156 |           0.375    |      0.0349678 |         10.7241  | Em projeto = gaia_ii, o tema 'embalagem / atencao / produto / parece' aparece em 37.5% dos chunks vs. 3.5% no total (lift 10.72x; n=156).                         |
| publico       | consultoras                | natura / perfume / vende / cliente      |                      231 |           0.519101 |      0.10209   |          5.08474 | Em publico = consultoras, o tema 'natura / perfume / vende / cliente' aparece em 51.9% dos chunks vs. 10.2% no total (lift 5.08x; n=231).                         |
| projeto       | natura_3cs                 | presente / mae / dar / gosto            |                      267 |           0.271066 |      0.0653135 |          4.15023 | Em projeto = natura_3cs, o tema 'presente / mae / dar / gosto' aparece em 27.1% dos chunks vs. 6.5% no total (lift 4.15x; n=267).                                 |
| projeto       | gaia_ii                    | produto / pele / propaganda / natura    |                      207 |           0.497596 |      0.171423  |          2.90274 | Em projeto = gaia_ii, o tema 'produto / pele / propaganda / natura' aparece em 49.8% dos chunks vs. 17.1% no total (lift 2.90x; n=207).                           |
| marca_foco    | natura                     | presente / mae / dar / gosto            |                      268 |           0.21718  |      0.0653135 |          3.32519 | Em marca_foco = natura, o tema 'presente / mae / dar / gosto' aparece em 21.7% dos chunks vs. 6.5% no total (lift 3.33x; n=268).                                  |

## 7. Segmentos que mais diferem da média

| segment_col   | segment_value              |   n_chunks |   js_divergence_vs_global |
|:--------------|:---------------------------|-----------:|--------------------------:|
| projeto       | havana_iii                 |        126 |                 0.860316  |
| projeto       | jack_pearson               |        200 |                 0.720104  |
| projeto       | bem_maes                   |        101 |                 0.715528  |
| projeto       | anima                      |        406 |                 0.676328  |
| projeto       | gaia_ii                    |        416 |                 0.65836   |
| publico       | consumidoras               |        261 |                 0.593335  |
| projeto       | compras_digitais           |        492 |                 0.591654  |
| projeto       | rosacea                    |        539 |                 0.555014  |
| projeto       | biome                      |        236 |                 0.542996  |
| projeto       | radiosa                    |        474 |                 0.536996  |
| projeto       | mercato_brasil             |        516 |                 0.515885  |
| tipo_sessao   | entrevista_em_profundidade |        485 |                 0.473402  |
| projeto       | 3cs_perfumes               |        485 |                 0.473402  |
| publico       | consultoras                |        445 |                 0.464364  |
| publico       | lideres                    |         52 |                 0.374178  |
| projeto       | natura_3cs                 |        985 |                 0.367353  |
| marca_foco    | natura                     |       1234 |                 0.267092  |
| marca_foco    | nao_inferido               |       3742 |                 0.0407415 |
| publico       | nao_inferido               |       4218 |                 0.037591  |
| tipo_sessao   | nao_inferido               |       4491 |                 0.0123259 |

## 8. Como transformar isso em insights reais

1. Validar manualmente os 5 exemplos representativos de cada cluster.
2. Renomear clusters com linguagem de negócio, não com palavras soltas.
3. Fundir clusters muito parecidos e dividir clusters com exemplos heterogêneos.
4. Priorizar insights com lift alto, share relevante e pelo menos 8 chunks no segmento.
5. Sempre incluir uma evidência textual curta para cada insight.
6. Separar resultado descritivo de recomendação: o modelo mostra padrão; a recomendação vem da interpretação do analista.
