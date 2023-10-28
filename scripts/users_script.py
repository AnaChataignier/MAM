# scripts/users_script.py
from django.contrib.auth.models import Group
from authentication.models import CustomUser
from faker import Faker  # Certifique-se de que o Faker esteja instalado


fake = Faker(["pt_BR"])

# Defina as variáveis de grupo no escopo global
staff_group = None
tecnico_group = None


def create_groups():
    # Use as variáveis globais
    global staff_group, tecnico_group

    # Cria o grupo "Staff" se ele não existir
    staff_group, _ = Group.objects.get_or_create(name="Staff")

    # Cria o grupo "Técnico" se ele não existir
    tecnico_group, _ = Group.objects.get_or_create(name="Técnico")


def create_users(num_users=10):
    # Use as variáveis globais
    global staff_group, tecnico_group

    # Cria 10 usuários com a senha "Teste123@"
    for _ in range(num_users):
        user = CustomUser.objects.create_user(
            username=fake.user_name(),  # Substitua por um valor adequado
            email=fake.email(),  # Substitua por um valor adequado
            first_name=fake.first_name(),  # Substitua por um valor adequado
            last_name=fake.last_name(),  # Substitua por um valor adequado
            password="Teste123@",
            cep="22010-010",  # Substitua por um valor adequado
            telefone=fake.phone_number(),  # Substitua por um valor adequado
            endereco_completo=fake.address(),  # Substitua por um valor adequado
        )

        # Adiciona 2 usuários ao grupo "Staff"
        if _ < 2:
            user.groups.add(staff_group)

        # Adiciona os outros 8 usuários ao grupo "Técnico"
        else:
            user.groups.add(tecnico_group)


def run():
    create_groups()
    create_users()


if __name__ == "__main__":
    run()
