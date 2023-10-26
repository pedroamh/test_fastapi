import pandas as pd
import os
import json
import asyncio

from handlers.email_handler import send_email
from utils.comUtil import consultar_enviar_attachment,cargar_archivo_configuracion

def get_feature_attributes(response_json):
    feature_attributes = response_json.get("feature", {})
    return feature_attributes.get("attributes")

def get_layer_info(response_json):
    feature_attributes = response_json.get("feature", {})
    return feature_attributes.get("layerInfo")

def get_survey_info(response_json):
    survey_info = response_json.get("surveyInfo", {})
    return survey_info.get("formItemId"),survey_info.get("formTitle")

def get_token(response_json):
    survey_info = response_json.get("portalInfo", {})
    return survey_info.get("token")

def validate_attachment(response_json):
    #print(f'entro acaaa')
    survey_info = response_json.get("feature", {})
    attachments = survey_info.get("attachments", {})
    print(f'validate attachments {survey_info} - {attachments}')
    if attachments is not None:
        variable = list(attachments.keys())[0]
        #print(f'revisar el nombre {variable}')
        imagen = attachments.get(variable, [])
        #imagen = attachments.get("archivo_area_proyecto", [])
        if imagen:
            id_attachment = imagen[0].get("id")
            name_attachment = imagen[0].get("name")
        else:
            raise Exception("No se encontraron adjuntos de imagen ")
    else:
        id_attachment = None
        name_attachment = None
        return id_attachment,name_attachment
    return id_attachment,name_attachment

async def process_survey1(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    '''Lógica para procesar los datos de la encuesta 1
    utilizando los datos del response_json'''

    #print(adjuntar_archivo_en_correo, get_attachment_name)

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    globalid = feature_attributes.get('globalid')
    email_entidad = feature_attributes.get('correo')
    for key, value in base_url.items():
        extra_args[key]= f"{value}?portalUrl=https://mapas.igac.gov.co/portal&mode=edit&globalId={globalid}&hide=header,description,footer,navbar&locale=es&width=1200"


    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        print(receiver)
        template_name = f'{survey_name}_{receiver}_{survey_id}.html'
        tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                email_parameters=email_parameters,template_name=template_name,
                                email_entidad=email_entidad,email_igac=email_igac,
                                extra_args=extra_args,get_attachment_name=get_attachment_name,
                                attachment_data=adjuntar_archivo_en_correo))    
    await asyncio.gather(*tasks)

async def process_survey2(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    # Lógica para procesar los datos de la encuesta 2
    # utilizando los datos del response_json


    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get('correo')
    for key, value in base_url.items():
        extra_args[key]= f"{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}"

    
    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    if feature_attributes.get('solicitud_confirmada') == 'Si':
        estado = 'aprobado'
        for receiver in receivers:
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        await asyncio.gather(*tasks)
    else:
        estado = 'desaprobado'
        for receiver in receivers:
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        await asyncio.gather(*tasks)
        print(f'Todos los correos electrónicos enviados correctamente')

async def process_survey3(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    

    for key, value in base_url.items():
        extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:id_registro={id_registro}&field:tipo_producto_chequeo={key}'
    print(f'extra_args en survey {extra_args}')

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        print(f'Receiver - {receiver}')
        print(extra_args)
        template_name = f'{survey_name}_{receiver}_{survey_id}.html'
        tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                email_parameters=email_parameters,template_name=template_name,
                                email_igac=email_igac,extra_args=extra_args))    
    await asyncio.gather(*tasks)

