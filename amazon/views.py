from django.views.generic import TemplateView, ListView

from .models import Product


class Lp(TemplateView):
    template_name = 'amazon/lp.html'


class ItemList(ListView):
    model = Product
    template_name = 'amazon/item_list.html'

    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] is not None:
            q = self.request.GET['q']
            products = products.filter(name__icontains=q)
        return products
