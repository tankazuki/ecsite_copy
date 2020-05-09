from django.views.generic import TemplateView, ListView, DetailView

from .models import Product


class Lp(TemplateView):
    template_name = 'amazon/lp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Product.objects.all()
        context['items'] = items
        return context


class ItemList(ListView):
    model = Product
    template_name = 'amazon/item_list.html'

    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] is not None:
            q = self.request.GET['q']
            products = products.filter(name__icontains=q)
        return products


class ItemDetail(DetailView):
    model = Product
    template_name = 'amazon/item_detail.html'