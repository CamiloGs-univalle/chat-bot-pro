# Integración con SortTime - Portal de empleados PSV
import cloudscraper
from bs4 import BeautifulSoup
from typing import Optional, Dict, Tuple
import re
import time
import json

SORTTIME_BASE = "https://www.sorttime.co/Sorttime2/Oficina/PSV"

# Headers de navegador real
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


class SortTimeClient:
    def __init__(self):
        # Usar cloudscraper para evadir bloqueos
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.scraper.headers.update(HEADERS)
        self.authenticated = False
        self.cedula = None
    
    def autenticar(self, cedula: str, clave: str) -> Tuple[bool, str]:
        """Autentica en SortTime con evasión de bloqueos"""
        try:
            login_url = f"{SORTTIME_BASE}/Inicio.aspx"
            print(f"🔐 Conectando a {login_url}")
            
            # Obtener página de login
            response = self.scraper.get(login_url, timeout=30)
            
            if response.status_code != 200:
                return False, f"Error HTTP {response.status_code}"
            
            print(f"✅ Página cargada, status: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer campos ASP.NET
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_value = viewstate.get('value', '') if viewstate else ''
            
            viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            viewstate_generator_value = viewstate_generator.get('value', '') if viewstate_generator else ''
            
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
            event_validation_value = event_validation.get('value', '') if event_validation else ''
            
            # Datos del formulario
            data = {
                '__VIEWSTATE': viewstate_value,
                '__VIEWSTATEGENERATOR': viewstate_generator_value,
                '__EVENTVALIDATION': event_validation_value,
                'txtUsuario': cedula,
                'txtClave': clave,
                'btnIngresar': 'Ingresar',
            }
            
            print(f"📤 Enviando login para cédula: {cedula}")
            
            # Enviar login
            response = self.scraper.post(login_url, data=data, timeout=30)
            
            # Verificar login exitoso
            if "Empleado.aspx" in response.url:
                self.authenticated = True
                self.cedula = cedula
                print("✅ Autenticación exitosa")
                return True, "Autenticación exitosa"
            
            if "CerrarSesion" in response.text or "Bienvenido" in response.text:
                self.authenticated = True
                self.cedula = cedula
                print("✅ Autenticación exitosa")
                return True, "Autenticación exitosa"
            
            # Verificar mensaje de error
            if "usuario" in response.text.lower() and "contraseña" in response.text.lower():
                return False, "Cédula o contraseña incorrectas"
            
            if "bloqueado" in response.text.lower():
                return False, "Usuario bloqueado"
            
            return False, "No se pudo autenticar"
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, f"Error: {str(e)[:100]}"
    
    def obtener_desprendibles(self) -> Optional[list]:
        """Obtiene la lista de desprendibles disponibles"""
        if not self.authenticated:
            return None
        
        try:
            desprendibles_url = f"{SORTTIME_BASE}/Empleado.aspx"
            response = self.scraper.get(desprendibles_url, timeout=30)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            desprendibles = []
            
            # Buscar la tabla de volantes de pago
            tabla = soup.find('table', {'class': 'table'})
            if not tabla:
                tabla = soup.find('table', {'id': 'gvDesprendibles'})
            
            if tabla:
                filas = tabla.find_all('tr')
                for fila in filas[1:]:  # Saltar cabecera
                    celdas = fila.find_all('td')
                    if len(celdas) >= 3:
                        anio = celdas[0].get_text().strip()
                        mes = celdas[1].get_text().strip()
                        detalle = celdas[2].get_text().strip()
                        
                        # Buscar enlace en las acciones
                        enlace = fila.find('a')
                        url = None
                        if enlace and enlace.get('href'):
                            url = enlace['href']
                            if not url.startswith('http'):
                                url = SORTTIME_BASE + '/' + url.lstrip('/')
                        
                        desprendibles.append({
                            "anio": anio,
                            "mes": mes,
                            "detalle": detalle,
                            "url": url
                        })
            
            return desprendibles
            
        except Exception as e:
            print(f"Error obteniendo desprendibles: {e}")
            return None
    
    def obtener_desprendible(self, mes: str, anio: str) -> Optional[Dict]:
        """Obtiene un desprendible específico"""
        desprendibles = self.obtener_desprendibles()
        
        if not desprendibles:
            return None
        
        # Normalizar mes (mayo -> 05)
        meses_numeros = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }
        
        mes_numero = meses_numeros.get(mes.lower(), mes)
        
        for d in desprendibles:
            if d['anio'] == anio and (d['mes'] == mes_numero or d['mes'].lower() == mes.lower()):
                return {
                    "url": d['url'],
                    "nombre": f"Desprendible_{mes}_{anio}.pdf",
                    "detalle": d['detalle']
                }
        
        return None


class SortTimeAPI:
    @staticmethod
    def obtener_enlace_desprendible(cedula: str, mes: str, anio: str) -> Tuple[bool, str, Optional[str]]:
        """Obtiene el enlace del desprendible"""
        if not cedula or not mes:
            return False, "Faltan datos (cédula o mes)", None
        
        clave = cedula[-4:] if len(cedula) >= 4 else cedula
        
        print(f"🔐 Intentando autenticar cédula: {cedula}")
        
        client = SortTimeClient()
        success, message = client.autenticar(cedula, clave)
        
        if not success:
            return False, message, None
        
        desprendible = client.obtener_desprendible(mes, anio)
        
        if desprendible and desprendible.get('url'):
            return True, f"Desprendible encontrado para {mes} {anio}", desprendible['url']
        
        return False, f"No se encontró desprendible para {mes} {anio}", None
    
    @staticmethod
    def probar_conexion(cedula: str) -> Tuple[bool, str]:
        """Prueba de conexión básica"""
        clave = cedula[-4:] if len(cedula) >= 4 else cedula
        
        client = SortTimeClient()
        return client.autenticar(cedula, clave)
