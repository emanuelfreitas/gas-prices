from prometheus_client import Summary, Gauge, generate_latest, CollectorRegistry
from flask import Flask, request
import urllib.request
import json
import re

REGISTRY = CollectorRegistry()

GASPRICE = Gauge('gas_price', 'Gas Prices', ['attribute', 'id'], registry=REGISTRY)
GET_URL_TIME = Summary('get_url_time', 'Time spent getting url', registry=REGISTRY)

@GET_URL_TIME.time()
def getURLAsJSON(url):

    req = urllib.request.Request(url)

#    try:
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        encoding = response.info().get_content_charset('utf-8')
        return json.loads(the_page.decode(encoding))
#    except Exception as e:
#        pass

    return None

def getGasInfo(idsTiposComb, idMarca, idTipoPosto, idDistrito, idsMunicipios, qtdPorPagina, pagina):
    url =  "https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/PesquisarPostos?"
    url += "idsTiposComb=" + str(idsTiposComb)
    url += "&idMarca=" + str(idMarca)
    url += "&idTipoPosto=" + str(idTipoPosto)
    url += "&idDistrito=" + str(idDistrito)
    url += "&idsMunicipios=" + str(idsMunicipios)
    url += "&qtdPorPagina=" + str(qtdPorPagina)
    url += "&pagina=" + str(pagina)

    gasInfo = getURLAsJSON(url)

    if 'status' not in gasInfo or not gasInfo['status']: return

    for result in gasInfo['resultado']:
        nome = str(result['Marca']) + ' - ' + str(result['Localidade']) + ' - ' + str(result['Morada'])
        price = re.sub(',', '.', re.findall(r'\d+\,\d+', result['Preco'])[0]).strip()
        GASPRICE.labels('price', nome).set(float(price))
        #GASPRICE.labels('price', 'nome').inc()

    #print(gasInfo)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/metrics')
def metrics():
    idsTiposComb    = request.args.get('idsTiposComb',  type = int, default = 2101)
    idMarca         = request.args.get('idMarca',       type = int )
    idTipoPosto     = request.args.get('idTipoPosto',   type = int )
    idDistrito      = request.args.get('idDistrito',    type = int, default = 1 )
    idsMunicipios   = request.args.get('idsMunicipios', type = int, default = 5 )
    qtdPorPagina    = request.args.get('qtdPorPagina',  type = int, default = 50 )
    pagina          = request.args.get('pagina',        type = int, default = 1 )

    getGasInfo(idsTiposComb, idMarca, idTipoPosto, idDistrito, idsMunicipios, qtdPorPagina, pagina)

    return generate_latest(REGISTRY)