import flet as ft
from datetime import datetime
import requests
import pytz

API_URL = "https://api-jose-barrios-production.up.railway.app/bitacora"

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.RED)
    page.title = "Bitacora de Movimientos - BT01"
    page.padding = 10
    page.expand = True   # Para que la página ocupe toda la ventana

    zona_horaria = pytz.timezone("America/Merida")
    hoy = datetime.now(zona_horaria).date()
    hoy_str = hoy.isoformat()

    # Logo y encabezado
    logo = ft.Image(
        src="s",
        width=60, height=60, fit=ft.ImageFit.CONTAIN
    )

    titulo_empresa = ft.Text("Bitacora - BT01", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    titulo = ft.Text("Movimientos", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    txt_fecha = ft.TextField(label="Fecha", read_only=True, width=150,
                             value=hoy.strftime("%d-%m-%Y"), bgcolor=ft.Colors.WHITE)
    txt_fecha.data = hoy_str

    def actualizar_fecha(txt, nueva_fecha):
        txt.data = nueva_fecha
        txt.value = datetime.fromisoformat(nueva_fecha).strftime("%d-%m-%Y")
        page.update()

    date_picker_fecha = ft.DatePicker(on_change=lambda e: actualizar_fecha(txt_fecha, e.data))
    page.overlay.append(date_picker_fecha)

    fecha_btn = ft.ElevatedButton("Fecha",
                                  icon=ft.icons.CALENDAR_MONTH,
                                  on_click=lambda e: page.open(date_picker_fecha),
                                  width=150, height=50)

    buscar_btn = ft.ElevatedButton("Buscar",
                                   width=300, height=40, icon=ft.icons.SEARCH,
                                   bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, icon_color=ft.Colors.WHITE)

    encabezado = ft.Container(
        content=ft.Column([
            ft.Row([logo, titulo_empresa]),
            titulo,
            ft.Row([txt_fecha, fecha_btn]),
            ft.Row([buscar_btn], alignment=ft.MainAxisAlignment.START),
        ]),
        padding=20,
        bgcolor=ft.Colors.RED,
        border_radius=ft.BorderRadius(0, 0, 20, 20)
    )

    loader = ft.ProgressRing(visible=False, color=ft.Colors.ORANGE, stroke_width=4)

    # Tabla
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Hora", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Cj", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Tn", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Cheque", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Movimiento", weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        column_spacing=20,
        heading_row_color=ft.Colors.BLUE_100
    )

    # 📜 Envolvemos la tabla en un ListView para que tenga scroll
    tabla_scroll = ft.ListView(
        controls=[tabla],
        expand=True,             # Ocupa todo el espacio disponible
        auto_scroll=False        # No baja automático al final
    )

    # Lo metemos en un container para estilo
    tabla_container = ft.Container(
        content=tabla_scroll,
        padding=10,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        expand=True
    )

    def buscar_bitacora(_):
        buscar_btn.disabled = True
        loader.visible = True
        page.update()

        fecha_date = datetime.fromisoformat(txt_fecha.data).date()
        fecha = fecha_date.strftime("%y%m%d")  # Formato YYMMDD

        try:
            response = requests.get(API_URL, params={"fecha": fecha})
            if response.status_code == 200:
                data = response.json()

                # Limpiamos la tabla
                tabla.rows.clear()

                # Agregamos filas
                for r in data:
                    tabla.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(r.get("hora", ""))),
                                ft.DataCell(ft.Text(r.get("cajero", ""))),
                                ft.DataCell(ft.Text(r.get("turno", ""))),
                                ft.DataCell(
                                    ft.Container(  # 👈 Contenedor para dar altura y permitir wrap
                                        content=ft.Text(
                                            r.get("cheque", "---"),
                                            no_wrap=False,        # Permite salto de línea
                                            max_lines=2,          # Máximo de líneas
                                            size=14
                                        ),
                                    )
                                ),
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            r.get("movimiento", ""),
                                            no_wrap=False,
                                            max_lines=2,          # Aquí damos más líneas porque “movimiento” puede ser más largo
                                            size=14
                                        ),
                                    )
                                ),
                            ]
                        )
                    )

                page.update()
            else:
                print("Error en la API:", response.status_code)
        except Exception as e:
            print("Error al consultar la API:", e)

        loader.visible = False
        buscar_btn.disabled = False
        page.update()

    buscar_btn.on_click = buscar_bitacora

    page.add(
        ft.Column([
            encabezado,
            loader,
            tabla_container,
        ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)
    )
    buscar_bitacora(None)

ft.app(target=main)
