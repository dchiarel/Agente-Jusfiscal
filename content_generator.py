import openai
import json
from typing import Dict, List, Optional
from src.models.content import ContentTemplate, ContentTopic

class ContentGenerator:
    def __init__(self):
        self.client = openai.OpenAI()
    
    def generate_content(self, content_type: str, topic: str, target_sector: Optional[str] = None, template_id: Optional[int] = None) -> Dict:
        """
        Gera conteúdo automaticamente usando LLMs
        
        Args:
            content_type: Tipo de conteúdo ('article', 'post', 'email')
            topic: Tópico do conteúdo
            target_sector: Setor alvo (opcional)
            template_id: ID do template a ser usado (opcional)
        
        Returns:
            Dict com título, conteúdo e palavras-chave
        """
        
        # Busca template se fornecido
        template = None
        if template_id:
            template = ContentTemplate.query.get(template_id)
        
        # Constrói o prompt baseado no tipo de conteúdo
        prompt = self._build_prompt(content_type, topic, target_sector, template)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em recuperação de créditos tributários e marketing de conteúdo. Crie conteúdo informativo, preciso e envolvente para empresas brasileiras."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content_text = response.choices[0].message.content
            
            # Processa a resposta para extrair título, conteúdo e palavras-chave
            return self._parse_generated_content(content_text, content_type)
            
        except Exception as e:
            raise Exception(f"Erro ao gerar conteúdo: {str(e)}")
    
    def _build_prompt(self, content_type: str, topic: str, target_sector: Optional[str], template: Optional[ContentTemplate]) -> str:
        """Constrói o prompt para geração de conteúdo"""
        
        base_context = """
        Contexto: Recuperação de créditos tributários no Brasil
        
        Informações importantes:
        - Prazo de recuperação: 5 anos
        - Principais tributos recuperáveis: ICMS, PIS/COFINS, INSS, IPI, ISS, IRPJ/CSLL
        - Processo: diagnóstico, revisão documental, pedido formal, acompanhamento
        - Benefícios: melhoria do fluxo de caixa, conformidade fiscal, redução de custos
        """
        
        if content_type == 'article':
            prompt = f"""
            {base_context}
            
            Crie um artigo completo sobre: {topic}
            
            Estrutura desejada:
            - Título atrativo e otimizado para SEO
            - Introdução envolvente
            - 3-4 seções principais com subtítulos
            - Conclusão com call-to-action
            - Lista de 5-7 palavras-chave relevantes
            
            Público-alvo: {target_sector if target_sector else 'Empresas brasileiras em geral'}
            
            Formato de resposta:
            TÍTULO: [título do artigo]
            
            CONTEÚDO:
            [conteúdo completo do artigo]
            
            PALAVRAS-CHAVE: [palavra1, palavra2, palavra3, ...]
            """
            
        elif content_type == 'post':
            prompt = f"""
            {base_context}
            
            Crie um post para LinkedIn sobre: {topic}
            
            Características:
            - Máximo 1300 caracteres
            - Tom profissional mas acessível
            - Inclua hashtags relevantes
            - Call-to-action no final
            
            Público-alvo: {target_sector if target_sector else 'Profissionais e empresários brasileiros'}
            
            Formato de resposta:
            TÍTULO: [título do post]
            
            CONTEÚDO:
            [conteúdo do post com hashtags]
            
            PALAVRAS-CHAVE: [palavra1, palavra2, palavra3, ...]
            """
            
        elif content_type == 'email':
            prompt = f"""
            {base_context}
            
            Crie um e-mail de prospecção sobre: {topic}
            
            Características:
            - Assunto atrativo
            - Personalização para o setor
            - Foco nos benefícios
            - Call-to-action claro
            - Tom profissional e consultivo
            
            Público-alvo: {target_sector if target_sector else 'Empresas brasileiras'}
            
            Formato de resposta:
            TÍTULO: [assunto do e-mail]
            
            CONTEÚDO:
            [corpo do e-mail]
            
            PALAVRAS-CHAVE: [palavra1, palavra2, palavra3, ...]
            """
        
        # Se há template, adiciona instruções específicas
        if template:
            prompt += f"""
            
            Use o seguinte template como base:
            {template.template_content}
            
            Variáveis do template: {template.get_variables()}
            """
        
        return prompt
    
    def _parse_generated_content(self, content_text: str, content_type: str) -> Dict:
        """Processa o conteúdo gerado para extrair componentes"""
        
        lines = content_text.strip().split('\n')
        
        title = ""
        content = ""
        keywords = []
        
        current_section = None
        content_lines = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TÍTULO:'):
                title = line.replace('TÍTULO:', '').strip()
                current_section = 'title'
            elif line.startswith('CONTEÚDO:'):
                current_section = 'content'
            elif line.startswith('PALAVRAS-CHAVE:'):
                keywords_text = line.replace('PALAVRAS-CHAVE:', '').strip()
                keywords = [k.strip() for k in keywords_text.split(',')]
                current_section = 'keywords'
            elif current_section == 'content' and line:
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        
        # Se não conseguiu extrair título, usa a primeira linha
        if not title and content_lines:
            title = content_lines[0]
            content = '\n'.join(content_lines[1:]).strip()
        
        return {
            'title': title,
            'content': content,
            'keywords': keywords
        }
    
    def generate_content_ideas(self, target_sector: Optional[str] = None, count: int = 10) -> List[Dict]:
        """Gera ideias de conteúdo para um setor específico"""
        
        prompt = f"""
        Gere {count} ideias de conteúdo sobre recuperação de créditos tributários para o setor: {target_sector if target_sector else 'empresas em geral'}
        
        Para cada ideia, forneça:
        - Título/tópico
        - Tipo de conteúdo recomendado (artigo, post, email)
        - Breve descrição
        - Palavras-chave principais
        
        Formato JSON:
        [
            {{
                "titulo": "...",
                "tipo": "...",
                "descricao": "...",
                "palavras_chave": ["...", "..."]
            }}
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing de conteúdo tributário. Retorne apenas o JSON solicitado."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            content_text = response.choices[0].message.content
            return json.loads(content_text)
            
        except Exception as e:
            raise Exception(f"Erro ao gerar ideias de conteúdo: {str(e)}")

