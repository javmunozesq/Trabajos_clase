# Hecho por Javier Muñoz
# Este script lee archivos de texto con facturas desde una carpeta
# y genera un script SQL para insertar los datos en una base de datos MySQL

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_insert_from_tickets.py

Lee archivos .txt (tickets) en una carpeta y genera InsertUnderlineTicket.sql
con sentencias INSERT para poblar la base de datos MariaDB/MySQL diseñada.

Uso:
    python build_insert_from_tickets.py path_a_carpeta_facturas/

Salida:
    InsertUnderlineTicket.sql
    parse_log.txt (resumen de avisos/errores durante el parseo)
"""

import sys
import re
import os
from pathlib import Path
from datetime import datetime
import unicodedata
from typing import Optional, Dict, Any, List, Tuple

# ---------- Utilidades y normalización ----------

def sql_escape(s: Optional[str]) -> str:
    """Escapa una cadena para usar en SQL dentro de comillas simples.
    Si s es None, devuelve 'NULL' (sin comillas)."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def normalize_text(s: str) -> str:
    """Normalización básica de texto para deduplicación:
    - trims
    - minúsculas
    - elimina acentos
    - reduce múltiples espacios"""
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'\s+', ' ', s)
    return s

def parse_number(s: str) -> Optional[float]:
    """Convierte una cadena numérica con coma o punto en float.
    Devuelve None si no es convertible."""
    if s is None:
        return None
    s = s.strip()
    if s == '':
        return None
    # eliminar símbolos de euro y espacios
    s = s.replace('€', '').replace('EUR', '').replace(' ', '')
    s = s.replace(',', '.')  # aceptar coma como separador decimal
    try:
        return float(s)
    except Exception:
        return None

# ---------- Parsing de líneas de producto ----------

# Regex principal para líneas: cantidad descripcion importe(€)
LINEA_REGEX = re.compile(
    r'^\s*(?P<cantidad>[\d]+(?:[.,]\d+)?)\s+(?P<descripcion>.+?)\s+(?P<importe>[\d]+(?:[.,]\d+)?)\s*(?:€)?\s*$'
)

# Variante cuando no hay cantidad explícita al principio (p. ej. "Descripcion  3.50 €")
LINEA_SIN_CANTIDAD = re.compile(
    r'^\s*(?P<descripcion>[^\d\n].*?)\s+(?P<importe>[\d]+(?:[.,]\d+)?)\s*(?:€)?\s*$'
)

UNIT_IN_PAREN = re.compile(r'\((?P<unidad>[a-zA-Z0-9%]+)\)')  # extrae unidades en paréntesis

def parse_linea_producto(line: str) -> Optional[Dict[str, Any]]:
    """Intenta extraer cantidad, descripcion, unidad, importe y precio_unitario de una línea.
    Devuelve dict con keys: cantidad (float), descripcion (raw), descripcion_norm,
    unidad (opcional), importe (float), precio_unitario (float or None).
    Devuelve None si no se interpreta como línea de producto."""
    m = LINEA_REGEX.match(line)
    if m:
        cantidad_raw = m.group('cantidad')
        descripcion_raw = m.group('descripcion')
        importe_raw = m.group('importe')
    else:
        m2 = LINEA_SIN_CANTIDAD.match(line)
        if m2:
            cantidad_raw = None
            descripcion_raw = m2.group('descripcion')
            importe_raw = m2.group('importe')
        else:
            return None

    cantidad = parse_number(cantidad_raw) if cantidad_raw is not None else 1.0
    importe = parse_number(importe_raw)
    descripcion = descripcion_raw.strip()

    unidad = None
    up = UNIT_IN_PAREN.search(descripcion)
    if up:
        unidad = up.group('unidad').lower()
        descripcion = re.sub(r'\s*\(' + re.escape(up.group('unidad')) + r'\)\s*', ' ', descripcion).strip()
    # intentar extraer sufijos como '250g', '1kg', '12u' al final de la descripción
    suf_match = re.search(r'(\d+\s?(g|kg|l|ml|u|un|unidad|pack))$', descripcion.lower())
    if suf_match and unidad is None:
        unidad = suf_match.group(1).strip()

    # calcular precio_unitario si posible
    precio_unitario = None
    if cantidad and cantidad != 0 and importe is not None:
        try:
            precio_unitario = round(importe / float(cantidad), 4)
        except Exception:
            precio_unitario = None

    descripcion_norm = normalize_text(descripcion)

    return {
        'cantidad': float(cantidad) if cantidad is not None else 1.0,
        'descripcion': descripcion,
        'descripcion_norm': descripcion_norm,
        'unidad': unidad,
        'importe': importe,
        'precio_unitario': precio_unitario
    }

