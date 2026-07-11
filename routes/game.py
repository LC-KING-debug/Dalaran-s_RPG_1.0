"""Motor de jogo por texto (text-based) para o Dalaran's RPG.

Este modulo contem toda a logica de personagens, inimigos e progressao da
partida usada pelo terminal web do jogo. Nenhuma funcao aqui usa print()/
input(): toda a interacao acontece atraves de Game.process_command(), que
recebe uma linha digitada no terminal web e devolve as linhas de saida a
serem exibidas -- por isso pode ser chamado livremente de dentro de uma
rota HTTP (Flask, FastAPI, etc.) sem bloquear o servidor.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple


class Tag:
    """Prefixos usados nas mensagens de saida.

    Centralizar os prefixos aqui evita erros de digitacao e deixa explicito
    o "protocolo" de texto que o front-end do terminal usa para colorir/
    categorizar cada linha exibida.
    """

    SISTEMA = "[SISTEMA]"
    ERRO = "[ERRO]"
    AVISO = "[AVISO]"
    COMBATE = "[COMBATE]"
    FALHA = "[FALHA]"
    MOVIMENTO = "[MOVIMENTO]"
    ALERTA = "[ALERTA]"
    ACAO = "[AÇÃO]"
    HABILIDADE = "[HABILIDADE]"
    PERIGO = "[PERIGO]"
    VITORIA = "[VITORIA]"
    DROP = "[DROP]"
    LEVEL_UP = "[LEVEL UP]"
    GAME_OVER = "[GAME OVER]"
    ITEM = "[ITEM]"
    INVENTARIO = "[INVENTARIO]"
    STATUS = "[STATUS]"


# ---------------------------------------------------------------------------
# Configuracao: personagem e classes
# ---------------------------------------------------------------------------

EXP_INICIAL_NECESSARIA = 100
ITENS_INICIAIS: Tuple[str, ...] = ("Pocao de Vida",)

MULTIPLICADOR_LEVEL_HP = 1.2
MULTIPLICADOR_LEVEL_ATRIBUTOS = 1.15
MULTIPLICADOR_LEVEL_EXP_NECESSARIA = 1.5


@dataclass(frozen=True)
class ClasseStats:
    """Atributos base concedidos por uma classe de personagem."""

    hp_max: int
    ataque: int
    defesa: int
    habilidade_especial: str


CLASSES_DISPONIVEIS: Dict[str, ClasseStats] = {
    "monge": ClasseStats(hp_max=120, ataque=15, defesa=10, habilidade_especial="Palma de Ferro"),
    "mago": ClasseStats(hp_max=80, ataque=25, defesa=5, habilidade_especial="Bola de Fogo"),
    "assassino": ClasseStats(hp_max=95, ataque=20, defesa=7, habilidade_especial="Ataque Furtivo"),
}
CLASSE_PADRAO = ClasseStats(hp_max=100, ataque=15, defesa=8, habilidade_especial="Socar")


class Inventario:
    """Inventario do personagem, guardado como contagem de itens.

    Comporta-se como uma lista para uso externo (len(), 'in', iteracao)
    para nao quebrar codigo que ainda espere o formato antigo, mas guarda
    os dados internamente como {item: quantidade} para evitar duplicar
    entradas repetidas indefinidamente.
    """

    def __init__(self, itens_iniciais: Optional[Iterable[str]] = None) -> None:
        self._itens: Dict[str, int] = {}
        for item in itens_iniciais or ():
            self.adicionar(item)

    def adicionar(self, item: str, quantidade: int = 1) -> None:
        self._itens[item] = self._itens.get(item, 0) + quantidade

    def remover(self, item: str, quantidade: int = 1) -> bool:
        """Remove `quantidade` unidades de `item`. Retorna False se nao houver o suficiente."""
        if self._itens.get(item, 0) < quantidade:
            return False
        self._itens[item] -= quantidade
        if self._itens[item] <= 0:
            del self._itens[item]
        return True

    def possui(self, item: str, quantidade: int = 1) -> bool:
        return self._itens.get(item, 0) >= quantidade

    @property
    def vazio(self) -> bool:
        return not self._itens

    def listar_formatado(self) -> str:
        """Ex.: 'Pocao de Vida x3, Chave Antiga' (sem 'xN' quando ha so 1 unidade)."""
        return ", ".join(
            f"{item} x{qtd}" if qtd > 1 else item
            for item, qtd in self._itens.items()
        )

    def to_dict(self) -> Dict[str, int]:
        return dict(self._itens)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Inventario":
        inventario = cls()
        inventario._itens = dict(data)
        return inventario

    def __iter__(self):
        for item, qtd in self._itens.items():
            for _ in range(qtd):
                yield item

    def __contains__(self, item: str) -> bool:
        return self.possui(item)

    def __len__(self) -> int:
        return sum(self._itens.values())

    def __bool__(self) -> bool:
        return not self.vazio

    def __repr__(self) -> str:
        return f"Inventario({self._itens!r})"


class Personagem:
    """Personagem jogavel: atributos, progressao de nivel e inventario."""

    def __init__(self, nome: str, classe: str) -> None:
        if not nome or not nome.strip():
            raise ValueError("O nome do personagem nao pode ser vazio.")

        self.nome = nome.strip()
        self.classe = classe.strip() if classe else ""
        self.nivel = 1
        self.exp = 0
        self.exp_necessaria = EXP_INICIAL_NECESSARIA
        self.inventario = Inventario(ITENS_INICIAIS)

        stats = CLASSES_DISPONIVEIS.get(self.classe.lower(), CLASSE_PADRAO)
        self.hp_max = stats.hp_max
        self.hp = stats.hp_max
        self.ataque = stats.ataque
        self.defesa = stats.defesa
        self.habilidade_especial = stats.habilidade_especial

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, valor: int) -> None:
        """HP e sempre mantido dentro de [0, hp_max], nunca negativo ou acima do maximo."""
        self._hp = max(0, min(self.hp_max, valor))

    @property
    def esta_vivo(self) -> bool:
        return self.hp > 0

    def status_formatado(self) -> str:
        return (
            f"{Tag.STATUS} {self.nome} ({self.classe.upper()}) | Nivel: {self.nivel} | "
            f"HP: {self.hp}/{self.hp_max} | ATK: {self.ataque} | DEF: {self.defesa} | "
            f"EXP: {self.exp}/{self.exp_necessaria}"
        )

    def ganhar_experiencia(self, quantidade: int) -> List[str]:
        """Adiciona EXP e aplica quantos level-ups forem necessarios (nao so um)."""
        self.exp += quantidade
        logs = [f"{Tag.SISTEMA} Voce ganhou {quantidade} de EXP."]

        while self.exp >= self.exp_necessaria:
            self.exp -= self.exp_necessaria
            self.nivel += 1
            self.hp_max = int(self.hp_max * MULTIPLICADOR_LEVEL_HP)
            self.hp = self.hp_max  # cura total ao subir de nivel
            self.ataque = int(self.ataque * MULTIPLICADOR_LEVEL_ATRIBUTOS)
            self.defesa = int(self.defesa * MULTIPLICADOR_LEVEL_ATRIBUTOS)
            self.exp_necessaria = int(self.exp_necessaria * MULTIPLICADOR_LEVEL_EXP_NECESSARIA)
            logs.append(f"{Tag.LEVEL_UP} Parabens! Voce alcancou o Nivel {self.nivel}!")

        return logs

    def to_dict(self) -> Dict[str, object]:
        return {
            "nome": self.nome,
            "classe": self.classe,
            "nivel": self.nivel,
            "exp": self.exp,
            "exp_necessaria": self.exp_necessaria,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "ataque": self.ataque,
            "defesa": self.defesa,
            "habilidade_especial": self.habilidade_especial,
            "inventario": self.inventario.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Personagem":
        personagem = cls(data["nome"], data["classe"])
        personagem.nivel = data["nivel"]
        personagem.exp = data["exp"]
        personagem.exp_necessaria = data["exp_necessaria"]
        personagem.hp_max = data["hp_max"]
        personagem.hp = data["hp"]
        personagem.ataque = data["ataque"]
        personagem.defesa = data["defesa"]
        personagem.habilidade_especial = data["habilidade_especial"]
        personagem.inventario = Inventario.from_dict(data["inventario"])
        return personagem

    def __repr__(self) -> str:
        return (
            f"Personagem(nome={self.nome!r}, classe={self.classe!r}, "
            f"nivel={self.nivel}, hp={self.hp}/{self.hp_max})"
        )


class Inimigo:
    """Inimigo encontrado durante a exploracao."""

    def __init__(self, nome: str, hp: int, ataque: int, defesa: int, exp_recompensa: int) -> None:
        self.nome = nome
        self.hp_max = hp
        self.hp = hp
        self.ataque = ataque
        self.defesa = defesa
        self.exp_recompensa = exp_recompensa

    @property
    def esta_vivo(self) -> bool:
        return self.hp > 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "nome": self.nome,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "ataque": self.ataque,
            "defesa": self.defesa,
            "exp_recompensa": self.exp_recompensa,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Inimigo":
        inimigo = cls(data["nome"], data["hp_max"], data["ataque"], data["defesa"], data["exp_recompensa"])
        inimigo.hp = data["hp"]
        return inimigo

    def __repr__(self) -> str:
        return f"Inimigo(nome={self.nome!r}, hp={self.hp}/{self.hp_max})"


# ---------------------------------------------------------------------------
# Configuracao: mundo e combate
# ---------------------------------------------------------------------------

SALA_INICIAL = "Entrada de Dalaran"

MAPA_MUNDO: Dict[str, Dict[str, str]] = {
    "Entrada de Dalaran": {"norte": "Sala dos Espelhos", "leste": "Laboratorio do Mago"},
    "Sala dos Espelhos": {"sul": "Entrada de Dalaran", "leste": "Cripta Sombria"},
    "Laboratorio do Mago": {"oeste": "Entrada de Dalaran"},
    "Cripta Sombria": {"oeste": "Sala dos Espelhos"},
}

MONSTROS_DISPONIVEIS: Tuple[Dict[str, object], ...] = (
    {"nome": "Constructo de Silicio", "hp": 40, "ataque": 12, "defesa": 4, "exp": 40},
    {"nome": "Espectro de Codigo Malicioso", "hp": 50, "ataque": 16, "defesa": 2, "exp": 50},
    {"nome": "Drogado de Corrente de Dados", "hp": 60, "ataque": 10, "defesa": 6, "exp": 60},
)

CHANCE_ENCONTRO_INIMIGO = 0.5   # chance de encontrar um inimigo ao mudar de sala
CHANCE_FUGA_SUCESSO = 0.6       # chance de fugir com sucesso do combate
CHANCE_CRITICO = 0.2            # chance de acerto critico do jogador
MULTIPLICADOR_CRITICO = 1.5
CHANCE_DROP_POCAO = 0.4         # chance de o inimigo derrotado dropar uma pocao

CURA_POCAO_PERCENTUAL = 0.5     # % do hp_max recuperado ao usar Pocao de Vida
REVIVE_HP_PERCENTUAL = 0.5      # % do hp_max com que o jogador reaparece apos "morrer"

DANO_MINIMO_JOGADOR = 3
DANO_MINIMO_INIMIGO = 1
VARIACAO_DANO_JOGADOR: Tuple[int, int] = (-2, 3)
VARIACAO_DANO_INIMIGO: Tuple[int, int] = (-1, 2)


class Game:
    """Motor de uma partida do RPG de terminal (Dalaran's RPG).

    Cada instancia representa uma sessao de jogo isolada. Toda interacao com
    o jogador acontece atraves de process_command(), que recebe uma linha de
    texto digitada no terminal web e devolve uma lista de linhas de saida --
    nenhum metodo aqui bloqueia esperando por print()/input().
    """

    def __init__(self, nome_personagem: str, classe_personagem: str, seed: Optional[int] = None) -> None:
        self.player = Personagem(nome_personagem, classe_personagem)
        self.sala_atual = SALA_INICIAL
        self.inimigo_atual: Optional[Inimigo] = None
        self.mapa = MAPA_MUNDO
        self._rng = random.Random(seed)

        self._comandos_livres: Dict[str, Callable[[str], List[str]]] = {
            "ir": self._cmd_ir,
            "status": self._cmd_status,
            "inventario": self._cmd_inventario,
            "usar": self._cmd_usar,
        }
        self._itens_usaveis: Dict[str, Callable[[], List[str]]] = {
            "pocao de vida": self._usar_pocao_de_vida,
        }

    @property
    def em_combate(self) -> bool:
        return self.inimigo_atual is not None

    # ---------------- API publica ----------------

    def process_command(self, command_text: str) -> List[str]:
        """Interpreta uma linha de comando do terminal e retorna a saida a exibir."""
        cmd, arg = self._parse_comando(command_text)

        if self.em_combate:
            return self._processar_turno_combate(cmd)

        handler = self._comandos_livres.get(cmd)
        if handler is None:
            return [self._mensagem_comando_invalido(cmd)]
        return handler(arg)

    def to_dict(self) -> Dict[str, object]:
        """Serializa o estado da partida (ex.: para salvar na sessao/BD entre requisicoes HTTP)."""
        return {
            "player": self.player.to_dict(),
            "sala_atual": self.sala_atual,
            "inimigo_atual": self.inimigo_atual.to_dict() if self.inimigo_atual else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Game":
        """Reconstroi uma partida a partir do estado salvo por to_dict()."""
        jogador_data = data["player"]
        game = cls(jogador_data["nome"], jogador_data["classe"])
        game.player = Personagem.from_dict(jogador_data)
        game.sala_atual = data["sala_atual"]
        inimigo_data = data.get("inimigo_atual")
        game.inimigo_atual = Inimigo.from_dict(inimigo_data) if inimigo_data else None
        return game

    # ---------------- parsing ----------------

    @staticmethod
    def _parse_comando(command_text: str) -> Tuple[str, str]:
        partes = command_text.strip().lower().split(" ", 1)
        cmd = partes[0]
        arg = partes[1] if len(partes) > 1 else ""
        return cmd, arg

    @staticmethod
    def _mensagem_comando_invalido(cmd: str) -> str:
        return (
            f"{Tag.SISTEMA} Comando '{cmd}' invalido. "
            "Digite: 'ir norte', 'status', 'inventario' ou 'usar pocao de vida'."
        )

    # ---------------- comandos fora de combate ----------------

    def _cmd_ir(self, arg: str) -> List[str]:
        if not arg:
            return [f"{Tag.ERRO} Ir para onde? Use: ir norte, ir sul, ir leste, ir oeste."]

        destinos = self.mapa.get(self.sala_atual, {})
        destino = destinos.get(arg)
        if destino is None:
            return [f"{Tag.ERRO} Nao ha caminhos para o '{arg}' a partir daqui."]

        self.sala_atual = destino
        output = [
            f"{Tag.MOVIMENTO} Voce se moveu para o {arg.upper()}.",
            f"{Tag.SISTEMA} Nova localizacao: {self.sala_atual}.",
        ]

        if self._rng.random() < CHANCE_ENCONTRO_INIMIGO:
            self.inimigo_atual = self._gerar_inimigo()
            output.append(f"⚠️ {Tag.ALERTA} Um inimigo perigoso apareceu: **{self.inimigo_atual.nome}**!")
            output.append(f"{Tag.SISTEMA} Comandos disponiveis: 'atacar' ou 'fugir'.")

        return output

    def _cmd_status(self, arg: str) -> List[str]:
        return [self.player.status_formatado()]

    def _cmd_inventario(self, arg: str) -> List[str]:
        if self.player.inventario.vazio:
            return [f"{Tag.INVENTARIO} Seu inventario esta completamente vazio."]
        return [f"{Tag.INVENTARIO} Itens carregados: [ {self.player.inventario.listar_formatado()} ]"]

    def _cmd_usar(self, arg: str) -> List[str]:
        item = arg.strip()
        if not item:
            return [f"{Tag.ERRO} Usar o que? Ex.: 'usar pocao de vida'."]

        handler = self._itens_usaveis.get(item)
        if handler is None:
            return [f"{Tag.ERRO} Voce nao sabe como usar '{item}'."]
        return handler()

    def _usar_pocao_de_vida(self) -> List[str]:
        if not self.player.inventario.possui("Pocao de Vida"):
            return [f"{Tag.ERRO} Voce nao possui Pocao de Vida no seu inventario."]

        self.player.inventario.remover("Pocao de Vida")
        cura = int(self.player.hp_max * CURA_POCAO_PERCENTUAL)
        self.player.hp = self.player.hp + cura  # o setter ja limita ao hp_max
        return [
            f"{Tag.ITEM} Voce usou uma Pocao de Vida e recuperou {cura} de HP!",
            f"{Tag.STATUS} HP Atual: {self.player.hp}/{self.player.hp_max}",
        ]

    # ---------------- combate ----------------

    def _processar_turno_combate(self, cmd: str) -> List[str]:
        if cmd == "atacar":
            return self._atacar_inimigo()
        if cmd == "fugir":
            return self._tentar_fuga()
        return [f"{Tag.AVISO} Voce esta em combate com um {self.inimigo_atual.nome}! Use 'atacar' ou 'fugir'."]

    def _tentar_fuga(self) -> List[str]:
        if self._rng.random() < CHANCE_FUGA_SUCESSO:
            self.inimigo_atual = None
            return [
                f"{Tag.COMBATE} Voce conseguiu escapar com sucesso!",
                f"{Tag.SISTEMA} Voce esta na sala: {self.sala_atual}.",
            ]

        output = [f"{Tag.FALHA} Voce tentou fugir, mas o inimigo bloqueou sua passagem!"]
        output.extend(self._turno_do_inimigo())
        return output

    def _atacar_inimigo(self) -> List[str]:
        output: List[str] = []
        player = self.player
        inimigo = self.inimigo_atual
        assert inimigo is not None  # garantido pelo chamador (self.em_combate)

        dano = self._rolar_dano(player.ataque, inimigo.defesa, VARIACAO_DANO_JOGADOR, DANO_MINIMO_JOGADOR)
        critico = self._rng.random() < CHANCE_CRITICO
        if critico:
            dano = int(dano * MULTIPLICADOR_CRITICO)
            output.append(f"{Tag.HABILIDADE} CRITICO! {player.nome} ativou {player.habilidade_especial}!")

        inimigo.hp -= dano
        output.append(
            f"{Tag.ACAO} Voce atacou o {inimigo.nome} causando {dano} de dano. "
            f"({max(0, inimigo.hp)}/{inimigo.hp_max} HP restante)"
        )

        if not inimigo.esta_vivo:
            output.append(f"☠️ {Tag.VITORIA} Voce derrotou o {inimigo.nome}!")
            output.extend(player.ganhar_experiencia(inimigo.exp_recompensa))

            if self._rng.random() < CHANCE_DROP_POCAO:
                player.inventario.adicionar("Pocao de Vida")
                output.append(f"{Tag.DROP} O inimigo deixou cair uma 'Pocao de Vida'. Adicionado ao inventario.")

            self.inimigo_atual = None
            return output

        output.extend(self._turno_do_inimigo())
        return output

    def _turno_do_inimigo(self) -> List[str]:
        output = []
        player = self.player
        inimigo = self.inimigo_atual
        assert inimigo is not None

        dano = self._rolar_dano(inimigo.ataque, player.defesa, VARIACAO_DANO_INIMIGO, DANO_MINIMO_INIMIGO)
        player.hp -= dano
        output.append(f"{Tag.PERIGO} O {inimigo.nome} atacou de volta causando {dano} de dano!")

        if not player.esta_vivo:
            output.append(f"💀 {Tag.GAME_OVER} Seu HP chegou a zero!")
            player.hp = int(player.hp_max * REVIVE_HP_PERCENTUAL)
            self.sala_atual = SALA_INICIAL
            self.inimigo_atual = None
            output.append(f"{Tag.SISTEMA} Voce foi reinicializado na Entrada de Dalaran com 50% de HP.")

        return output

    def _rolar_dano(self, ataque: int, defesa: int, variacao: Tuple[int, int], minimo: int) -> int:
        """Calcula dano = ataque - defesa + variacao aleatoria, com piso minimo garantido."""
        minimo_var, maximo_var = variacao
        return max(minimo, ataque - defesa + self._rng.randint(minimo_var, maximo_var))

    def _gerar_inimigo(self) -> Inimigo:
        escolha = self._rng.choice(MONSTROS_DISPONIVEIS)
        return Inimigo(escolha["nome"], escolha["hp"], escolha["ataque"], escolha["defesa"], escolha["exp"])

    def __repr__(self) -> str:
        estado = f"em combate com {self.inimigo_atual.nome}" if self.em_combate else "explorando"
        return f"Game(player={self.player.nome!r}, sala={self.sala_atual!r}, {estado})"