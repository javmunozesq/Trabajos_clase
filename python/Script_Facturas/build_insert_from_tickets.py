# Hecho por Javier Muñoz
# Este script lee archivos de texto con facturas desde una carpeta
# y genera un script SQL para insertar los datos en una base de datos MySQL


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

import sys, re, unicodedata
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

# ---------- Utilidades ----------

def sql_escape(s: Optional[str]) -> str:
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"

def normalize_text(s: Optional[str]) -> str:
    if not s: return ""
    s = unicodedata.normalize('NFKD', s.strip().lower())
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', s)

def parse_number(s: Optional[str]) -> Optional[float]:
    if not s: return None
    s = re.sub(r'(EUR|€|\s)', '', s, flags=re.IGNORECASE).replace(',', '.')
    try: return float(s)
    except: return None

# ---------- Patrones ----------

RX_DATE    = re.compile(r'fecha\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', re.I)
RX_HOUR    = re.compile(r'hora\s*[:\-]?\s*(\d{1,2}:\d{2})', re.I)
RX_CAJERO  = re.compile(r'cajero\s*[:\-]?\s*(\d+)\s*(?:-\s*(.+))?', re.I)
RX_TICKET  = re.compile(r'ticket\s*[:\-]?\s*(\d+)', re.I)

RX_SUBTOTAL = re.compile(r'\bsubtotal\b\s+([\d\.,]+)\s*€?', re.I)
RX_IVA      = re.compile(r'\biva\b\s*(?:\(([\d\.,]+)%\))?[\)\:\s]*([\d\.,]+)\s*€?', re.I)
RX_TOTAL    = re.compile(r'\btotal(?:\s+a\s+pagar)?\b\s+([\d\.,]+)\s*€?', re.I)
RX_PAGO     = re.compile(r'forma\s+de\s+pago\s*[:\-]?\s*([A-Z0-9ÁÉÍÓÚÜÑ \-]+)', re.I)
RX_AUTH     = re.compile(r'autorizaci[oó]n\s*[:\-]?\s*(\d+)', re.I)

RX_LINE         = re.compile(r'^\s*(\d+(?:[.,]\d+)?)\s+(.+?)\s+(\d+(?:[.,]\d+)?)\s*€?\s*$', re.I)
RX_LINE_NOQTY   = re.compile(r'^\s*([^\d\n].*?)\s+(\d+(?:[.,]\d+)?)\s*€?\s*$', re.I)
RX_UNIT_PAREN   = re.compile(r'\(([a-zA-Z0-9%]+)\)')
RX_UNIT_SUFFIX  = re.compile(r'(?:\s|^)(\d+\s?(?:g|kg|l|ml|u|un|unidad|pack))\s*$', re.I)
RX_SEPARATOR    = re.compile(r'^\s*-{3,}\s*$')

# ---------- Parsing ----------

def parse_producto_line(line: str) -> Optional[Dict[str, Any]]:
    m = RX_LINE.match(line)
    if m:
        cantidad_s, desc, importe_s = m.group(1), m.group(2), m.group(3)
    else:
        m2 = RX_LINE_NOQTY.match(line)
        if not m2: return None
        cantidad_s, desc, importe_s = None, m2.group(1), m2.group(2)

    cantidad = parse_number(cantidad_s) if cantidad_s else 1.0
    importe = parse_number(importe_s)
    desc = desc.strip()

    unidad = None
    up = RX_UNIT_PAREN.search(desc)
    if up:
        unidad = up.group(1).lower()
        desc = re.sub(r'\s*\(' + re.escape(up.group(1)) + r'\)\s*', ' ', desc).strip()
    if not unidad:
        suf = RX_UNIT_SUFFIX.search(desc)
        if suf: unidad = suf.group(1).strip().lower()

    precio_unit = round(importe / cantidad, 4) if (importe is not None and cantidad) else None
    return {
        'cantidad': float(cantidad),
        'descripcion': desc,
        'descripcion_norm': normalize_text(desc),
        'unidad': unidad,
        'unidad_norm': normalize_text(unidad),
        'importe': importe,
        'precio_unitario': precio_unit
    }

def parse_date(raw: str) -> Optional[str]:
    for fmt in ('%d/%m/%Y','%d-%m-%Y','%d/%m/%y','%d-%m-%y'):
        try: return datetime.strptime(raw, fmt).date().isoformat()
        except: pass
    return None

