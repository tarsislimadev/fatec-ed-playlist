from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, Optional

"""Sistema de playlist em Python com lista encadeada e filas FIFO.

O arquivo concentra as estruturas pedidas no enunciado e o menu final do
projeto:

- `Musica` modela cada faixa da biblioteca.
- `Biblioteca` guarda as musicas em uma lista encadeada simples.
- `Fila` implementa uma fila FIFO encadeada, reutilizavel para humor e
  historico.
- `SistemaPlaylist` orquestra biblioteca, filas de humor, historico,
  reproducao e estatisticas.
"""

LIMITES_HUMOR = (
	("Relaxar", 80),
	("Focar", 120),
	("Animar", 160),
	("Treinar", sys.maxsize),
)

# Cada faixa de BPM aponta para uma fila de humor especifica.


@dataclass(slots=True)
class Musica:
	"""Representa uma musica cadastrada na biblioteca."""

	id: int
	titulo: str
	artista: str
	genero: str
	bpm: int

	def __str__(self) -> str:
		# Formato padronizado para exibicao no terminal.
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
		# Mantemos inicio e fim para inserir no final em tempo constante.
		self._primeiro: Optional[NodoLista] = None
		self._ultimo: Optional[NodoLista] = None
		self._tamanho = 0
		# O ID nunca e reutilizado, mesmo depois de remocoes.
		self._proximo_id = 1

	@property
	def tamanho(self) -> int:
		return self._tamanho

	@property
	def proximo_id(self) -> int:
		return self._proximo_id

	def adicionar_musica(self, titulo: str, artista: str, genero: str, bpm: int) -> Musica:
		# Validacao centralizada para evitar musicas vazias ou BPM invalido.
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

		if self._primeiro is None:
			# Primeira insercao: o novo nodo vira inicio e fim da lista.
			self._primeiro = nodo
			self._ultimo = nodo
		else:
			# Insercao no final sem percorrer a lista inteira.
			assert self._ultimo is not None
			self._ultimo.proximo = nodo
			self._ultimo = nodo

		self._tamanho += 1
		self._proximo_id += 1
		return musica

	def buscar_por_id(self, musica_id: int) -> Optional[Musica]:
		# Percorre a lista ate encontrar o ID informado.
		nodo_atual = self._primeiro
		while nodo_atual is not None:
			if nodo_atual.musica.id == musica_id:
				return nodo_atual.musica
			nodo_atual = nodo_atual.proximo
		return None

	def buscar_por_titulo(self, titulo: str) -> Optional[Musica]:
		# Busca case-insensitive para facilitar o uso no terminal.
		titulo_normalizado = titulo.strip().casefold()
		nodo_atual = self._primeiro
		while nodo_atual is not None:
			if nodo_atual.musica.titulo.casefold() == titulo_normalizado:
				return nodo_atual.musica
			nodo_atual = nodo_atual.proximo
		return None

	def remover_por_id(self, musica_id: int) -> Optional[Musica]:
		# Remocao ajusta os ponteiros da lista sem usar estruturas prontas.
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
		# Iteracao sequencial sem converter a lista encadeada em list Python.
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
	"""Fila FIFO com nos encadeados e operacoes basicas."""

	def __init__(self) -> None:
		# Frente e tras permitem enfileirar e desenfileirar em tempo constante.
		self._frente: Optional[NodoFila] = None
		self._tras: Optional[NodoFila] = None
		self._tamanho = 0

	@property
	def tamanho(self) -> int:
		return self._tamanho

	def esta_vazia(self) -> bool:
		return self._tamanho == 0

	def enfileirar(self, musica: Musica) -> None:
		# A musica entra sempre no fim da fila.
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
		# Remove o primeiro elemento da fila e devolve a musica retirada.
		if self._frente is None:
			return None

		nodo = self._frente
		self._frente = nodo.proximo
		if self._frente is None:
			self._tras = None
		self._tamanho -= 1
		return nodo.musica

	def espiar(self) -> Optional[Musica]:
		# Consulta o primeiro elemento sem alterar a fila.
		if self._frente is None:
			return None
		return self._frente.musica

	def limpar(self) -> None:
		# Usado para reconstruir as filas de humor do zero.
		self._frente = None
		self._tras = None
		self._tamanho = 0

	def iterar(self) -> Iterator[Musica]:
		# Percorre a fila na ordem de reproducao sem removar itens.
		nodo_atual = self._frente
		while nodo_atual is not None:
			yield nodo_atual.musica
			nodo_atual = nodo_atual.proximo


def classificar_humor_por_bpm(bpm: int) -> str:
	"""Classifica uma musica em um dos humores do projeto."""
	# As faixas seguem exatamente os cortes de BPM definidos no enunciado.
	if bpm <= 80:
		return "Relaxar"
	if bpm <= 120:
		return "Focar"
	if bpm <= 160:
		return "Animar"
	return "Treinar"


