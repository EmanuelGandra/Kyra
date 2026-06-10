# Kyra Pesquisa — Relatório Final

**Gerado em:** 2026-05-30 21:17:05  
**Run ID:** `20260520_113457`  
**Equipe:** Maria Beatriz Ribeiro · Juliane Oliveira · Emanuel Gandra

---

## 1. Visão Geral do Corpus

| Métrica | Valor |
|---|---|
| Chunks analisados | 4,976 |
| Documentos | 131 |
| Projetos | 12 |
| Clusters KMeans | 18 |
| Tópicos NMF | 18 |
| Tópicos LDA | 10 |
| Sentimento geral (POS) | 81.4% |
| Sentimento geral (NEU) | 11.9% |
| Sentimento geral (NEG) | 6.7% |

---

## 2. Resumo por Projeto

| Projeto | Chunks | Tema Dominante (NMF) | % POS | % NEG | Score Léxico |
|---|---:|---|---:|---:|---:|
| natura_3cs | 985 | presente / dar / presentear / gosta | 82.4 | 7.0 | 3.31 |
| rosacea | 539 | propaganda / impressao / propaganda | 84.8 | 3.9 | 3.16 |
| mercato_brasil | 516 | pedido / fusao / lider / avon | 63.8 | 17.2 | 1.62 |
| compras_digitais | 492 | revista / site / compra / comprar | 82.5 | 4.7 | 3.03 |
| 3cs_perfumes | 485 | loja / lojas / boticario / experien | 74.0 | 7.8 | 2.03 |
| radiosa | 474 | negra / pele negra / pele / acha | 85.0 | 5.5 | 3.68 |
| gaia_ii | 416 | transmite / atencao / parece / emba | 87.7 | 3.4 | 3.47 |
| anima | 406 | refil / embalagem / parece / format | 91.6 | 3.7 | 4.79 |
| biome | 236 | vegano / bebe / produto / produto v | 84.3 | 5.5 | 3.16 |
| jack_pearson | 200 | tecnologia / bio / bioeficiente / l | 95.5 | 1.5 | 5.54 |
| havana_iii | 126 | corpo / banho / uso / hidratante | 74.6 | 10.3 | 2.2 |
| bem_maes | 101 | idade / trabalho / casa / filhos | 60.4 | 10.9 | 1.27 |

---

## 3. Tópicos Robustos (LDA × NMF, Jaccard ≥ 0.25)

10/10 tópicos LDA confirmados por correspondente NMF.

| Tópico LDA | Tópico NMF | Jaccard | Termos Comuns |
|---|---|---:|---|
| embalagem / atencao / produto / par | transmite / atencao / parece / emba | 0.71 | atencao, chama, chama atencao, embalagem |
| pele / corpo / uso / gosto | corpo / banho / uso / hidratante | 0.60 | banho, cheiro, corpo, creme, gosto, hidr |
| loja / boticario / natura / experie | loja / lojas / boticario / experien | 0.50 | boticario, experiencia, loja, lojas, nat |
| natura / perfume / vende / cliente | boticario / natura / perfume / vend | 0.50 | boticario, clientes, marca, marcas, natu |
| presente / mae / dar / gosto | presente / dar / presentear / gosta | 0.50 | comprar, dar, gosta, gosto, mae, maes |
| natura / tempo / pedido / depois | pedido / fusao / lider / avon | 0.33 | avon, fusao, lider, natura, pedido, teve |
| comprar / revista / compra / site | revista / site / compra / comprar | 0.33 | compra, comprar, compro, consultora, rev |
| nome / idade / comecar / papo | nome / comecar / papo / vontade | 0.33 | comecar, nome, ouvir, papo, prazer, vont |
| produto / embalagem / parece / ver | refil / embalagem / parece / format | 0.26 | diferente, embalagem, legal, parece, ref |
| produto / pele / propaganda / natur | propaganda / impressao / propaganda | 0.26 | impressao, marca, pele, produto, propaga |

---

## 4. Validação do Modelo

**Classificação supervisionada (alvo: projeto):**

Melhor modelo: **LinearSVC** | F1-macro = **0.9557132581625024**

| Modelo | Accuracy | F1-macro |
|---|---:|---:|
| LinearSVC | 0.9518 | 0.9557 |
| LogReg | 0.9271 | 0.9333 |
| RandomForest | 0.8531 | 0.8548 |
| MultinomialNB | 0.7195 | 0.624 |
| DummyClassifier | 0.198 | 0.0275 |

