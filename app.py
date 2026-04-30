from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, Optional

"""Sistema de playlist em Python com lista encadeada e filas FIFO.

O objetivo deste arquivo e concentrar a base funcional do projeto em um unico
ponto de entrada, deixando o comportamento claro para quem for continuar as
entregas seguintes:

- `Musica` modela cada faixa da biblioteca.
- `Biblioteca` guarda as musicas em uma lista encadeada simples.
- `Fila` implementa uma fila FIFO encadeada, reutilizavel nas proximas etapas.
- `executar_menu_basico` oferece uma interface de terminal para testar a base.

As entregas futuras vao reutilizar estas estruturas para adicionar filas de
humor, historico de reproducoes e o menu completo do sistema.
"""

@dataclass(slots=True)
class Musica:
	"""Representa uma musica cadastrada na biblioteca."""

	id: int
	titulo: str
	artista: str
	genero: str
	bpm: int

	def __str__(self) -> str:
		# O texto padronizado ajuda na exibicao do terminal e nos testes.
		return f"[{self.id}] {self.titulo} - {self.artista} ({self.genero}, {self.bpm} BPM)"


class NodoLista:
	"""Nodo da lista encadeada simples usada pela biblioteca."""

	__slots__ = ("musica", "proximo")

	def __init__(self, musica: Musica, proximo: Optional[NodoLista] = None) -> None:
		self.musica = musica
		self.proximo = proximo

class Biblioteca:
	"""Lista encadeada simples com insercao, busca, remocao e iteracao."""

	def __init__(self) -> None:
		# Guardar inicio e fim evita percorrer a lista inteira ao inserir no final.
		self._primeiro: Optional[NodoLista] = None
		self._ultimo: Optional[NodoLista] = None
		self._tamanho = 0
		# O id cresce de forma sequencial e nunca e reutilizado apos remocoes.
		self._proximo_id = 1

	@property
	def tamanho(self) -> int:
		"""Retorna quantas musicas existem na biblioteca."""
		return self._tamanho

	def adicionar_musica(self, titulo: str, artista: str, genero: str, bpm: int) -> Musica:
		"""Valida os dados e insere uma nova musica no final da lista."""
		if not titulo.strip():
			raise ValueError("Titulo nao pode ser vazio.")
		if not artista.strip():
			raise ValueError("Artista nao pode ser vazio.")
		if not genero.strip():
			raise ValueError("Genero nao pode ser vazio.")
		if not isinstance(bpm, int):
			raise ValueError("BPM deve ser um numero inteiro.")
		if bpm <= 0:
			raise ValueError("BPM deve ser maior que zero.")

		musica = Musica(
			id=self._proximo_id,
			titulo=titulo.strip(),
			artista=artista.strip(),
			genero=genero.strip(),
			bpm=bpm,
		)
		nodo = NodoLista(musica)

		# Se a lista estiver vazia, o novo nodo vira o primeiro e o ultimo.
		if self._primeiro is None:
			self._primeiro = nodo
			self._ultimo = nodo
		else:
			assert self._ultimo is not None
			self._ultimo.proximo = nodo
			self._ultimo = nodo

		self._tamanho += 1
		self._proximo_id += 1
		return musica

	def buscar_por_id(self, musica_id: int) -> Optional[Musica]:
		"""Percorre a lista ate encontrar a musica com o id informado."""
		nodo_atual = self._primeiro
		while nodo_atual is not None:
			if nodo_atual.musica.id == musica_id:
				return nodo_atual.musica
			nodo_atual = nodo_atual.proximo
		return None

	def buscar_por_titulo(self, titulo: str) -> Optional[Musica]:
		"""Busca case-insensitive por titulo para facilitar o uso no terminal."""
		titulo_normalizado = titulo.strip().casefold()
		nodo_atual = self._primeiro
		while nodo_atual is not None:
			if nodo_atual.musica.titulo.casefold() == titulo_normalizado:
				return nodo_atual.musica
			nodo_atual = nodo_atual.proximo
		return None

	def remover_por_id(self, musica_id: int) -> Optional[Musica]:
		"""Remove a musica correspondente ao id informado e ajusta os ponteiros."""
		nodo_anterior: Optional[NodoLista] = None
		nodo_atual = self._primeiro

		while nodo_atual is not None:
			if nodo_atual.musica.id == musica_id:
				if nodo_anterior is None:
					self._primeiro = nodo_atual.proximo
				else:
					nodo_anterior.proximo = nodo_atual.proximo

				if nodo_atual is self._ultimo:
					self._ultimo = nodo_anterior

				self._tamanho -= 1
				return nodo_atual.musica

			nodo_anterior = nodo_atual
			nodo_atual = nodo_atual.proximo

		return None

	def iterar(self) -> Iterator[Musica]:
		"""Gera as musicas da biblioteca sem converter a estrutura para lista."""
		nodo_atual = self._primeiro
		while nodo_atual is not None:
			yield nodo_atual.musica
			nodo_atual = nodo_atual.proximo

class NodoFila:
	"""Nodo da fila encadeada usada pela estrutura FIFO."""

	__slots__ = ("musica", "proximo")

	def __init__(self, musica: Musica, proximo: Optional[NodoFila] = None) -> None:
		self.musica = musica
		self.proximo = proximo