class SistemaPlaylist:
	"""Orquestra biblioteca, filas de humor, historico e estatisticas."""

	def __init__(self) -> None:
		# A aplicacao separa biblioteca, filas de humor e historico.
		self.biblioteca = Biblioteca()
		self.filas_humor: dict[str, Fila] = {humor: Fila() for humor, _ in LIMITES_HUMOR}
		self.historico = Fila()

	def adicionar_musica(self, titulo: str, artista: str, genero: str, bpm: int) -> Musica:
		# Toda mudanca na biblioteca pede reconstruir as filas de humor.
		musica = self.biblioteca.adicionar_musica(titulo, artista, genero, bpm)
		self.reconstruir_filas_humor()
		return musica

	def remover_musica(self, musica_id: int) -> Optional[Musica]:
		# A remocao tambem exige sincronizar as filas com o novo estado.
		musica = self.biblioteca.remover_por_id(musica_id)
		if musica is not None:
			self.reconstruir_filas_humor()
		return musica

	def reconstruir_filas_humor(self) -> None:
		# Limpa as filas e redistribui todas as musicas pela faixa de BPM.
		for fila in self.filas_humor.values():
			fila.limpar()

		for musica in self.biblioteca.iterar():
			humor = classificar_humor_por_bpm(musica.bpm)
			self.filas_humor[humor].enfileirar(musica)

	def reproduzir_proxima(self, humor: str) -> Optional[Musica]:
		# Reproduzir significa remover da fila e registrar no historico.
		fila = self.filas_humor[humor]
		musica = fila.desenfileirar()
		if musica is not None:
			self.historico.enfileirar(musica)
		return musica

	def obter_fila(self, humor: str) -> Fila:
		return self.filas_humor[humor]

	def mostrar_estatisticas(self) -> None:
		# Estatisticas resumem a situacao atual das estruturas principais.
		print("\n=== Estatisticas ===")
		print(f"Total na biblioteca: {self.biblioteca.tamanho}")
		for humor, _ in LIMITES_HUMOR:
			print(f"Fila {humor}: {self.filas_humor[humor].tamanho}")
		print(f"Historico: {self.historico.tamanho}")
		print(f"Proximo ID: {self.biblioteca.proximo_id}")


def _ler_texto(rotulo: str) -> str:
	# Leitura simples com rejeicao de entrada vazia.
	valor = input(rotulo).strip()
	if not valor:
		raise ValueError("Entrada vazia.")
	return valor


def _ler_inteiro(rotulo: str) -> int:
	# Conversao padronizada para campos numericos do menu.
	valor_texto = _ler_texto(rotulo)
	return int(valor_texto)


def _imprimir_musica(musica: Optional[Musica], mensagem_vazio: str = "Nenhuma musica encontrada.") -> None:
	# Evita repetir a mesma logica de exibicao em varios caminhos do menu.
	if musica is None:
		print(mensagem_vazio)
		return
	print(musica)


def _imprimir_iteravel(titulo: str, elementos: Iterator[Musica]) -> None:
	# Mostra qualquer fila ou historico sem precisar converter para lista.
	print(titulo)
	tem_elementos = False
	for musica in elementos:
		print(musica)
		tem_elementos = True
	if not tem_elementos:
		print("(vazio)")


def _selecionar_humor() -> Optional[str]:
	# Menu auxiliar para escolher uma fila especifica ou todas elas.
	print("\nSelecione o humor:")
	for indice, (humor, _) in enumerate(LIMITES_HUMOR, start=1):
		print(f"{indice} - {humor}")
	print("5 - Todas")
	print("0 - Cancelar")

	opcao = _ler_texto("Opcao: ")
	mapa = {str(indice): humor for indice, (humor, _) in enumerate(LIMITES_HUMOR, start=1)}
	if opcao == "5":
		return None
	if opcao == "0":
		return ""
	if opcao not in mapa:
		raise ValueError("Humor invalido.")
	return mapa[opcao]


