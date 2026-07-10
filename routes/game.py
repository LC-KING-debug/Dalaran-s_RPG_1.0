import random

class Personagem:
    def __init__(self, nome, classe):
        self.nome = nome
        self.classe = classe
        self.nivel = 1
        self.exp = 0
        self.exp_necessaria = 100
        self.inventario = ["Pocao de Vida"]
        
        if classe.lower() == "monge":
            self.hp_max = 120
            self.hp = 120
            self.ataque = 15
            self.defesa = 10
            self.habilidade_especial = "Palma de Ferro"
        elif classe.lower() == "mago":
            self.hp_max = 80
            self.hp = 80
            self.ataque = 25
            self.defesa = 5
            self.habilidade_especial = "Bola de Fogo"
        elif classe.lower() == "assassino":
            self.hp_max = 95
            self.hp = 95
            self.ataque = 20
            self.defesa = 7
            self.habilidade_especial = "Ataque Furtivo"
        else:
            self.hp_max = 100
            self.hp = 100
            self.ataque = 15
            self.defesa = 8
            self.habilidade_especial = "Socar"

    def status_formatado(self):
        return (
            f"[STATUS] {self.nome} ({self.classe.upper()}) | Nivel: {self.nivel} | "
            f"HP: {self.hp}/{self.hp_max} | ATK: {self.ataque} | DEF: {self.defesa} | "
            f"EXP: {self.exp}/{self.exp_necessaria}"
        )

    def ganhar_experiencia(self, quantidade):
        self.exp += quantidade
        logs = [f"[SISTEMA] Voce ganhou {quantidade} de EXP."]
        if self.exp >= self.exp_necessaria:
            self.exp -= self.exp_necessaria
            self.nivel += 1
            self.hp_max = int(self.hp_max * 1.2)
            self.hp = self.hp_max
            self.ataque = int(self.ataque * 1.15)
            self.defesa = int(self.defesa * 1.15)
            self.exp_necessaria = int(self.exp_necessaria * 1.5)
            logs.append(f"[LEVEL UP] Parabens! Voce alcancou o Nivel {self.nivel}!")
        return logs


class Inimigo:
    def __init__(self, nome, hp, ataque, defensa, exp_recompensa):
        self.nome = nome
        self.hp = hp
        self.hp_max = hp
        self.ataque = ataque
        self.defesa = defensa
        self.exp_recompensa = exp_recompensa


