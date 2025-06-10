from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.InfoScrapperDefaultPage, basename='default')
#router.register(r'', views.InfoScrapperViewSet, basename='info')

urlpatterns = router.urls