class Fila:
	"""Fila FIFO com nos encadeados e operacoes basicas de enfileirar/desenfileirar."""

	def __init__(self) -> None:
		# Os dois extremos permitem operar a fila em tempo constante.
		self._frente: Optional[NodoFila] = None
		self._tras: Optional[NodoFila] = None
		self._tamanho = 0

	@property
	def tamanho(self) -> int:
		"""Retorna o numero de elementos presentes na fila."""
		return self._tamanho

	def esta_vazia(self) -> bool:
		"""Indica se a fila nao tem nenhum elemento."""
		return self._tamanho == 0

	def enfileirar(self, musica: Musica) -> None:
		"""Insere uma musica no final da fila."""
		nodo = NodoFila(musica)
		if self._frente is None:
			self._frente = nodo
			self._tras = nodo
		else:
			assert self._tras is not None
			self._tras.proximo = nodo
			self._tras = nodo
		self._tamanho += 1

	def desenfileirar(self) -> Optional[Musica]:
		"""Remove e devolve a musica que esta na frente da fila."""
		if self._frente is None:
			return None

		nodo = self._frente
		self._frente = nodo.proximo
		if self._frente is None:
			self._tras = None
		self._tamanho -= 1
		return nodo.musica

	def espiar(self) -> Optional[Musica]:
		"""Consulta a primeira musica sem removela da fila."""
		if self._frente is None:
			return None
		return self._frente.musica

	def limpar(self) -> None:
		"""Esvazia a fila inteira."""
		self._frente = None
		self._tras = None
		self._tamanho = 0

	def iterar(self) -> Iterator[Musica]:
		"""Percorre a fila sem alterar sua ordem ou seu conteudo."""
		nodo_atual = self._frente
		while nodo_atual is not None:
			yield nodo_atual.musica
			nodo_atual = nodo_atual.proximo

def _ler_texto(rotulo: str) -> str:
	"""Ler um texto nao vazio e padronizar a validacao de entrada."""
	valor = input(rotulo).strip()
	if not valor:
		raise ValueError("Entrada vazia.")
	return valor

def _ler_inteiro(rotulo: str) -> int:
	"""Ler texto do usuario e converter para inteiro."""
	valor_texto = _ler_texto(rotulo)
	return int(valor_texto)

def _exibir_musica(musica: Optional[Musica]) -> None:
	"""Mostrar uma musica ou informar que a busca nao encontrou nada."""
	if musica is None:
		print("Nenhuma musica encontrada.")
		return
	print(musica)

def executar_menu_basico() -> None:
	"""Menu textual usado para testar a base da biblioteca nesta etapa.

	Este menu nao inclui ainda as entregas de filas de humor, historico e
	estatisticas; ele existe para validar as operacoes essenciais da biblioteca.
	"""
	biblioteca = Biblioteca()

	while True:
		# O menu eh reimpresso a cada iteracao para manter a interacao simples.
		print("\n=== Reprodutor de musicas ===")
		print("1 - Adicionar musica")
		print("2 - Remover musica por ID")
		print("3 - Buscar musica por ID")
		print("4 - Buscar musica por titulo")
		print("5 - Listar biblioteca")
		print("0 - Sair")

		try:
			opcao = _ler_texto("Opcao: ")
		except EOFError:
			print("\nEntrada encerrada.")
			return
		except ValueError:
			print("Opcao invalida.")
			continue

		if opcao == "1":
			try:
				# Cadastro completo de uma musica na biblioteca.
				titulo = _ler_texto("Titulo: ")
				artista = _ler_texto("Artista: ")
				genero = _ler_texto("Genero: ")
				bpm = _ler_inteiro("BPM: ")
				musica = biblioteca.adicionar_musica(titulo, artista, genero, bpm)
				print("Musica adicionada:")
				print(musica)
			except ValueError as erro:
				print(f"Erro: {erro}")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "2":
			try:
				# Remocao direta por id para exercitar a exclusao da lista.
				musica_id = _ler_inteiro("ID: ")
				musica = biblioteca.remover_por_id(musica_id)
				if musica is None:
					print("Musica nao encontrada.")
				else:
					print("Musica removida:")
					print(musica)
			except ValueError:
				print("ID invalido.")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "3":
			try:
				# Busca por identificador para validar acesso direto ao nodo.
				musica_id = _ler_inteiro("ID: ")
				_exibir_musica(biblioteca.buscar_por_id(musica_id))
			except ValueError:
				print("ID invalido.")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "4":
			try:
				# Busca textual, normalizada para nao depender de maiusculas/minusculas.
				titulo = _ler_texto("Titulo: ")
				_exibir_musica(biblioteca.buscar_por_titulo(titulo))
			except ValueError:
				print("Titulo invalido.")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "5":
			# A listagem percorre a estrutura encadeada sem usar listas prontas.
			if biblioteca.tamanho == 0:
				print("Biblioteca vazia.")
			else:
				for musica in biblioteca.iterar():
					print(musica)

		elif opcao == "0":
			print("Encerrando.")
			return

		else:
			print("Opcao invalida.")

def main() -> None:
	"""Ponto de entrada do programa.

	O argumento `--demo` existe como atalho para demonstrar a biblioteca sem
	passar pelo menu interativo.
	"""
	if len(sys.argv) > 1 and sys.argv[1] == "--demo":
		# Caminho rapido para validar a estrutura sem depender de input do usuario.
		biblioteca = Biblioteca()
		biblioteca.adicionar_musica("Exemplo", "Sistema", "Demo", 120)
		for musica in biblioteca.iterar():
			print(musica)
		return

	try:
		executar_menu_basico()
	except KeyboardInterrupt:
		print("\nEncerrado pelo usuario.")

if __name__ == "__main__":
	main()