---

## 5. Evidências Citáveis (top-3 por tópico NMF)

### Tópico 00 — boticario / natura / perfume / vende
**Termos:** boticario; natura; perfume; vende; marca; marcas; vender; perfumaria; perfumes; 

> #1 `doc_eeb118edb6d745e0_pp_ch_0024` (score=0.812)
> Se a comissão acabar se igualando, ela vai vender boticário. Bom, é... E tem uma demanda maior com o Boticário? Não, ela tem uma demanda maior com a Natura. São os clientes fiéis dela, a Natura, de anos. Vira e mexe outro pé de vodkaro e isso acontece, mas pouco. Ela é quase exclusiva, ela vende mui

> #2 `doc_5c06d290f301eadb_pp_ch_0005` (score=0.681)
> Olha, são duas excelentes marcas eu acho que ainda existe sabu com a perfumaria da Natura, tá? Sim, diminuindo, né? Mas ainda em relação ao Boticário, perfumes sempre eu vendo mais do Boticário que da Natura. Mesmo a Natura tendo perfumes maravilhosos, né? Como a Luna, o Essencial. Então, eu sempre 

> #3 `doc_1d7aeba5c3deb241_pp_ch_0022` (score=0.668)
> Pensando mais em produto, além disso que os clientes falam que o Boticário tem melhor duração, ela traz alguma percepção dela também em relação à diferença de produto? Sim, ela pessoalmente gosta de perfumes que façam você... Para ela o perfume é para você ser elogiada. Essa é a relação dela com o p

### Tópico 01 — propaganda / impressao / propagandas / mulheres
**Termos:** propaganda; impressao; propagandas; mulheres; mulher; produto; marca; tempo; exp

> #1 `doc_8f0f9dbe32c1bce3_pp_ch_0027` (score=0.951)
> Como é que chama? Aumenta a nossa autoestima, essas coisas. A gente se preocupa bastante com isso e tenta buscar, tipo, todos os nichos de mulheres, assim, tipo, tem as da natureza, que nem o outro, daí você mostra umas pessoas mais elegantes, assim, tipo, digamos assim. Alguém mais percebeu isso aí

> #2 `doc_20c080a645217030_pp_ch_0029` (score=0.942)
> Eu vou mostrar uma outra propaganda pra vocês e a gente vai conversar sobre ela, tá? E se você fosse mais amiga do tempo? Reduza rugas e linhas de expressão em duas semanas com o super sero de Natura Chronos. Volta de novo, tá? E se você fosse mais amiga de tempo? Ter duas arrugas e linhas de expres

> #3 `doc_8f0f9dbe32c1bce3_pp_ch_0021` (score=0.935)
> Eu acho que eu colocaria como palavra-chave saúde. Porque saúde, porque a natureza, esse contato com a natureza e a imagem que a propaganda passa é de que esse contato traz saúde, traz, como tem no final, bem-estar. Então eu pensaria em saúde. Eu pensaria que a natureza te faz bem. Tudo que é da nat

### Tópico 02 — idade / trabalho / casa / filhos
**Termos:** idade; trabalho; casa; filhos; nome; mae; tempo; vida; filho; semana; mora; moro

> #1 `doc_295321b3ea85e862_pp_ch_0003` (score=0.988)
> E com o que você mora, Jéssica? Eu moro com meus pais no momento. Legal, tá ótimo. Obrigada a você. Muito obrigada. E você? Boa tarde, meu nome é Gisele, eu tenho [IDADE] anos, sou casada, moro com a minha filha no ar livre. Legal. Nas horas de lazer, piscina no [ENDERECO], parque. Tranquilo. Trabal

> #2 `doc_1434a07027866aa7_pp_ch_0003` (score=0.980)
> É uma tranquilidade, né? O Rebeca, e seu marido faz o que? Ele trabalha de costura também. De costura. Mas vocês costuram para clientes ou trabalham em alguma empresa, alguma fábrica comum? Então, eu trabalho para uma empresa, eles trazem pouco de corte, tipo assim, uma vestida, alguma coisa assim, 

> #3 `doc_bd7e79d2d8b662f0_pp_ch_0005` (score=0.939)
> Então, gente, eu gosto bastante de dançar de salão. Já entrei várias vezes pra fazer dança. Esse esporte, né, não deixa de ser uma oportunidade de artista no esporte. Porém, né, enfim, a correria acaba desistindo, mas agora eu vou pegar firme. Matriculei, comecei essa semana, agora vou. Mas começa a

