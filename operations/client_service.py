import requests


class CotizadorDolarsiJson:
    URL = 'https://www.dolarsi.com/api/api.php?type=valoresprincipales'

    def __init__(self, tipo_dolar):
        self.tipo_dolar = tipo_dolar
        self.data = requests.get(self.URL).json()

    def obtener_listado(self):
        listado = [element.get('casa') for element in self.data]
        if not listado:
            raise ValueError("no esta el tipo de dolar indicado")
        return listado

    def obtener_dict_info_dolar(self):
        listado_filtrado = [element.get('casa') for element in self.data if
                            self.tipo_dolar in element.get('casa').values()]
        if not listado_filtrado:
            raise ValueError("no esta el tipo de dolar indicado")
        return [element.get('casa') for element in self.data if self.tipo_dolar in element.get('casa').values()][0]

    def obtener_precio_compra(self):
        dolar_str = self.obtener_dict_info_dolar().get("compra")
        dolar_str = dolar_str.replace(",", ".")
        return float(dolar_str)

    def obtener_precio_venta(self):
        dolar_str = self.obtener_dict_info_dolar().get("venta")
        dolar_str = dolar_str.replace(",", ".")
        return float(dolar_str)


if __name__ == '__main__':
    c = CotizadorDolarsiJson("Dolar Bolsa")
    print(c.obtener_precio_venta())
    print(c.obtener_precio_compra())
