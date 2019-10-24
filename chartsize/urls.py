from django.urls import path
from .views import ChartSizeListView, ChartSizeCreateView, ChartSizeUpdateView, chart_size_delete_view, ChartSizeManagerView
from .ajax_views import ajax_chart_size_modify_view
app_name = 'size_chart'

urlpatterns = [
    path('list-view/', ChartSizeListView.as_view(), name='list'),
    path('create-view/', ChartSizeCreateView.as_view(), name='create'),
    path('update-view/<int:pk>/', ChartSizeUpdateView.as_view(), name='update'),
    path('delete-view/<int:pk>/', chart_size_delete_view, name='delete'),
    path('manager/<int:pk>/', ChartSizeManagerView.as_view(), name='chart_manager'),

    #  ajax views
    path('ajax/modify-manager/<int:pk>/<int:dk>/<slug:action>/', ajax_chart_size_modify_view, name='ajax_modify_manager'),

]