def parse_ticket(path: Path, log: List[str]) -> Optional[Dict[str, Any]]:
    text = None
    for enc in ('utf-8', 'latin-1'):
        try: text = path.read_text(encoding=enc); break
        except: continue
    if text is None:
        log.append(f"{path.name}: no se pudo leer."); return None

    lines = [ln.rstrip('\n\r') for ln in text.splitlines()]
    if not any(ln.strip() for ln in lines):
        log.append(f"{path.name}: fichero vacío."); return None

    data = {'sucursal': {}, 'empleado': {}, 'ticket': {}, 'lineas': [], 'pago': {}}

    header = [ln for ln in lines[:6] if ln.strip()]
    data['sucursal']['nombre'] = header[0].strip() if header else None
    data['sucursal']['direccion'] = header[1].strip() if len(header) > 1 else None

    for ln in lines:
        low = ln.lower()
        if 'fecha' in low and 'ticket' not in low:
            m = RX_DATE.search(ln); 
            if m: data['ticket']['fecha'] = parse_date(m.group(1))
        if 'hora' in low:
            m = RX_HOUR.search(ln); 
            if m: data['ticket']['hora'] = m.group(1)
        if 'cajero' in low:
            m = RX_CAJERO.search(ln)
            if m:
                data['empleado']['codigo'] = (m.group(1) or '').strip()
                data['empleado']['nombre'] = (m.group(2).strip() if m.group(2) else None)
        if 'ticket' in low:
            m = RX_TICKET.search(ln); 
            if m: data['ticket']['numero'] = m.group(1).strip()

        if 'subtotal' in low:
            m = RX_SUBTOTAL.search(ln); 
            if m: data['ticket']['subtotal'] = parse_number(m.group(1))
        if 'iva' in low:
            m = RX_IVA.search(ln)
            if m:
                data['ticket']['iva_pct'] = parse_number(m.group(1)) if m.group(1) else None
                data['ticket']['iva'] = parse_number(m.group(2))
        if re.search(r'\btotal\b', low):
            m = RX_TOTAL.search(ln); 
            if m: data['ticket']['total'] = parse_number(m.group(1))
        if 'forma de pago' in low:
            m = RX_PAGO.search(ln); 
            if m: data['pago']['metodo'] = m.group(1).strip()
        if 'autoriz' in low:
            m = RX_AUTH.search(ln); 
            if m: data['pago']['autorizacion'] = m.group(1).strip()

        if ln.strip() and not RX_SEPARATOR.match(ln):
            p = parse_producto_line(ln)
            if p: data['lineas'].append(p)

    if not data['ticket'].get('fecha'):
        log.append(f"{path.name}: fecha no detectada.")
    if not data['ticket'].get('numero'):
        log.append(f"{path.name}: número de ticket no detectado.")
    if not data['empleado'].get('codigo'):
        placeholder = f"UNKNOWN_{path.stem}"
        log.append(f"{path.name}: cajero no detectado, usando {placeholder}.")
        data['empleado']['codigo'] = placeholder
        data['empleado']['nombre'] = None
    if not data['lineas']:
        log.append(f"{path.name}: no se detectaron líneas de producto.")

    for k in ('subtotal','iva','total'):
        v = data['ticket'].get(k)
        data['ticket'][k] = (float(v) if v is not None else None)

    return data

# ---------- Generador SQL ----------