### Tópico 03 — corpo / banho / uso / hidratante
**Termos:** corpo; banho; uso; hidratante; passo; creme; pele; sabonete; gosto; oleo; cheiro

> #1 `doc_80a271097010f616_pp_ch_0004` (score=0.998)
> E Mariana, pensando então nos produtos mais específicos que você pensa quando a gente fala de cuidados pessoais, quais os produtos que você costuma utilizar? Eu uso bastante coisa. Eu uso sabonete e marra, o comum. Eu uso óleo corporal também, não é todo dia, eu uso uma vez por semana. Eu uso creme 

> #2 `doc_a1d2b9d6eaf7c8a9_pp_ch_0031` (score=0.986)
> E ele deixa a pele como? Fredosa, hidratada. Ok. Karen, e você? Obrigada, Andressa. Agora conta pra gente a sua rotina. Gente, eu tomo banho uns dois ou três por dia, né? Tomo quando eu levanto. Hoje eu sei que eu vou tomar no meio do dia e antes de dormir. Toda vez que eu tomo banho, toda vez é o m

> #3 `doc_a0b281c2785ae1ed_pp_ch_0030` (score=0.982)
> Entendi, entendi. Meninas, agora eu queria saber que cada uma de vocês me falasse assim, qual que é a rotina aí de cuidar da pele e do corpo, tá? O que usa, quando usa, por que usa e como sente nesses momentos, tá? Vamos lá. Vou começar com a Elisa, vai Elisa. De manhã eu uso hidratante e também pro

### Tópico 04 — revista / site / compra / comprar
**Termos:** revista; site; compra; comprar; compro; digital; espaco; interativa; consultora;

> #1 `doc_80a271097010f616_pp_ch_0028` (score=0.988)
> E aí, então, talvez por você já estar mais acostumada e por ter essa experiência, então, que você disse, né, de trazer mais proximidade à revista interativa, você acaba preferindo fazer a compra por lá mesmo. Tem alguma coisa, então, que você não conhecia? Não, né? A gente falou, você falou que já..

> #2 `doc_76c629289d2e414c_pp_ch_0024` (score=0.981)
> É parecida, sim, mas é mais... É porque tá a casinha aqui em cima, deixa eu ver. É, assim, tá. E aí, nesse caso? Essa já é a do carrinho, assim, tá certo? Só que aí, claro, aparece tudo, né? Do lado aqui aparece para finalizar, se eu quisesse. Essa aqui, nesse caso, você não finaliza, você envia o p

> #3 `doc_fbdf5e17373e8de3_pp_ch_0030` (score=0.974)
> Olha, depende, vamos dizer, às vezes eu quero produto que ela já tem. Então é como se fosse envio imediato, né? E aí demoraria dois dias, três, é rápido também. No meu endereço chega rápido. Mas assim, tem a historinha do correio em si, né? Então com ela é mais fácil. É, você tem a compra. Pela Revi

### Tópico 05 — presente / dar / presentear / gosta
**Termos:** presente; dar; presentear; gosta; dar presente; aniversario; mae; comprar; prese

> #1 `doc_1055808810073bc2_pp_ch_0007` (score=0.942)
> As próprias crianças te ajudam nessa ideia do presente, né? Eu vi que você envolve a família. É, quando se trata de professor, vai longe. É, é. Ai, que legal. Ai, é uma delícia. Uma com a outra também, né? Aí quando tá chegando aniversário de uma, as outras duas já ficam todas agitadas, já pensando 

> #2 `doc_1e5ee5a39b2288b7_pp_ch_0003` (score=0.936)
> Entendi. E além de aniversário que você falou, que ocasiões, de maneira geral, você costuma presentear? Em datas, né? Dia dos namorados, dia das mães, dia dos pais, Páscoa, com chocolate padrão, Natal, o que é essas? Entendi. E quando você presenteia alguém, o que você sente? Me sinto feliz, né? Que

> #3 `doc_0a02c0b1be74620a_pp_ch_0007` (score=0.912)
> Legal. Você falou aqui de algumas ocasiões específicas, né? Você acha que você dá mais presente nessas datas que estão dadas, ou você percebe que tem outros momentos que você também consegue presentear meio sem motivo? Então, minhas irmãs, elas costumam me presentear também, né? A gente tem uma rela