# ---------- Parsing de ticket completo ----------

DATE_REGEX = re.compile(r'Fecha\s*[:\-]?\s*(?P<fecha>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', re.IGNORECASE)
HOUR_REGEX = re.compile(r'Hora\s*[:\-]?\s*(?P<hora>\d{1,2}:\d{2})', re.IGNORECASE)
CAJERO_REGEX = re.compile(r'Cajero\s*[:\-]?\s*(?P<codigo>\d+)\s*-\s*(?P<nombre>.+)', re.IGNORECASE)
TICKET_REGEX = re.compile(r'Ticket\s*[:\-]?\s*(?P<ticket>\d+)', re.IGNORECASE)
SUBTOTAL_REGEX = re.compile(r'SUBTOTAL\s+([\d\.,]+)\s*(?:€)?', re.IGNORECASE)
IVA_REGEX = re.compile(r'IVA\s*(?:\((?P<pct>[\d\.,]+)%\))?\s*[\)\:]?\s*([\d\.,]+)\s*(?:€)?', re.IGNORECASE)
TOTAL_REGEX = re.compile(r'TOTAL(?:\s+A\s+PAGAR)?\s+([\d\.,]+)\s*(?:€)?', re.IGNORECASE)
FORMA_PAGO_REGEX = re.compile(r'FORMA DE PAGO\s*[:\-]?\s*(?P<metodo>[A-Z0-9 ]+)', re.IGNORECASE)
AUTORIZACION_REGEX = re.compile(r'Autorizaci[oó]n\s*[:\-]?\s*(?P<auth>\d+)', re.IGNORECASE)

