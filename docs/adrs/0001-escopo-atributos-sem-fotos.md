# 0001 · O motor usa só atributos estruturados, sem fotos
Data: 2026-11-04   Status: aceita

## Contexto

Em um portal real, as fotos parecem pesar na escolha de um imóvel. Em um estudo com rastreamento ocular, a foto está entre as primeiras áreas vistas no anúncio, e o tempo olhando para ela ajuda a explicar a opinião sobre o imóvel (Seiler, Madhavan e Liechty, 2012). O número de fotos também se associa ao preço e ao tempo de venda (Benefield, Cain e Johnson, 2011). Esses estudos medem atenção e mercado, e não a escolha personalizada que o ImobScore modela.

O motor representa cada imóvel por 12 atributos estruturados e usa uma utilidade linear por pessoa:

```latex
P(A \succ B \mid w) = \sigma\big(w^\top (z_A - z_B)\big)
```

Na leitura de utilidade aleatória, o que influencia a escolha e não está em z vai para o termo de erro. Se v_i for o apelo visual do imóvel i, o modelo completo seria:

```latex
P(A \succ B \mid w) = \sigma\big(w^\top (z_A - z_B) + v_A - v_B\big)
```

Estimar v personalizado com o motor atual não é viável, por três motivos:

1. **Representação:** foto não é um número pronto. Ela exigiria um extrator visual, com vetores de centenas ou milhares de dimensões.
2. **Identificação:** cada pessoa dá 25 pares, e no máximo 15 treinam o modelo. Isso mal basta para os 12 pesos atuais. Com muitas dimensões a mais, a posteriori desses pesos visuais ficaria perto da priori, e as personas não dão uma priori com sentido para eles.
3. **Dados:** o catálogo é simulado e não tem fotos. O app também precisa funcionar sem internet (seção 1.8 do plano).

Fotos não são apenas subjetivas nem impossíveis de modelar. Redes convolucionais já estimam o nível de luxo de um imóvel a partir de fotos (Poursaeed, Matera e Belongie, 2018), e o VBPR leva características visuais à recomendação personalizada (He e McAuley, 2016). Essas abordagens aprendem com grandes volumes de dados de muitos usuários, o que este experimento não tem.

## Decisão

O MVP aprende preferências individuais sobre atributos estruturados. O cartão mostra só esses atributos e uma ilustração neutra por tipo de imóvel. O efeito das fotos fica fora do escopo e é declarado como limitação.

## Alternativas consideradas

- **Fotos reais ou geradas nos cartões, fora do modelo:** rejeitada. O apelo visual entraria nas escolhas sem o modelo o ver, o que aumenta o ruído. Se ele se correlacionar com preço ou idade, também distorce os pesos desses atributos.
- **Atributos visuais anotados à mão (acabamento, luz, conservação):** adiada. Reduz a dimensão, mas não há fotos a anotar no catálogo simulado. A vistoria do plano é um passo nessa direção, fora do modelo.
- **Embeddings de imagem no motor bayesiano:** rejeitada no MVP, pelos motivos de identificação acima. Exige uma camada global aprendida com muitos usuários (guia, seções 13 e 15; fase 4 do plano).

## Consequências

- **O que os atributos não capturam:** "atributo objetivo" descreve a entrada, e não a preferência. Os pesos w são justamente a parte subjetiva que o modelo aprende.
- **Validade externa:** os resultados valem para escolhas feitas diante de cartões de atributos. Não medem o desempenho em um portal com fotos, e isso precisa constar do relatório e do artigo.
- **Outros sinais não modelados:** o nome do bairro aparece no cartão, mas o modelo só vê a distância ao centro. A reputação que um colega de Goiânia atribui a um bairro também vai para o termo de erro.
- **Ilustrações:** não podem sugerir qualidade. O executor deve mantê-las genéricas, e a A-REV2 confere isso.
- **Trabalho futuro:** repetir os mesmos pares com e sem fotos, em anúncios reais, mediria quanto a acurácia muda (fase 2). Depois, um modelo global com características visuais poderia alimentar a camada bayesiana individual (fase 4).

## Referências

- Bradley, R. A.; Terry, M. E. (1952). *Rank analysis of incomplete block designs*. Biometrika. (Lista do guia, seção 21.4.)
- McFadden, D. (1974). *Conditional logit analysis of qualitative choice behavior*. Em *Frontiers in Econometrics*. (Conferir antes de citar.)
- Benefield, J. D.; Cain, C. L.; Johnson, K. H. (2011). *On the relationship between property price, time-on-market, and photo depictions in a multiple listing service*. Journal of Real Estate Finance and Economics, 43(3), 401-422.
- Seiler, M. J.; Madhavan, P.; Liechty, M. (2012). *Toward an understanding of real estate homebuyer internet search behavior: an application of ocular tracking technology*. Journal of Real Estate Research, 34(2), 211-242.
- Poursaeed, O.; Matera, T.; Belongie, S. (2018). *Vision-based real estate price estimation*. Machine Vision and Applications, 29, 667-676.
- He, R.; McAuley, J. (2016). *VBPR: Visual Bayesian Personalized Ranking from implicit feedback*. AAAI.
