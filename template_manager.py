from src.models.content import db, ContentTemplate, ContentTopic
from datetime import datetime

class TemplateManager:
    """Gerencia templates de conteúdo e tópicos pré-definidos"""
    
    @staticmethod
    def initialize_default_templates():
        """Inicializa templates padrão no banco de dados"""
        
        # Template para artigos focado em PMEs
        article_template = ContentTemplate(
            name="Artigo Educativo - Recuperação Tributária para PMEs",
            content_type="article",
            template_content="""
# {titulo}

## Introdução
{introducao}

## O que sua PME precisa saber sobre {topico}
{conteudo_principal}

## Benefícios específicos para {setor_alvo}
{beneficios}

## Como implementar na sua empresa
{implementacao}

## Conclusão
{conclusao}

**Sua PME pode estar perdendo dinheiro com impostos pagos a maior!** Entre em contato conosco para uma análise gratuita e descubra quanto sua empresa pode recuperar.

📞 Agende uma conversa: [link]
📧 E-mail: contato@exemplo.com
            """.strip()
        )
        article_template.set_variables({
            "titulo": "Título do artigo",
            "introducao": "Parágrafo introdutório focado em PMEs",
            "topico": "Tópico principal",
            "conteudo_principal": "Conteúdo detalhado para PMEs",
            "setor_alvo": "Setor específico da PME",
            "beneficios": "Lista de benefícios para PMEs",
            "implementacao": "Passos práticos para PMEs",
            "conclusao": "Conclusão e CTA"
        })
        
        # Template para posts LinkedIn focado em PMEs
        linkedin_template = ContentTemplate(
            name="Post LinkedIn - Dica Tributária para PMEs",
            content_type="post",
            template_content="""
🎯 {titulo}

{conteudo_principal}

✅ Principais benefícios para PMEs:
{beneficios}

💡 Dica prática: {dica_pratica}

Sua PME já fez uma revisão tributária nos últimos 5 anos? 

Muitas pequenas e médias empresas deixam de recuperar milhares de reais em impostos pagos a maior.

👉 Quer saber quanto sua empresa pode recuperar? Mande uma DM!

#PME #PequenasEmpresas #RecuperacaoTributaria #PIS #COFINS #ICMS #GestaoFiscal #Contabilidade #EmpreendedorismoBrasil
            """.strip()
        )
        linkedin_template.set_variables({
            "titulo": "Título chamativo para PMEs",
            "conteudo_principal": "Conteúdo do post",
            "beneficios": "Lista de benefícios para PMEs",
            "dica_pratica": "Dica prática para PMEs"
        })
        
        # Template para posts Instagram focado em PMEs
        instagram_template = ContentTemplate(
            name="Post Instagram - Conteúdo Visual para PMEs",
            content_type="instagram_post",
            template_content="""
🚀 {titulo}

{conteudo_principal}

💰 {beneficio_financeiro}

📊 {estatistica_relevante}

👆 SALVE este post para não esquecer!

💬 Conta pra gente: sua empresa já recuperou créditos tributários?

#PME #PequenasEmpresas #RecuperacaoTributaria #DicasTributarias #EmpreendedorismoBrasil #GestaoFinanceira #Impostos #Contabilidade #NegociosProprios #MicroEmpresa
            """.strip()
        )
        instagram_template.set_variables({
            "titulo": "Título chamativo e visual",
            "conteudo_principal": "Conteúdo principal do post",
            "beneficio_financeiro": "Benefício financeiro específico",
            "estatistica_relevante": "Estatística ou dado relevante"
        })
        
        # Template para e-mail de prospecção focado em PMEs com identidade JusFiscal
        email_template = ContentTemplate(
            name="E-mail Prospecção JusFiscal - Análise Gratuita para PMEs",
            content_type="email",
            template_content="""
Assunto: {assunto}

Olá {nome_contato},

{introducao_personalizada}

Sabemos que PMEs do setor {setor} frequentemente têm oportunidades significativas de recuperação de créditos tributários, especialmente relacionados a:

• {oportunidade_1}
• {oportunidade_2}
• {oportunidade_3}

{proposta_valor}

Como especialistas em recuperação tributária para pequenas e médias empresas, a **JusFiscal** gostaria de oferecer uma análise gratuita e sem compromisso para identificar possíveis créditos na {nome_empresa}.

📊 **Nossa análise inclui:**
- Revisão dos últimos 5 anos de tributos
- Identificação de oportunidades específicas para seu setor
- Cálculo estimado dos valores recuperáveis
- Plano de ação personalizado

{call_to_action}

Atenciosamente,
**{nome_consultor}**
JusFiscal - Recuperação Tributária
📞 {contato}
🌐 www.jusfiscal.com.br

---
*P.S.: Muitas PMEs recuperam entre R$ 50.000 e R$ 500.000 em créditos tributários. Não deixe esse dinheiro parado na Receita Federal!*

*Esta mensagem foi enviada porque identificamos sua empresa como tendo potencial para recuperação de créditos tributários. Se não deseja mais receber nossas comunicações, responda com "DESCADASTRAR".*
            """.strip()
        )
        email_template.set_variables({
            "assunto": "Assunto do e-mail",
            "nome_contato": "Nome do contato",
            "introducao_personalizada": "Introdução personalizada para PME",
            "setor": "Setor da PME",
            "oportunidade_1": "Primeira oportunidade para PMEs",
            "oportunidade_2": "Segunda oportunidade para PMEs", 
            "oportunidade_3": "Terceira oportunidade para PMEs",
            "proposta_valor": "Proposta de valor específica para PMEs",
            "nome_empresa": "Nome da PME",
            "call_to_action": "Chamada para ação",
            "nome_consultor": "Nome do consultor",
            "contato": "Informações de contato"
        })
        
        # Template para e-mail de follow-up
        email_followup_template = ContentTemplate(
            name="E-mail Follow-up JusFiscal - PMEs",
            content_type="email_follow_up",
            template_content="""
Assunto: Re: Oportunidade de Recuperação Tributária - {nome_empresa}

Olá {nome_contato},

Espero que esteja tudo bem com vocês na {nome_empresa}!

Enviei uma mensagem há alguns dias sobre oportunidades de recuperação de créditos tributários para PMEs do setor {setor}, e gostaria de retomar nossa conversa.

Sei que o dia a dia é corrido, mas essa pode ser uma oportunidade importante para melhorar significativamente o fluxo de caixa da empresa.

**Preparei um material específico** com as principais oportunidades para empresas como a {nome_empresa}:

📋 **Checklist Tributário Gratuito:**
- ✅ Principais créditos recuperáveis para {setor}
- ✅ Documentos necessários
- ✅ Prazos importantes
- ✅ Estimativa de valores

{call_to_action}

Qualquer dúvida, estou à disposição!

Atenciosamente,
**{nome_consultor}**
JusFiscal - Recuperação Tributária
📞 {contato}

---
*P.S.: O prazo para recuperação de créditos é de 5 anos. Cada mês que passa, você pode estar perdendo oportunidades valiosas.*
            """.strip()
        )
        email_followup_template.set_variables({
            "nome_contato": "Nome do contato",
            "nome_empresa": "Nome da PME",
            "setor": "Setor da PME",
            "call_to_action": "Chamada para ação específica",
            "nome_consultor": "Nome do consultor",
            "contato": "Informações de contato"
        })
        
        # Adiciona templates ao banco se não existirem
        existing_templates = ContentTemplate.query.all()
        if not existing_templates:
            db.session.add(article_template)
            db.session.add(linkedin_template)
            db.session.add(instagram_template)
            db.session.add(email_template)
            db.session.add(email_followup_template)
            db.session.commit()
    
    @staticmethod
    def initialize_default_topics():
        """Inicializa tópicos padrão no banco de dados focados em PMEs"""
        
        topics = [
            {
                "topic": "Como PMEs podem recuperar ICMS na base de cálculo do PIS e COFINS",
                "category": "Recuperação de Créditos",
                "target_sectors": ["Comércio", "Indústria", "Serviços"],
                "keywords": ["ICMS", "PIS", "COFINS", "base de cálculo", "STF", "PME"],
                "priority": 5
            },
            {
                "topic": "Créditos de PIS e COFINS para PMEs do Lucro Real",
                "category": "Recuperação de Créditos",
                "target_sectors": ["Indústria", "Comércio"],
                "keywords": ["PIS", "COFINS", "Lucro Real", "não cumulatividade", "créditos", "PME"],
                "priority": 5
            },
            {
                "topic": "INSS sobre verbas indenizatórias: oportunidade para PMEs",
                "category": "Recuperação de Créditos",
                "target_sectors": ["Todos os setores"],
                "keywords": ["INSS", "verbas indenizatórias", "férias", "aviso prévio", "PME"],
                "priority": 4
            },
            {
                "topic": "Recuperação de IPI para pequenas indústrias",
                "category": "Recuperação de Créditos",
                "target_sectors": ["Indústria"],
                "keywords": ["IPI", "indústria", "insumos", "processo produtivo", "PME"],
                "priority": 4
            },
            {
                "topic": "5 anos para recuperar: PMEs não podem perder esse prazo",
                "category": "Legislação",
                "target_sectors": ["Todos os setores"],
                "keywords": ["prazo", "5 anos", "decadência", "CTN", "PME"],
                "priority": 5
            },
            {
                "topic": "Diagnóstico tributário gratuito para PMEs: como funciona",
                "category": "Processo",
                "target_sectors": ["Todos os setores"],
                "keywords": ["diagnóstico", "revisão fiscal", "auditoria", "gratuito", "PME"],
                "priority": 4
            },
            {
                "topic": "Como a recuperação tributária melhora o fluxo de caixa da PME",
                "category": "Benefícios",
                "target_sectors": ["Todos os setores"],
                "keywords": ["fluxo de caixa", "benefícios", "liquidez", "PME"],
                "priority": 5
            },
            {
                "topic": "Restituição vs Compensação: qual a melhor opção para PMEs",
                "category": "Processo",
                "target_sectors": ["Todos os setores"],
                "keywords": ["restituição", "compensação", "modalidades", "PME"],
                "priority": 3
            },
            {
                "topic": "Documentos que toda PME precisa ter para recuperar créditos",
                "category": "Processo",
                "target_sectors": ["Todos os setores"],
                "keywords": ["documentos", "SPED", "EFD", "DCTF", "PME"],
                "priority": 4
            },
            {
                "topic": "Cases de sucesso: PMEs que recuperaram milhares em impostos",
                "category": "Cases",
                "target_sectors": ["Todos os setores"],
                "keywords": ["casos de sucesso", "resultados", "exemplos", "PME"],
                "priority": 5
            },
            {
                "topic": "Simples Nacional vs Lucro Real: qual regime gera mais créditos",
                "category": "Planejamento",
                "target_sectors": ["Todos os setores"],
                "keywords": ["Simples Nacional", "Lucro Real", "regime tributário", "PME"],
                "priority": 4
            },
            {
                "topic": "Erros comuns que PMEs cometem na recuperação tributária",
                "category": "Educação",
                "target_sectors": ["Todos os setores"],
                "keywords": ["erros", "cuidados", "dicas", "PME"],
                "priority": 3
            }
        ]
        
        # Adiciona tópicos ao banco se não existirem
        existing_topics = ContentTopic.query.all()
        if not existing_topics:
            for topic_data in topics:
                topic = ContentTopic(
                    topic=topic_data["topic"],
                    category=topic_data["category"],
                    priority=topic_data["priority"]
                )
                topic.set_target_sectors(topic_data["target_sectors"])
                topic.set_keywords(topic_data["keywords"])
                db.session.add(topic)
            
            db.session.commit()
    
    @staticmethod
    def get_template_by_type(content_type: str):
        """Retorna template padrão por tipo de conteúdo"""
        return ContentTemplate.query.filter_by(content_type=content_type).first()
    
    @staticmethod
    def get_topics_by_sector(sector: str = None):
        """Retorna tópicos filtrados por setor"""
        if sector:
            topics = ContentTopic.query.all()
            filtered_topics = []
            for topic in topics:
                if sector in topic.get_target_sectors() or "Todos os setores" in topic.get_target_sectors():
                    filtered_topics.append(topic)
            return filtered_topics
        else:
            return ContentTopic.query.order_by(ContentTopic.priority.desc()).all()

