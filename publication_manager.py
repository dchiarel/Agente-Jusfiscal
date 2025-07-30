import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.publication import db, PublicationChannel, ScheduledPublication, PublicationLog
from src.models.content import GeneratedContent
from src.services.instagram_manager import InstagramManager

class PublicationManager:
    """Gerencia publicações em diferentes canais"""
    
    def __init__(self):
        pass
    
    def publish_content(self, content_id: int, channel_id: int) -> Dict:
        """
        Publica conteúdo em um canal específico
        
        Args:
            content_id: ID do conteúdo a ser publicado
            channel_id: ID do canal de publicação
        
        Returns:
            Dict com resultado da publicação
        """
        
        content = GeneratedContent.query.get(content_id)
        channel = PublicationChannel.query.get(channel_id)
        
        if not content or not channel:
            return {'success': False, 'error': 'Conteúdo ou canal não encontrado'}
        
        if not channel.is_active:
            return {'success': False, 'error': 'Canal inativo'}
        
        try:
            if channel.channel_type == 'linkedin':
                result = self._publish_to_linkedin(content, channel)
            elif channel.channel_type == 'instagram':
                result = self._publish_to_instagram(content, channel)
            elif channel.channel_type == 'wordpress':
                result = self._publish_to_wordpress(content, channel)
            elif channel.channel_type == 'email':
                result = self._send_email(content, channel)
            else:
                return {'success': False, 'error': 'Tipo de canal não suportado'}
            
            # Log da publicação
            log = PublicationLog(
                content_id=content_id,
                channel_id=channel_id,
                publication_status='success' if result['success'] else 'failed',
                publication_url=result.get('url'),
                error_message=result.get('error')
            )
            
            if 'response_data' in result:
                log.set_response_data(result['response_data'])
            
            db.session.add(log)
            
            # Atualiza status do conteúdo se publicado com sucesso
            if result['success']:
                content.status = 'published'
                content.published_at = datetime.utcnow()
            
            db.session.commit()
            
            return result
            
        except Exception as e:
            # Log de erro
            log = PublicationLog(
                content_id=content_id,
                channel_id=channel_id,
                publication_status='failed',
                error_message=str(e)
            )
            db.session.add(log)
            db.session.commit()
            
            return {'success': False, 'error': str(e)}
    
    def _publish_to_linkedin(self, content: GeneratedContent, channel: PublicationChannel) -> Dict:
        """Publica conteúdo no LinkedIn"""
        
        config = channel.get_api_config()
        access_token = config.get('access_token')
        person_id = config.get('person_id')
        
        if not access_token or not person_id:
            return {'success': False, 'error': 'Configuração do LinkedIn incompleta'}
        
        # Prepara o conteúdo para LinkedIn
        post_text = f"{content.title}\n\n{content.content}"
        
        # Limita o tamanho do post (LinkedIn tem limite de caracteres)
        if len(post_text) > 1300:
            post_text = post_text[:1297] + "..."
        
        # Adiciona hashtags se disponível
        keywords = content.get_keywords()
        if keywords:
            hashtags = " ".join([f"#{keyword.replace(' ', '')}" for keyword in keywords[:5]])
            post_text += f"\n\n{hashtags}"
        
        # Dados para a API do LinkedIn
        post_data = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                post_id = response_data.get('id')
                post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                
                return {
                    'success': True,
                    'url': post_url,
                    'response_data': response_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro na API do LinkedIn: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Erro ao conectar com LinkedIn: {str(e)}'}
    
    def _publish_to_instagram(self, content: GeneratedContent, channel: PublicationChannel) -> Dict:
        """Publica conteúdo no Instagram"""
        
        config = channel.get_api_config()
        access_token = config.get('access_token')
        page_id = config.get('page_id')
        
        if not access_token or not page_id:
            return {'success': False, 'error': 'Configuração do Instagram incompleta'}
        
        instagram_manager = InstagramManager(access_token, page_id)
        
        # Prepara o conteúdo para Instagram
        post_text = f"{content.title}\n\n{content.content}"
        
        # Limita o tamanho do post (Instagram tem limite de caracteres)
        if len(post_text) > 2200:
            post_text = post_text[:2197] + "..."
        
        # Gera hashtags específicas para conteúdo tributário
        hashtags = InstagramManager.generate_hashtags_for_tax_content()
        
        # Adiciona hashtags das keywords do conteúdo
        keywords = content.get_keywords()
        if keywords:
            for keyword in keywords[:5]:
                clean_keyword = keyword.replace(' ', '').lower()
                if clean_keyword not in hashtags:
                    hashtags.append(clean_keyword)
        
        # Verifica se há imagem configurada no canal
        image_url = config.get('default_image_url')
        
        try:
            if image_url:
                result = instagram_manager.publish_post(
                    content=post_text,
                    image_url=image_url,
                    hashtags=hashtags[:30]  # Instagram permite até 30 hashtags
                )
            else:
                # Publica como story se não há imagem
                result = instagram_manager.publish_post(
                    content=post_text,
                    hashtags=hashtags[:30]
                )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'Erro ao publicar no Instagram: {str(e)}'}
    
    def _publish_to_wordpress(self, content: GeneratedContent, channel: PublicationChannel) -> Dict:
        """Publica conteúdo no WordPress"""
        
        config = channel.get_api_config()
        site_url = config.get('site_url')
        username = config.get('username')
        password = config.get('password')  # Application password
        
        if not all([site_url, username, password]):
            return {'success': False, 'error': 'Configuração do WordPress incompleta'}
        
        # Dados para a API do WordPress
        post_data = {
            'title': content.title,
            'content': content.content,
            'status': 'publish',
            'categories': [1],  # Categoria padrão
            'tags': content.get_keywords()
        }
        
        try:
            response = requests.post(
                f'{site_url}/wp-json/wp/v2/posts',
                auth=(username, password),
                json=post_data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                post_url = response_data.get('link')
                
                return {
                    'success': True,
                    'url': post_url,
                    'response_data': response_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro na API do WordPress: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Erro ao conectar com WordPress: {str(e)}'}
    
    def _send_email(self, content: GeneratedContent, channel: PublicationChannel) -> Dict:
        """Envia conteúdo por e-mail"""
        
        config = channel.get_api_config()
        
        # Aqui você pode integrar com serviços como SendGrid, Mailchimp, etc.
        # Por enquanto, retorna sucesso simulado
        
        return {
            'success': True,
            'message': 'E-mail enviado com sucesso (simulado)'
        }
    
    def schedule_publication(self, content_id: int, channel_id: int, scheduled_time: datetime) -> Dict:
        """Agenda uma publicação"""
        
        scheduled_pub = ScheduledPublication(
            content_id=content_id,
            channel_id=channel_id,
            scheduled_time=scheduled_time
        )
        
        db.session.add(scheduled_pub)
        db.session.commit()
        
        return {
            'success': True,
            'scheduled_id': scheduled_pub.id,
            'message': 'Publicação agendada com sucesso'
        }
    
    def process_scheduled_publications(self):
        """Processa publicações agendadas que estão prontas"""
        
        now = datetime.utcnow()
        
        scheduled_pubs = ScheduledPublication.query.filter(
            ScheduledPublication.scheduled_time <= now,
            ScheduledPublication.status == 'scheduled'
        ).all()
        
        results = []
        
        for pub in scheduled_pubs:
            try:
                result = self.publish_content(pub.content_id, pub.channel_id)
                
                if result['success']:
                    pub.status = 'published'
                    pub.published_at = datetime.utcnow()
                    pub.publication_url = result.get('url')
                else:
                    pub.status = 'failed'
                    pub.error_message = result.get('error')
                
                db.session.commit()
                results.append({
                    'scheduled_id': pub.id,
                    'success': result['success'],
                    'error': result.get('error')
                })
                
            except Exception as e:
                pub.status = 'failed'
                pub.error_message = str(e)
                db.session.commit()
                
                results.append({
                    'scheduled_id': pub.id,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_publication_stats(self, days: int = 30) -> Dict:
        """Retorna estatísticas de publicação"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_publications = PublicationLog.query.filter(
            PublicationLog.published_at >= start_date
        ).count()
        
        successful_publications = PublicationLog.query.filter(
            PublicationLog.published_at >= start_date,
            PublicationLog.publication_status == 'success'
        ).count()
        
        failed_publications = PublicationLog.query.filter(
            PublicationLog.published_at >= start_date,
            PublicationLog.publication_status == 'failed'
        ).count()
        
        success_rate = (successful_publications / total_publications * 100) if total_publications > 0 else 0
        
        return {
            'total_publications': total_publications,
            'successful_publications': successful_publications,
            'failed_publications': failed_publications,
            'success_rate': round(success_rate, 2),
            'period_days': days
        }

