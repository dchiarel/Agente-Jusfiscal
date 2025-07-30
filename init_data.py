#!/usr/bin/env python3
"""
Script para inicializar dados padrão do sistema
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.services.template_manager import TemplateManager

def initialize_default_data():
    """Inicializa templates e tópicos padrão"""
    with app.app_context():
        print("Inicializando templates padrão...")
        TemplateManager.initialize_default_templates()
        print("Templates criados com sucesso!")
        
        print("Inicializando tópicos padrão...")
        TemplateManager.initialize_default_topics()
        print("Tópicos criados com sucesso!")
        
        print("Inicialização concluída!")

if __name__ == "__main__":
    initialize_default_data()

