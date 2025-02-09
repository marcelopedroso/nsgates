from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserAdminForm(forms.ModelForm):
    restore_user = forms.BooleanField(
        required=False, 
        initial=False, 
        label="Restaurar usuário excluído?",
        help_text="Este usuário já existe e foi excluído. Marque essa opção para restaurá-lo."
    )

    class Meta:
        model = CustomUser
        fields = "__all__"

    def clean(self):
        """Verifica se o usuário já existe e foi excluído"""
        cleaned_data = super().clean()
        username = cleaned_data.get("username")

        existing_user = CustomUser.all_objects.filter(username=username).first()
        if existing_user and existing_user.deleted_at is not None:
            if not cleaned_data.get("restore_user"):
                raise forms.ValidationError(
                    "Este usuário já foi excluído. Marque a opção 'Restaurar usuário excluído?' para reativá-lo."
                )

        return cleaned_data
