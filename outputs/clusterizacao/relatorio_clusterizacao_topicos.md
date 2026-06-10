# Relatório de clusterização e tópicos — KYRA
Run ID: `20260520_112329`
Base: `/Users/emanuelgandra/Desktop/Faculdade/6Período/ProjetoCienciaDados/Kyra/kyrav2/data/processed/interviews_chunks_modeling.parquet`
Chunks analisados: **4.976**
Método principal selecionado: **kmeans**

## Modelo selecionado
```json
{
  "method": "kmeans",
  "k": 18.0,
  "silhouette": 0.22727949917316437,
  "stability_ari_mean": 0.983439508347377,
  "inertia_mean": 294.06386108398436,
  "inertia_std": 0.015900280257520147,
  "calinski_harabasz": 510.38461967476456,
  "davies_bouldin": 1.464600384621516,
  "score": 0.46076703799736896,
  "n_clusters": 18.0,
  "noise_share": 0.0,
  "largest_cluster_share": 0.08440514469453377
}
```

## Principais clusters

### km_005 — propaganda / produto / pele / natura
- Chunks: 420
- Termos: propaganda; produto; pele; natura; acido; amazonia; natureza; impressao; questao; hialuronico; acido hialuronico; natural; pergunta; tempo; cuidado
- Exemplo: Mas como que era? O que mostrava? Descreve para mim essa propaganda. Mostrava uma mulher se hidratando, mostrou no fundo essa coisa da Amazônia, do produto Tucumã, que eu também não conheço, e é uma calmaria, como se você estivesse em ambiente de uma calmaria, uma coisa mais, sabe? Estou na paz. Falou alguma coisa sobre o produto? Você lembra de ter ouvido ou visto alguma mensagem sobre o produto? Falou, teve uma mensagem sobre o produto falando do Tucumã, mas eu não me lembro exatamente das pal...

### km_010 — refil / embalagem / parece / formato
- Chunks: 368
- Termos: refil; embalagem; parece; formato; plastico; cor; ecos; diferente; atual; design; material; ver; lembra; produto; bonito
- Exemplo: Eu gostei também desse design. Não, não é que eu não gostei, é que eu falei do MAD. Eu achei mais pobre. Mais pobre? Não é? É que assim, tipo, tava o brilho, aí parece que deu uma caída assim, entendeu? Não, MAD tem coisa natural. É claro que se fosse comparado com o atual, De primeira a gente ia. Dizer, tá melhor, tá bom. Mas pra mim... Tem tudo a ver. Isso, tem tudo a ver. O que transmite sobre o Naturaecos esse BTF? O que faz pensar sobre o Naturaecos? Eu acho que ficou tão... Mas ficou meio ...

### km_016 — natura / boticario / vende / avon
- Chunks: 353
- Termos: natura; boticario; vende; avon; vender; clientes; cliente; marcas; vendo; venda; marca; produtos; consultora; bastante; perfume
- Exemplo: Que legal, você faz uma atividade mais digital então, de venda de produtos. Isso, sim. E faz muito tempo que você trabalha com isso? Na verdade, faz muito tempinho, eu acho que deve ser uns [IDADE] anos por aí ou mais, não lembro direito, mas deve ser por esse lado. E como você começou? Por que você começou a vender produtos? Eu tinha uma amiga, como eu te posso falar, ela não conhecia muitos bolivianos, né? E eu tinha bastante conhecimento com eles. É que eles falam para mim, as minhas amigas m...

### km_003 — pedido / fusao / lider / natura
- Chunks: 348
- Termos: pedido; fusao; lider; natura; avon; avo; teve; ciclo; pontos; gerente; vender; aplicativo; grupo; mudou; minimo
- Exemplo: Fez o sentido, o bobo, falando o que ia acontecer, é porque teve o tempo e ficou assim. Tá, entendi. O último que eu passei foi o ciclo XVI de Avon? Natura. Avon, aquela imóvel da casa que veio de Chupacabita, vendia uns copinhos, mas nem passei o pedido, porque nem ia pontuar mesmo, então... Nem ia, né? E tá difícil de vender mesmo. Você apresenta o catálogo, apresenta o espaço digital. E tipo assim, não entendo muito o interesse das pessoas. Tá. Deixa eu só pegar uma coisa da Amanda, que foi l...