async def process_survey4(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')

    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Carto'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey5(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')

    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Orto'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey6(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}

    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    id_solicitud_registro = feature_attributes.get('id_solicitud_registro')
    id_registro = feature_attributes.get('id_registro')
    id_chequeo = feature_attributes.get('id_chequeo')
    producto_carto_aprobado = feature_attributes.get('aprobado')
    email_igac_encargado_validacion = feature_attributes.get('resp_validacion_correo')
    email_entidad = feature_attributes.get('correo')


    for key, value in base_url.items():
        if key=='url_validacion_producto':
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud={id_solicitud_registro}&field:id_registro={id_registro}&field:id_chequeo={id_chequeo}'
        else:
            extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=MDT'

    if producto_carto_aprobado == 'No':
        if 'IGAC' in receivers:
            # Encuentra el índice del nombre que deseas eliminar
            indice_a_eliminar = receivers.index('IGAC')
            # Elimina el nombre de la lista utilizando el índice
            receivers.pop(indice_a_eliminar)

    if email_igac == '':
        email_igac = email_igac_encargado_validacion

    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    for receiver in receivers:
        if producto_carto_aprobado == 'No':
            print(f'Receiver - {receiver}')
            estado = 'desaprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
        else:
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac,
                                    extra_args=extra_args))    
   
    await asyncio.gather(*tasks)

async def process_survey7(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}


    print(f'ESto es base URL {base_url}')
    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']

    resultado_validacion = feature_attributes.get('resul_validacion')
    n_inspeccion = int(feature_attributes.get('n_inspeccion'))
    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get("correo_solicitante", "")

    for key, value in base_url.items():
        extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Carto'


    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    print(f'resultado de la validacion {resultado_validacion}')
    for receiver in receivers:
        if resultado_validacion == 'conforme':
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac))    
        else:
            if n_inspeccion == 1 or n_inspeccion == 2 or n_inspeccion == 3:
                print(f'Receiver - {receiver}')
                print(f'extra args {extra_args}')
                estado = 'desaprobado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))    
            else:
                print('OTRO')
    await asyncio.gather(*tasks)

async def process_survey8(response_json,adjuntar_archivo_en_correo=None,get_attachment_name=None):
    
    # Lógica para procesar los datos de la encuesta 3
    # utilizando los datos del response_json

    # Obtener la ruta absoluta del archivo de configuración
    survey_id,survey_name = get_survey_info(response_json)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', 'config', f'{survey_name}.json')

    # Leer el archivo de configuración de campos
    with open(config_path) as config_file:
        config_data = json.load(config_file)

    # Obtener el mapeo de campos y el subject del archivo de configuración
    fields_mapping = config_data.get("fields_mapping", {})
    email_parameters = config_data.get("email_parameters", "")
    email_igac = config_data.get("email", "")
    subject = config_data.get("subject", {})
    receivers = config_data.get("receiver", "")
    base_url = config_data.get("base_url", {})
    extra_args = {}


    print(f'ESto es base URL {base_url}')
    # Obtener los atributos del response_json
    feature_attributes = response_json['feature']['attributes']


    resultado_validacion = feature_attributes.get('resul_validacion')
    n_inspeccion = int(feature_attributes.get('n_inspeccion'))
    id_solicitud_registro = feature_attributes.get('id_solicitud')
    email_entidad = feature_attributes.get("correo_solicitante", "")

    for key, value in base_url.items():
        extra_args[key]= f'{value}?portalUrl=https://mapas.igac.gov.co/portal&hide=header,description,footer,navbar&locale=es&width=1200&field:id_solicitud_registro={id_solicitud_registro}&field:productos_registro=Carto'


    # Filtrar los atributos del response_json que coinciden con los campos del archivo de configuración
    attributes = {parameter: feature_attributes.get(attribute) for parameter, attribute in fields_mapping.items()}


    tasks = []
    print(f'Enviando email')
    print(f'resultado de la validacion {resultado_validacion}')
    for receiver in receivers:
        if resultado_validacion == 'conforme':
            print(f'Receiver - {receiver}')
            estado = 'aprobado'
            template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
            tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                    email_parameters=email_parameters,template_name=template_name,
                                    email_entidad=email_entidad,email_igac=email_igac))    
        else:
            if n_inspeccion == 1 or n_inspeccion == 2:
                print(f'Receiver - {receiver}')
                print(f'extra args {extra_args}')
                estado = 'desaprobado'
                template_name = f'{survey_name}_{receiver}_{estado}_{survey_id}.html'
                tasks.append(send_email(receiver=receiver,attributes=attributes,subject=subject,
                                        email_parameters=email_parameters,template_name=template_name,
                                        email_entidad=email_entidad,email_igac=email_igac,extra_args=extra_args))    
            else:
                print('OTRO')
    await asyncio.gather(*tasks)
