from odoo import fields, osv, models
from odoo.tools.translate import _
import pdb
import json

#CHANGE WARNING_MODULE with your module name
WARNING_MODULE = 'meli_oerp'
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
import logging
_logger = logging.getLogger(__name__)

meli_errors = {
    "item.category_id.invalid": "Categoría de MercadoLibre inválida, seleccione una categoría en la plantilla de MercadoLibre",
    #"item.category_id.invalid": "Categoría de MercadoLibre inválida, seleccione una categoría en la plantilla de MercadoLibre",
}

class warning(models.TransientModel):
    _name = 'meli.warning'
    _description = 'warning'
    type = fields.Selection(WARNING_TYPES, string='Type', readonly=True);
    title = fields.Char(string="Title", size=100, readonly=True);
    message = fields.Text(string="Message", readonly=True);
    message_html = fields.Html(string="Message HTML", readonly=True);

    _req_name = 'title'

    def _format_meli_error( self, title, message, message_html='', context=None ):
        context = context or self.env.context
        
        #process error messages:
        
        #0 longitud del titulo
        #1 Debe cargar una imagen de base en el producto, si chequeo el 'Dont use first image' debe al menos poner una imagen adicional en el producto.
        #2 Problemas cargando la imagen principal
        #3 Error publicando imagenes
        #4 Debe iniciar sesión en MELI con el usuario correcto
        #5 Completar todos los campos y revise el mensaje siguiente. ("<br><br>"+error_msg)
        #6 Debe completar el campo description en la plantilla de MercadoLibre o del producto (Descripción de Ventas)
        #7 Debe iniciar sesión en MELI
        #8 Recuerde completar todos los campos y revise el mensaje siguiente
        
        rjson = context and "rjson" in context and context["rjson"]
        if rjson:
            _logger.info("_format_meli_error rjson:"+str(rjson))
            
            rstatus = "status" in rjson and rjson["status"]
            rcause = "cause" in rjson and rjson["cause"]
            rmessage = "message" in rjson and rjson["message"] and json.loads(rjson["message"])
            rerror = "error" in rjson and rjson["error"]
            
            if rstatus in ["error"]:
                title = "ERROR MELI: " + title
            
            if rstatus in ["warning"]:
                title = "WARNING MELI: " + title
                
            if rmessage:
                _logger.info("_format_meli_error message:"+str(rmessage))
                _logger.info(rmessage)
                for rmess in rmessage:
                    _logger.info("rmess:"+str(rmess))
                    if rmess == "error":
                        ecode = rmessage[rmess]
                        message_html = '<div role="alert" class="alert alert-warning" title="Meli Message"><i class="fa fa-comments" role="img" aria-label="Meli Message"/>%s</div>' % ((ecode in meli_errors and meli_errors[ecode]) or ecode)
                    if rmess == "message":
                        message = rmessage[rmess]
                        #message_html+= "<br/>"+str(rmessage[rmess])
                    if rmess == "status":
                        estatus = rmessage[rmess]
                        message_html+= "<br/>Estado: "+str(estatus)
                    if rmess == "cause":
                        ecause = rmessage[rmess]
                        message_html+= "<br/>Causa: "+str(ecause)
                    
        
        return title, message, message_html

    def _get_view_id(self ):
        """Get the view id
        @return: view id, or False if no view found
        """
        res = self.env['ir.model.data'].get_object_reference( WARNING_MODULE, 'warning_form')
        return res and res[1] or False

    def _message(self, id):
        #pdb.set_trace()
        message = self.browse( id)
        message_type = [t[1]for t in WARNING_TYPES if message.type == t[0]][0]
        #_logger.info( '%s: %s' % (_(message_type), _(message.title)) )
        res = {
            'name': '%s: %s' % (_(message_type), _(message.title)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self._get_view_id(),
            'res_model': 'meli.warning',
            'domain': [],
            #'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id
        }
        return res

    def warning(self, title, message, message_html='', context=None):
        context = context or self.env.context
        title, message, message_html = self._format_meli_error(title=title,message=message,message_html=message_html,context=context)
        id = self.create( {'title': title, 'message': message, 'message_html': message_html, 'type': 'warning'}).id
        res = self._message( id )
        return res

    def info(self, title, message, message_html='', context=None):
        context = context or self.env.context
        title, message, message_html = self._format_meli_error(title=title,message=message,message_html=message_html,context=context)
        id = self.create( {'title': title, 'message': message, 'message_html': message_html, 'type': 'info'}).id
        res = self._message( id )
        return res

    def error(self, title, message, message_html='', context=None):
        context = context or self.env.context
        title, message, message_html = self._format_meli_error(title=title,message=message,message_html=message_html, context=context)
        id = self.create( {'title': title, 'message': message, 'message_html': message_html, 'type': 'error'}).id
        res = self._message( id)
        return res

warning()
