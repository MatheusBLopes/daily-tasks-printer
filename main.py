import sys
import json
import os
from datetime import datetime
from escpos.printer import Usb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QInputDialog,
    QMessageBox, QHBoxLayout, QListWidgetItem, QCheckBox
)

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


def imprimir_lista(lista):
    try:
        p = Usb(0x6868, 0x0200)  # Ajuste aqui para sua impressora
        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y %H:%M")

        p.set(align='center', bold=True, double_height=True)
        p.text("Lista de Tarefas\n")
        p.set(align='center', bold=False)
        p.text(f"{data_hora}\n")
        p.set(align='left', width=1, height=1)

        for item in lista:
            p.text(f"[ ] {item['tarefa']}\n")
            if item.get("avaliar", False):
                p.text("[ ] Ruim   [ ] Médio   [ ] Bom\n")
        p.text("\n")
        p.cut()
    except Exception as e:
        QMessageBox.critical(None, "Erro de Impressão", f"Erro ao imprimir: {e}")


class JanelaTarefas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Tarefas")
        self.setMinimumWidth(400)
        self.tarefas = carregar_tarefas()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.lista = QListWidget()
        self.carregar_lista()

        layout.addWidget(self.lista)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Adicionar")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Remover")
        self.btn_print = QPushButton("Imprimir Selecionadas")
        self.btn_reprint = QPushButton("Reimprimir Última")

        self.btn_add.clicked.connect(self.adicionar_tarefa)
        self.btn_edit.clicked.connect(self.editar_tarefa)
        self.btn_delete.clicked.connect(self.remover_tarefa)
        self.btn_print.clicked.connect(self.imprimir_tarefas)
        self.btn_reprint.clicked.connect(self.reimprimir_lista)

        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_delete)
        layout.addLayout(btns)
        layout.addWidget(self.btn_print)
        layout.addWidget(self.btn_reprint)

        self.setLayout(layout)

    def carregar_lista(self):
        self.lista.clear()
        for tarefa in self.tarefas:
            item = QListWidgetItem(tarefa)
            item.setCheckState(False)
            self.lista.addItem(item)

    def adicionar_tarefa(self):
        texto, ok = QInputDialog.getText(self, "Nova Tarefa", "Digite a tarefa:")
        if ok and texto.strip():
            self.tarefas.append(texto.strip())
            salvar_tarefas(self.tarefas)
            self.carregar_lista()

    def editar_tarefa(self):
        item = self.lista.currentItem()
        if not item:
            return
        index = self.lista.row(item)
        texto, ok = QInputDialog.getText(self, "Editar Tarefa", "Atualizar tarefa:", text=item.text())
        if ok and texto.strip():
            self.tarefas[index] = texto.strip()
            salvar_tarefas(self.tarefas)
            self.carregar_lista()

    def remover_tarefa(self):
        item = self.lista.currentItem()
        if not item:
            return
        index = self.lista.row(item)
        confirm = QMessageBox.question(self, "Remover", "Deseja remover esta tarefa?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            del self.tarefas[index]
            salvar_tarefas(self.tarefas)
            self.carregar_lista()

    def imprimir_tarefas(self):
        lista_impressao = []
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            if item.checkState():
                avaliar = QMessageBox.question(
                    self, "Avaliação", f"Incluir avaliação para '{item.text()}'?",
                    QMessageBox.Yes | QMessageBox.No
                ) == QMessageBox.Yes
                lista_impressao.append({"tarefa": item.text(), "avaliar": avaliar})

        if not lista_impressao:
            QMessageBox.information(self, "Nenhuma Selecionada", "Nenhuma tarefa selecionada.")
            return

        imprimir_lista(lista_impressao)
        salvar_ultima_impressao(lista_impressao)
        QMessageBox.information(self, "Sucesso", "Tarefas impressas com sucesso.")

    def reimprimir_lista(self):
        lista = carregar_ultima_impressao()
        if not lista:
            QMessageBox.information(self, "Nada a imprimir", "Nenhuma impressão anterior encontrada.")
            return
        imprimir_lista(lista)
        QMessageBox.information(self, "Reimpressão", "Última lista reimpressa com sucesso.")


def main():
    app = QApplication(sys.argv)
    janela = JanelaTarefas()
    janela.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