class SqlGenerator:
    def __init__(self):
        self.counters = {'sucursal':1,'empleado':1,'producto':1,'ticket':1,'linea':1,'pago':1}
        self.sucursales: Dict[Tuple[str,str], int] = {}
        self.empleados: Dict[Tuple[str,int], int] = {}
        self.productos: Dict[Tuple[str,str], int] = {}
        self.tickets: set = set()
        self.inserts: List[str] = []
        self.warnings: List[str] = []
        self.fmt4 = lambda v: f"{v:.4f}" if v is not None else "NULL"
        self.fmt2 = lambda v: f"{v:.2f}" if v is not None else "NULL"

    def _next(self, t: str) -> int:
        i = self.counters[t]; self.counters[t] += 1; return i

    def ensure_sucursal(self, s: Dict[str, Optional[str]]) -> int:
        nombre = s.get('nombre') or 'UNKNOWN_SUCURSAL'
        direccion = s.get('direccion') or ''
        key = (normalize_text(nombre), normalize_text(direccion))
        if key in self.sucursales: return self.sucursales[key]
        sid = self._next('sucursal'); self.sucursales[key] = sid
        self.inserts.append(f"INSERT INTO sucursal (sucursal_id, nombre, direccion) VALUES ({sid}, {sql_escape(nombre)}, {sql_escape(direccion)});")
        return sid

    def ensure_empleado(self, e: Dict[str, Optional[str]], sucursal_id: int) -> int:
        codigo = e.get('codigo') or f"UNKNOWN_{sucursal_id}"
        key = (codigo, sucursal_id)
        if key in self.empleados: return self.empleados[key]
        eid = self._next('empleado'); self.empleados[key] = eid
        self.inserts.append(f"INSERT INTO empleado (empleado_id, codigo_cajero, nombre, sucursal_id) VALUES ({eid}, {sql_escape(codigo)}, {sql_escape(e.get('nombre'))}, {sucursal_id});")
        return eid

    def ensure_producto(self, p: Dict[str, Any]) -> int:
        desc_norm = p.get('descripcion_norm') or normalize_text(p.get('descripcion'))
        unidad_norm = p.get('unidad_norm') or ''
        key = (desc_norm, unidad_norm)
        if key in self.productos: return self.productos[key]
        pid = self._next('producto'); self.productos[key] = pid
        self.inserts.append(f"INSERT INTO producto (producto_id, descripcion, descripcion_norm, unidad) VALUES ({pid}, {sql_escape(p.get('descripcion'))}, {sql_escape(desc_norm)}, {sql_escape(p.get('unidad'))});")
        return pid

    def insert_ticket_bundle(self, parsed: Dict[str, Any], sid: int, eid: int):
        t = parsed['ticket']
        numero = t.get('numero') or f"T{self._next('ticket')}"
        key = (numero, t.get('fecha'), sid)
        if key in self.tickets:
            self.warnings.append(f"Ticket duplicado detectado: {key}, se omite."); return
        tid = self._next('ticket'); self.tickets.add(key)

        self.inserts.append(
            f"INSERT INTO ticket (ticket_id, numero_ticket, fecha, hora, sucursal_id, empleado_id, subtotal, iva, iva_pct, total) "
            f"VALUES ({tid}, {sql_escape(numero)}, {sql_escape(t.get('fecha'))}, {sql_escape(t.get('hora'))}, {sid}, {eid}, {self.fmt4(t.get('subtotal'))}, {self.fmt4(t.get('iva'))}, {self.fmt2(t.get('iva_pct'))}, {self.fmt4(t.get('total'))});"
        )

        orden = 1
        for ln in parsed.get('lineas', []):
            pid = self.ensure_producto(ln)
            lid = self._next('linea')
            cantidad = self.fmt4(float(ln.get('cantidad') or 1.0))
            importe = self.fmt4(float(ln.get('importe') or 0.0))
            pu = ln.get('precio_unitario'); pu_sql = self.fmt4(pu) if pu is not None else "NULL"
            self.inserts.append(
                f"INSERT INTO ticket_linea (linea_id, ticket_id, producto_id, cantidad, precio_unitario, importe, orden_linea) "
                f"VALUES ({lid}, {tid}, {pid}, {cantidad}, {pu_sql}, {importe}, {orden});"
            )
            orden += 1

        pago = parsed.get('pago') or {}
        if pago:
            pidp = self._next('pago')
            importe_pago = t.get('total')
            self.inserts.append(
                f"INSERT INTO pago (pago_id, ticket_id, metodo, importe, autorizacion) "
                f"VALUES ({pidp}, {tid}, {sql_escape(pago.get('metodo'))}, {self.fmt4(importe_pago)}, {sql_escape(pago.get('autorizacion'))});"
            )

# ---------- Orquestador ----------

def generar_sql_para_carpeta(path_carpeta: str, archivo_salida: str = "InsertUnderlineTicket.sql"):
    carpeta = Path(path_carpeta)
    if not carpeta.is_dir(): raise ValueError(f"La carpeta {path_carpeta} no existe o no es un directorio.")

    gen = SqlGenerator(); log: List[str] = []
    files = sorted(carpeta.glob("*.txt"))
    if not files: raise ValueError("No se han encontrado archivos .txt en la carpeta indicada.")

    for p in files:
        parsed = parse_ticket(p, log)
        if not parsed:
            log.append(f"{p.name}: parseo fallido, se omite."); continue
        sid = gen.ensure_sucursal(parsed.get('sucursal', {}))
        eid = gen.ensure_empleado(parsed.get('empleado', {}), sid)
        gen.insert_ticket_bundle(parsed, sid, eid)

    header = [
        "-- InsertUnderlineTicket.sql",
        "-- Generado por build_insert_from_tickets.py (versión compacta)",
        f"-- Fecha: {datetime.now().isoformat()}",
        "SET FOREIGN_KEY_CHECKS = 0;", ""
    ]
    footer = ["", "SET FOREIGN_KEY_CHECKS = 1;"]

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(header)); f.write("\n")
        for ins in gen.inserts: f.write(ins + "\n")
        f.write("\n".join(footer))

    with open("parse_log.txt", "w", encoding="utf-8") as lf:
        lf.write("LOG DE PARSEO\n================\n")
        for w in log + gen.warnings: lf.write(w + "\n")

    print(f"Generado {archivo_salida} con {len(gen.inserts)} sentencias INSERT.")
    print("Ver parse_log.txt para avisos y errores detectados durante el parseo.")

# ---------- CLI ----------

def main():
    if len(sys.argv) < 2:
        print("Uso: python build_insert_from_tickets.py carpeta_facturas/"); sys.exit(1)
    try:
        generar_sql_para_carpeta(sys.argv[1])
    except Exception as e:
        print("Error:", e); sys.exit(2)

if __name__ == "__main__":
    main()