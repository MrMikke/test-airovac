
# class CotizadorAirovac(http.Controller):
#     @http.route('/cotizador__airovac/cotizador__airovac/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cotizador__airovac/cotizador__airovac/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cotizador__airovac.listing', {
#             'root': '/cotizador__airovac/cotizador__airovac',
#             'objects': http.request.env['cotizador__airovac.cotizador__airovac'].search([]),
#         })

#     @http.route('/cotizador__airovac/cotizador__airovac/objects/<model("cotizador__airovac.cotizador__airovac"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cotizador__airovac.object', {
#             'object': obj
#         })
