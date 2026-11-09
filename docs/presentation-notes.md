# Notas para a apresentação e o artigo

Material de revisão de João para a banca e para o artigo futuro. Cada tema aponta para a decisão registrada, quando houver. Na A09, estas notas alimentam `docs/demo-script.md`.

## Por que o motor não usa fotos

Decisão registrada em `docs/adrs/0001-escopo-atributos-sem-fotos.md`.

### Como falar disso

| Evite | Prefira | Motivo |
| --- | --- | --- |
| "É notório que as fotos são decisivas" | "A evidência sugere que as fotos pesam" | Os estudos medem atenção e mercado, e não a escolha personalizada |
| "Foto é totalmente subjetiva" | "Foto mistura informação concreta e gosto" | Acabamento, conservação e luz são concretos, e já há redes que estimam o nível de luxo a partir de fotos |
| "É muito difícil" ou "é impossível" | "É inviável neste escopo" | A literatura já recomenda com imagens, mas com muitos dados de muitos usuários |
| "Critérios objetivos" | "Atributos estruturados" | Os atributos são objetivos, mas a preferência é subjetiva, e é ela que os pesos aprendem |

### Fala (cerca de 30 segundos)

> As fotos provavelmente pesam muito na escolha de um imóvel, e o ImobScore não tenta aprender isso agora. Com 20 escolhas por pessoa, não há dados para descobrir o que, em uma foto, agrada a cada um. Por isso, os cartões não têm fotos, e o motor aprende só o peso que cada pessoa dá a preço, área, localização e outros atributos. Isso limita o resultado: ele não prevê o comportamento em um portal com fotos. Medir esse efeito é o próximo passo, com anúncios reais.

### Texto para o artigo

> O ImobScore modela a preferência individual sobre 12 atributos estruturados, com utilidade linear e o modelo de Bradley-Terry: P(A ≻ B | w) = σ(wᵀ(z_A − z_B)). Fatores que influenciam a escolha, mas não integram z, como o apelo visual das fotos, passam ao termo de erro da utilidade. Evidências de rastreamento ocular e de mercado sugerem que as fotos têm papel relevante na avaliação de anúncios (Seiler et al., 2012; Benefield et al., 2011), e há modelos que extraem sinais visuais para estimar preços e personalizar recomendações (Poursaeed et al., 2018; He e McAuley, 2016).
>
> Esses métodos, porém, dependem de grandes volumes de dados de muitos usuários. Incorporá-los aqui acrescentaria centenas de dimensões a um modelo treinado com no máximo 10 pares por pessoa, e a posteriori dos pesos visuais permaneceria próxima da priori. Por isso, o estudo se limita a atributos estruturados e apresenta cartões sem fotos, com ilustrações neutras. Os resultados valem, portanto, para escolhas feitas a partir de atributos, e não estimam o desempenho em anúncios com fotos.

### Perguntas prováveis

- **"Então seu modelo ignora o que mais importa?"** Ele ignora de propósito, e isso está declarado. Os cartões não têm fotos justamente para que elas não influenciem as escolhas sem o modelo ver.
- **"E se você tivesse mostrado fotos?"** Elas entrariam no termo de erro. Se o apelo visual acompanhasse preço ou idade, ainda distorceria esses pesos.
- **"Dá para incluir fotos depois?"** Sim, com um modelo global treinado em muitos usuários, alimentando a camada bayesiana individual. Isso se encaixa na fase 4 do plano.

### Cuidados

- **O bairro tem o mesmo problema.** O cartão mostra o nome do bairro, mas o modelo só vê a distância ao centro. A fama que um colega de Goiânia atribui a um bairro também vai para o termo de erro. Vale mencionar antes que perguntem.
- **Não diga que o plano tirou as fotos por esse motivo.** "Sem fotos externas" está no plano junto do requisito de rodar sem internet. O argumento sobre os dados é uma justificativa adicional, e válida.

### Referências a conferir antes de citar

As referências estão completas no ADR. Só o Bradley-Terry vem da lista do guia. Dos outros, a existência foi confirmada e só resumos foram lidos: Benefield et al. (2011), Seiler et al. (2012), Poursaeed et al. (2018) e He e McAuley (2016). McFadden (1974) foi citado de memória e ainda não foi conferido.

## Decisões do experimento que a banca pode cobrar

Decisões de 04/11 a 09/11, registradas em `docs/decisions.md`.

- **20 pares, e não 40:** para reduzir a desistência. Começou com 25 e caiu para 20 em 05/11, depois de as 3 primeiras pessoas acharem longo. Como 10 ficam para teste, a curva de acurácia vai só até `n_train = 10`. P01 a P03 responderam 25 e entram normalmente.
- **Só sessões completas entram na avaliação:** quem abandona antes do 20º par fica de fora (3 sessões).
- **Quem responde rápido demais fica de fora:** mediana abaixo de 1 s por par, regra fixada em 09/11, antes de rodar a avaliação. Saíram P09 e P30, e ficaram 31 participantes.
- **Código gerado pelo servidor:** quem troca de aparelho vira outro participante. Se completar duas vezes, conta como duas pessoas.
- **Catálogo inteiro só em Goiânia e compra:** a coleta e a demo usam a mesma população de imóveis, então o que a demo mostra é o que os dados sustentam. O custo é que os resultados não valem para aluguel nem para outras cidades.
- **Nenhum dado pessoal:** o projeto não guarda nome, e-mail, telefone nem IP. A coleta rodou na Vercel e no Render, que ainda veem o IP em trânsito, como qualquer servidor web.
