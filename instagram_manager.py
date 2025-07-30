import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class InstagramManager:
    """Gerencia publicações no Instagram via Instagram Basic Display API e Graph API"""
    
    def __init__(self, access_token: str = None, page_id: str = None):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def publish_post(self, content: str, image_url: str = None, hashtags: List[str] = None) -> Dict:
        """
        Publica um post no Instagram
        
        Args:
            content: Texto do post
            image_url: URL da imagem (opcional)
            hashtags: Lista de hashtags (opcional)
        
        Returns:
            Dict com resultado da publicação
        """
        
        if not self.access_token or not self.page_id:
            return {'success': False, 'error': 'Configuração do Instagram incompleta'}
        
        # Prepara o conteúdo
        caption = content
        if hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
            caption = f"{content}\n\n{hashtag_text}"
        
        try:
            if image_url:
                # Publica post com imagem
                return self._publish_image_post(caption, image_url)
            else:
                # Publica post apenas com texto (story ou carousel)
                return self._publish_text_post(caption)
                
        except Exception as e:
            return {'success': False, 'error': f'Erro ao publicar no Instagram: {str(e)}'}
    
    def _publish_image_post(self, caption: str, image_url: str) -> Dict:
        """Publica post com imagem"""
        
        # Primeiro, cria o container de mídia
        media_data = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }
        
        media_response = requests.post(
            f"{self.base_url}/{self.page_id}/media",
            data=media_data
        )
        
        if media_response.status_code != 200:
            return {
                'success': False,
                'error': f'Erro ao criar mídia: {media_response.text}'
            }
        
        media_id = media_response.json().get('id')
        
        # Depois, publica o post
        publish_data = {
            'creation_id': media_id,
            'access_token': self.access_token
        }
        
        publish_response = requests.post(
            f"{self.base_url}/{self.page_id}/media_publish",
            data=publish_data
        )
        
        if publish_response.status_code == 200:
            post_id = publish_response.json().get('id')
            return {
                'success': True,
                'post_id': post_id,
                'url': f"https://www.instagram.com/p/{post_id}/"
            }
        else:
            return {
                'success': False,
                'error': f'Erro ao publicar: {publish_response.text}'
            }
    
    def _publish_text_post(self, caption: str) -> Dict:
        """Publica post apenas com texto (como story)"""
        
        # Para posts apenas com texto, podemos usar stories
        story_data = {
            'media_type': 'STORIES',
            'caption': caption,
            'access_token': self.access_token
        }
        
        response = requests.post(
            f"{self.base_url}/{self.page_id}/media",
            data=story_data
        )
        
        if response.status_code == 200:
            media_id = response.json().get('id')
            
            # Publica o story
            publish_data = {
                'creation_id': media_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(
                f"{self.base_url}/{self.page_id}/media_publish",
                data=publish_data
            )
            
            if publish_response.status_code == 200:
                return {
                    'success': True,
                    'story_id': publish_response.json().get('id'),
                    'message': 'Story publicado com sucesso'
                }
        
        return {
            'success': False,
            'error': f'Erro ao publicar story: {response.text}'
        }
    
    def create_carousel_post(self, items: List[Dict], caption: str, hashtags: List[str] = None) -> Dict:
        """
        Cria um post carousel (múltiplas imagens)
        
        Args:
            items: Lista de dicts com 'image_url' para cada item do carousel
            caption: Legenda do post
            hashtags: Lista de hashtags
        
        Returns:
            Dict com resultado da publicação
        """
        
        if not self.access_token or not self.page_id:
            return {'success': False, 'error': 'Configuração do Instagram incompleta'}
        
        # Prepara a legenda com hashtags
        full_caption = caption
        if hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{hashtag_text}"
        
        try:
            # Cria containers de mídia para cada item
            media_ids = []
            
            for item in items:
                media_data = {
                    'image_url': item['image_url'],
                    'is_carousel_item': True,
                    'access_token': self.access_token
                }
                
                response = requests.post(
                    f"{self.base_url}/{self.page_id}/media",
                    data=media_data
                )
                
                if response.status_code == 200:
                    media_ids.append(response.json().get('id'))
                else:
                    return {
                        'success': False,
                        'error': f'Erro ao criar item do carousel: {response.text}'
                    }
            
            # Cria o container do carousel
            carousel_data = {
                'media_type': 'CAROUSEL',
                'children': ','.join(media_ids),
                'caption': full_caption,
                'access_token': self.access_token
            }
            
            carousel_response = requests.post(
                f"{self.base_url}/{self.page_id}/media",
                data=carousel_data
            )
            
            if carousel_response.status_code == 200:
                carousel_id = carousel_response.json().get('id')
                
                # Publica o carousel
                publish_data = {
                    'creation_id': carousel_id,
                    'access_token': self.access_token
                }
                
                publish_response = requests.post(
                    f"{self.base_url}/{self.page_id}/media_publish",
                    data=publish_data
                )
                
                if publish_response.status_code == 200:
                    post_id = publish_response.json().get('id')
                    return {
                        'success': True,
                        'post_id': post_id,
                        'url': f"https://www.instagram.com/p/{post_id}/"
                    }
            
            return {
                'success': False,
                'error': f'Erro ao publicar carousel: {carousel_response.text}'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Erro ao criar carousel: {str(e)}'}
    
    def get_account_info(self) -> Dict:
        """Retorna informações da conta do Instagram"""
        
        if not self.access_token or not self.page_id:
            return {'success': False, 'error': 'Configuração do Instagram incompleta'}
        
        try:
            response = requests.get(
                f"{self.base_url}/{self.page_id}",
                params={
                    'fields': 'id,username,account_type,media_count,followers_count',
                    'access_token': self.access_token
                }
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'account_info': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro ao obter informações da conta: {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Erro ao conectar com Instagram: {str(e)}'}
    
    def get_recent_posts(self, limit: int = 10) -> Dict:
        """Retorna posts recentes da conta"""
        
        if not self.access_token or not self.page_id:
            return {'success': False, 'error': 'Configuração do Instagram incompleta'}
        
        try:
            response = requests.get(
                f"{self.base_url}/{self.page_id}/media",
                params={
                    'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                    'limit': limit,
                    'access_token': self.access_token
                }
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'posts': response.json().get('data', [])
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro ao obter posts: {response.text}'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Erro ao conectar com Instagram: {str(e)}'}
    
    @staticmethod
    def generate_hashtags_for_tax_content(content_type: str = "general") -> List[str]:
        """Gera hashtags relevantes para conteúdo tributário"""
        
        base_hashtags = [
            "recuperacaotributaria", "creditostributarios", "impostos", 
            "contabilidade", "gestaofinanceira", "pme", "pequenasempresas",
            "medias empresas", "tributacao", "fiscalizacao"
        ]
        
        specific_hashtags = {
            "pis_cofins": ["pis", "cofins", "naocomulatividade", "creditos"],
            "icms": ["icms", "substituicaotributaria", "basedeCalculo"],
            "inss": ["inss", "verbasIndenizatorias", "folhapagamento"],
            "general": ["dicas tributarias", "planejamentotributario", "consultoriatributaria"]
        }
        
        hashtags = base_hashtags.copy()
        if content_type in specific_hashtags:
            hashtags.extend(specific_hashtags[content_type])
        else:
            hashtags.extend(specific_hashtags["general"])
        
        return hashtags[:30]  # Instagram permite até 30 hashtags

