from functools import wraps
from django.http import HttpResponse
from staff.models import OrdemDeServico


def is_staff(user):
    return user.groups.filter(name="Staff").exists()


def is_tecnico(user):
    return user.groups.filter(name="Técnico").exists()

def is_gerente(user):
    return user.groups.filter(name="Gerente").exists()



def is_tecnico_and_owner(view_func):
    @wraps(view_func)
    def _wrapped_view(request, ordem_id, *args, **kwargs):
        user = request.user
        try:
            ordem = OrdemDeServico.objects.get(id=ordem_id)
            if user.groups.filter(name="Técnico").exists() and ordem.tecnico == user:
                return view_func(request, ordem_id, *args, **kwargs)
        except OrdemDeServico.DoesNotExist:
            return HttpResponse("Os não existe")

        return HttpResponse(
            "Acesso não autorizado"
        )  # Ou redirecione para uma página de erro

    return _wrapped_view
