# Integración con SortTime usando Selenium (navegador real)
import time
import re
from typing import Tuple, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

SORTTIME_BASE = "https://www.sorttime.co/Sorttime2/Oficina/PSV"


class SortTimeSeleniumClient:
    def __init__(self, headless: bool = True):
        """
        headless=True: navegador invisible (recomendado para servidor)
        headless=False: muestra el navegador (para debug)
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.authenticated = False
    
    def autenticar(self, usuario: str, clave: str) -> Tuple[bool, str]:
        """Autentica en SortTime usando navegador real"""
        try:
            print(f"🔐 Navegando a {SORTTIME_BASE}/Inicio.aspx")
            self.driver.get(f"{SORTTIME_BASE}/Inicio.aspx")
            time.sleep(2)
            
            # Esperar campos de login
            usuario_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "txtUsuario"))
            )
            clave_input = self.driver.find_element(By.ID, "txtClave")
            btn_ingresar = self.driver.find_element(By.ID, "btnIngresar")
            
            # Limpiar y escribir
            usuario_input.clear()
            usuario_input.send_keys(usuario)
            clave_input.clear()
            clave_input.send_keys(clave)
            
            print(f"📤 Enviando login para usuario: {usuario}")
            btn_ingresar.click()
            time.sleep(3)
            
            # Verificar login exitoso
            if "Empleado.aspx" in self.driver.current_url:
                self.authenticated = True
                print("✅ Autenticación exitosa")
                return True, "Autenticación exitosa"
            elif "Inicio.aspx" in self.driver.current_url:
                # Buscar mensaje de error
                try:
                    error_msg = self.driver.find_element(By.CLASS_NAME, "mensaje-error")
                    return False, f"Error: {error_msg.text}"
                except:
                    return False, "Usuario o contraseña incorrectos"
            else:
                return False, f"Redirección inesperada a {self.driver.current_url}"
                
        except Exception as e:
            return False, f"Error en autenticación: {str(e)[:100]}"
    
    def obtener_desprendibles(self) -> Optional[list]:
        """Obtiene la lista de desprendibles disponibles"""
        if not self.authenticated:
            return None
        
        try:
            # Ya estamos en Empleado.aspx después del login
            time.sleep(2)
            
            # Buscar la tabla de volantes de pago
            desprendibles = []
            
            # Intentar diferentes selectores
            tabla = None
            selectores = [
                "table#gvDesprendibles",
                "table.table",
                "table:contains('Año')",
                "table:contains('Mes')"
            ]
            
            for selector in selectores:
                try:
                    if selector.startswith("table:"):
                        # Selector con texto
                        pass
                    else:
                        tabla = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if tabla:
                            break
                except:
                    continue
            
            if tabla:
                filas = tabla.find_elements(By.TAG_NAME, "tr")
                for fila in filas[1:]:  # Saltar cabecera
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 4:
                        anio = celdas[0].text.strip()
                        mes = celdas[1].text.strip()
                        detalle = celdas[2].text.strip()
                        valor = celdas[3].text.strip()
                        
                        # Buscar enlace en las acciones
                        enlace = None
                        try:
                            btn_descargar = fila.find_element(By.TAG_NAME, "a")
                            if btn_descargar and btn_descargar.get_attribute("href"):
                                enlace = btn_descargar.get_attribute("href")
                        except:
                            pass
                        
                        desprendibles.append({
                            "anio": anio,
                            "mes": mes,
                            "detalle": detalle,
                            "valor": valor,
                            "url": enlace
                        })
            
            return desprendibles if desprendibles else None
            
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
                return d
        
        return None
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()


class SortTimeAPI:
    @staticmethod
    def obtener_enlace_desprendible(usuario: str, mes: str, anio: str, headless: bool = True) -> Tuple[bool, str, Optional[str]]:
        """
        Obtiene el enlace del desprendible usando Selenium
        """
        if not usuario or not mes:
            return False, "Faltan datos (usuario o mes)", None
        
        clave = usuario[-4:] if len(usuario) >= 4 else usuario
        
        client = SortTimeSeleniumClient(headless=headless)
        
        try:
            success, message = client.autenticar(usuario, clave)
            
            if not success:
                return False, message, None
            
            desprendible = client.obtener_desprendible(mes, anio)
            
            if desprendible and desprendible.get('url'):
                return True, f"Desprendible encontrado para {mes} {anio}", desprendible['url']
            elif desprendible:
                # Hay desprendible pero sin URL directa, necesitamos hacer clic
                return True, f"Desprendible de {mes} {anio} disponible. Necesita descarga manual.", None
            else:
                return False, f"No se encontró desprendible para {mes} {anio}", None
                
        finally:
            client.cerrar()
    
    @staticmethod
    def probar_conexion(usuario: str, headless: bool = False) -> Tuple[bool, str]:
        """Prueba de conexión (con navegador visible para debug)"""
        clave = usuario[-4:] if len(usuario) >= 4 else usuario
        
        client = SortTimeSeleniumClient(headless=headless)
        try:
            return client.autenticar(usuario, clave)
        finally:
            client.cerrar()