class Game:
    def __init__(self, nome_personagem, classe_personagem):
        self.player = Personagem(nome_personagem, classe_personagem)
        self.sala_atual = "Entrada de Dalaran"
        self.inimigo_atual = None
        
        self.mapa = {
            "Entrada de Dalaran": {"norte": "Sala dos Espelhos", "leste": "Laboratorio do Mago"},
            "Sala dos Espelhos": {"sul": "Entrada de Dalaran", "leste": "Cripta Sombria"},
            "Laboratorio do Mago": {"oeste": "Entrada de Dalaran"},
            "Cripta Sombria": {"oeste": "Sala dos Espelhos"}
        }

    def gerar_inimigo(self):
        monstros = [
            {"nome": "Constructo de Silicio", "hp": 40, "ataque": 12, "defesa": 4, "exp": 40},
            {"nome": "Espectro de Codigo Malicioso", "hp": 50, "ataque": 16, "defesa": 2, "exp": 50},
            {"nome": "Drogado de Corrente de Dados", "hp": 60, "ataque": 10, "defesa": 6, "exp": 60}
        ]
        escolha = random.choice(monstros)
        return Inimigo(escolha["nome"], escolha["hp"], escolha["ataque"], escolha["defesa"], escolha["exp"])

    def process_command(self, command_text):
        parts = command_text.strip().lower().split(" ", 1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        output = []

        if self.inimigo_atual:
            if cmd == "atacar":
                return self._executar_combate()
            elif cmd == "fugir":
                if random.random() > 0.4:
                    self.inimigo_atual = None
                    output.append("[COMBATE] Voce conseguiu escapar com sucesso!")
                    output.append(f"[SISTEMA] Voce esta na sala: {self.sala_atual}.")
                    return output
                else:
                    output.append("[FALHA] Voce tentou fugir, mas o inimigo bloqueou sua passagem!")
                    output.extend(self._turno_do_inimigo())
                    return output
            else:
                return [f"[AVISO] Voce esta em combate com um {self.inimigo_atual.nome}! Use 'atacar' ou 'fugir'."]

        if cmd == "ir":
            if not arg:
                return ["[ERRO] Ir para onde? Use: ir norte, ir sul, ir leste, ir oeste."]
            
            direcoes_disponiveis = self.mapa.get(self.sala_atual, {})
            if arg in direcoes_disponiveis:
                self.sala_atual = direcoes_disponiveis[arg]
                output.append(f"[MOVIMENTO] Voce se moveu para o {arg.upper()}.")
                output.append(f"[SISTEMA] Nova localizacao: {self.sala_atual}.")
                
                if random.random() < 0.5:
                    self.inimigo_atual = self.gerar_inimigo()
                    output.append(f"⚠️ [ALERTA] Um inimigo perigoso apareceu: **{self.inimigo_atual.nome}**!")
                    output.append("[SISTEMA] Comandos disponiveis: 'atacar' ou 'fugir'.")
            else:
                output.append(f"[ERRO] Nao ha caminhos para o '{arg}' a partir daqui.")
            return output

        elif cmd == "status":
            return [self.player.status_formatado()]

        elif cmd == "inventario":
            if not self.player.inventario:
                return ["[INVENTARIO] Seu inventario esta completamente vazio."]
            itens = ", ".join(self.player.inventario)
            return [f"[INVENTARIO] Itens carregados: [ {itens} ]"]

        elif cmd == "usar" and arg == "pocao de vida":
            if "Pocao de Vida" in self.player.inventario:
                self.player.inventario.remove("Pocao de Vida")
                cura = int(self.player.hp_max * 0.5)
                self.player.hp = min(self.player.hp_max, self.player.hp + cura)
                return [f"[ITEM] Voce usou uma Pocao de Vida e recuperou {cura} de HP!", f"[STATUS] HP Atual: {self.player.hp}/{self.player.hp_max}"]
            return ["[ERRO] Voce nao possui Pocao de Vida no seu inventario."]

        else:
            return [f"[SISTEMA] Comando '{cmd}' invalido. Digite: 'ir norte', 'status', 'inventario' ou 'usar pocao de vida'."]

    def _executar_combate(self):
        output = []
        player = self.player
        inimigo = self.inimigo_atual

        dano_player = max(3, player.ataque - inimigo.defesa + random.randint(-2, 3))
        critico = random.random() < 0.2
        if critico:
            dano_player = int(dano_player * 1.5)
            output.append(f"[HABILIDADE] CRITICO! {player.nome} ativou {player.habilidade_especial}!")

        inimigo.hp -= dano_player
        output.append(f"[AÇÃO] Voce atacou o {inimigo.nome} causando {dano_player} de dano. ({max(0, inimigo.hp)}/{inimigo.hp_max} HP restante)")

        if inimigo.hp <= 0:
            output.append(f"☠️ [VITORIA] Voce derrotou o {inimigo.nome}!")
            logs_exp = player.ganhar_experiencia(inimigo.exp_recompensa)
            output.extend(logs_exp)
            
            if random.random() < 0.4:
                player.inventario.append("Pocao de Vida")
                output.append("[DROP] O inimigo deixou cair uma 'Pocao de Vida'. Adicionado ao inventario.")
                
            self.inimigo_atual = None
            return output

        output.extend(self._turno_do_inimigo())
        return output

    def _turno_do_inimigo(self):
        output = []
        player = self.player
        inimigo = self.inimigo_atual

        dano_inimigo = max(1, inimigo.ataque - player.defesa + random.randint(-1, 2))
        player.hp -= dano_inimigo
        output.append(f"[PERIGO] O {inimigo.nome} atacou de volta causando {dano_inimigo} de dano!")

        if player.hp <= 0:
            output.append("💀 [GAME OVER] Seu HP chegou a zero!")
            player.hp = int(player.hp_max * 0.5)
            self.sala_atual = "Entrada de Dalaran"
            self.inimigo_atual = None
            output.append("[SISTEMA] Voce foi reinicializado na Entrada de Dalaran com 50% de HP.")
        
        return output