def parse_ticket(path: Path, log_warnings: List[str]) -> Optional[Dict[str, Any]]:
    """Parsea un archivo .txt y devuelve una estructura dict con sucursal, empleado,
    ticket (numero, fecha, hora, subtotal, iva, iva_pct, total), lineas (lista) y pago.
    Si el archivo no contiene datos válidos retornará None (y añade mensaje a log)."""
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding='latin-1')
        except Exception as e:
            log_warnings.append(f"{path.name}: no se pudo leer - {e}")
            return None
    if not text.strip():
        log_warnings.append(f"{path.name}: fichero vacío.")
        return None

    lines = [ln.rstrip() for ln in text.splitlines()]
    data = {
        'sucursal': {},
        'empleado': {},
        'ticket': {},
        'lineas': [],
        'pago': {}
    }

    # Sucursal: intentar extraer las primeras líneas como nombre y direccion
    # heurística: nombre en la primera línea no vacía
    header_lines = [ln for ln in lines[:6] if ln.strip()]
    if header_lines:
        data['sucursal']['nombre'] = header_lines[0].strip()
        if len(header_lines) > 1:
            data['sucursal']['direccion'] = header_lines[1].strip()
        else:
            data['sucursal']['direccion'] = None
    else:
        data['sucursal']['nombre'] = None
        data['sucursal']['direccion'] = None

    # Buscar cabecera con fecha, hora, cajero, ticket
    for ln in lines:
        if 'fecha' in ln.lower() and 'ticket' not in ln.lower():
            m = DATE_REGEX.search(ln)
            if m:
                raw = m.group('fecha')
                # normalizar fecha a ISO YYYY-MM-DD
                try:
                    fecha_dt = datetime.strptime(raw, '%d/%m/%Y')
                except Exception:
                    try:
                        fecha_dt = datetime.strptime(raw, '%d-%m-%Y')
                    except Exception:
                        fecha_dt = None
                data['ticket']['fecha'] = fecha_dt.date().isoformat() if fecha_dt else None
        if 'hora' in ln.lower():
            m = HOUR_REGEX.search(ln)
            if m:
                data['ticket']['hora'] = m.group('hora')
        if 'cajero' in ln.lower():
            m = CAJERO_REGEX.search(ln)
            if m:
                data['empleado']['codigo'] = m.group('codigo').strip()
                data['empleado']['nombre'] = m.group('nombre').strip()
            else:
                # tratar caso en que solo haya código sin nombre
                m2 = re.search(r'Cajero\s*[:\-]?\s*(\d+)', ln, re.IGNORECASE)
                if m2:
                    data['empleado']['codigo'] = m2.group(1).strip()
                    data['empleado']['nombre'] = None
        if 'ticket' in ln.lower():
            m = TICKET_REGEX.search(ln)
            if m:
                data['ticket']['numero'] = m.group('ticket').strip()

    # Extraer totales y pago (se buscan en todo el fichero)
    for ln in lines:
        if 'subtotal' in ln.lower():
            m = SUBTOTAL_REGEX.search(ln)
            if m:
                data['ticket']['subtotal'] = parse_number(m.group(1))
        if 'iva' in ln.lower():
            m = IVA_REGEX.search(ln)
            if m:
                pct_raw = m.group('pct')
                val_raw = m.group(2)
                data['ticket']['iva'] = parse_number(val_raw)
                data['ticket']['iva_pct'] = parse_number(pct_raw) if pct_raw else None
        if 'total' in ln.lower():
            # evitar capturar SUBTOTAL como TOTAL; se usa regex para evitar
            m = TOTAL_REGEX.search(ln)
            if m:
                data['ticket']['total'] = parse_number(m.group(1))
        if 'forma de pago' in ln.lower():
            m = FORMA_PAGO_REGEX.search(ln)
            if m:
                data['pago']['metodo'] = m.group('metodo').strip()
        if 'autoriz' in ln.lower():
            m = AUTORIZACION_REGEX.search(ln)
            if m:
                data['pago']['autorizacion'] = m.group('auth').strip()

    # --- Selección robusta del rango de líneas a parsear ---
    parse_range = range(len(lines))

    line_count = 0
    for idx in parse_range:
        ln = lines[idx]
        # Omitir líneas vacías y separadores de guiones
        if ln.strip() == "" or re.match(r'^\s*-{3,}\s*$', ln):
            continue
        # usar la versión de parser más tolerante si existe
        parsed = parse_linea_producto_v2(ln) if 'parse_linea_producto_v2' in globals() else parse_linea_producto(ln)
        if parsed:
            data['lineas'].append(parsed)
            line_count += 1

    if line_count == 0:
        log_warnings.append(f"{path.name}: no se detectaron líneas de producto.")

    # Validaciones y normalizaciones finales
    if 'fecha' not in data['ticket'] or not data['ticket'].get('fecha'):
        log_warnings.append(f"{path.name}: fecha no detectada.")
        data['ticket']['fecha'] = None
    if 'numero' not in data['ticket'] or not data['ticket'].get('numero'):
        log_warnings.append(f"{path.name}: número de ticket no detectado.")
        data['ticket']['numero'] = None
    if 'codigo' not in data['empleado'] or not data['empleado'].get('codigo'):
        placeholder = f"UNKNOWN_{path.stem}"
        log_warnings.append(f"{path.name}: cajero no detectado, usando {placeholder}.")
        data['empleado']['codigo'] = placeholder
        data['empleado']['nombre'] = None

    for k in ('subtotal', 'iva', 'total'):
        if k in data['ticket']:
            data['ticket'][k] = float(data['ticket'][k]) if data['ticket'][k] is not None else None
    return data


    line_count = 0
    for idx in parse_range:
        if idx < 0 or idx >= len(lines):
            continue
        ln = lines[idx]
        parsed = parse_linea_producto(ln)
        if parsed:
            data['lineas'].append(parsed)
            line_count += 1
    if line_count == 0:
        log_warnings.append(f"{path.name}: no se detectaron líneas de producto.")
        # No retornar None; puede tratarse de ticket vacío o anomalía
    # Validaciones y normalizaciones finales
    # fecha obligatoria preferente
    if 'fecha' not in data['ticket'] or not data['ticket'].get('fecha'):
        log_warnings.append(f"{path.name}: fecha no detectada.")
        data['ticket']['fecha'] = None
    if 'numero' not in data['ticket'] or not data['ticket'].get('numero'):
        log_warnings.append(f"{path.name}: número de ticket no detectado.")
        data['ticket']['numero'] = None
    # Si cajero ausente, crear placeholder
    if 'codigo' not in data['empleado'] or not data['empleado'].get('codigo'):
        placeholder = f"UNKNOWN_{path.stem}"
        log_warnings.append(f"{path.name}: cajero no detectado, usando {placeholder}.")
        data['empleado']['codigo'] = placeholder
        data['empleado']['nombre'] = None

    # Asegurar campos numéricos como floats/None
    for k in ('subtotal', 'iva', 'total'):
        if k in data['ticket']:
            data['ticket'][k] = float(data['ticket'][k]) if data['ticket'][k] is not None else None
    return data

