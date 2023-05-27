import mimetypes

from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProductForm, ProductAttachmentInlineFormset
from .models import Product, ProductAttachment


def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save(commit=False)
        if request.user.is_authenticated:
            product.user = request.user
            product.save()
            return redirect('/products')
        form.add_error(None, error='You must be logged in to create products')
    context = {'form': form}
    return render(request, 'products/create.html', context)


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/list.html', {'products': products})


def product_detail(request, handle):
    product = get_object_or_404(Product, handle=handle)
    is_owner = False
    if request.user.is_authenticated:
        is_owner = request.user.purchase_set.filter(product=product, completed=True).exists()
    context = {'product': product, 'is_owner': is_owner}
    return render(request, 'products/detail.html', context)


def product_update(request, handle):
    product = get_object_or_404(Product, handle=handle)
    is_owner = product.user == request.user
    if not is_owner:
        return HttpResponseBadRequest()
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    formset = ProductAttachmentInlineFormset(
        request.POST or None,
        request.FILES or None,
        queryset=product.productattachment_set.all()
    )
    if form.is_valid() and formset.is_valid():
        instance = form.save()
        formset.save(commit=False)
        for f in formset:
            is_delete = f.cleaned_data.get('DELETE')
            try:
                attachment = f.save(commit=False)
            except:
                attachment = None
            if attachment is not None:
                if is_delete:
                    if attachment.pk:
                        attachment.delete()
                else:
                    attachment.product = instance
                    attachment.save()
        return redirect(product.get_update_url())
    context = {'product': product, 'form': form, 'formset': formset}
    return render(request, 'products/update.html', context)


def product_attachment_download(request, handle, pk):
    attachment = get_object_or_404(ProductAttachment, product__handle=handle, pk=pk)
    can_download = attachment.is_free or False
    if request.user.is_authenticated:
        can_download = True
    if not can_download:
        return HttpResponseBadRequest()
    file = attachment.file.open(mode='rb')
    filename = attachment.file.name
    content_type, _ = mimetypes.guess_type(filename)
    response = FileResponse(file)
    response['Content-Type'] = content_type or 'application/octet-stream'
    # response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
