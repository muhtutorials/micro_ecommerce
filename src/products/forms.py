from django.forms import ModelForm, modelformset_factory, inlineformset_factory, FileField

from .models import Product, ProductAttachment


input_class = 'form-control'


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'handle', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = input_class


class ProductAttachmentForm(ModelForm):
    file = FileField(required=True)

    class Meta:
        model = ProductAttachment
        fields = ['file', 'name', 'is_free', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field in ['is_free', 'is_active']:
                continue
            self.fields[field].widget.attrs['class'] = input_class


ProductAttachmentFormset = modelformset_factory(
    ProductAttachment,
    form=ProductAttachmentForm,
)


ProductAttachmentInlineFormset = inlineformset_factory(
    Product,
    ProductAttachment,
    form=ProductAttachmentForm,
    formset=ProductAttachmentFormset,
    fields=['file', 'name', 'is_free', 'is_active'],
    extra=0,
    can_delete=True
)