### km_012 — mae / casa / filhos / filho
- Chunks: 317
- Termos: mae; casa; filhos; filho; hoje; cuidar; tempo; vida; momento; sempre; semana; trabalho; mulher; gosto; idade
- Exemplo: Costumo sair com as caixonas no final da tarde, porque o sol já abaixou. Se eu estiver muito cansado, o que eu faço? Ou assisto, sei lá, streaming, Netflix. Aí depois eu sempre tiro uma hora, duas horas para dar uma estudada, ver alguma coisa do mercado. Ver se possivelmente posso tentar investir ou ainda não é o momento, aí eu converso sempre com a minha mãe, estamos sempre conversando alguma coisa do futuro, alguma coisa da... Da nossa rotina que mudou também bastante. Hoje minha mãe, hoje a m...

### km_007 — produto / questao / cabelo / shampoo
- Chunks: 303
- Termos: produto; questao; cabelo; shampoo; produtos; barra; marca; embalagem; hoje; natural; ambiente; uso; natura; natureza; usar
- Exemplo: Vocês estão falando muito do rendimento, vocês estão falando que deixa o cabelo ter a coisa de cuidado, que deixa o cabelo macio, enfim. E vocês falaram também da questão do. Meio da naturalidade, vocês falaram, né, que é natural, não tem componentes químicos, e também da questão do meio ambiente. O que vocês acham que pesa mais ou pesou mais pra vocês na escola? Eu acho que não ser testada em animais. Para mim, isso daí é o mínimo de uma marca que eu procuro hoje. Para mim, o que eu gostei foi ...

### km_017 — corpo / pele / banho / uso
- Chunks: 301
- Termos: corpo; pele; banho; uso; hidratante; creme; oleo; passo; noite; gosto; energia; sabonete; passar; usar; cheiro
- Exemplo: E ele deixa a pele como? Fredosa, hidratada. Ok. Karen, e você? Obrigada, Andressa. Agora conta pra gente a sua rotina. Gente, eu tomo banho uns dois ou três por dia, né? Tomo quando eu levanto. Hoje eu sei que eu vou tomar no meio do dia e antes de dormir. Toda vez que eu tomo banho, toda vez é o mesmo processo. Eu passo creme e óleo em tudo. Eu não tenho assim, não vou dormir, não vou passar, não. Todo banho eu uso de sabonete, sim, eu não tenho muita marca. Eu uso qualquer marca de sabonete. ...

### km_006 — loja / boticario / natura / lojas
- Chunks: 295
- Termos: loja; boticario; natura; lojas; experiencia; presente; perfumaria; shopping; consumidor; ponto; loja natura; atendimento; consultora; dentro; varejo
- Exemplo: Eu acho que a Natura tem uma coisa assim, primeiro, Aí eu vou falar de outro âmbito que eu não consigo desconectar assim. Primeiro que o consumidor de loja natura, especificamente loja própria, ele não entra para pegar perfumaria, a gente não é relacionado com perfumaria. Então a gente... Eu percebo que modelos de loja mais high, tipo a que a gente for, a do Ijanópolis, a gente tem time de loja com treinamento diferenciado na categoria, que aí consegue trazer elementos da categoria que nos ajuda...

### km_001 — nome / comecar / idade / papo
- Chunks: 290
- Termos: nome; comecar; idade; papo; bate papo; trabalho; bate; vontade; prazer; pouquinho; ouvir; conversa; pode; mora; conhecer
- Exemplo: Não, vai ser só você nesse momento e o pessoal da minha equipe mesmo. É só bate-papo para vocês se conhecerem, você vai ver. Deixa eu ver se eles estão aqui. Não aparecem, deixa eu tentar mandar para eles o convite direto. Tá conseguindo. É cafezinho? Ai, gente! Eu bem queria, viu? Olha só, acho que as meninas estão aqui depois do almoço, né? Pedem cafezinho. É bom, né? Deixa eu ver se agora elas vão conseguir entrar. Sim! Oi, Priscila! Olá, gente! Olá, Priscila! Erika, me desculpe por ter seu n...

