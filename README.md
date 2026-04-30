# Fatec ED Playlist

Reprodutor de Músicas

Sistema de playlist em Python com lista encadeada simples para a biblioteca e filas FIFO encadeadas para os humores e o historico de reproducoes.

## Instalação

1. Garanta que o Python 3.12 ou superior esteja instalado.
2. Clone o repositório ou abra a pasta do projeto no editor.
3. Se quiser usar um ambiente isolado, crie e ative uma virtualenv:

```bash
python -m venv .venv

source .venv/bin/activate
```

## Execucao

```bash
python app.py
```

Nesta fase o projeto roda sem dependencias externas obrigatorias. O arquivo `app.py` contem a biblioteca em lista encadeada, as filas de humor, o historico e o menu completo do sistema.

Para uma demonstracao automatica dos principais fluxos, use:

```bash
python app.py --demo
```

## Funcionalidades disponiveis nesta fase

- Adicionar musica na biblioteca.
- Remover musica por ID.
- Buscar musica por ID.
- Buscar musica por titulo.
- Listar todas as musicas cadastradas.
- Montar e exibir filas por humor com base no BPM.
- Reproduzir a proxima musica de uma fila escolhida.
- Registrar historico das reproducoes.
- Exibir estatisticas gerais da biblioteca, filas e historico.

## Menu principal

1. Adicionar musica.
2. Remover musica por ID.
3. Buscar musica por ID.
4. Buscar musica por titulo.
5. Listar biblioteca.
6. Montar filas de humor.
7. Exibir filas de humor.
8. Reproduzir proxima musica.
9. Exibir historico.
10. Mostrar estatisticas.
0. Sair.

## Prazos

- Entrega link do projeto: próximas 24 horas na issue do repositório da disciplina Estrutura de Dados (https://github.com/orlandosaraivajr/FATEC_1SEM26_ED/issues/3).
-  Desenvolvimento Projeto: Durante a semana, entregas incrementais tendo como prazo final o início da aula do dia 30/04/2026.
- Apresentação: 14/04/2026 (negociado em sala de aula).
