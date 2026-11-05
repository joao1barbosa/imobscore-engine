// Textos da interface. Dono: arquiteto (seção 1.3 do plano).
// Nenhum texto visível ao usuário é escrito direto em um componente.

const plural = (n: number, one: string, many: string) => (n === 1 ? one : many);

export const copy = {
  common: {
    appName: "ImobScore",
    demoCatalog: "Catálogo de demonstração",
    retry: "Tentar de novo",
    errorTitle: "Algo deu errado",
    nav: {
      label: "Navegação",
      feed: "Feed",
      model: "Modelo",
      experiment: "Experimento",
    },
    apiErrors: {
      session_not_found: "Não encontramos esta sessão. Comece de novo.",
      listing_not_found: "Não encontramos este imóvel.",
      pair_already_answered: "Este par já foi respondido. Vamos para o próximo.",
      pair_out_of_order: "Este par não é o próximo da fila. Vamos atualizar.",
      session_done: "Esta sessão já foi concluída.",
      validation_error: "Alguns dados não foram aceitos. Revise e envie de novo.",
      not_available: "Esta função ainda não está disponível.",
      network: "Sem conexão com o servidor. Verifique a internet e tente de novo.",
      unknown: "Não foi possível concluir agora. Tente de novo.",
    },
  },

  collection: {
    welcome: {
      title: "Ajude a testar o ImobScore",
      lead: "O ImobScore tenta descobrir de qual imóvel cada pessoa gosta só pelas escolhas que ela faz. Este experimento mede se ele consegue.",
      whatToDo: {
        title: "O que você vai fazer",
        body: "Escolher, em 20 pares de imóveis fictícios à venda em Goiânia-GO, qual você prefere. Antes, você informa uma faixa de preço e um perfil. Leva cerca de 5 minutos, e não existe resposta certa.",
      },
      howWeUse: {
        title: "Como usamos suas respostas",
        body: "Suas escolhas treinam um modelo, e depois medimos se ele acerta suas preferências melhor que outros métodos. Os resultados entram em um trabalho acadêmico, sem identificar ninguém.",
      },
      noPersonalData: {
        title: "Nenhum dado pessoal",
        body: "Não coletamos nome, e-mail, telefone nem qualquer outro dado pessoal. Guardamos só um código gerado automaticamente, suas respostas e o tempo de cada escolha.",
      },
      start: "Quero participar",
    },
    form: {
      title: "Antes de começar",
      lead: "Só mais três respostas rápidas.",
    },
    loadingForm: "Carregando o formulário",
    sections: {
      participation: "Sua participação",
      search: "O que você procuraria",
      persona: "Qual perfil mais parece com você?",
    },
    consent: {
      label: "Concordo em participar e em ter estas respostas usadas no experimento.",
      details:
        "Guardamos só um código gerado automaticamente, as respostas deste formulário, cada escolha e o tempo de cada resposta.",
    },
    segment: "Imóveis à venda em Goiânia-GO",
    price: {
      label: "Faixa de preço",
      min: "Mínimo",
      max: "Máximo",
      limits: (floor: string, ceiling: string) => `Neste catálogo: de ${floor} a ${ceiling}`,
    },
    submit: "Começar os 20 pares",
    submitting: "Preparando os pares",
    validation: {
      consent: "É preciso concordar para participar",
      priceOrder: "O máximo precisa ser maior que o mínimo",
      priceEmpty: "Nenhum imóvel nessa faixa",
      priceRequired: "Informe um valor maior que zero",
      persona: "Escolha um perfil",
    },
    loadError: {
      title: "Não foi possível abrir a coleta",
      description: "Verifique sua conexão e tente de novo.",
    },
    empty: {
      title: "A coleta não está disponível agora",
      description: "O catálogo ainda não foi carregado. Avise quem enviou o link.",
    },
    submitError: "Não foi possível começar. Tente de novo.",
    thanks: {
      title: "Obrigado por participar!",
      body: (total: number) => `Suas ${total} escolhas foram registradas.`,
      purpose: "Elas vão ajudar a medir se o ImobScore aprende o gosto de cada pessoa.",
      close: "Você já pode fechar esta página.",
    },
  },

  compare: {
    question: "Qual você prefere?",
    hint: "Escolha o que mais combina com você, mesmo que nenhum seja perfeito.",
    progress: (i: number, n: number) => `Par ${i} de ${n}`,
    loading: "Carregando o próximo par",
    sending: "Registrando sua escolha",
    keyboardHint: "Use as setas do teclado para escolher",
    keyLeft: "←",
    keyRight: "→",
    chooseLabel: (title: string, price: string) => `Escolher ${title}, ${price}`,
    empty: {
      title: "Você respondeu a todos os pares",
      description: "Estamos abrindo o próximo passo.",
    },
    loadError: {
      title: "Não foi possível carregar o par",
      description: "Suas respostas anteriores estão salvas. Tente de novo.",
    },
    answerError: "Sua escolha não foi registrada. Toque de novo no imóvel.",
    listing: {
      bedrooms: (n: number) => `${n} ${plural(n, "quarto", "quartos")}`,
      bathrooms: (n: number) => `${n} ${plural(n, "banheiro", "banheiros")}`,
      parking: (n: number) => (n === 0 ? "Sem vaga" : `${n} ${plural(n, "vaga", "vagas")}`),
      age: (n: number) => (n === 0 ? "Novo" : `${n} ${plural(n, "ano", "anos")}`),
      leisure: (n: number) => (n === 0 ? "Sem lazer" : `Lazer: ${n} ${plural(n, "item", "itens")}`),
      distCenter: (distance: string) => `${distance} do centro`,
      location: (neighborhood: string, city: string) => `${neighborhood} · ${city}`,
      petFriendly: "Aceita pet",
      doorman: "Portaria 24 h",
      illustrationAlt: {
        apartment: "Ilustração de um prédio",
        house: "Ilustração de uma casa",
      },
    },
  },

  home: {
    headline: "Pare de filtrar. Comece a escolher.",
    lead: "O ImobScore aprende do que você gosta com poucas escolhas entre dois imóveis e monta um ranking só para você.",
    start: "Começar",
    demo: "Modo demo",
    steps: [
      { title: "Escolha um perfil", body: "Ele é só o ponto de partida." },
      { title: "Compare alguns pares", body: "Em cada par, diga qual imóvel você prefere." },
      {
        title: "Veja seu ranking",
        body: "Cada imóvel recebe uma nota de afinidade, com o grau de incerteza.",
      },
    ],
    stepTitle: (n: number, title: string) => `${n}. ${title}`,
    catalogNote: "Imóveis fictícios à venda em Goiânia-GO.",
    experimentLink: "Ver os resultados do experimento",
  },

  onboarding: {
    step: (i: number, n: number) => `Passo ${i} de ${n}`,
    price: {
      title: "Quanto você quer pagar?",
      lead: "Só mostramos imóveis perto dessa faixa.",
    },
    persona: {
      title: "Qual perfil mais parece com você?",
      lead: "Ele é só o ponto de partida: suas escolhas ajustam o resto.",
    },
    next: "Continuar",
    back: "Voltar",
    submit: "Começar as comparações",
    submitting: "Preparando os pares",
    submitError: "Não foi possível começar. Tente de novo.",
    loading: "Carregando o formulário",
    empty: {
      title: "O catálogo ainda não está disponível",
      description: "Rode o comando de carga do catálogo e tente de novo.",
    },
    loadError: {
      title: "Não foi possível abrir esta tela",
      description: "Verifique sua conexão e tente de novo.",
    },
  },

  demo: {
    title: "Toque em um perfil para começar",
    lead: "São 3 escolhas e um ranking feito para esse perfil, em menos de 1 minuto.",
    chooseLabel: (name: string) => `Usar o perfil ${name}`,
    range: (min: string, max: string) => `${min} a ${max}`,
    submitting: "Preparando os pares",
    loading: "Carregando os perfis",
  },

  feed: {
    title: "Seu ranking",
    summary: (persona: string, n: number) =>
      n === 0
        ? `Perfil ${persona} · nenhuma escolha respondida`
        : `Perfil ${persona} · ${n} ${plural(n, "escolha respondida", "escolhas respondidas")}`,
    toggleLabel: "Comparar o ranking",
    before: "Antes",
    after: "Depois",
    beforeHint: "Antes: só o perfil, sem nenhuma escolha sua.",
    afterHint: (n: number) =>
      `Depois: ajustado ${plural(n, "pela sua", "pelas suas")} ${n} ${plural(n, "escolha", "escolhas")}.`,
    noPairsHint: "Este ranking usa só o perfil. Compare alguns pares para ajustá-lo.",
    rank: (n: number) => `${n}º`,
    movedUp: (n: number) => `Subiu ${n}`,
    movedDown: (n: number) => `Desceu ${n}`,
    kept: "Manteve a posição",
    enteredTop: "Entrou no top 30",
    scoreTooltip: (score: number) => `${score}% de chance de você preferir este a um imóvel típico`,
    interval: (low: number, high: number) => `entre ${low} e ${high}`,
    toModel: "Ver o que o modelo aprendeu",
    loading: "Calculando seu ranking",
    empty: {
      title: "Nenhum imóvel nesta faixa",
      description: "Comece de novo com uma faixa de preço mais ampla.",
      action: "Começar de novo",
    },
    loadError: {
      title: "Não foi possível calcular seu ranking",
      description: "Suas escolhas estão salvas. Tente de novo.",
    },
  },

  modelPanel: {
    title: "O que o modelo aprendeu",
    weights: {
      title: "O que pesa para você",
      lead: "À direita do zero, a característica aumenta sua preferência; à esquerda, reduz. A barra vai de 5% a 95%.",
      priorOnlyLead: "Ainda sem escolhas: os pesos são só os do perfil.",
      posterior: "Depois das suas escolhas",
      prior: "Só o perfil",
      chartLabel: "Pesos de cada característica, antes e depois das escolhas",
      tableToggle: "Ver como tabela",
      tableFeature: "Característica",
      tablePrior: "Priori",
      tablePosterior: "Posteriori",
      tableInterval: "5% a 95%",
      interval: (low: string, high: string) => `${low} a ${high}`,
    },
    diagnostics: {
      title: "A cadeia convergiu?",
      ok: "Diagnósticos dentro da faixa esperada.",
      alert:
        "Os diagnósticos ficaram fora da faixa nesta rodada. Os pesos podem estar menos confiáveis.",
      acceptance: {
        label: "Aceitação",
        hint: "Parte dos passos aceitos. Entre 15% e 50% é saudável.",
      },
      rhat: { label: "R-hat", hint: "Perto de 1: as cadeias concordam." },
      ess: {
        label: "ESS",
        hint: "Amostras independentes equivalentes. Acima de 400 é bom.",
      },
      time: { label: "Tempo", hint: "Tempo para recalcular depois da última escolha." },
      timeValue: (ms: number) => `${ms} ms`,
    },
    trace: {
      title: "Traço das cadeias",
      lead: "Cada linha é uma cadeia percorrendo os valores possíveis de um peso. Linhas misturadas indicam que elas concordam.",
      select: "Peso",
      chain: (i: number) => `Cadeia ${i}`,
      points: "250 pontos guardados",
      chartLabel: "Traço de quatro cadeias para o peso escolhido",
    },
    loading: "Carregando o modelo",
    loadError: {
      title: "Não foi possível carregar o modelo",
      description: "Suas escolhas estão salvas. Tente de novo.",
    },
  },

  experiment: {
    title: "O experimento",
    lead: "Com poucas escolhas, qual método acerta mais a preferência de cada pessoa?",
    how: (n: number) =>
      `${n} participantes. Cada um respondeu a pelo menos 20 pares aleatórios: até 10 treinam os métodos, e 10 ficam de fora para o teste.`,
    simulated: "Dados simulados: estes resultados não vêm de pessoas reais.",
    methods: {
      bayes: "Motor bayesiano",
      mle: "Regressão logística",
      persona: "Média da persona",
      equal: "Pesos iguais",
    },
    curve: {
      title: "Acurácia por número de pares",
      lead: "Acerto em pares que os métodos nunca viram. A faixa mostra ±1 desvio.",
      xAxis: "Pares usados no treino",
      chartLabel: "Acurácia de cada método por número de pares de treino",
    },
    table: {
      title: "Números da curva",
      method: "Método",
      pairs: (n: number) => `${n} pares`,
      note: "Cada célula mostra a acurácia e a perda logarítmica. Na perda, menor é melhor.",
    },
    participants: {
      title: "Por participante, com 5 pares",
      lead: "Os resultados saem por pessoa: são poucos colegas, em um estudo exploratório.",
      chartLabel: "Acurácia com 5 pares, por participante e método",
    },
    loading: "Carregando os resultados",
    empty: {
      title: "Ainda não há resultados",
      description: "Os gráficos aparecem depois que a coleta terminar e a avaliação rodar.",
    },
    loadError: {
      title: "Não foi possível carregar os resultados",
      description: "Verifique sua conexão e tente de novo.",
    },
  },
} as const;