### km_004 — perfume / boticario / perfumaria / natura
- Chunks: 270
- Termos: perfume; boticario; perfumaria; natura; perfumes; essencial; cheiro; usa; marca; fragrancia; gosta; relacao; exemplo; embalagem; caiaque
- Exemplo: Imagem de marca, então, sem muita distinção também entre Boticário, Natura. Embalagem, né? A gente perguntou sobre a embalagem e ele, enfim, pouco liga, né? Assim, não tirou nada ali. Cesteiro pra ele que é o importante, né, Dani? É o cheiro. O que? O cheiro. Era o cheiro, assim. E ele falou, voltou muito na questão, né? A gente falou do que melhorar, não sei o que. Ele não fala assim, sei lá, não vejo uma propaganda. Ele não falou nada, assim. Era o lugar do... Não, o perfume tem que fixar bem,...

### km_013 — presente / kit / kits / caixa
- Chunks: 258
- Termos: presente; kit; kits; caixa; sacola; natura; embalagem; cliente; presentes; vem; boticario; maes; sabonete; vende; comprar
- Exemplo: Muda, muda. Porque, normalmente, Natal é mais lembrancinho, ó. Né? Não esqueça, assim, de 50 reais. Que dizia que é R$ 80,00. Então, até que eu nem ponho a pronta-entrega em kits muito caros, porque eu fico com ele parado. Tem que ser coisa útil e num preço ok. Porque, às vezes, a pessoa quer por aniversário e tal, mas ela não quer também. Ou não tem, não é que não quer, só não tá fácil pra ninguém. Então, o que eu mais vendo aqui são kits em torno de R$ 50,00 a R$ 80,00. R$ 50,00? A R$ 80,00. R...

### km_000 — compro / compra / comprar / site
- Chunks: 256
- Termos: compro; compra; comprar; site; loja; exemplo; frete; comprei; mercado livre; internet; produto; gosto; produtos; mercado; sempre
- Exemplo: Você falou o nome da sua marca, mas eu não gravei. Qual que era? Não entendi. Qual é a marca? B.O.B. B.O.B. Foi eu, Também uso da B.O.B. Também é em barra e tal? É, em barra. E ele é pequenininho assim, acho bem legal, porque dá pra levar pra todo lugar facilmente. A compra desses produtos? Alguns de vocês falaram que é a internet. Como é que é? Onde vocês encontram? Onde vocês compram? Eu compro muito no Mercado Livre. Eu gosto de comprar lá, eu tenho frete grátis. Às vezes tem que pagar, mas e...

### km_011 — revista / digital / espaco / interativa
- Chunks: 231
- Termos: revista; digital; espaco; interativa; consultora; revista interativa; espaco digital; site; compra; comprar; manda; whatsapp; exemplo; seria; carrinho
- Exemplo: É parecida, sim, mas é mais... É porque tá a casinha aqui em cima, deixa eu ver. É, assim, tá. E aí, nesse caso? Essa já é a do carrinho, assim, tá certo? Só que aí, claro, aparece tudo, né? Do lado aqui aparece para finalizar, se eu quisesse. Essa aqui, nesse caso, você não finaliza, você envia o pedido por WhatsApp para a consultora. Você põe no carrinho, mas você envia. Para a consultora via WhatsApp. Não, mas assim não aparece para mim. É, não, porque chama outra forma. Essa é uma outra form...

### km_008 — presente / dar / aniversario / gosta
- Chunks: 221
- Termos: presente; dar; aniversario; gosta; presentear; mae; comprar; dar presente; gosto; sempre; presentes; perfume; gostar; comprar presente; dou
- Exemplo: É, nessas percepções do que a pessoa já gosta é sempre mais legal, né? Mas você, quando você dá esse presente, por exemplo, esse exemplo que você deu das flores, né? Você tem alguma expectativa? Você tem algum você espera algo também? Você sente que você consegue nomear alguma expectativa quando você tá entregando esse presente pra ela ou enfim, pra outras pessoas também? Eu acho que assim, a minha expectativa é de ver a pessoa feliz, assim, eu acho muito legal você ver a pessoa recebendo presen...

