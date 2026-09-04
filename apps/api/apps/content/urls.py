from django.urls import path

from . import views

urlpatterns = [
    path("zoos/<slug:zoo_slug>/", views.ZooSummaryView.as_view(), name="zoo-summary"),
    path("zoos/<slug:zoo_slug>/quests/", views.QuestListView.as_view(), name="quest-list"),
    path(
        "zoos/<slug:zoo_slug>/quests/<slug:quest_slug>/", views.QuestDetailView.as_view(), name="quest-detail"
    ),
    path("zoos/<slug:zoo_slug>/map/", views.MapView.as_view(), name="zoo-map"),
    path("zoos/<slug:zoo_slug>/animals/", views.AnimalListView.as_view(), name="animal-list"),
    path(
        "zoos/<slug:zoo_slug>/animals/<slug:animal_slug>/",
        views.AnimalDetailView.as_view(),
        name="animal-detail",
    ),
    path("markers/<str:code>/", views.MarkerLookupView.as_view(), name="marker-lookup"),
]