# ---------- Generación de INSERTs (control de duplicados) ----------

class SqlGenerator:
    """Generador de INSERTs en memoria con control de duplicados usando claves lógicas."""
    def __init__(self):
        # contadores de ID internos (simulan AUTO_INCREMENT)
        self.counters = {
            'sucursal': 1,
            'empleado': 1,
            'producto': 1,
            'ticket': 1,
            'linea': 1,
            'pago': 1
        }
        # mapear claves lógicas a ids
        self.sucursales = {}  # key: (nombre_norm, direccion_norm) -> id
        self.empleados = {}   # key: codigo_cajero -> id
        self.productos = {}   # key: descripcion_norm -> id
        self.tickets = set()  # set of (numero, fecha, sucursal_id)

        # lista de sentencias SQL
        self.inserts: List[str] = []
        self.warnings: List[str] = []

    def next_id(self, tabla: str) -> int:
        idv = self.counters[tabla]
        self.counters[tabla] += 1
        return idv

    def ensure_sucursal(self, sucursal: Dict[str, Optional[str]]) -> int:
        nombre = sucursal.get('nombre') or 'UNKNOWN_SUCURSAL'
        direccion = sucursal.get('direccion') or ''
        key = (normalize_text(nombre), normalize_text(direccion))
        if key in self.sucursales:
            return self.sucursales[key]
        sid = self.next_id('sucursal')
        self.sucursales[key] = sid
        sql = f"INSERT INTO sucursal (sucursal_id, nombre, direccion) VALUES ({sid}, {sql_escape(nombre)}, {sql_escape(direccion)});"
        self.inserts.append(sql)
        return sid

    def ensure_empleado(self, empleado: Dict[str, Optional[str]], sucursal_id: int) -> int:
        codigo = empleado.get('codigo') or f"UNKNOWN_{sucursal_id}"
        if codigo in self.empleados:
            return self.empleados[codigo]
        eid = self.next_id('empleado')
        self.empleados[codigo] = eid
        nombre = empleado.get('nombre')
        sql = f"INSERT INTO empleado (empleado_id, codigo_cajero, nombre, sucursal_id) VALUES ({eid}, {sql_escape(codigo)}, {sql_escape(nombre)}, {sucursal_id});"
        self.inserts.append(sql)
        return eid

    def ensure_producto(self, prod: Dict[str, Any]) -> int:
        key = prod.get('descripcion_norm') or normalize_text(prod.get('descripcion') or 'unknown')
        if key in self.productos:
            return self.productos[key]
        pid = self.next_id('producto')
        self.productos[key] = pid
        descripcion = prod.get('descripcion')
        unidad = prod.get('unidad')
        # no guardamos precio_unitario_default aquí salvo que queramos
        sql = f"INSERT INTO producto (producto_id, descripcion, descripcion_norm, unidad) VALUES ({pid}, {sql_escape(descripcion)}, {sql_escape(key)}, {sql_escape(unidad)});"
        self.inserts.append(sql)
        return pid

    def insert_ticket_with_lines_and_pago(self, parsed: Dict[str, Any], sucursal_id: int, empleado_id: int):
        t = parsed['ticket']
        numero = t.get('numero') or f"T{self.next_id('ticket')}"
        fecha = t.get('fecha')
        hora = t.get('hora')
        subtotal = t.get('subtotal')
        iva = t.get('iva')
        iva_pct = t.get('iva_pct')
        total = t.get('total')
        key_ticket = (numero, fecha, sucursal_id)
        if key_ticket in self.tickets:
            self.warnings.append(f"Ticket duplicado detectado: {key_ticket}, se omite.")
            return
        tid = self.next_id('ticket')
        self.tickets.add(key_ticket)
        fecha_sql = sql_escape(fecha) if fecha else "NULL"
        hora_sql = sql_escape(hora) if hora else "NULL"
        subtotal_sql = f"{subtotal:.4f}" if subtotal is not None else "NULL"
        iva_sql = f"{iva:.4f}" if iva is not None else "NULL"
        iva_pct_sql = f"{iva_pct:.2f}" if iva_pct is not None else "NULL"
        total_sql = f"{total:.4f}" if total is not None else "NULL"
        sql_ticket = (
            f"INSERT INTO ticket (ticket_id, numero_ticket, fecha, hora, sucursal_id, empleado_id, subtotal, iva, iva_pct, total) "
            f"VALUES ({tid}, {sql_escape(numero)}, {fecha_sql}, {hora_sql}, {sucursal_id}, {empleado_id}, {subtotal_sql}, {iva_sql}, {iva_pct_sql}, {total_sql});"
        )
        self.inserts.append(sql_ticket)

        # lineas
        orden = 1
        for linea in parsed.get('lineas', []):
            pid = self.ensure_producto(linea)
            lid = self.next_id('linea')
            cantidad = linea.get('cantidad') or 1.0
            importe = linea.get('importe') if linea.get('importe') is not None else 0.0
            precio_unitario = linea.get('precio_unitario')
            cantidad_sql = f"{float(cantidad):.4f}"
            importe_sql = f"{float(importe):.4f}"
            precio_unitario_sql = f"{precio_unitario:.4f}" if precio_unitario is not None else "NULL"
            sql_linea = (
                f"INSERT INTO ticket_linea (linea_id, ticket_id, producto_id, cantidad, precio_unitario, importe, orden_linea) "
                f"VALUES ({lid}, {tid}, {pid}, {cantidad_sql}, {precio_unitario_sql}, {importe_sql}, {orden});"
            )
            self.inserts.append(sql_linea)
            orden += 1

        # pago
        pago = parsed.get('pago', {})
        if pago:
            metodo = pago.get('metodo')
            auth = pago.get('autorizacion')
            # si no hay importe por linea de pago, asumimos total
            importe_pago = total if total is not None else None
            pidp = self.next_id('pago')
            importe_sql = f"{importe_pago:.4f}" if importe_pago is not None else "NULL"
            sql_pago = (
                f"INSERT INTO pago (pago_id, ticket_id, metodo, importe, autorizacion) "
                f"VALUES ({pidp}, {tid}, {sql_escape(metodo)}, {importe_sql}, {sql_escape(auth)});"
            )
            self.inserts.append(sql_pago)