### km_014 — transmite / embalagem / tecnologia / parece
- Chunks: 221
- Termos: transmite; embalagem; tecnologia; parece; produto; atencao; imagem; inovacao; avancada; sofisticacao; tecnologia avancada; ideia; chama atencao; cor; chama
- Exemplo: Não dá para pegar só a imagem... Mas a cor, a embalagem me atrai. Transmite o quê para você? O que mais? Certamente, eu pegaria para olhar, para ler, para ver do que se trata. Essa imagem de fundo te transmite alguma mensagem, Suzana? Eu gosto, eu gosto dessa imagem de fundo também. Parece moléculas, parece água, sabe? Uma coisa assim de profundidade, sabe? Do mais superficial ao mais profundo. Qual deles, gente, transmite mais a mensagem de inovação? É o S5. S5. Eda, qual transmite para você a ...

### km_002 — pele / mulheres / propagandas / mulher
- Chunks: 191
- Termos: pele; mulheres; propagandas; mulher; impressao; produto; propaganda; transmite; idade; essas; passa; mostra; transmitem; diversidade; mensagem
- Exemplo: O que mais que transmite quando a gente olha para essas propagandas? Josiane, o que transmite para você essas propagandas? Não tem idade, né? A pessoa assim, tanto jovem como mais pessoas idosas, pode utilizar ele que dá o resultado, né? Principalmente porque com o tempo a gente vai perdendo a elasticidade da pele, na elasticidade, mas tem que usar antes de perder a elasticidade, né? Já tem que começar a usar logo. Não deixar para quando já estiver cheia de rúga, tem que ter a prevenção, né? De ...

### km_015 — tecnologia / bio / bioeficiente / produto
- Chunks: 184
- Termos: tecnologia; bio; bioeficiente; produto; linha; nome; palavra; produtos; eficiente; cabeca; bioinovacao; homem; dermotech; pele; biotec
- Exemplo: Pode ir. Bio... Foi muito rápido? Não? Então tá bom. Bioeficiente. Terceiro nome da tecnologia. Bioeficiente. O que vem na cabeça, o que faz pensar sobre a linha de produtos da natural. Se ela vier com esse nome, bioeficiente, como tecnologia, Quarto. Como é que vocês leriam? Alguém vai ler de jeito diferente? Biomais, então. O que vem na cabeça? O que faz pensar sobre os produtos da linha da Natura? Vou para o quinto. Dermobalance. A tecnologia chamaria Dermobalance. O que vem na cabeça e o que...

### km_009 — pele negra / negra / pele / linha
- Chunks: 149
- Termos: pele negra; negra; pele; linha; marca; hidratacao; produto; seria; especifico; hidratante; oleo; produtos; negras; branca; quero
- Exemplo: Mas você acha que seria melhor lançar produto, uma linha para pele mais ressecada ou para pele negra, exclusivamente também falar para pele negra? Eu acho que papele negra ia deixar a gente mais assim, sabe? Mas sentindo pouquinho mais na visão de todo mundo. Todo mundo tem, né? É pra todo tipo de pele, mas a pessoa fala, ó, essa aqui é pra pele morena, essa aqui é pra pele... Ninguém fala assim, essa aqui é pra pele negra, essa aqui é pra pele morena. Então, assim, quando colocar assim, pra pel...

