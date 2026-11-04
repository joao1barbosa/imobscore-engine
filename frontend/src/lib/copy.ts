// Textos da interface. Dono: arquiteto (seção 1.3 do plano).
// Nenhum texto visível ao usuário é escrito direto em um componente.

const plural = (n: number, one: string, many: string) => (n === 1 ? one : many);

export const copy = {
  common: {
    appName: "ImobScore",
    demoCatalog: "Catálogo de demonstração",
    retry: "Tentar de novo",
    errorTitle: "Algo deu errado",
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
        body: "Escolher, em 25 pares de imóveis fictícios à venda em Goiânia-GO, qual você prefere. Antes, você informa uma faixa de preço e um perfil. Leva cerca de 2 minutos, e não existe resposta certa.",
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
    submit: "Começar os 25 pares",
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
} as const;