# ---------- Orquestador principal ----------

def generar_sql_para_carpeta(path_carpeta: str, archivo_salida: str = "InsertUnderlineTicket.sql"):
    carpeta = Path(path_carpeta)
    if not carpeta.exists() or not carpeta.is_dir():
        raise ValueError(f"La carpeta {path_carpeta} no existe o no es un directorio.")

    generator = SqlGenerator()
    log_warnings: List[str] = []

    txt_files = sorted([p for p in carpeta.glob("*.txt")])
    if not txt_files:
        raise ValueError("No se han encontrado archivos .txt en la carpeta indicada.")

    for p in txt_files:
        parsed = parse_ticket(p, log_warnings)
        if parsed is None:
            log_warnings.append(f"{p.name}: parseo fallido, se omite.")
            continue
        # asegurar sucursal y empleado
        sid = generator.ensure_sucursal(parsed.get('sucursal', {}))
        eid = generator.ensure_empleado(parsed.get('empleado', {}), sid)
        generator.insert_ticket_with_lines_and_pago(parsed, sid, eid)

    # escribir archivo SQL
    header = [
        "-- InsertUnderlineTicket.sql",
        "-- Generado por build_insert_from_tickets.py",
        f"-- Fecha: {datetime.now().isoformat()}",
        "SET FOREIGN_KEY_CHECKS = 0;",
        ""
    ]
    footer = ["", "SET FOREIGN_KEY_CHECKS = 1;"]

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        f.write("\n")
        for ins in generator.inserts:
            f.write(ins + "\n")
        f.write("\n".join(footer))


    # escribir log de parseo
    with open("parse_log.txt", "w", encoding="utf-8") as lf:
        lf.write("LOG DE PARSEO\n")
        lf.write("================\n")
        for w in log_warnings + generator.warnings:
            lf.write(w + "\n")

    print(f"Generado {archivo_salida} con {len(generator.inserts)} sentencias INSERT.")
    print("Ver parse_log.txt para avisos y errores detectados durante el parseo.")

# ---------- Entrada CLI ----------

def main():
    if len(sys.argv) < 2:
        print("Uso: python build_insert_from_tickets.py carpeta_facturas/")
        sys.exit(1)
    carpeta = sys.argv[1]
    try:
        generar_sql_para_carpeta(carpeta)
    except Exception as e:
        print("Error:", e)
        sys.exit(2)

if __name__ == "__main__":
    main()