## Leituras por segmento
- **projeto = jack_pearson**: cluster `km_015` (tecnologia / bio / bioeficiente / produto) aparece com share 85.5% e lift 23.12x vs. base.
- **projeto = bem_maes**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 89.1% e lift 13.99x vs. base.
- **publico = consumidoras**: cluster `km_008` (presente / dar / aniversario / gosta) aparece com share 59.8% e lift 13.46x vs. base.
- **projeto = havana_iii**: cluster `km_017` (corpo / pele / banho / uso) aparece com share 79.4% e lift 13.12x vs. base.
- **projeto = anima**: cluster `km_010` (refil / embalagem / parece / formato) aparece com share 85.0% e lift 11.49x vs. base.
- **projeto = gaia_ii**: cluster `km_014` (transmite / embalagem / tecnologia / parece) aparece com share 50.2% e lift 11.31x vs. base.
- **projeto = biome**: cluster `km_007` (produto / questao / cabelo / shampoo) aparece com share 66.1% e lift 10.86x vs. base.
- **projeto = radiosa**: cluster `km_009` (pele negra / negra / pele / linha) aparece com share 30.8% e lift 10.29x vs. base.
- **projeto = compras_digitais**: cluster `km_011` (revista / digital / espaco / interativa) aparece com share 43.9% e lift 9.46x vs. base.
- **projeto = gaia_ii**: cluster `km_002` (pele / mulheres / propagandas / mulher) aparece com share 34.9% e lift 9.08x vs. base.
- **projeto = mercato_brasil**: cluster `km_003` (pedido / fusao / lider / natura) aparece com share 63.4% e lift 9.06x vs. base.
- **projeto = rosacea**: cluster `km_005` (propaganda / produto / pele / natura) aparece com share 72.5% e lift 8.59x vs. base.
- **projeto = compras_digitais**: cluster `km_000` (compro / compra / comprar / site) aparece com share 42.3% e lift 8.22x vs. base.
- **tipo_sessao = entrevista_em_profundidade**: cluster `km_004` (perfume / boticario / perfumaria / natura) aparece com share 42.7% e lift 7.87x vs. base.
- **projeto = 3cs_perfumes**: cluster `km_004` (perfume / boticario / perfumaria / natura) aparece com share 42.7% e lift 7.87x vs. base.
- **publico = consultoras**: cluster `km_013` (presente / kit / kits / caixa) aparece com share 33.9% e lift 6.54x vs. base.
- **publico = lideres**: cluster `km_004` (perfume / boticario / perfumaria / natura) aparece com share 30.8% e lift 5.67x vs. base.
- **projeto = radiosa**: cluster `km_017` (corpo / pele / banho / uso) aparece com share 33.3% e lift 5.51x vs. base.
- **tipo_sessao = entrevista_em_profundidade**: cluster `km_006` (loja / boticario / natura / lojas) aparece com share 31.8% e lift 5.36x vs. base.
- **projeto = 3cs_perfumes**: cluster `km_006` (loja / boticario / natura / lojas) aparece com share 31.8% e lift 5.36x vs. base.
- **projeto = natura_3cs**: cluster `km_008` (presente / dar / aniversario / gosta) aparece com share 21.3% e lift 4.80x vs. base.
- **projeto = natura_3cs**: cluster `km_013` (presente / kit / kits / caixa) aparece com share 23.7% e lift 4.56x vs. base.
- **publico = lideres**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 30.8% e lift 4.34x vs. base.
- **marca_foco = natura**: cluster `km_008` (presente / dar / aniversario / gosta) aparece com share 17.1% e lift 3.85x vs. base.
- **publico = consultoras**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 27.2% e lift 3.83x vs. base.
- **marca_foco = natura**: cluster `km_013` (presente / kit / kits / caixa) aparece com share 19.0% e lift 3.66x vs. base.
- **projeto = mercato_brasil**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 22.5% e lift 3.17x vs. base.
- **publico = consumidoras**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 13.8% e lift 2.37x vs. base.
- **projeto = natura_3cs**: cluster `km_006` (loja / boticario / natura / lojas) aparece com share 13.8% e lift 2.33x vs. base.
- **publico = lideres**: cluster `km_003` (pedido / fusao / lider / natura) aparece com share 15.4% e lift 2.20x vs. base.
- **projeto = rosacea**: cluster `km_002` (pele / mulheres / propagandas / mulher) aparece com share 7.8% e lift 2.03x vs. base.
- **publico = consumidoras**: cluster `km_000` (compro / compra / comprar / site) aparece com share 10.0% e lift 1.94x vs. base.
- **projeto = havana_iii**: cluster `km_015` (tecnologia / bio / bioeficiente / produto) aparece com share 7.1% e lift 1.93x vs. base.
- **projeto = natura_3cs**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 13.4% e lift 1.89x vs. base.
- **projeto = radiosa**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 12.0% e lift 1.89x vs. base.
- **marca_foco = natura**: cluster `km_006` (loja / boticario / natura / lojas) aparece com share 11.0% e lift 1.86x vs. base.
- **projeto = biome**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 11.0% e lift 1.73x vs. base.
- **marca_foco = natura**: cluster `km_005` (propaganda / produto / pele / natura) aparece com share 14.3% e lift 1.70x vs. base.
- **publico = consultoras**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 10.8% e lift 1.69x vs. base.
- **publico = consultoras**: cluster `km_008` (presente / dar / aniversario / gosta) aparece com share 7.4% e lift 1.67x vs. base.
- **projeto = natura_3cs**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 9.0% e lift 1.55x vs. base.
- **tipo_sessao = entrevista_em_profundidade**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 10.7% e lift 1.51x vs. base.
- **projeto = 3cs_perfumes**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 10.7% e lift 1.51x vs. base.
- **marca_foco = natura**: cluster `km_016` (natura / boticario / vende / avon) aparece com share 10.7% e lift 1.51x vs. base.
- **publico = consumidoras**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 9.6% e lift 1.50x vs. base.
- **marca_foco = natura**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 7.9% e lift 1.36x vs. base.
- **marca_foco = nao_inferido**: cluster `km_009` (pele negra / negra / pele / linha) aparece com share 4.0% e lift 1.33x vs. base.
- **marca_foco = nao_inferido**: cluster `km_015` (tecnologia / bio / bioeficiente / produto) aparece com share 4.9% e lift 1.32x vs. base.
- **marca_foco = nao_inferido**: cluster `km_010` (refil / embalagem / parece / formato) aparece com share 9.7% e lift 1.31x vs. base.
- **marca_foco = nao_inferido**: cluster `km_003` (pedido / fusao / lider / natura) aparece com share 9.2% e lift 1.31x vs. base.
- **marca_foco = nao_inferido**: cluster `km_014` (transmite / embalagem / tecnologia / parece) aparece com share 5.8% e lift 1.31x vs. base.
- **marca_foco = nao_inferido**: cluster `km_011` (revista / digital / espaco / interativa) aparece com share 6.0% e lift 1.30x vs. base.
- **projeto = radiosa**: cluster `km_007` (produto / questao / cabelo / shampoo) aparece com share 7.8% e lift 1.28x vs. base.
- **marca_foco = nao_inferido**: cluster `km_017` (corpo / pele / banho / uso) aparece com share 7.7% e lift 1.28x vs. base.
- **projeto = natura_3cs**: cluster `km_012` (mae / casa / filhos / filho) aparece com share 8.0% e lift 1.26x vs. base.
- **publico = consultoras**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 7.2% e lift 1.23x vs. base.
- **marca_foco = nao_inferido**: cluster `km_007` (produto / questao / cabelo / shampoo) aparece com share 7.5% e lift 1.23x vs. base.
- **publico = consultoras**: cluster `km_004` (perfume / boticario / perfumaria / natura) aparece com share 6.5% e lift 1.20x vs. base.
- **projeto = rosacea**: cluster `km_007` (produto / questao / cabelo / shampoo) aparece com share 7.2% e lift 1.19x vs. base.
- **publico = nao_inferido**: cluster `km_002` (pele / mulheres / propagandas / mulher) aparece com share 4.5% e lift 1.18x vs. base.
- **publico = nao_inferido**: cluster `km_015` (tecnologia / bio / bioeficiente / produto) aparece com share 4.4% e lift 1.18x vs. base.
- **publico = nao_inferido**: cluster `km_014` (transmite / embalagem / tecnologia / parece) aparece com share 5.2% e lift 1.18x vs. base.
- **publico = nao_inferido**: cluster `km_009` (pele negra / negra / pele / linha) aparece com share 3.5% e lift 1.18x vs. base.
- **publico = nao_inferido**: cluster `km_005` (propaganda / produto / pele / natura) aparece com share 10.0% e lift 1.18x vs. base.
- **marca_foco = nao_inferido**: cluster `km_000` (compro / compra / comprar / site) aparece com share 6.0% e lift 1.17x vs. base.
- **publico = nao_inferido**: cluster `km_010` (refil / embalagem / parece / formato) aparece com share 8.6% e lift 1.17x vs. base.
- **publico = nao_inferido**: cluster `km_011` (revista / digital / espaco / interativa) aparece com share 5.4% e lift 1.16x vs. base.
- **projeto = biome**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 6.8% e lift 1.16x vs. base.
- **publico = nao_inferido**: cluster `km_007` (produto / questao / cabelo / shampoo) aparece com share 7.0% e lift 1.16x vs. base.
- **publico = nao_inferido**: cluster `km_017` (corpo / pele / banho / uso) aparece com share 7.0% e lift 1.16x vs. base.
- **projeto = biome**: cluster `km_000` (compro / compra / comprar / site) aparece com share 5.9% e lift 1.15x vs. base.
- **marca_foco = nao_inferido**: cluster `km_002` (pele / mulheres / propagandas / mulher) aparece com share 4.4% e lift 1.15x vs. base.
- **publico = nao_inferido**: cluster `km_003` (pedido / fusao / lider / natura) aparece com share 8.0% e lift 1.14x vs. base.
- **publico = nao_inferido**: cluster `km_006` (loja / boticario / natura / lojas) aparece com share 6.6% e lift 1.12x vs. base.
- **projeto = jack_pearson**: cluster `km_001` (nome / comecar / idade / papo) aparece com share 6.5% e lift 1.12x vs. base.
- **tipo_sessao = nao_inferido**: cluster `km_017` (corpo / pele / banho / uso) aparece com share 6.7% e lift 1.11x vs. base.
- **tipo_sessao = nao_inferido**: cluster `km_010` (refil / embalagem / parece / formato) aparece com share 8.2% e lift 1.11x vs. base.
- **tipo_sessao = nao_inferido**: cluster `km_015` (tecnologia / bio / bioeficiente / produto) aparece com share 4.1% e lift 1.11x vs. base.
- **tipo_sessao = nao_inferido**: cluster `km_014` (transmite / embalagem / tecnologia / parece) aparece com share 4.9% e lift 1.11x vs. base.
- **tipo_sessao = nao_inferido**: cluster `km_002` (pele / mulheres / propagandas / mulher) aparece com share 4.3% e lift 1.11x vs. base.

