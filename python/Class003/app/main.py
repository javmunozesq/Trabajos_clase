from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="SumaAPI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):  
    return templates.TemplateResponse("pages/index.html", {"request": request})

@app.post("/calcular", response_class=HTMLResponse)
def post_calcular(
    request: Request,
    numero1: float = Form(...),
    numero2: float = Form(...)
):
    suma = numero1 + numero2
    contexto = {"request": request, "numero1": numero1, "numero2": numero2, "suma": suma}
    return templates.TemplateResponse("pages/resultados.html", contexto)