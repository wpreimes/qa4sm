import base64
import os
from collections import OrderedDict

from django.core.files import File
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from validator.models import ValidationRun
from django.conf import settings

import mimetypes
from wsgiref.util import FileWrapper

from validator.validation import get_inspection_table, get_dataset_combis_and_metrics_from_files


@api_view(['GET'])
@permission_classes([AllowAny])
def get_results(request):
    validation_id = request.query_params.get('validationId', None)
    file_type = request.query_params.get('fileType', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)

    try:
        file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    except AttributeError:
        return HttpResponse('Given validation has no output directory assigned', status=404)

    if file_type == 'netCDF':
        filename = file_path + validation.output_file_name
    elif file_type == 'graphics':
        filename = file_path + 'graphs.zip'
    else:
        return HttpResponse('No file type given', status=404)

    try:
        file_wrapper = FileWrapper(open(filename, 'rb'))
    except FileNotFoundError as e:
        return HttpResponse(e, status=404)

    file_mimetype = mimetypes.guess_type(filename)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csv_with_statistics(request):
    """Download .csv of the statistics"""
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    inspection_table = get_inspection_table(validation)

    if isinstance(inspection_table, str):
        return HttpResponse('error file size', 404)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Stats_summary.csv'

    inspection_table.reset_index().to_csv(
        path_or_buf=response,
        sep=',',
        float_format='%.2f',
        index=False,
        decimal="."
    )

    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_metric_names_and_associated_files(request):
    validation_id = request.query_params.get('validationId', None)
    validation = get_object_or_404(ValidationRun, pk=validation_id)
    try:
        file_path = validation.output_dir_url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT)
    except AttributeError:
        return JsonResponse({'message': 'Given validation has no output directory assigned'}, status=404)

    try:
        files = os.listdir(file_path)
        if len(files) == 0:
            return JsonResponse({'message': 'There are no files in the given directory'}, status=404)
    except FileNotFoundError as e:
        return JsonResponse({'message': str(e)}, status=404)

    pairs, triples, metrics, ref0_config = get_dataset_combis_and_metrics_from_files(validation)
    combis = OrderedDict(sorted({**pairs, **triples}.items()))
    metrics = OrderedDict(sorted([(v, k) for k, v in metrics.items()]))
    response = []

    for ind, key in enumerate(metrics):
        boxplot_file = ''
        boxplot_file_name = 'boxplot_' + metrics[key] + '.png'

        # 'n_obs' doesn't refer to datasets so I create a list with independent metrics, if there are other similar
        # metrics it's just enough to add them here:
        independent_metrics = ['n_obs']

        if metrics[key] not in independent_metrics:
            overview_plots = [{'file_name': 'overview_' + name_key + '_' + metrics[key] + '.png',
                               'datasets': name_key} for name_key in combis]
        else:
            overview_plots = [{'file_name': 'overview_' + metrics[key] + '.png', 'datasets': ''}]

        if boxplot_file_name in files:
            boxplot_file = file_path + boxplot_file_name

        overview_files = [file_path + file_dict['file_name'] for file_dict in overview_plots if file_dict['file_name'] in files]
        datasets = [' '.join(file_dict['datasets'].split('_')) for file_dict in overview_plots if file_dict['file_name'] in files]
        metric_dict = {'ind': ind,
                       'metric_query_name': metrics[key],
                       'metric_pretty_name': key,
                       'boxplot_file': boxplot_file,
                       'overview_files': overview_files,
                       'datasets': datasets}
        response.append(metric_dict)
    #
    return JsonResponse(response, status=200, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_graphic_files(request):
    # Here we take a list of parameters 'file' and return a list of plots encoded to base64
    files = request.query_params.getlist('file', None)
    if not files:
        return JsonResponse({'message': 'No file names given'}, status=404, safe=False)
    plots = []
    for file in files:
        if '/static/' in file:
            file = file.replace('/static/', os.path.join(settings.BASE_DIR, 'validator/static/'))
        open_file = open(file, 'rb')
        image = File(open_file)
        name = base64.b64encode(image.read())
        open_file.close()
        plots.append({'plot': name.decode('utf-8')})
    return JsonResponse(plots, safe=False)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_graphic_file(request):
    # Here we take only one file and return one plot;
    # Sometimes it's just easier to read a single file, and this function is created not to refer to index 0 every time
    file = request.query_params.get('file', None)
    if not file:
        return JsonResponse({'message': 'No file name given'}, status=404, safe=False)
    if '/static/' in file:
        file = file.replace('/static/', os.path.join(settings.BASE_DIR, 'validator/static/'))
    open_file = open(file, 'rb')
    image = File(open_file)
    name = base64.b64encode(image.read())
    open_file.close()

    return JsonResponse({'plot': name.decode('utf-8')}, safe=True)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary_statistics(request):
    """Show statistics table on results page"""
    validation_id = request.query_params.get('id', None)
    validation = get_object_or_404(ValidationRun, id=validation_id)
    # resetting index added, otherwise there would be a row shift between the index column header and the header of the
    # rest of the columns when df rendered as html
    inspection_table = get_inspection_table(validation)

    if isinstance(inspection_table, str):
        return HttpResponse('error file size')

    return HttpResponse(
        inspection_table.reset_index().to_html(
            table_id=None,
            classes=['table', 'table-bordered', 'table-striped'],
            index=False
        ))