## Tópicos NMF
- `nmf_00` — boticario / presente / natura / perfume — boticario; presente; natura; perfume; loja; perfumaria; vende; marca; marcas; kit; gosta; dar; presentes; caixa; cliente
- `nmf_01` — embalagem / parece / produto / atencao — embalagem; parece; produto; atencao; cor; transmite; tecnologia; imagem; diferente; natureza; impressao; passa; chama; refil; chama atencao
- `nmf_02` — nome / idade / trabalho / hoje — nome; idade; trabalho; hoje; tempo; casa; natura; lider; avon; pouquinho; mundo; filhos; vida; comecar; pode
- `nmf_03` — pele / corpo / negra / pele negra — pele; corpo; negra; pele negra; hidratante; produto; propaganda; hidratacao; uso; creme; oleo; banho; linha; cuidado; usar
- `nmf_04` — revista / compra / comprar / site — revista; compra; comprar; site; compro; digital; consultora; espaco; exemplo; pelo; manda; interativa; aplicativo; revista interativa; promocao
- `nmf_05` — aproveite / bate papo / papo / conversa — aproveite; bate papo; papo; conversa; bate; camera; local; conexao; estiver; comecar; estamos; diferentes; basta; microfone; tenha

## Tópicos LDA
- `lda_00` — produto / pele / propaganda / produtos — produto; pele; propaganda; produtos; natura; questao; marca; atencao; parece; impressao; natureza; pode; embalagem; passa; negra
- `lda_01` — natura / boticario / loja / presente — natura; boticario; loja; presente; avon; perfume; vende; vender; cliente; produtos; perfumaria; pedido; caixa; consultora; clientes
- `lda_02` — nome / idade / sempre / mae — nome; idade; sempre; mae; gosto; tempo; hoje; casa; presente; trabalho; dar; pouquinho; pode; mundo; ver
- `lda_03` — pele / corpo / banho / passo — pele; corpo; banho; passo; linha; hidratante; noite; creme; nome; pode; produto; passar; uso; produtos; palavra
- `lda_04` — embalagem / marca / linha / perfume — embalagem; marca; linha; perfume; parece; presente; cheiro; refil; sabonete; ver; natura; ecos; diferente; gosto; hidratante
- `lda_05` — comprar / compra / revista / exemplo — comprar; compra; revista; exemplo; compro; produto; loja; site; produtos; pelo; sempre; consultora; promocao; manda; pela
