import os
import io 
from functools import wraps
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

# Librerías de Google API
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload 

# --- CONSTANTES Y DICCIONARIOS ---

# Mapeo de IDs numéricos de YouTube a nombres legibles
YOUTUBE_CATEGORIES = {
    '1': 'Cine y animaciones',
    '2': 'Autos y vehículos',
    '10': 'Música',
    '15': 'Mascotas y animales',
    '17': 'Deportes',
    '19': 'Viajes y eventos',
    '20': 'Videojuegos',
    '22': 'Personas y blogs',
    '23': 'Comedia',
    '24': 'Entretenimiento',
    '25': 'Noticias y política',
    '26': 'Guías y estilo',
    '27': 'Educación',
    '28': 'Ciencia y tecnología',
    '29': 'Activismo y organizaciones'
}

# --- DECORADOR DE SEGURIDAD ---
def require_youtube_auth(view_func):
    """Decorador que verifica autenticación con YouTube OAuth"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'youtube_credentials' not in request.session:
            messages.warning(request, 'Debes autorizar el acceso a YouTube primero.')
            return redirect('videos:oauth_authorize')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- VISTAS DEL SISTEMA ---

def inicio(request):
    """Dashboard principal con estadísticas reales sumadas manualmente"""
    context = {
        'youtube_conectado': 'youtube_credentials' in request.session,
        'user_info': request.session.get('youtube_user_info', {}),
        'total_videos': 0,
        'total_views': 0,
        'total_likes': 0,
        'videos': []  
    }

    if context['youtube_conectado']:
        try:
            creds_data = request.session.get('youtube_credentials')
            credentials = Credentials(**creds_data)
            youtube = build('youtube', 'v3', credentials=credentials)

            ch_resp = youtube.channels().list(
                mine=True, 
                part='statistics,contentDetails'
            ).execute()

            if ch_resp.get('items'):
                channel = ch_resp['items'][0]
                context['total_videos'] = int(channel['statistics'].get('videoCount', 0))
                uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
                
                playlist_resp = youtube.playlistItems().list(
                    playlistId=uploads_playlist_id,
                    part='contentDetails',
                    maxResults=50
                ).execute()

                video_ids = [item['contentDetails']['videoId'] for item in playlist_resp.get('items', [])]
                
                if video_ids:
                    v_details = youtube.videos().list(
                        id=','.join(video_ids),
                        part='statistics'
                    ).execute()

                    sum_likes = 0
                    sum_views = 0
                    for v in v_details.get('items', []):
                        v_stats = v['statistics']
                        sum_views += int(v_stats.get('viewCount', 0))
                        sum_likes += int(v_stats.get('likeCount', 0))
                    
                    context['total_views'] = sum_views
                    context['total_likes'] = sum_likes

        except Exception as e:
            print(f"Error calculando métricas en inicio: {e}")

    return render(request, 'videos/inicio.html', context)


@require_youtube_auth
def subir_video(request):
    """Maneja la subida de videos a YouTube"""
    if request.method == 'POST' and request.FILES.get('video_file'):
        try:
            creds_data = request.session.get('youtube_credentials')
            credentials = Credentials(**creds_data)
            youtube = build('youtube', 'v3', credentials=credentials)

            body = {
                'snippet': {
                    'title': request.POST.get('titulo', 'Video de Ingeniería UTH'),
                    'description': request.POST.get('descripcion', 'Subido desde mi app de Django'),
                    'tags': ['UTH', 'Django', 'API'],
                    'categoryId': request.POST.get('categoria', '22') 
                },
                'status': {
                    'privacyStatus': request.POST.get('privacidad', 'private') 
                }
            }

            video_file = request.FILES['video_file']
            fh = io.BytesIO(video_file.read())
            media = MediaIoBaseUpload(fh, mimetype=video_file.content_type, resumable=True)

            request_api = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request_api.execute()
            messages.success(request, f"¡Video subido con éxito! ID: {response['id']}")
            return redirect('videos:mis_videos')

        except Exception as e:
            messages.error(request, f"Error al subir: {str(e)}")
            return redirect('videos:subir_video')

    context = {
        'youtube_conectado': True,
        'user_info': request.session.get('youtube_user_info', {}),
    }
    return render(request, 'videos/subir_video.html', context)


@require_youtube_auth
def mis_videos(request):
    """Lista detallada con totales y botones funcionales"""
    videos_list = []
    total_views_all = 0
    total_likes_all = 0
    total_comments_all = 0

    try:
        creds_data = request.session.get('youtube_credentials')
        credentials = Credentials(**creds_data)
        youtube = build('youtube', 'v3', credentials=credentials)
        
        channels_resp = youtube.channels().list(mine=True, part='contentDetails').execute()
        uploads_playlist_id = channels_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        res = youtube.playlistItems().list(
            playlistId=uploads_playlist_id,
            part='snippet,contentDetails',
            maxResults=50
        ).execute()
        
        video_ids = [item['contentDetails']['videoId'] for item in res.get('items', [])]

        if video_ids:
            stats_resp = youtube.videos().list(
                id=','.join(video_ids),
                part='snippet,statistics'
            ).execute()

            for item in stats_resp.get('items', []):
                v_stats = item['statistics']
                v_views = int(v_stats.get('viewCount', 0))
                v_likes = int(v_stats.get('likeCount', 0))
                v_comments = int(v_stats.get('commentCount', 0))
                
                total_views_all += v_views
                total_likes_all += v_likes
                total_comments_all += v_comments

                videos_list.append({
                    'id': item['id'],
                    'titulo': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', ''),
                    'vistas': v_views,
                    'likes': v_likes,
                    'comentarios': v_comments,
                    'fecha': item['snippet']['publishedAt'],
                    'url_youtube': f"https://www.youtube.com/watch?v={item['id']}" 
                })
            
    except Exception as e:
        print(f"Error cargando mis_videos: {e}")

    context = {
        'videos': videos_list,
        'total_vistas': total_views_all,
        'total_likes': total_likes_all,
        'total_comentarios': total_comments_all,
        'total_videos': len(videos_list),
        'youtube_conectado': True,
        'user_info': request.session.get('youtube_user_info', {}),
    }
    return render(request, 'videos/mis_videos.html', context)


def buscar_videos(request):
    """Búsqueda pública usando API Key"""
    query = request.GET.get('q', '')
    resultados = []
    if query:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        request_api = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=12
        )
        response = request_api.execute()
        resultados = response.get('items', [])

    context = {
        'query': query,
        'resultados': resultados,
        'youtube_conectado': 'youtube_credentials' in request.session,
    }
    return render(request, 'videos/buscar.html', context)


@require_youtube_auth
def detalle_video(request, video_id):
    """Muestra el reproductor y traduce el ID de categoría a nombre real"""
    video_data = {}
    try:
        creds_data = request.session.get('youtube_credentials')
        credentials = Credentials(**creds_data)
        youtube = build('youtube', 'v3', credentials=credentials)

        response = youtube.videos().list(
            id=video_id,
            part='snippet,statistics,contentDetails'
        ).execute()

        if response.get('items'):
            item = response['items'][0]
            cat_id = item['snippet'].get('categoryId', 'N/A')
            nombre_categoria = YOUTUBE_CATEGORIES.get(cat_id, f"Categoría {cat_id}")

            video_data = {
                'titulo': item['snippet']['title'],
                'descripcion': item['snippet']['description'],
                'vistas': item['statistics'].get('viewCount', 0),
                'likes': item['statistics'].get('likeCount', 0),
                'comentarios': item['statistics'].get('commentCount', 0),
                'fecha_publicacion': item['snippet']['publishedAt'],
                'canal_nombre': item['snippet']['channelTitle'],
                'canal_id': item['snippet']['channelId'],
                'categoria': nombre_categoria,
                'duracion': item['contentDetails'].get('duration', 'N/A'),
                'youtube_id': video_id,
                'url_video': f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        print(f"Error cargando detalle: {e}")

    context = {
        'video': video_data,
        'video_id': video_id,
        'youtube_conectado': True,
        'user_info': request.session.get('youtube_user_info', {}),
    }
    return render(request, 'videos/detalle_video.html', context)


# --- FLUJO OAUTH 2.0 (CORREGIDO PARA EVITAR MISMATCHING_STATE) ---

def oauth_authorize(request):
    """Inicia el flujo y fuerza el guardado del estado en la sesión"""
    try:
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=settings.YOUTUBE_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        request.session['oauth_state'] = state
        request.session.modified = True # CRÍTICO: Asegura que el state se guarde en la cookie
        return redirect(authorization_url)
    except Exception as e:
        messages.error(request, f'Error al iniciar OAuth: {str(e)}')
        return redirect('videos:inicio')


def oauth_callback(request):
    """Valida el estado para evitar CSRF Warning"""
    state = request.session.get('oauth_state')
    if not state:
        messages.error(request, 'La sesión de autenticación expiró. Inténtalo de nuevo.')
        return redirect('videos:inicio')
        
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=settings.YOUTUBE_SCOPES,
        state=state,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    try:
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        
        credentials = flow.credentials
        request.session['youtube_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        youtube = build('youtube', 'v3', credentials=credentials)
        channels_response = youtube.channels().list(
            mine=True,
            part='snippet,statistics'
        ).execute()
        
        if channels_response.get('items'):
            channel = channels_response['items'][0]
            request.session['youtube_user_info'] = {
                'channel_title': channel['snippet']['title'],
                'channel_id': channel['id'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'subscribers': channel['statistics'].get('subscriberCount', 'N/A')
            }
        
        messages.success(request, '¡Autenticación exitosa!')
        return redirect('videos:inicio')
    except Exception as e:
        messages.error(request, f'Error de validación: {str(e)}')
        return redirect('videos:inicio')


def oauth_logout(request):
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('videos:inicio')

def procesar_subida(request):
    return redirect('videos:subir_video')