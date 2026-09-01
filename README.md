# Análise qualitativa — atitudes parentais e tecnologia na infância autista

Este repositório reúne o corpus, o codebook e os scripts da análise qualitativa da dissertação. A análise está **concluída**: o codebook alinhado ao corpus é `Metodologia/metodologia_final.docx`; o corpus de trabalho está em `dados_qual/processamento/dataset_processado.xlsx`; a redação dos resultados está em `Metodologia/resultados.docx`; as frequências, coocorrências e inventário estão em `analise_qualitativa.ipynb`.

- [1. O que é este projeto?](#1-o-que-é-este-projeto)
- [2. Como a alocação de passagens foi feita?](#2-como-a-alocação-de-passagens-foi-feita)
- [3. Domínios diagnosticados](#3-domínios-diagnosticados)
- [4. Limitações](#4-limitações)
- [5. Prompts utilizados nas sessões interativas](#5-prompts-utilizados-nas-sessões-interativas)
- [6. Estado final da análise](#6-estado-final-da-análise)

---

## 1. O que é este projeto?

Este trabalho busca investigar as atitudes e opiniões de pais e responsáveis de crianças autistas sobre a tecnologia como ferramenta pedagógica, assim como captar percepções acerca da infância na era digital. O objetivo desta investigação é extrair insights para inspirar intervenções educacionais com uso da tecnologia e da robótica para auxiliar no processo de aprendizagem e desenvolvimento de crianças autistas em escolas estaduais no Tocantins.

O método de coleta de dados foi a condução de entrevistas semi-estruturadas com pais e responsáveis de crianças portadoras de autismo e necessidades especiais. No total, dez entrevistas foram conduzidas, mas apenas nove foram utilizadas. No processo de extração, processamento e limpeza, problemas de transcrição de áudio tornaram um script ilegível, e optou-se por removê-lo da amostra de dados relevantes.

A metodologia de análise é **codificação temática indutiva**: o engajamento do pesquisador com os scripts de entrevista deu origem aos domínios relevantes. Os domínios apresentados aqui são resultado da interpretação do pesquisador acerca dos dados brutos. Em outras palavras, o conjunto de domínios deste trabalho **não** é apoiado por uma revisão prévia da literatura em pedagogia e tecnologia para delimitar categorias a serem buscadas nos dados. Os domínios são *a posteriori* e emergem da leitura do material.

As definições de cada domínio, subdomínio e subdomínio detalhado também são de criação do pesquisador e se referem ao seu processo de engajamento e interpretação dos dados brutos. Não são retiradas da literatura nem têm respaldo em materiais previamente publicados; são inspiradas no que o próprio conjunto de dados fornece.

A unidade de análise é a **passagem**. Toda passagem relevante é obrigatoriamente alocada em um par domínio/subdomínio. Uma codificação pode ter um terceiro nível opcional, o **subdomínio detalhado**. Uma mesma passagem pode receber mais de uma codificação, entre domínios ou entre subdomínios do mesmo domínio. Por causa dessa multi-alocação, as métricas reportadas são de **prevalência** (não composição que some 100%): prevalência no corpus, no domínio ou no caminho domínio › subdomínio.

Para suportar a relevância dessa análise qualitativa, uma breve análise quantitativa e descritiva de indicadores educacionais da rede estadual do Tocantins, extraídos do Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP), foi conduzida. Isto consta no script **analise_quantitativa.ipynb**. 

Arquivos centrais:

| Arquivo | Função |
| --- | --- |
| `Metodologia/metodologia_final.docx` | Codebook alinhado 1:1 ao corpus (fonte de verdade das definições) |
| `Metodologia/resultados.docx` | Redação dos resultados e limitações da análise |
| `dados_qual/processamento/dataset_processado.xlsx` | Corpus (abas `dataset_processado`, `formato_longo` e `removidas`) |
| `dados_qual/transcripts_crus/` | Transcrições integrais das entrevistas |
| `analise_qualitativa.ipynb` | Descritivos, diagramas, coocorrências, frequências e inventário de caminhos |
| `functions.py` | Funções usadas no notebook (`descreve_dataset`, `diagrama_descritivo`, `matriz_coocorrencia_dominios`, `heatmap_coocorrencia_subdominios`, `inventario_caminhos`, `plotar_categorias`) |
| `dados_quant/` | Dados e insumos da análise quantitativa (separada) |

---

## 2. Como a alocação de passagens foi feita?

A alocação de passagens nas categorias se deu a partir de sessões interativas entre IA e o pesquisador. As sessões interativas se iniciaram a partir de um documento cru, feito interamente por supervisão humana. A IA foi utilizada no processo de aprimoramento das alocações, numa espécie de revisão por pares. Todo o processo de alocação de passagens foi revisado por humanos.

Na prática, isso significou:

1. **Codificação inicial humana.** O pesquisador leu as transcrições, recortou passagens e as alocou na árvore de domínios, subdomínios e subdomínios detalhados. Esse documento cru é a base do `dataset_processado.xlsx`.
2. **Revisão por pares com IA.** Em sessões interativas, a IA relê cada passagem contra as definições do codebook e contra o transcript integral, e propõe manter, trocar, acrescentar ou retirar caminhos. A proposta sai no chat; nada entra no Excel sem validação.
3. **Decisão humana.** Só entram no dataset as recodificações e fusões aprovadas pelo pesquisador.
4. **Alinhamento de nomenclatura.** Rótulos do corpus e do `metodologia_final.docx` foram sincronizados (por exemplo `Tendência a hiperfoco`, `Dificuldade com autonomia`, `Parentalidade na era da cidadania digital`, `Bem-Estar Infantil na era da cidadania digital`).
5. **Fusões e limpeza.** Passagens vizinhas do mesmo turno foram fundidas quando aprovado; exclusões substantivas (viés de entrevista, transcript inviável, irrelevância analítica) foram registradas na aba `removidas`.

A aba `formato_longo` é a fonte da verdade operacional: cada linha é um caminho `id_passagem × Domínio × Sub-domínio × Sub-domínio detalhado`. A aba larga (`dataset_processado`) replica os mesmos caminhos em listas paralelas. `n_caminhos` deve coincidir com o número de linhas longas daquela passagem.

---

## 3. Domínios diagnosticados

As tabelas abaixo documentam a árvore temática. A fonte de verdade alinhada ao corpus é `Metodologia/metodologia_final.docx`. Células vazias no Word aparecem como "—". Algumas notas “Renomear para” abaixo são históricas do codebook original; no dataset e no `metodologia_final` os rótulos já estão atualizados (`Tendência a hiperfoco`, `Dificuldade com autonomia`, `Inteligência > Aprendizagem cinestésica`, `Tendência à hiperatividade`, etc.).

Regras de estrutura já aplicadas no corpus: `Atraso na fala` só existe aninhado em `Dificuldade com linguística`; `Otimistas quanto à tecnologia…` existe **com e sem** o detalhado de robótica.

### 3.1 Atitudes Parentais na era da cidadania digital

Passagens que expressam opiniões e percepções parentais sobre o uso da tecnologia como ferramenta pedagógica, o conceito de cidadania digital e o uso em geral da tecnologia por crianças.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Atitudes Parentais na era da cidadania digital | Otimismo perante à cidadania digital | N/A | Passagens em que os pais expressam otimismo perante à cidadania digital, concordando com a sua relevância no processo de aprendizagem e educação de seus filhos. | Duas passagens aqui foram eliminadas do corpus por viés de desejabilidade social e priming. A forma como a pergunta foi feita aos entrevistados os predispôs a sempre consentir com a entrevistadora, impedindo opiniões contrárias ou contra-argumentos. As passagens que foram mantidas são aquelas que possuem algum tipo de elaboração espontânea por parte do entrevistado, e que não expressa uma confirmação vazia. Entretanto, essa categoria não pode ser compreendida como uma representação real da opinião dos entrevistados e todos os dados derivados dela devem ser interpretados com cautela (evidência fraca em análise qualitativa). |
| Atitudes Parentais na era da cidadania digital | Conhecimento sobre o conceito de cidadania digital | N/A | Resposta positiva à pergunta “você conhece o conceito de cidadania digital?” | N/A |
| Atitudes Parentais na era da cidadania digital | Desconhecimento sobre o conceito de cidadania digital | N/A | Resposta negativa à pergunta “você conhece o conceito de cidadania digital?” | N/A |
| Atitudes Parentais na era da cidadania digital | Favoráveis à tecnologia | N/A | Quando a passagem expressa alguma opinião favorável ao uso de tecnologia, tanto por pais quanto por crianças. Geralmente vem acompanhado da tag “valor da tecnologia” porque estas passagens geralmente são elaborações espontâneas do porquê a tecnologia é positiva. | N/A |
| Atitudes Parentais na era da cidadania digital | Resistência à tecnologia | Conteúdo vazio/não agregador | Passagens que explicitam opiniões contrárias ao uso de tecnologia, julgando o conteúdo online como “vazio", “sem utilidade”. | N/A |
| Atitudes Parentais na era da cidadania digital | Resistência à tecnologia | O digital mina a infância | Passagens que explicitam opiniões contrárias ao uso de tecnologia, julgando o conteúdo online como um fator que corrompeu a infância e a essência de ser criança. | N/A |
| Atitudes Parentais na era da cidadania digital | Preocupação com a tecnologia | Conteúdo perigoso/deseducador/inapropriado | Quando a passagem expressa preocupação pela exposição online da criança a conteúdo inapropriado. | N/A |
| Atitudes Parentais na era da cidadania digital | Preocupação com a tecnologia | O digital é não amigável com crianças autistas | Quando a passagem expressa preocupação porque a digital expõe crianças a um ambiente hostil (bullying, pessoas mal intencionadas etc.) | N/A |
| Atitudes Parentais na era da cidadania digital | Preocupação com a tecnologia | Falta de controle das interações virtuais | Quando a passagem expressa, de forma explícita, o receio dos pais de não conseguirem controlar com quem ou com o que seus filhos interagem online. | N/A |
| Atitudes Parentais na era da cidadania digital | Preocupação com a tecnologia | Vício | Quando a passagem expressa uma preocupação parental com vício por redes sociais. | N/A |
| Atitudes Parentais na era da cidadania digital | Uso consciente da tecnologia | Preocupação com fontes confiáveis de informação | Quando a passagem expressa preocupação com o uso consciente da informação divulgada nas redes. | N/A |
| Atitudes Parentais na era da cidadania digital | Desconhecimento de como a tecnologia pode ser útil para o desenvolvimento infantil | N/A | Quando o pai ou responsável não sabe conceber como a tecnologia poderia auxiliar no desenvolvimento do seu filho autista. | N/A |
| Atitudes Parentais na era da cidadania digital | Descrença na tecnologia como ferramenta útil para o desenvolvimento infantil | N/A | Quando o pai ou responsável não acredita que a tecnologia pode auxiliar no desenvolvimento do seu filho autista. | N/A |
| Atitudes Parentais na era da cidadania digital | Otimistas quanto à tecnologia como ferramenta útil para o desenvolvimento infantil | N/A | Quando o pai ou responsável acredita que a tecnologia pode auxiliar no desenvolvimento do seu filho autista (juízo otimista geral; não exige menção à robótica). | N/A |
| Atitudes Parentais na era da cidadania digital | Otimistas quanto à tecnologia como ferramenta útil para o desenvolvimento infantil | Atitudes otimistas em relação à robótica como proposta de intervenção | Quando o pai ou responsável acredita que a tecnologia pode auxiliar no desenvolvimento do seu filho autista, por vezes expressando simpatia pela robótica. | N/A |
| Atitudes Parentais na era da cidadania digital | Opiniões mistas sobre a tecnologia como ferramenta útil para o desenvolvimento infantil | N/A | Quando o pai ou responsável têm opiniões ambíguas sobre a tecnologia como ferramenta pedagógica. | N/A |
| Atitudes Parentais na era da cidadania digital | Opiniões sobre como a tecnologia enfrenta barreira socioeconômica de acesso | N/A | Quando o pai ou responsável expressa opiniões de dificuldade de acesso por razões socioeconômicas ao que a tecnologia oferece. | N/A |

### 3.2 Aspectos clínicos da criança autista

Passagens que descrevem a criança autista por seus pais e responsáveis, a partir de diagnósticos clínicos e/ou de características comumente associadas ao autismo, mesmo sem expressão clara de diagnóstico médico. Diagnóstico e características de personalidade foram fundidos neste domínio porque não são o foco principal do projeto.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Aspectos clínicos da criança autista | Dificuldade com linguística | Atraso na fala | Passagens em que pais e responsáveis explicitamente mencionam atraso na fala da criança autista. | N/A |
| Aspectos clínicos da criança autista | Atraso (não especificado) | N/A | Passagens em que pais explicitamente mencionam atraso na criança autista, mas não explicitam o tipo de atraso. | N/A |
| Aspectos clínicos da criança autista | Dificuldade de atenção, concentração e foco | N/A | Passagens em que pais explicitamente mencionam dificuldade de atenção, concentração e foco pela criança autista. | N/A |
| Aspectos clínicos da criança autista | Dificuldade de contato visual | N/A | Passagens em que pais explicitamente mencionam dificuldade de contato visual pela criança autista. | N/A |
| Aspectos clínicos da criança autista | TDAH explicitamente mencionado | N/A | Passagens em que pais explicitamente mencionam que a criança tem diagnóstico de TDAH. | N/A |
| Aspectos clínicos da criança autista | Autismo explicitamente mencionado | N/A | Passagens em que pais explicitamente mencionam que a criança tem diagnóstico de autismo. | N/A |
| Aspectos clínicos da criança autista | Altas habilidades/superdotação explicitamente mencionado | N/A | Passagens em que pais explicitamente mencionam que a criança tem diagnóstico de altas habilidades/superdotação. | N/A |
| Aspectos clínicos da criança autista | Aprendizagem lenta | N/A | Passagens em que pais descrevem a criança como “lenta(o)” e/ou “não conseguir acompanhar”. | N/A |
| Aspectos clínicos da criança autista | Facilidade em aprendizagem | N/A | Passagens em que pais descrevem a criança como alguém que “aprende rápido” ou que tem “boas habilidades” ou apenas usa termos como “ele(a) tem facilidade”. | N/A |
| Aspectos clínicos da criança autista | Hiperfoco | N/A | Passagens em que pais mencionam algo de enorme interesse da criança e que são possíveis hiperfocos. Algumas passagens que não mencionam o termo “hiperfoco” mas sugerem hiperfoco também foram alocadas nesse caminho. | A entrevistadora usa o termo “hiperfoco” na pergunta, o termo não emerge da fala espontânea do entrevistado. Isso é uma espécie de priming e não configura evidência forte em análise qualitativa. Renomear para: • Tendência de hiperfoco |
| Aspectos clínicos da criança autista | Inteligência | Esperteza/destreza | Passagens em que pais descrevem seus filhos como “espertos” e/ou descrevem situações de destreza e boa compreensão das situações. É diferente de “inteligência” porque “destreza” está mais relacionada ao aspecto cognitivo de navegar bem a rotina e as relações, “inteligência” aloca passagens mais relacionadas a desempenho acadêmico. | Renomear para: • Inteligência: esperteza/destreza |
| Aspectos clínicos da criança autista | Inteligência | Bom desempenho acadêmico | Passagens em que os pais ressaltam o desempenho acadêmico de seus filhos, descrevendo o desempenho positivo deles em disciplinas específicas ou explicitamente mencionando o desempenho escolar positivo. | Renomear para • Inteligência: bom desempenho acadêmico |
| Aspectos clínicos da criança autista | Alta dependência dos pais | — | Passagens que expressam, sobretudo, dificuldade com autonomia em diferentes contextos. Os pais relatam a dificuldade de seus filhos de se autorregular emocionalmente fora da presença deles ou de executar tarefas simples sem a sua supervisão. | Renomear para • Dificuldade com autonomia |
| Aspectos clínicos da criança autista | Sentidos aguçados ( mudar para: inteligência) | Aprendizagem cinestésica | Passagens em que os pais descrevem seus filhos como indivíduos cinestésicos, que aprendem a partir de diferentes sentidos associados. | Renomear para • Inteligência: aprendizagem cinestésica |
| Aspectos clínicos da criança autista | Dificuldade com métodos repetitivos de aprendizagem | N/A | Passagens em que os pais mencionam a dificuldade de adaptação escolar de seus filhos, por não conseguirem se encaixar em métodos repetitivos e padronizados de aprendizagem. | N/A |
| Aspectos clínicos da criança autista | Dificuldade com abstração e necessidade de concretude | N/A | Passagens em que os pais descrevem a dificuldade de seus filhos com abstração, reportando que o conhecimento aplicado é melhor compreendido que o conhecimento abstrato. | N/A |
| Aspectos clínicos da criança autista | Sentimento de incapacidade | N/A | Passagens em que os pais descrevem um sentimento de incapacidade em realizar tarefas escolares. | N/A |
| Aspectos clínicos da criança autista | Habilidade manual (facilidade pronunciada de construir e/ou montar objetos) | N/A | Passagens em que os pais descrevem suas crianças com alta habilidade manual em construir ou consertar objetos. | N/A |
| Aspectos clínicos da criança autista | Dificuldade com linguística | Tendência à dislexia | Passagens em que pais e responsáveis descrevem algum sinal de dislexia (troca palavras e tem dificuldade para ler). Mas o termo "dislexia" não é usado para descrever o diagnóstico da criança. | N/A |
| Aspectos clínicos da criança autista | Dificuldade com linguística | Dificuldade grafomotora / aversão à escrita | Passagens em que pais e responsáveis descrevem aversão à escrita no processo de aprendizagem de seus filhos autistas (não gostam de escrever, se recusam a escrever ou não conseguem escrever por qualquer outro motivo). | — |
| Aspectos clínicos da criança autista | Autismo na família | N/A | Passagens em que explicitamente autismo na família é mencionado. | N/A |
| Aspectos clínicos da criança autista | Hiperatividade | N/A | Passagens em que os pais descrevem sinais de hiperatividade, como “não parar quieto” ou “não parar, nem quando dorme”. | Renomear para • Tendência à hiperatividade |
| Aspectos clínicos da criança autista | Lentidão para executar tarefas | N/A | Passagens que os pais descrevem situações em que seus filhos demoram para realizar alguma tarefa, por exemplo, copiar atividades do quadro. | N/A |
| Aspectos clínicos da criança autista | Estereotipia explicitamente mencionado | N/A | Passagens em que pais explicitamente mencionam estereotipia. | N/A |
| Aspectos clínicos da criança autista | Pensamento visual | N/A | Passagens em que os pais descrevem alguma situação em que a criança expressa capacidade de pensamento visual. | N/A |
| Aspectos clínicos da criança autista | Ansiedade | N/A | Passagens em que os pais descrevem sinais de ansiedade, como fala acelerada. | N/A |
| Aspectos clínicos da criança autista | Sensibilidade aguçada/muito emocionais | N/A | Passagens em que os pais descrevem seus filhos como indivíduos altamente emotivos/sensíveis, com dificuldade de esconder ou regular emoções. | N/A |
| Aspectos clínicos da criança autista | Orientado à rotinas/necessidade de rotinas | N/A | Passagens em que os pais descrevem seus filhos como indivíduos que precisam ou buscam seguir rotinas no dia a dia. | N/A |
| Aspectos clínicos da criança autista | Sono desregulado/dificuldade em dormir | N/A | Passagens em que os pais descrevem que seus filhos apresentam problemas para dormir. | N/A |
| Aspectos clínicos da criança autista | Autolesão | N/A | Passagens em que os pais descrevem comportamento de autolesão por seus filhos autistas. | N/A |
| Aspectos clínicos da criança autista | Frustração ao ser contrariado | N/A | Passagens que os pais descrevem seus filhos como pouco tolerantes à frustração. | N/A |

### 3.3 Socialização da criança autista

Passagens que descrevem a experiência de socialização da criança autista, principalmente em ambiente escolar.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Socialização da criança autista | Experiência positiva de socialização | N/A | Passagens em que pais relatam experiências positivas de socialização de seus filhos vivendo com autismo. | N/A |
| Socialização da criança autista | Experiência negativa de socialização | Mais facilidade para socializar fora da faixa etária (pessoas mais velhas) | Passagens em que pais relatam experiências negativas de seus filhos autistas, que possuem mais facilidade em socializar com pessoas fora da sua faixa etária (mais velhas). | N/A |
| Socialização da criança autista | Experiência negativa de socialização | Não acompanhar colegas de classe | Passagens em que pais descrevem dificuldades de socialização que envolvem a incapacidade de seus filhos de seguirem o grupo, seja em atividades escolares seja em não conseguir socializar de forma natural com os colegas de classe. | N/A |
| Socialização da criança autista | Experiência mista de socialização | N/A | Passagens em que pais descrevem uma experiência ambígua ou mista de socialização (quando, por exemplo, a criança melhora com os anos na interação com os colegas de classe). | N/A |

### 3.4 Dispositivos tecnológicos comuns

Passagens que informam qual dispositivo tecnológico é mais comum entre as crianças autistas.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Dispositivos tecnológicos comuns | Apenas tablet | N/A | Passagens em que pais explicitamente afirmam que seus filhos apenas têm acesso ao dispositivo “tablet”. | N/A |
| Dispositivos tecnológicos comuns | Apenas smartphone | N/A | Passagens em que pais explicitamente afirmam que seus filhos apenas têm acesso ao dispositivo “smartphone” (celular). | N/A |
| Dispositivos tecnológicos comuns | Apenas TV | N/A | Passagens em que pais explicitamente afirmam que seus filhos apenas têm acesso ao dispositivo “TV”. | N/A |
| Dispositivos tecnológicos comuns | Uso misto (celular, tablet, computador, TV) | N/A | Passagens em que pais descrevem o uso de múltiplos dispositivos digitais pelos seus filhos. Aplica-se quando pelo menos dois dispositivos digitais são mencionados pelos pais como de uso da criança, independentemente da frequência de cada um. | N/A |

### 3.5 Hábitos com tecnologia

Passagens que informam os principais hábitos com tecnologia detectados no corpus, tanto de crianças quanto de pais e responsáveis.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Hábitos com tecnologia | Muito tempo de tela | N/A | Passagens em que pais descrevem preocupação com o hábito de muito tempo de tela por seus filhos. | N/A |
| Hábitos com tecnologia | Hábitos não estruturados com tecnologia | N/A | Passagens que descrevem um uso mais esporádico de dispositivos tecnológicos ou de consumo de conteúdo virtual. | N/A |
| Hábitos com tecnologia | Obtenção e disseminação de informação (pais) | N/A | Passagens que descrevem o hábito com a tecnologia de pais e responsáveis, focado na obtenção e disseminação de informações sobre o autismo. | N/A |
| Hábitos com tecnologia | Uso comum | Entretenimento (assistir desenho) | Passagens em que pais descrevem o hábito de seus filhos com tecnologia, especificamente para entretenimento, como assistir desenho. | N/A |
| Hábitos com tecnologia | Uso comum | Jogos educacionais | Passagens em que pais descrevem o hábito de seus filhos com tecnologia, especificamente para consumo de jogos educacionais. | N/A |
| Hábitos com tecnologia | Uso comum | Conteúdo virtual (influenciadores, vídeos curtos e longos, rede social) | Passagens em que pais descrevem o hábito de seus filhos com tecnologia, especificamente para consumo de conteúdo virtual (vídeos no YouTube ou em mídias sociais, acompanhar influenciadores etc). | N/A |
| Hábitos com tecnologia | Uso comum | Jogos em geral | Passagens em que pais descrevem o hábito de seus filhos com tecnologia, especificamente para consumo de jogos em geral (quando os jogos não são especificados, como no caso de jogos educacionais). | N/A |
| Hábitos com tecnologia | Uso comum | Suporte educacional/aulas | Passagens em que pais descrevem o hábito de seus filhos com tecnologia, especificamente o uso de tecnologia para suporte educacional, como assistir aulas ou conteúdo educativo, geralmente em formato de vídeo. | N/A |

### 3.6 O papel da tecnologia no desenvolvimento de crianças autistas

Passagens que informam o papel da tecnologia no desenvolvimento de crianças autistas, segundo pais e responsáveis.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| O papel da tecnologia no desenvolvimento de crianças autistas | Formas alternativas de aprendizagem | Estímulo multissensorial | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita uma experiência de aprendizagem multissensorial ao seus filhos. | N/A |
| O papel da tecnologia no desenvolvimento de crianças autistas | Formas alternativas de aprendizagem | Vídeos | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita a aprendizagem por meio de vídeos. | N/A |
| O papel da tecnologia no desenvolvimento de crianças autistas | Suporte à saúde mental | Ferramenta de distração/relaxamento | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita suporte à saúde mental possibilitando distração, relaxamento e o cultivo de hobbies. | N/A |
| O papel da tecnologia no desenvolvimento de crianças autistas | O digital como ferramenta de estímulo à criatividade | N/A | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita a expansão da criatividade infantil. As passagens aqui podem expressar exemplos descritos por pais e responsáveis de conexões conceituais feitas a partir da exposição ao conteúdo digital ou à capacidade de criar mediada pela tecnologia. | N/A |
| O papel da tecnologia no desenvolvimento de crianças autistas | Ferramenta de revelação de competências anteriormente não observáveis | N/A | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita a expansão e a revelação de habilidades que antes eram não observáveis ou fontes de dificuldades cognitivas. Exemplos comuns é o uso da tecnologia para estímulos de comunicação em crianças com atraso na fala e dificuldades com linguística. | N/A |
| O papel da tecnologia no desenvolvimento de crianças autistas | Engajamento produtivo com tarefas adjacentes | N/A | Passagens em que pais descrevem a tecnologia como uma ferramenta que possibilita o engajamento produtivo com atividades adjacentes, isto é, quando a tecnologia é utilizada junto a outras tarefas no offline, como escutar música ou ver um vídeo enquanto pinta, desenha ou faz artesanato, auxiliando no foco. | N/A |

### 3.7 Lacunas no suporte institucionalizado

Passagens que informam as principais lacunas que pais e responsáveis encontram na rede de suporte institucionalizado (saúde e educação públicas) disponível a crianças autistas e portadoras de necessidades especiais.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Lacunas no suporte institucionalizado | Morosidade no diagnóstico | N/A | Quando pais e responsáveis relatam morosidade no processo de diagnóstico (“pular” de profissional a profissional para ter um laudo final) ou quando a passagem expressa claramente um diagnóstico tardio. | — |
| Lacunas no suporte institucionalizado | Morosidade na provisão do serviço | N/A | Quando pais e responsáveis relatam a experiência de enfrentar morosidade na provisão de serviços, expressa, geralmente, por longo tempo de espera em filas na rede pública para acessar um serviço específico. | Checar aqui se as passagens se referem a apenas serviço de saúde ou se também é sobre serviços de educação. |
| Lacunas no suporte institucionalizado | Qualidade do suporte condicionado ao grau de autismo | N/A | Quando pais e responsáveis relatam que a qualidade do suporte é condicionada ao grau de autismo do seu filho (comum na situação em que a família tem duas crianças e uma acaba por receber suporte enquanto a outra fica em espera). | — |
| Lacunas no suporte institucionalizado | Falta de suporte a pais de crianças autistas | N/A | Passagens que expressam o completo desamparo dos pais em navegar a realidade de ter uma criança atípica. Expressões comuns são se sentir de “olhos fechados”, sem saber identificar os sinais de neurodivergência da criança. | — |
| Lacunas no suporte institucionalizado | Qualidade questionável de suporte na rede pública de educação | N/A | Pais e cuidadores relatam experiências de qualidade questionável com o serviço público ou receio de usar a rede pública com incerteza sobre a sua capacidade de atender às necessidades de suas crianças. Muitas vezes essa falta de qualidade é relatada pela falta generalizada de profissionais de educação no serviço público. | Checar aqui se as passagens são realmente só sobre a educação. |
| Lacunas no suporte institucionalizado | Falta de preparo profissional (professores e educadores) | — | Pais e responsáveis relatam experiências com professores não capacitados para lidar com crianças autistas. | — |

### 3.8 Estilos de tratamento da criança autista

Passagens que informam os principais estilos de tratamento que pais e responsáveis descrevem e demandam para uma assistência de qualidade.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição | Limitação |
| --- | --- | --- | --- | --- |
| Estilos de tratamento da criança autista | Tratamento multidisciplinar | — | Pais e responsáveis relatam a necessidade de tratamento multidisciplinar, envolvendo mais de um tipo de especialidade médica para atender às necessidades da sua criança. | — |

### 3.9 Maternidade com criança autista

Passagens que informam os principais sentimentos de mães que vivem a maternidade atípica. O domínio permanece no corpus com baixa prevalência; a decisão de reportá-lo nos resultados depende da relevância relativa (frequência/profundidade) no material, não só do escopo original.

| Domínio | Sub-domínio | Definição | Limitação |
| --- | --- | --- | --- |
| Maternidade com criança autista | Incerteza | Mães que relatam muita incerteza na jornada de maternar crianças autistas, principalmente pela falta de suporte em como lidar com necessidades especiais da criança. | Esse domínio não é reportado por fuga ao tema principal do projeto. |
| Maternidade com criança autista | Pressão e julgamento social | Mães que relatam pressão e julgamento social ao maternar crianças autistas. | Esse domínio não é reportado por fuga ao tema principal do projeto. |
| Maternidade com crianças autistas | Solidão | Mães que relatam solidão na maternidade que é ampliada pelos cuidados especiais que uma criança autista demanda. | Esse domínio não é reportado por fuga ao tema principal do projeto. |
| Maternidade com crianças autistas | Culpa | Mães que relatam sentir culpa na pela dificuldade de lidar com as demandas especiais de uma criança autista. | Esse domínio não é reportado por fuga ao tema principal do projeto. |

### 3.10 Parentalidade na era da cidadania digital

Passagens que informam a experiência da parentalidade de crianças autistas na era digital.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição |
| --- | --- | --- | --- |
| Parentalidade na era da cidadania digital | Dificuldade em exercer autoridade | Tensão na relação pais e filhos | As passagens aqui se referem a situações em que a tecnologia dificultou o exercício de autoridade pelos pais porque é um objeto de tensão entre pais e filhos que acarreta conflitos. |
| Parentalidade na era da cidadania digital | Dificuldade em exercer autoridade | Desorientação/sobrecarga | As passagens aqui se referem ao sentimento de sobrecarga e desorientação que pais sentem no exercício da sua autoridade e como a tecnologia pode dificultar esse exercício, ampliando o sentimento de desorientação e sobrecarga. |
| Parentalidade na era da cidadania digital | Dificuldade de encontrar formas alternativas para entreter | N/A | Passagens que expressam a dificuldade dos pais em encontrar formas alternativas à tecnologia para oferecer entretenimento aos seus filhos no dia a dia. |
| Parentalidade na era da cidadania digital | Estratégias de imposição de limites | Busca de formas alternativas para entreter | Passagens que relatam exemplos dados pelos pais de formas alternativas de entretenimento como forma de reduzir a exposição da criança à tecnologia. |
| Parentalidade na era da cidadania digital | Estratégias de imposição de limites | Diálogo | Passagens que relatam como pais e responsáveis dialogam com seus filhos para a impor limites ao uso da tecnologia. |
| Parentalidade na era da cidadania digital | Estratégias de imposição de limites | Estabelecer e reforçar rotina | Passagens que relatam como pais e responsáveis se utilizam do reforço de mecanismos de rotina para controlar o uso da tecnologia (impor horários específicos para o uso; delimitar momentos no dia que não se pode usar celular, TV ou tablet, etc.) |
| Parentalidade na era da cidadania digital | Mediação no uso da tecnologia | Substituição de dispositivo/mídia | Passagens que relatam como pais e responsáveis fazem a mediação do uso da tecnologia por meio da substituição de dispositivos (como, por exemplo, se há muito tempo de tela jogando, eles decidem mudar a atividade para um filme na TV). |
| Parentalidade na era da cidadania digital | Mediação no uso da tecnologia | Co-uso | Passagens que relatam como pais e responsáveis fazem a mediação do uso da tecnologia por meio do co-uso, isto é, quando eles transformam o uso da tecnologia em um momento em família, por exemplo, deitando com a criança para assistir filme/desenho. |
| Parentalidade na era da cidadania digital | Mediação no uso da tecnologia | Curadoria de conteúdo | Passagens que relatam como pais e responsáveis fazem a mediação do uso da tecnologia por meio de curadoria de conteúdo, isto é, estabelecendo mecanismos de controle para o tipo de conteúdo que a criança pode acessar. |
| Parentalidade na era da cidadania digital | Necessidade de controle/regulação | — | Passagens que relatam a necessidade de controle e regulação de pais e responsáveis no uso da tecnologia por seus filhos. |
| Parentalidade na era da cidadania digital | Necessidade de intervenção para pais | Falta de suporte em como educar na era digital | Passagens que expressam uma possível demanda parental por maior suporte institucional em como educar na era digital. Tais passagens podem sugerir ou inspirar intervenções. |
| Parentalidade na era da cidadania digital | Necessidade de intervenção para pais | Falta de entendimento ou compreensão de como a criança interage com o digital | Passagens que expressam uma possível demanda parental por maior suporte institucional em como compreender e monitorar como seus filhos interagem e com o que interagem em ambientes digitais. Tais passagens podem sugerir ou inspirar intervenções. |
| Parentalidade na era da cidadania digital | Uso de aplicativos para monitoramento | N/A | Passagens em que pais explicitamente dizem fazer uso de aplicativos para monitoramento online de seus filhos. |
| Parentalidade na era da cidadania digital | Tecnologia como escape temporário das dificuldades parentais | N/A | Passagens em que pais explicitamente expressam usar a tecnologia como válvula de escape aos estresses do dia a dia no cuidado infantil. |
| Parentalidade na era da cidadania digital | Dificuldade em impor limites | N/A | Passagens que expressam a dificuldade que pais e responsáveis sentem em impor limites à criança para o uso de tecnologia. |

### 3.11 Valor da tecnologia

Passagens que informam o valor que pais e responsáveis enxergam na tecnologia a partir da experiência de parentalidade atípica. Este domínio não possui subdomínio detalhado.

| Domínio | Sub-domínio | Definição |
| --- | --- | --- |
| Valor da tecnologia | Conscientização sobre o autismo | Passagens em que pais e responsáveis refletem sobre como a tecnologia colabora para a conscientização do autismo em maior escala. |
| Valor da tecnologia | Instrumento de inclusão social | Passagens em que pais e responsáveis refletem sobre como a tecnologia colabora para a inclusão social de pessoas autistas. |
| Valor da tecnologia | Desenvolvimento de novas habilidades | Passagens em que pais e responsáveis refletem sobre como a tecnologia colabora para o desenvolvimento de novas habilidades em crianças autistas. |
| Valor da tecnologia | Jogos educacionais como benefício percebido | Passagens em que pais e responsáveis refletem sobre a tecnologia como uma facilitadora educacional via jogos educacionais para crianças autistas. |
| Valor da tecnologia | Facilidades na rotina | Passagens em que pais e responsáveis refletem sobre como a tecnologia pode facilitar tarefas cotidianas com crianças autistas. |
| Valor da tecnologia | Acesso facilitado a entretenimento | Passagens em que pais e responsáveis refletem sobre como a tecnologia promove acesso fácil a atividades de lazer para crianças autistas. |
| Valor da tecnologia | Busca de comunidade (maternidade com criança atípica) | Passagens em que pais e responsáveis refletem sobre como a tecnologia promove o acesso à comunidade de pessoas que também enfrentam os desafios da parentalidade atípica. |

### 3.12 Bem-Estar Infantil na era da cidadania digital

Passagens que informam como pais e responsáveis descrevem o bem-estar de seus filhos neurodivergentes ao se relacionar com a tecnologia no dia a dia.

| Domínio | Sub-domínio | Sub-domínio detalhado | Definição |
| --- | --- | --- | --- |
| Bem-Estar Infantil na era da cidadania digital | Efeitos negativos da tecnologia no bem-estar infantil | Isolamento/alheamento | Passagens em que pais e responsáveis descrevem uma espécie de estado de isolamento e abstração induzido pela tecnologia, mas que não é positivo, porque cria uma espécie de alienação. |
| Bem-Estar Infantil na era da cidadania digital | Efeitos negativos da tecnologia no bem-estar infantil | Comportamento alterado | Passagens em que pais e responsáveis mencionam ou descrevem mudanças comportamentais bruscas ou o estado de ânimo de estar "alterado" (xingar, ficar mais agressivo ou superestimulado) ou mudar de personalidade quando em relação com a tecnologia. |
| Bem-Estar Infantil na era da cidadania digital | Efeitos negativos da tecnologia no bem-estar infantil | Dessensibilização a conteúdo violento/inapropriado | Passagens em que pais e responsáveis explicitam a falta de compreensão da criança sobre a gravidade do conteúdo consumido (a criança ri ou repete o comportamento problemático). |
| Bem-Estar Infantil na era da cidadania digital | Efeitos negativos da tecnologia no bem-estar infantil | Medo/ansiedade | Passagens em que pais e responsáveis descrevem situações em que o digital despertou medo e ansiedade nos seus filhos. |

### 3.13 Propostas de intervenção com a Robótica

Passagens em que pais e responsáveis sugerem como a robótica pode ser uma intervenção interessante para seus filhos com autismo. Este domínio não possui subdomínio detalhado.

| Domínio | Sub-domínio | Definição |
| --- | --- | --- |
| Propostas de intervenção com a Robótica | A robótica como ferramenta para entreter no dia a dia | Passagens em que pais e responsáveis descrevem a robótica como uma possível ferramenta efetiva para entretenimento e lazer, com alto potencial de engajar crianças autistas. |
| Propostas de intervenção com a Robótica | A robótica como ferramenta de socialização e detecção de problemas socioemocionais | Passagens em que pais e responsáveis descrevem a robótica como uma possível ferramenta de auxílio em socialização e educação socioemocional para crianças autistas. |

---

## 4. Limitações

Texto alinhado à seção **Limitações** de `Metodologia/resultados.docx`, com os dois parágrafos de conclusão que o próprio documento reitera como restrições de evidência.

**Replicabilidade.** Esse projeto tem baixa capacidade de ser replicado dado que o conjunto de domínios e a alocação de passagens são de criação particular do pesquisador. Nesse sentido, outra pessoa interagindo com os dados brutos poderia chegar a um resultado completamente diferente. Isso é inato da metodologia escolhida e é um problema comum em análise qualitativa. A única forma de reduzir o nível de subjetividade da análise é por meio de revisão por pares, o que não foi possível de ser feito de forma ideal dentro do prazo do projeto.

**Baixa validação externa.** Os dados analisados dizem respeito apenas ao que acontece na amostra de entrevistas disponível, que é pequena (9 entrevistas no total). Todos os insights aqui não podem ser generalizados para a população e para o contexto do Tocantins.

**Evidência insuficiente sobre robótica em sala de aula.** Não há evidências suficientes nem a favor nem contrária ao uso da robótica em sala de aula. Há algum otimismo a respeito da robótica como proposta de intervenção, mas tais quotes não são representativos da amostra de passagens únicas, representando apenas 1% dos tópicos debatidos.

**Evidência insuficiente sobre cidadania digital.** Não há evidências suficientes para concluir algo substancial sobre a opinião dos pais a respeito da cidadania digital infantil. Algumas perguntas feitas aos entrevistados foram alvo de priming e viés de desejabilidade social, impedindo elaboração espontânea de opiniões. Isso afetou, principalmente, a pergunta sobre cidadania digital infantil.

Limitações adicionais já registradas no codebook (`metodologia_final.docx`) e que devem ser lidas junto com as tabelas da seção 3:

- Duas passagens de *Otimismo perante à cidadania digital* foram eliminadas do corpus por viés de desejabilidade social e priming. As que restaram exigem elaboração espontânea; mesmo assim, o subdomínio é evidência fraca.
- *Hiperfoco* / *Tendência de hiperfoco* sofre priming da entrevistadora (o termo entra pela pergunta). Observações com elaboração espontânea foram mantidas.
- O domínio *Maternidade com criança autista* tem baixa prevalência; foi mantido no corpus porque aparece com alguma densidade em entrevistas específicas, ainda que periférico ao foco principal.

---

## 5. Prompts utilizados nas sessões interativas

Prompt de abertura da sessão de revisão por pares (alocação + fusão). Copiado na íntegra:

```
Você é meu assistente de pesquisa qualitativa. Faça uma revisão da alocação de categorias para mim. Vá novamente em dataset_processado.xlsx, analise as passagens e como elas estão alocadas e compare com o documento "Metodologia.docx". Me dê um relatório NO CHAT (não crie arquivos novos) com o seguinte formato:
• Id da passagem:
• Passagem escrita
• Caminho atual (domínio > subdomínio > subdomínio detalhado)
• Caminho sugerido

Gostaria também que você avaliasse os transcripts em transcripts_crus e me sugerisse possíveis passagens que poderiam se fundir para melhorar a interpretação e o entendimento da passagem. Me dê um relatório:
• Id das passagens a serem fundidas
• Caminho atual de cada ID
• Novo caminho com a fundição
```

---

## 6. Estado final da análise

A rodada de revisão, fusão, alinhamento codebook–corpus e a análise descritiva foram concluídas (agosto/2026).

### 6.1 Corpus final

| Indicador | Valor |
| --- | ---: |
| Passagens únicas | 167 |
| Codificações (linhas no `formato_longo`) | 300 |
| Média de codificações por passagem | 1,80 |
| Transcrições | 9 |
| Domínios | 13 |
| Subdomínios | 81 |
| Subdomínios detalhados preenchidos | 37 |

Prevalência no corpus (passagens únicas / 167), principais domínios:

| Domínio | Passagens | Prevalência |
| --- | ---: | ---: |
| Atitudes Parentais na era da cidadania digital | 50 | 29,9% |
| Parentalidade na era da cidadania digital | 38 | 22,8% |
| Aspectos clínicos da criança autista | 33 | 19,8% |
| Hábitos com tecnologia | 29 | 17,4% |
| Lacunas no suporte institucionalizado | 21 | 12,6% |
| O papel da tecnologia no desenvolvimento de crianças autistas | 12 | 7,2% |
| Bem-Estar Infantil na era da cidadania digital | 9 | 5,4% |
| Valor da tecnologia | 9 | 5,4% |
| Demais domínios | ≤ 8 cada | ≤ 4,8% |

As percentagens **não somam 100%**: multi-alocação é parte do desenho.

### 6.2 Como ler as métricas

| Tipo | Denominador | Onde no notebook |
| --- | --- | --- |
| Prevalência no corpus | 167 passagens | `qual1` / `plotar_categorias(..., logica="coluna_simples", prevalencia=True)` |
| Prevalência no domínio | passagens do domínio | `logica="hierarquia"` |
| Prevalência no caminho | passagens do domínio › subdomínio | `logica="subdominio_detalhado"` |
| Inventário de caminhos | n absoluto por caminho completo | `inventario_caminhos()` → `OUTPUT/inventario_caminhos.html` |

Com `prevalencia=True`, os rótulos das barras exibem `% (n)`.

### 6.3 Figuras e funções de suporte

| Função | Saída típica |
| --- | --- |
| `descreve_dataset` | Tabela descritiva + HTML |
| `diagrama_descritivo` | Árvore 1 vs >1 codificação + uso do detalhado opcional |
| `matriz_coocorrencia_dominios` | Heatmap de overlap entre domínios |
| `heatmap_coocorrencia_subdominios` | Heatmaps intradomínio (só domínios com overlap) |
| `inventario_caminhos` | Apêndice: n por caminho |
| `plotar_categorias` | Barras de prevalência / contagem |

### 6.4 Remoções (`aba removidas`, n = 27)

| Grupo | n | Significado |
| --- | ---: | --- |
| Fusão de passagens vizinhas | 16 | Conteúdo absorvido noutro ID (não é exclusão substantiva) |
| Qualidade da evidência / viés de entrevista | 3 | Assentimento vazio / priming / desejabilidade social |
| Transcrição / dado inviável | 4 | Só fala da entrevistadora, transcript ilegível ou dado implausível |
| Fora de escopo **e** sem relevância analítica no corpus | 4 | Não basta ser periférico: ausência de frequência/profundidade (diferente de temas periféricos mantidos, como *Maternidade…*, quando têm densidade) |

### 6.6 Como reproduzir

```bash
# na raiz do repositório, com o .venv ativo
jupyter notebook analise_qualitativa.ipynb
```

O notebook lê `dados_qual/processamento/dataset_processado.xlsx` (aba `formato_longo`) e grava figuras/HTML em `OUTPUT/`.
