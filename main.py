import json
import os
from datetime import datetime
from escpos.printer import Usb

ARQUIVO_TAREFAS = "tarefas.json"
ARQUIVO_ULTIMA_IMPRESSAO = "ultima_impressao.json"

def carregar_tarefas():
    if not os.path.exists(ARQUIVO_TAREFAS):
        return []
    with open(ARQUIVO_TAREFAS, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, 'w', encoding='utf-8') as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

def salvar_ultima_impressao(lista):
    with open(ARQUIVO_ULTIMA_IMPRESSAO, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def carregar_ultima_impressao():
    if not os.path.exists(ARQUIVO_ULTIMA_IMPRESSAO):
        return []
    with open(ARQUIVO_ULTIMA_IMPRESSAO, 'r', encoding='utf-8') as f:
        return json.load(f)

def listar_tarefas(tarefas):
    if not tarefas:
        print("Nenhuma tarefa encontrada.")
    else:
        for i, tarefa in enumerate(tarefas, 1):
            print(f"{i}. {tarefa}")

def criar_tarefa(tarefas):
    nova = input("Digite a nova tarefa: ").strip()
    if nova:
        tarefas.append(nova)
        salvar_tarefas(tarefas)
        print("Tarefa adicionada.")
    else:
        print("Tarefa vazia não adicionada.")

def atualizar_tarefa(tarefas):
    listar_tarefas(tarefas)
    try:
        idx = int(input("Digite o número da tarefa que deseja atualizar: ")) - 1
        if 0 <= idx < len(tarefas):
            nova = input("Digite o novo texto: ").strip()
            if nova:
                tarefas[idx] = nova
                salvar_tarefas(tarefas)
                print("Tarefa atualizada.")
            else:
                print("Tarefa vazia não atualizada.")
        else:
            print("Índice inválido.")
    except ValueError:
        print("Entrada inválida.")

def remover_tarefa(tarefas):
    listar_tarefas(tarefas)
    try:
        idx = int(input("Digite o número da tarefa que deseja remover: ")) - 1
        if 0 <= idx < len(tarefas):
            removida = tarefas.pop(idx)
            salvar_tarefas(tarefas)
            print(f"Tarefa '{removida}' removida.")
        else:
            print("Índice inválido.")
    except ValueError:
        print("Entrada inválida.")

def imprimir_lista(lista):
    try:
        p = Usb(0x6868, 0x0200)  # Ajuste se necessário
        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y %H:%M")

        p.set(align='center', bold=True, double_height=True)
        p.text("Lista de Tarefas\n")
        p.set(align='center', bold=False)
        p.text(f"{data_hora}\n")
        p.set(align='left')
        p.set(align='left', font='b', width=1, height=1)

        for item in lista:
            p.text(f"[ ] {item['tarefa']}\n")
            if item.get("avaliar", False):
                p.text("[ ] Ruim   [ ] Médio   [ ] Bom\n")

        p.text("\n")
        print("Tarefas impressas com sucesso!")
    except Exception as e:
        print("Erro ao imprimir:", e)

def imprimir_tarefas(tarefas):
    listar_tarefas(tarefas)
    selecionadas = input("Digite os números das tarefas que deseja imprimir (ex: 1,3,4): ")
    try:
        indices = [int(x.strip()) - 1 for x in selecionadas.split(",")]
        lista_impressao = []

        for i in indices:
            if 0 <= i < len(tarefas):
                tarefa = tarefas[i]
                avaliar = input(f"Incluir avaliação para \"{tarefa}\"? (s/n): ").lower().strip() == 's'
                lista_impressao.append({"tarefa": tarefa, "avaliar": avaliar})

        if not lista_impressao:
            print("Nenhuma tarefa válida selecionada.")
            return

        imprimir_lista(lista_impressao)
        salvar_ultima_impressao(lista_impressao)

    except Exception as e:
        print("Erro ao imprimir:", e)

def reimprimir_ultima_lista():
    lista = carregar_ultima_impressao()
    if not lista:
        print("Nenhuma impressão anterior encontrada.")
        return
    imprimir_lista(lista)

def menu():
    print("\n== GERENCIADOR DE TAREFAS ==")
    print("1. Listar tarefas")
    print("2. Adicionar tarefa")
    print("3. Atualizar tarefa")
    print("4. Remover tarefa")
    print("5. Imprimir tarefas selecionadas")
    print("6. Reimprimir última lista")
    print("0. Sair")

def main():
    while True:
        tarefas = carregar_tarefas()
        menu()
        opcao = input("Escolha uma opção: ").strip()
        if opcao == '1':
            listar_tarefas(tarefas)
        elif opcao == '2':
            criar_tarefa(tarefas)
        elif opcao == '3':
            atualizar_tarefa(tarefas)
        elif opcao == '4':
            remover_tarefa(tarefas)
        elif opcao == '5':
            imprimir_tarefas(tarefas)
        elif opcao == '6':
            reimprimir_ultima_lista()
        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