def executar_menu() -> None:
	"""Menu principal com biblioteca, filas de humor, historico e estatisticas."""
	# O menu fica no topo da aplicacao e chama a camada de dominio abaixo.
	sistema = SistemaPlaylist()

	while True:
		print("\n=== Reprodutor de musicas ===")
		print("1 - Adicionar musica")
		print("2 - Remover musica por ID")
		print("3 - Buscar musica por ID")
		print("4 - Buscar musica por titulo")
		print("5 - Listar biblioteca")
		print("6 - Montar filas de humor")
		print("7 - Exibir filas de humor")
		print("8 - Reproduzir proxima musica")
		print("9 - Exibir historico")
		print("10 - Mostrar estatisticas")
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
				# Cadastro de musica com validacao completa.
				titulo = _ler_texto("Titulo: ")
				artista = _ler_texto("Artista: ")
				genero = _ler_texto("Genero: ")
				bpm = _ler_inteiro("BPM: ")
				musica = sistema.adicionar_musica(titulo, artista, genero, bpm)
				print("Musica adicionada:")
				print(musica)
			except ValueError as erro:
				print(f"Erro: {erro}")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "2":
			try:
				# Remocao por ID reaproveita a logica da biblioteca e reajusta filas.
				musica_id = _ler_inteiro("ID: ")
				musica = sistema.remover_musica(musica_id)
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
				# Busca direta por identificador.
				musica_id = _ler_inteiro("ID: ")
				_imprimir_musica(sistema.biblioteca.buscar_por_id(musica_id))
			except ValueError:
				print("ID invalido.")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "4":
			try:
				# Busca textual case-insensitive.
				titulo = _ler_texto("Titulo: ")
				_imprimir_musica(sistema.biblioteca.buscar_por_titulo(titulo))
			except ValueError:
				print("Titulo invalido.")
			except EOFError:
				print("\nEntrada encerrada.")
				return

		elif opcao == "5":
			# Listagem completa sem usar lista pronta como armazenamento.
			if sistema.biblioteca.tamanho == 0:
				print("Biblioteca vazia.")
			else:
				for musica in sistema.biblioteca.iterar():
					print(musica)

		elif opcao == "6":
			# Reconstrucao manual das filas, util apos alteracoes em lote.
			sistema.reconstruir_filas_humor()
			print("Filas de humor montadas com sucesso.")

		elif opcao == "7":
			try:
				# Exibe uma fila especifica ou todas, sem remover elementos.
				humor = _selecionar_humor()
			except ValueError as erro:
				print(f"Erro: {erro}")
				continue
			except EOFError:
				print("\nEntrada encerrada.")
				return

			if humor is None:
				for nome_humor, _ in LIMITES_HUMOR:
					_imprimir_iteravel(f"\nFila {nome_humor}:", sistema.obter_fila(nome_humor).iterar())
			elif humor:
				_imprimir_iteravel(f"\nFila {humor}:", sistema.obter_fila(humor).iterar())

		elif opcao == "8":
			try:
				# Toca a proxima musica da fila e manda para o historico.
				humor = _selecionar_humor()
			except ValueError as erro:
				print(f"Erro: {erro}")
				continue
			except EOFError:
				print("\nEntrada encerrada.")
				return

			if humor is None:
				print("Escolha um humor especifico para reproduzir.")
			elif humor == "":
				print("Operacao cancelada.")
			else:
				musica = sistema.reproduzir_proxima(humor)
				if musica is None:
					print(f"Fila {humor} vazia.")
				else:
					print("Reproduzindo:")
					print(musica)

		elif opcao == "9":
			# Historico e apenas mais uma fila encadeada, exibida sem consumo.
			_imprimir_iteravel("\nHistorico:", sistema.historico.iterar())

		elif opcao == "10":
			# Consolida o estado atual das estruturas para o usuario.
			sistema.mostrar_estatisticas()

		elif opcao == "0":
			print("Encerrando.")
			return

		else:
			print("Opcao invalida.")


def executar_demo() -> None:
	"""Executa um fluxo curto para validar a solucao sem entrada interativa."""
	# A demo monta um caso pequeno para validar as estruturas principais.
	sistema = SistemaPlaylist()
	sistema.adicionar_musica("Exemplo 1", "Sistema", "Demo", 70)
	sistema.adicionar_musica("Exemplo 2", "Sistema", "Demo", 110)
	sistema.adicionar_musica("Exemplo 3", "Sistema", "Demo", 150)
	sistema.adicionar_musica("Exemplo 4", "Sistema", "Demo", 180)
	sistema.reconstruir_filas_humor()

	for musica in sistema.biblioteca.iterar():
		print(musica)

	sistema.mostrar_estatisticas()
	musica = sistema.reproduzir_proxima("Relaxar")
	if musica is not None:
		# A musica tocada sai da fila e aparece no historico.
		print("\nDemo reproduzida:")
		print(musica)
	print("\nHistorico apos demo:")
	for musica in sistema.historico.iterar():
		print(musica)


def main() -> None:
	"""Ponto de entrada do programa."""
	# `--demo` executa um fluxo automatico; sem ele o programa abre o menu.
	if len(sys.argv) > 1 and sys.argv[1] == "--demo":
		executar_demo()
		return

	try:
		executar_menu()
	except KeyboardInterrupt:
		print("\nEncerrado pelo usuario.")


if __name__ == "__main__":
	main()
