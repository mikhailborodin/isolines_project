import geojson
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseRedirect

from scipy.interpolate import griddata

from .models import UploadedFile
from .forms import UploadFileForm

matplotlib.use('agg')  # Use non-GUI backend


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            UploadedFile.objects.create(file=file)
            return HttpResponseRedirect('/isolines/')  # Redirect to success page
    else:
        form = UploadFileForm()

    return render(request, 'upload.html', {'form': form})


@csrf_exempt
def generate_isolines(request):
    last_geojson = UploadedFile.objects.last()
    data = gpd.read_file(last_geojson.file.path)
    # Determine the bounding box
    min_lon, min_lat, max_lon, max_lat = data.total_bounds

    spacing = 0.1  # Spacing of 0.1 degrees

    # Generate the grid points
    lat = np.arange(min_lat, max_lat + spacing, spacing)
    lon = np.arange(min_lon, max_lon + spacing, spacing)
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    grid_points = np.column_stack((lon_grid.ravel(), lat_grid.ravel()))

    # Assign values to the grid points
    z = data['title'].tolist()

    # Set isoline intervals
    isoline_intervals = set(data['title'])
    points = data.geometry.apply(lambda point: (point.x, point.y))
    # Perform interpolation
    interpolated_values = griddata(
        np.transpose(np.column_stack(points.values)),
        z,
        grid_points,
        method='linear',
    )

    # Generate isolines
    isolines = {}
    for interval in isoline_intervals:
        contour = plt.contour(
            lon_grid,
            lat_grid,
            interpolated_values.reshape(lon_grid.shape),
            levels=[interval],
            algorithm='mpl2014',  # 'mpl2005', 'mpl2014', 'serial', 'threaded'
        )
        if contour.allsegs[0]:
            geometry = [list(coords) for coords in contour.allsegs[0][0]]
            isoline = geojson.Feature(geometry=geojson.LineString(geometry), properties={"value": interval})
            isolines[str(interval)] = isoline

    # Create a GeoJSON FeatureCollection
    feature_collection = geojson.FeatureCollection(list(isolines.values()))

    return JsonResponse(feature_collection, safe=False)
