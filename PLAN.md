# Plano do Projeto - Sistema de Playlist

## Objetivo

Implementar o backend de um sistema de playlist em Python usando estruturas de dados proprias: lista encadeada simples para a biblioteca e filas FIFO encadeadas para reproducoes e historico.

## Requisitos principais

- Criar a classe `Musica` com `id`, `titulo`, `artista`, `genero` e `bpm`.
- Criar `NodoLista` e `Biblioteca` para armazenar musicas em lista encadeada simples.
- Criar `NodoFila` e `Fila` para implementar filas FIFO sem usar `list`, `deque` ou estruturas prontas equivalentes.
- Permitir adicionar, remover, buscar e listar musicas na biblioteca.
- Montar filas de humor com base no BPM:
  - Relaxar: ate 80
  - Focar: 81 a 120
  - Animar: 121 a 160
  - Treinar: acima de 160
- Reproduzir a proxima musica de uma fila escolhida e enviar a musica para o historico.
- Exibir o conteudo de qualquer fila sem remover elementos.
- Mostrar historico de reproducoes e estatisticas gerais.
- Tratar entradas invalidas e manter o `id` sequencial sem reutilizacao.

## Ordem de implementacao

1. Estruturar as classes base (`Musica`, `NodoLista`, `NodoFila`, `Biblioteca`, `Fila`).
2. Implementar operacoes basicas da biblioteca:
   - insercao no final
   - busca por `id` e por `titulo`
   - remocao por `id`
   - listagem completa
3. Implementar as filas de humor e a logica de classificacao por BPM.
4. Implementar o historico como uma fila separada.
5. Implementar o menu principal com todas as opcoes do enunciado.
6. Adicionar validacoes de entrada e mensagens de erro claras.
7. Fechar com estatisticas e testes manuais dos principais fluxos.

## Estrutura sugerida do codigo

- `app.py`: ponto de entrada do menu e orquestracao das operacoes.
- Classes de dominio e estruturas: podem ficar no proprio `app.py` no inicio, ou ser separadas depois se o projeto crescer.

## Casos de teste essenciais

- Adicionar musicas com BPM valido e invalido.
- Remover musica existente e inexistente.
- Buscar por `id` e por `titulo`.
- Listar a biblioteca apos multiplas insercoes.
- Montar as filas de humor mais de uma vez e confirmar limpeza/reconstrucao.
- Reproduzir quando a fila estiver vazia e quando tiver itens.
- Conferir se o historico recebe a musica reproduzida.
- Validar estatisticas da biblioteca, das filas e do historico.

## Criterios de conclusao

- Nao usar `list`, `deque` ou outra estrutura pronta para representar biblioteca, filas ou historico.
- Manter a separacao entre biblioteca, filas de humor e historico.
- Atender todas as opcoes do menu descritas no PDF.
- Garantir comportamento previsivel para entradas invalidas.

## Entrega incremental

- Primeira entrega: publicar o link do repositório na issue da disciplina e garantir que o projeto inicial esteja acessivel.
- Segundo marco: entregar as estruturas de dados base com insercao, busca, remocao e listagem da biblioteca funcionando.
- Terceiro marco: adicionar a montagem das filas de humor, o historico de reproducoes e a reproducao da proxima musica.
- Quarto marco: fechar o menu principal completo, validacoes de entrada, estatisticas e mensagens de erro consistentes.
- Entrega final: revisar o comportamento geral, testar todos os fluxos do menu e confirmar que o codigo demonstra dominio da solucao.

## Detalhamento das entregas

- Entrega 1: versionamento inicial do projeto, com estrutura minima, README atualizado e acesso ao repositório compartilhado.
- Entrega 2: implementacao da biblioteca em lista encadeada simples, sem estruturas prontas do Python para armazenamento.
- Entrega 3: implementacao das filas FIFO por humor e da fila separada para historico.
- Entrega 4: integracao do menu, estatisticas, tratamento de erros e refinamento da experiencia de uso no terminal.
