#from django.shortcuts import render
import json
from collections import OrderedDict
from decimal import Decimal
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_POST, require_GET
from .models import MetadataSchema

@require_GET
def view_schema_list(request):

    if 'pretty' in request.GET:
        indent=4
    else:
        indent=None

    l = [m.as_dict() for m in MetadataSchema.objects.filter(published=True).all()]

    return HttpResponse(json.dumps(l, indent=indent), content_type='application/json')


@require_GET
def view_schema(request, schema_name_slug=None, version=None):
    schema_qs = MetadataSchema.objects.filter(slug=schema_name_slug)
    if version:
        version_num = Decimal(version)
        print ('version_num', version_num)
        schema_qs = schema_qs.filter(version=version_num)

    schema_info = schema_qs.first()
    if schema_info is None:
        raise Http404('Schema not found')

    if 'pretty' in request.GET:
        indent=4
    else:
        indent=None

    #return render(schema_info.as_json(), mimetype='json'
    return HttpResponse(schema_info.as_json(indent=indent), content_type='application/json')


@require_GET
def view_schema_data(request, schema_name_slug, datafile_id):

    schema_qs = MetadataSchema.objects.filter(slug=schema_name_slug)
    if version:
        version_num = Decimal(version)
        print ('version_num', version_num)
        schema_qs = schema_qs.filter(version=version_num)

    schema_info = schema_qs.first()
    if schema_info is None:
        raise Http404('Schema not found')

    if 'pretty' in request.GET:
        indent=4
    else:
        indent=None

    #return render(schema_info.as_json(), mimetype='json'
    return HttpResponse(schema_info.as_json(indent=indent), content_type='application/json')


@require_POST
def validate(request, schema_name_slug, version):
    schema_qs = MetadataSchema.objects.filter(slug=schema_name_slug)
    if version:
        version_num = Decimal(version)
        print ('version_num', version_num)
        schema_qs = schema_qs.filter(version=version_num)

    schema_info = schema_qs.first()
    if schema_info is None:
        raise Http404('Schema not found')

    # get JSON data out of the post
    if 'data' not in request.POST:
        return HttpResponse('You did not supply data to validate')

    json_data = request.POST['data']
    try:
        data_dict = json.loads(json_data, object_pairs_hook=OrderedDict)
    except:
        return HttpResponse('The data you sent was not valid JSON')

    #try:
    #schema_info
    return HttpResponse('validate it')

#@require_POST
#def add_schema(request):
